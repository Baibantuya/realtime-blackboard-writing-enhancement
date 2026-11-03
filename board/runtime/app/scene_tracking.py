"""Small-image object persistence and frame-bound tile evidence.

This is a classical-vision candidate, not a semantic person detector. Ambiguous
thick writing can be held as occlusion; real scene replay is a release gate.
"""
from dataclasses import dataclass, replace
import math
import struct
import zlib

import cv2
import numpy as np

VISIBLE, INITIALIZE, SURFACE_VALID, OCCLUDED = (1 << 16, 1 << 17, 1 << 18, 1 << 19)
REVEAL_OBSERVATION = 1 << 20
UNKNOWN_STATE, OCCLUDED_STATE, REVEAL_PENDING, VISIBLE_STATE = range(4)
ABI = 0x57425321


@dataclass(frozen=True)
class RGB565Lattice:
    """Owned CPU snapshot; safe to pass to workers after releasing a DMA view."""
    width: int
    height: int
    step: int
    pixels: np.ndarray

    def __post_init__(self):
        if self.step < 1 or self.width < 1 or self.height < 1:
            raise ValueError('Invalid lattice geometry')
        expected=((self.height+self.step-1)//self.step,
                  (self.width+self.step-1)//self.step)
        if self.pixels.shape!=expected or self.pixels.dtype!=np.uint16:
            raise ValueError('Invalid lattice raster')
        owned=np.array(self.pixels,copy=True,order='C')
        owned.flags.writeable=False
        object.__setattr__(self,'pixels',owned)


def unpack565(p):
    p = np.asarray(p, dtype=np.uint16)
    r, g, b = (p >> 11) & 31, (p >> 5) & 63, p & 31
    return np.stack(((r << 3) | (r >> 2), (g << 2) | (g >> 4),
                     (b << 3) | (b >> 2)), axis=-1).astype(np.uint8)


def pack565(rgb):
    p = np.asarray(rgb, dtype=np.uint16)
    return ((p[..., 0] & 248) << 8) | ((p[..., 1] & 252) << 3) | (p[..., 2] >> 3)


def max_channel_difference(a,b):
    """Exact L-infinity residual using contiguous SIMD channel operations."""
    channels=cv2.split(cv2.absdiff(a,b))
    return cv2.max(cv2.max(channels[0],channels[1]),channels[2])


def channel_bounds(values):
    """Exact channel extrema without strided NumPy reductions on ARM."""
    a,b,c=cv2.split(values)
    return cv2.min(cv2.min(a,b),c),cv2.max(cv2.max(a,b),c)


@dataclass(frozen=True)
class FrameContext:
    capture_epoch: int
    sequence: int
    geometry_epoch: int
    history_epoch: int
    capture_ts: float

    def __post_init__(self):
        if min(self.identity) < 0 or not math.isfinite(self.capture_ts):
            raise ValueError('Invalid frame identity/time')
        if max(self.identity) >= 1 << 64:
            raise ValueError('Identity exceeds uint64')

    @property
    def identity(self):
        return self.capture_epoch, self.sequence, self.geometry_epoch, self.history_epoch

    @property
    def epochs(self):
        return self.capture_epoch, self.geometry_epoch, self.history_epoch

    @property
    def cookie(self):
        # A kernel tripwire; full tuple matching on the host is still mandatory.
        return zlib.crc32(struct.pack('<4Q', *self.identity)) or 1


@dataclass(frozen=True)
class ScenePacket:
    context: FrameContext
    metadata: np.ndarray
    visibility: np.ndarray
    object_ids: np.ndarray
    hold: bool
    valid_until: float
    reason: str
    finalized: bool = True

    def __post_init__(self):
        if not math.isfinite(self.valid_until) or self.valid_until < self.context.capture_ts:
            raise ValueError('Invalid metadata lifetime')
        # Own snapshots: later tracker work must not mutate an in-flight packet.
        for name in ('metadata', 'visibility', 'object_ids'):
            value = np.array(getattr(self, name), copy=True)
            value.flags.writeable = False
            object.__setattr__(self, name, value)


class SceneTracker:
    def __init__(self, width, height, max_gap=0.75, reveal_observations=2,
                 object_delta=28, max_small_width=320, max_small_height=180):
        if width < 16 or width > 1920 or width % 16 or not 1 <= height <= 1080:
            raise ValueError('Unsupported RGB565 raster')
        if (not math.isfinite(max_gap) or max_gap <= 0 or not 2 <= reveal_observations <= 15 or
                not 1 <= object_delta <= 255 or max_small_width < 16 or max_small_height < 1):
            raise ValueError('Invalid tracking policy')
        self.width, self.height = width, height
        self.gw, self.gh = width // 16, (height + 15) // 16
        self.step = max(1, math.ceil(max(width / max_small_width, height / max_small_height)))
        self.max_gap, self.reveal_observations = max_gap, reveal_observations
        self.object_delta = object_delta
        self.last = None
        self.roi=np.ones((self.gh,self.gw),bool)
        self._reset()

    def _reset(self):
        self.reference = self.surface_rgb = self.previous_ids = None
        self.foreground_reference = None
        self.previous_frame_rgb = None
        self.visibility = np.zeros((self.gh, self.gw), np.uint8)
        self.reveal_count = np.zeros_like(self.visibility)
        self.initialized = np.zeros_like(self.visibility, dtype=bool)
        self.next_object_id = 1
        self.needs_bootstrap = True
        self.last_commit_sequence = -1
        self.light_offset = np.zeros(3, np.int16)
        self.latest_rgb = self.latest_change = self.latest_bare = self.prior_reference = None
        self.illumination_ready = True
        self.material_updates = 0
        self.last_aligned = None

    def snapshot(self, raw):
        # Caller still owns the ring lease and its cache-coherent CPU view here.
        if raw.shape != (self.height,self.width) or raw.dtype!=np.uint16:
            raise ValueError('Expected exact uint16 RGB565 frame')
        return RGB565Lattice(self.width,self.height,self.step,raw[::self.step,::self.step])

    def _small(self, raw, order):
        if order not in (0, 1, 2, 3):
            raise ValueError('Invalid channel order')
        # Copy only the sampling lattice before the producer may release A/B.
        if isinstance(raw,RGB565Lattice):
            if (raw.width,raw.height,raw.step)!=(self.width,self.height,self.step):
                raise ValueError('Snapshot belongs to a different tracker geometry')
            pixels=raw.pixels
        else:
            if raw.shape != (self.height,self.width) or raw.dtype!=np.uint16:
                raise ValueError('Expected exact uint16 RGB565 frame')
            pixels=raw[::self.step,::self.step].copy()
        rgb = unpack565(pixels)
        return rgb[..., ::-1].copy() if order & 1 else rgb

    def _grid_any(self, mask):
        # Conservative footprint: any covered sample blocks the tile and margin.
        dilated = cv2.dilate(mask.astype(np.uint8), np.ones((5, 5), np.uint8))
        return cv2.resize(dilated.astype(np.float32), (self.gw, self.gh),
                          interpolation=cv2.INTER_AREA) > 0

    def _surface(self, rgb):
        # Trusted startup only. Infer the material under existing ink from its
        # exposed surroundings; clipping a white-filled tile to board+24 left
        # a permanent residual above the erase threshold after erasure.
        roi=cv2.resize(self.roi.astype(np.uint8),(rgb.shape[1],rgb.shape[0]),interpolation=cv2.INTER_NEAREST)>0
        samples=rgb[roi] if np.any(roi) else rgb.reshape(-1,3)
        material=np.percentile(samples,20,axis=0).astype(np.uint8)
        base=rgb.copy();base[~roi]=material
        # Trusted startup only: a local morphological background rejects narrow
        # chalk while retaining broad illumination/glare. The old global color
        # outlier test removed the bright middle of an otherwise bare board.
        local=cv2.morphologyEx(base,cv2.MORPH_OPEN,np.ones((31,31),np.uint8))
        ink=np.max(np.abs(base.astype(np.int16)-local.astype(np.int16)),axis=2)>24
        clean=cv2.inpaint(base,(ink&roi).astype(np.uint8),3,cv2.INPAINT_TELEA)
        return cv2.resize(cv2.medianBlur(clean,5),(self.gw,self.gh),interpolation=cv2.INTER_AREA)

    def _contrast_limit(self):
        # The same relative occlusion contrast is weaker in an unlit part of
        # the board. Scale from trusted local material, never from a person.
        level=np.max(self.surface_rgb,axis=2).astype(np.float32)
        limit=np.clip(self.object_delta*level/80.,18,self.object_delta)
        return cv2.resize(limit,(self.latest_rgb.shape[1],self.latest_rgb.shape[0]),
                          interpolation=cv2.INTER_NEAREST)

    def _align_light(self, rgb):
        """Estimate an absolute offset from canonical, exposed board samples.

        All stored references use the same photometric coordinates. In
        particular a frozen surface must never be compared after subtracting
        only the most recent exposure increment.
        """
        shape = (rgb.shape[1], rgb.shape[0])
        exposed = cv2.resize(((self.visibility == VISIBLE_STATE) & self.roi).astype(np.uint8),
                             shape, interpolation=cv2.INTER_NEAREST) != 0
        surface = cv2.resize(self.surface_rgb, shape, interpolation=cv2.INTER_NEAREST)
        known_bare = max_channel_difference(self.reference, surface) <= 16
        delta = cv2.subtract(rgb, self.reference, dtype=cv2.CV_16S)
        residual = cv2.subtract(delta, tuple(float(v) for v in self.light_offset)+(0.,))
        low, high = channel_bounds(residual)
        close = (low >= -24) & (high <= 24)
        samples = exposed & known_bare & close
        minimum = max(12, np.count_nonzero(exposed) // 10)
        if np.count_nonzero(samples) >= minimum:
            estimate = np.rint(np.median(delta[samples], axis=0)).astype(np.int16)
            unchanged = np.max(np.abs(estimate - self.light_offset)) <= 2
            # Support must be spatially distributed, not one sleeve or hand.
            support = 0
            required = 0
            # The unchanged-offset branch already accepts without a quorum;
            # avoid computing spatial medians which cannot change its result.
            if not unchanged:
                roi_small = cv2.resize(self.roi.astype(np.uint8), shape, interpolation=cv2.INTER_NEAREST) != 0
                ry, rx = np.nonzero(roi_small)
                for rows in np.array_split(np.arange(ry.min(), ry.max()+1), 2):
                    for cols in np.array_split(np.arange(rx.min(), rx.max()+1), 2):
                        if not len(rows) or not len(cols):
                            continue
                        required += 1
                        region = (slice(rows[0], rows[-1]+1), slice(cols[0], cols[-1]+1))
                        mask = samples[region]
                        values = delta[region][mask]
                        if len(values) >= 4 and np.max(np.abs(np.median(values, axis=0) - estimate)) <= 8:
                            support += 1
            if (support >= min(3, required) or unchanged) and np.max(np.abs(estimate)) <= 96:
                self.light_offset = estimate
                self.illumination_ready = True
            else:
                self.illumination_ready = False
        else:
            # Missing samples during occlusion do not authorize a new board.
            # Keep the established offset. Regions still have their object mask.
            self.illumination_ready = True
        return cv2.subtract(rgb, tuple(float(v) for v in self.light_offset)+(0.,), dtype=cv2.CV_8U)


    def _objects(self, changed):
        filled = cv2.morphologyEx(changed.astype(np.uint8), cv2.MORPH_CLOSE,
                                 np.ones((3, 3), np.uint8))
        # Require a genuinely thick changed core. Closing a network of chalk
        # strokes must not manufacture a solid "person" interior.
        interior = cv2.erode(changed.astype(np.uint8),np.ones((5,5),np.uint8))
        _,core_labels,core_stats,_=cv2.connectedComponentsWithStats(interior,connectivity=8)
        core_ok=core_stats[:,cv2.CC_STAT_AREA]>=4;core_ok[0]=False
        interior=core_ok[core_labels]
        count, labels, stats, _ = cv2.connectedComponentsWithStats(filled, connectivity=8)
        ids = np.zeros_like(labels, dtype=np.int32)
        for label in range(1, count):
            x, y, w, h, area = stats[label]
            if area < max(12, changed.size//800):
                continue
            region = labels[y:y+h,x:x+w] == label
            previous = self.previous_ids[y:y+h,x:x+w][region]
            if self.previous_frame_rgb is not None and self.latest_rgb is not None:
                same_appearance=max_channel_difference(
                    self.latest_rgb[y:y+h,x:x+w],
                    self.previous_frame_rgb[y:y+h,x:x+w])[region] <= 16
                previous=previous[same_appearance]
            previous = previous[previous > 0]
            if previous.size:
                # A retreat exposing a few same-colored chalk strokes is not
                # identity continuity for the vanished, much larger person.
                oid=int(np.bincount(previous).argmax())
                if previous.size < max(4, .08*np.count_nonzero(self.previous_ids==oid)):
                    previous=previous[:0]
            # Thickness is a birth test, never a repeated identity test: a
            # tracked person's remaining narrow silhouette is still foreground.
            if not previous.size and np.count_nonzero(interior[y:y+h,x:x+w][region]) < 4:
                continue
            if previous.size:
                oid = int(np.bincount(previous).argmax())
            else:
                oid = self.next_object_id
                self.next_object_id += 1
            # A component's bounding rectangle is an index range, not occupied
            # foreground. Filling it froze large exposed board areas in field.
            view=ids[y:y+h,x:x+w]
            view[region]=oid
        return ids

    def prepare(self, raw, context, **kwargs):
        """Run during v15 Restore; the returned packet is provisional until B done."""
        return replace(self.analyze(raw, context, restored=None, **kwargs), finalized=False)

    def refine(self, packet, restored, restored_context, order=0):
        """Bounded same-frame v15 supplement; never reuse stale B or commit first."""
        if (restored_context != packet.context or packet.context != self.last or
                packet.context.sequence <= self.last_commit_sequence):
            raise ValueError('Refinement must precede commit and the next PS frame')
        if packet.hold:
            return replace(packet, finalized=True)
        auxiliary = self._small(restored, order).astype(np.int16)
        difference = max_channel_difference(self.latest_rgb.astype(np.int16),auxiliary)
        small_roi=cv2.resize(self.roi.astype(np.uint8),(difference.shape[1],difference.shape[0]),interpolation=cv2.INTER_NEAREST)>0
        limit=self._contrast_limit()
        weak_object = (difference >= limit) & (self.latest_change >= limit/2) & small_roi
        ids = self._objects(((self.previous_ids > 0) | weak_object) & ~self.latest_bare)
        occupied = self._grid_any(ids > 0)
        self.visibility[occupied] = OCCLUDED_STATE
        self.reveal_count[occupied] = 0
        rollback = cv2.resize(occupied.astype(np.uint8), (self.reference.shape[1], self.reference.shape[0]),
                              interpolation=cv2.INTER_NEAREST) > 0
        cv2.copyTo(self.prior_reference,rollback.astype(np.uint8),self.reference)
        self.previous_ids = ids
        return self._packet(packet.context, False, packet.reason+'_v15_refined')

    def analyze(self, raw, context, restored=None, geometry_safe=True,
                trusted_bootstrap=False, order=0, restored_context=None):
        self.frame_material_updates = 0
        rgb = self._small(raw, order)
        if restored is not None and restored_context != context:
            raise ValueError('Auxiliary v15 frame identity mismatch')
        auxiliary_rgb = self._small(restored, order) if restored is not None else None
        if self.last is not None:
            if context.epochs == self.last.epochs:
                if context.sequence <= self.last.sequence or context.capture_ts <= self.last.capture_ts:
                    raise ValueError('Duplicate/out-of-order frame')
            elif context.capture_ts <= self.last.capture_ts:
                raise ValueError('Reordered epoch transition')
        if self.last is not None and context.epochs != self.last.epochs:
            if (context.capture_epoch,context.geometry_epoch)==(self.last.capture_epoch,self.last.geometry_epoch):
                # Admission revocation invalidates consecutive evidence, not the
                # identity/material/content of the same coordinate system.
                self.reveal_count.fill(0)
            else:self._reset()
        gap = self.last is not None and context.capture_ts - self.last.capture_ts > self.max_gap
        if gap:
            # No consecutive evidence survives a processing gap; objects persist.
            self.reveal_count.fill(0)
        self.last = context
        if not geometry_safe:
            self.needs_bootstrap = True
            return self._packet(context, True, 'geometry_unsafe')
        if trusted_bootstrap and not self.needs_bootstrap:
            self._reset()
        self.previous_frame_rgb = self.latest_rgb
        self.latest_rgb = rgb.copy()
        if self.needs_bootstrap:
            if not trusted_bootstrap:
                return self._packet(context, True, 'trusted_board_required')
            self.surface_rgb = self._surface(rgb)
            self.light_offset.fill(0)
            self.illumination_ready = True
            self.reference = rgb.copy()
            self.foreground_reference = rgb.copy()
            self.visibility.fill(VISIBLE_STATE)
            self.visibility[~self.roi]=UNKNOWN_STATE
            self.reveal_count.fill(0)
            self.previous_ids = np.zeros(rgb.shape[:2], np.int32)
            self.latest_change = np.zeros(rgb.shape[:2], np.int16)
            surface=cv2.resize(self.surface_rgb,(rgb.shape[1],rgb.shape[0]),interpolation=cv2.INTER_NEAREST)
            self.latest_bare=max_channel_difference(rgb.astype(np.int16),surface.astype(np.int16))<=16
            self.prior_reference = self.reference.copy()
            self.last_aligned = rgb.copy()
            self.needs_bootstrap = False
            # The caller also resets the palette canvas on a trusted rebase.
            self.initialized.fill(False)
        else:
            self.prior_reference = self.reference.copy()
            aligned = self._align_light(rgb)
            if not self.illumination_ready:
                return self._packet(context, True, 'illumination_untrusted')
            self.last_aligned = aligned.copy()
            material_change = max_channel_difference(aligned.astype(np.int16), self.reference.astype(np.int16))
            self.latest_change = material_change
            surface=cv2.resize(self.surface_rgb,(rgb.shape[1],rgb.shape[0]),interpolation=cv2.INTER_NEAREST)
            is_normal_bare = max_channel_difference(aligned, surface) <= 16
            darkening = cv2.subtract(surface, aligned)
            b, g, r = cv2.split(darkening)
            chroma = cv2.max(cv2.absdiff(r, g), cv2.absdiff(g, b))
            max_dark = cv2.max(cv2.max(r, g), b)
            brightening = cv2.subtract(aligned, surface)
            br_b, br_g, br_r = cv2.split(brightening)
            max_bright = cv2.max(cv2.max(br_b, br_g), br_r)
            is_shadow_bare = (max_dark <= 36) & (chroma <= 10) & (max_bright <= 4)
            self.latest_bare = is_normal_bare | is_shadow_bare
            limit=self._contrast_limit()
            changed = material_change >= limit
            # A slowly entering silhouette must not disappear into the mutable
            # text reference one thin edge at a time. Keep a trusted anchor for
            # object birth; sparse lettering still cannot pass the thick core.
            anchored = max_channel_difference(
                aligned.astype(np.int16),
                self.foreground_reference.astype(np.int16))
            changed |= anchored >= limit
            changed |= (self.previous_ids > 0) & (material_change >= limit/2)
            if restored is not None:
                auxiliary = auxiliary_rgb.astype(np.int16)
                # v15 is an auxiliary object seed, never an erase veto. A sparse
                # old-letter difference does not form a thick object interior.
                restored_difference = max_channel_difference(rgb.astype(np.int16),auxiliary)
                changed |= ((restored_difference >= limit) &
                            (material_change >= limit/2))
            small_roi=cv2.resize(self.roi.astype(np.uint8),(changed.shape[1],changed.shape[0]),interpolation=cv2.INTER_NEAREST)>0
            changed &= small_roi
            # Temporal change alone is not a person: erasure exposes the trusted
            # board material. Only non-material dense regions seed foreground.
            changed &= ~self.latest_bare
            ids = self._objects(changed)
            occupied = self._grid_any(ids > 0)
            was_blocked = (self.visibility == OCCLUDED_STATE) | (self.visibility == REVEAL_PENDING)
            reveal = was_blocked & ~occupied
            self.reveal_count[occupied] = 0
            self.reveal_count[reveal] = np.minimum(self.reveal_count[reveal] + 1, self.reveal_observations)
            self.visibility[occupied] = OCCLUDED_STATE
            self.visibility[reveal] = REVEAL_PENDING
            self.visibility[reveal & (self.reveal_count >= self.reveal_observations)] = VISIBLE_STATE
            self.previous_ids = ids
            # Visible changes (new writing/erasure) become the PS object reference;
            # the PL palette remains the sole owner of confirmed output content.
            exposed = cv2.resize((self.visibility == VISIBLE_STATE).astype(np.uint8),
                                 (rgb.shape[1], rgb.shape[0]), interpolation=cv2.INTER_NEAREST) > 0
            cv2.copyTo(aligned,exposed.astype(np.uint8),self.reference)
        return self._packet(context, bool(gap), 'ok' if not gap else 'gap_cleared_candidates')

    def _packet(self, context, hold, reason):
        metadata = np.zeros((self.gh, self.gw), np.uint32)
        if self.surface_rgb is not None and not hold:
            lit_surface = np.clip(self.surface_rgb.astype(np.int16) + self.light_offset, 0, 255)
            metadata[:] = pack565(lit_surface).astype(np.uint32) | SURFACE_VALID
            visible = self.visibility == VISIBLE_STATE
            metadata[visible] |= VISIBLE
            metadata[visible & ~self.initialized] |= INITIALIZE
            metadata[self.visibility == OCCLUDED_STATE] |= OCCLUDED
            metadata[self.visibility == REVEAL_PENDING] |= REVEAL_OBSERVATION
            metadata[~self.roi]=0
            # Frozen startup material. This initial candidate deliberately does
            # not learn a stationary person's color into a new board model.
        object_ids = np.zeros((self.gh, self.gw), np.int32)
        if self.previous_ids is not None:
            object_ids = cv2.resize(self.previous_ids.astype(np.float32), (self.gw, self.gh),
                                    interpolation=cv2.INTER_NEAREST).astype(np.int32)
        return ScenePacket(context, metadata, self.visibility, object_ids, hold,
                           context.capture_ts + self.max_gap, reason)

    def committed(self, packet):
        if (not packet.finalized or self.needs_bootstrap or self.last is None or self.last.epochs != packet.context.epochs or
                packet.context.sequence > self.last.sequence or
                packet.context.sequence <= self.last_commit_sequence):
            raise ValueError('Out-of-order/cross-epoch commit acknowledgment')
        if not packet.hold:
            self.initialized[(packet.metadata & VISIBLE) != 0] = True
            self.last_commit_sequence = packet.context.sequence


class ScenePairScheduler:
    """Own both A/B leases until quantize done, timeout or explicit cancellation.

    The adapter owns CMA sync and IP launch. This state machine never frees an
    active buffer; it also never waits forever for a missing PS result.
    """
    def __init__(self, capacity=3):
        if capacity < 1: raise ValueError('Positive pair capacity required')
        self.capacity = capacity
        self.pending = {}

    def admit(self, context, a, b, release, deadline):
        if context.identity in self.pending or not math.isfinite(deadline):
            raise ValueError('Duplicate pair/invalid deadline')
        if len(self.pending) >= self.capacity:
            raise RuntimeError('Pair capacity exhausted; apply upstream backpressure')
        if a is b or any(a is p[1] or b is p[2] for p in self.pending.values()):
            raise ValueError('Interstage buffer is already owned')
        self.pending[context.identity] = [context, a, b, release, deadline, 'WAITING', None, False]

    def restore_done(self, context, restored_context):
        pair = self.pending[context.identity]
        if restored_context != context or pair[7] or pair[5] != 'WAITING':
            raise ValueError('Unexpected/mismatched Restore completion')
        pair[7] = True

    def ready(self, context, packet, now):
        pair = self.pending[context.identity]
        if next(iter(self.pending)) != context.identity:
            raise RuntimeError('Stateful canvas must consume pairs in admission order')
        if pair[5] != 'WAITING':
            raise RuntimeError('Pair already launched')
        if packet is not None and packet.context != context:
            raise ValueError('Cross-frame metadata')
        if not pair[7]:
            return None  # A timeout never relinquishes an active Restore writer.
        if packet is None and now < pair[4]:
            return None
        if packet is not None and not packet.finalized and now < pair[4]:
            return None
        hold = packet is None or packet.hold or not packet.finalized or now > packet.valid_until
        pair[5], pair[6] = 'RUNNING', packet
        return {'a': pair[1], 'b': pair[2], 'packet': packet, 'hold': hold}

    def done(self, context):
        pair = self.pending[context.identity]
        if pair[5] != 'RUNNING':
            raise RuntimeError('No completed launch')
        pair[3](pair[1], pair[2])
        del self.pending[context.identity]

    def cancel(self, context):
        pair = self.pending[context.identity]
        if pair[5] == 'RUNNING' or not pair[7]:
            raise RuntimeError('Quiesce Restore/Quantize before canceling an owned pair')
        pair[3](pair[1], pair[2])
        del self.pending[context.identity]
