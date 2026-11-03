"""Chinese PS screen compositor. NumPy/OpenCV only on the board; no LVGL calls.

Static Chinese text is rendered into bundled assets at build time. The source
frame is always fitted without cropping; every returned RGB565 frame is owned.
"""
from collections import OrderedDict
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

WIDTH, HEIGHT = 1920, 1080
VIDEO_REGION = (32, 168, 1440, 810)
HISTORY_RAW_REGION = (1536, 224, 320, 180)
POSITION_CODES = ('up', 'down', 'left', 'right', 'zoom_out', 'zoom_in')
ROTATION_CODES = ('clockwise', 'counterclockwise')
GUIDANCE_CODES = ('search', 'left', 'right', 'up', 'down', 'zoom_out', 'zoom_in', 'hold',
                  'clockwise', 'counterclockwise', 'confirming', 'recalibrating')


@dataclass(frozen=True)
class GuidanceSpec:
    code: str = 'search'
    evidence: str = 'no_current_board_candidate'
    next_code: Optional[str] = None
    image_rotation_degrees: Optional[float] = None

    def __post_init__(self):
        if self.code not in GUIDANCE_CODES:
            raise ValueError('unknown guidance state')
        if self.next_code is not None:
            position_sequence = self.code in ('up','down') and self.next_code in ('left','right')
            if not (position_sequence or (self.code in POSITION_CODES and self.next_code in ROTATION_CODES)):
                raise ValueError('unsupported guidance sequence')
        if self.image_rotation_degrees is not None:
            angle = self.image_rotation_degrees
            rotation = self.next_code or self.code
            if (not math.isfinite(angle) or not 3 < abs(angle) <= 20
                    or rotation not in ROTATION_CODES
                    or (rotation == 'clockwise') != (angle > 0)):
                raise ValueError('invalid image rotation convention')


def _valid_quad(corners, width, height):
    """Require an in-frame convex TL/TR/BR/BL quadrilateral, not just a bbox."""
    try:
        points = np.asarray(corners, dtype=np.float64)
        if (points.shape != (4, 2) or not np.all(np.isfinite(points))
                or width <= 0 or height <= 0
                or np.any(points[:, 0] < 0) or np.any(points[:, 0] >= width)
                or np.any(points[:, 1] < 0) or np.any(points[:, 1] >= height)):
            return None
        edges = np.roll(points, -1, axis=0) - points
        following = np.roll(edges, -1, axis=0)
        cross = edges[:, 0] * following[:, 1] - edges[:, 1] * following[:, 0]
        area = .5 * abs(np.dot(points[:, 0], np.roll(points[:, 1], -1))
                         - np.dot(points[:, 1], np.roll(points[:, 0], -1)))
        if (not np.all(cross > 0) or area < .08 * width * height
                or points[1, 0] - points[0, 0] < .1 * width
                or points[2, 0] - points[3, 0] < .1 * width
                or points[3, 1] - points[0, 1] < .05 * height
                or points[2, 1] - points[1, 1] < .05 * height):
            return None
        return points
    except (TypeError, ValueError):
        return None


def _plan_from_quad(points, width, height, evidence):
    xmin, ymin = np.min(points, axis=0)
    xmax, ymax = np.max(points, axis=0)
    top = points[1] - points[0]
    bottom = points[2] - points[3]
    angles = [math.degrees(math.atan2(edge[1], edge[0])) for edge in (top, bottom)]
    return plan_from_bounds((xmin, ymin, xmax, ymax), width, height, evidence, *angles)


def plan_from_bounds(bounds, width, height, evidence, top_angle=None, bottom_angle=None, *, small=False):
    """Advisory plan from observed extents/edges; does not manufacture corners."""
    xmin, ymin, xmax, ymax = bounds
    near = dict(up=ymin < .04 * height, down=height - 1 - ymax < .04 * height,
                left=xmin < .04 * width, right=width - 1 - xmax < .04 * width)
    position = None
    if (near['up'] and near['down']) or (near['left'] and near['right']):
        position = 'zoom_out'
    else:
        # Establish vertical clearance before suggesting a horizontal adjustment.
        position = next((code for code in ('up', 'down', 'left', 'right') if near[code]), None)
    if position is None and small:
        position = 'zoom_in'
    image_angle = None
    # Different top/bottom slopes can be perspective, not a common image tilt.
    if (top_angle is not None and bottom_angle is not None
            and top_angle * bottom_angle > 0 and abs(top_angle - bottom_angle) <= 3):
        candidate = -(top_angle + bottom_angle) / 2
        if 3 < abs(candidate) <= 20:
            image_angle = candidate
    rotation = None if image_angle is None else ('clockwise' if image_angle > 0 else 'counterclockwise')
    if position is not None:
        if position in ('up','down'):
            horizontal = next((code for code in ('left','right') if near[code]),None)
            if horizontal is not None:
                return GuidanceSpec(position,evidence,horizontal)
        return GuidanceSpec(position, evidence, rotation, image_angle)
    if rotation is not None:
        return GuidanceSpec(rotation, evidence, image_rotation_degrees=image_angle)
    return None


def guidance_from_tracker(tracker, pending_geometry=False, width=WIDTH, height=HEIGHT):
    """UI-only description; never changes geometry, admission or restoration.

    Prefer a current confirmation candidate. Never infer a movement direction
    from stale accepted corners while recalibrating or after a failed measure.
    Position arrows mean camera aiming. Rotation arrows mean rotating the IMAGE
    as seen on screen; they must not be interpreted as camera-body roll commands.
    These are advisory UI rules, never new geometry acceptance requirements.
    """
    state = getattr(tracker, 'last', {}).get('geometry_state', '')
    recalibrating = bool(getattr(tracker, 'recalibrating', False))
    corners = getattr(tracker, 'pending', None)
    evidence = 'current_confirmation_candidate'
    if corners is None and state == 'locked' and not recalibrating:
        corners = getattr(tracker, 'accepted', None)
        evidence = 'locked_board_measurement'
    if corners is not None:
        points = _valid_quad(corners, width, height)
        if points is not None:
            planned = _plan_from_quad(points, width, height, evidence)
            if planned is not None:
                return planned
    if pending_geometry or state == 'confirming':
        return GuidanceSpec('confirming', 'geometry_confirmation_in_progress')
    if recalibrating:
        return GuidanceSpec('recalibrating', 'explicit_recalibration')
    return GuidanceSpec()


def bgr_to_rgb565(image):
    image = np.asarray(image)
    if image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 3:
        raise ValueError('uint8 BGR image required')
    return (((image[:,:,2].astype(np.uint16) >> 3) << 11)
            | ((image[:,:,1].astype(np.uint16) >> 2) << 5)
            | (image[:,:,0].astype(np.uint16) >> 3))


def validate_frame(frame):
    frame = np.asarray(frame)
    if (frame.dtype.str != '<u2' or frame.ndim != 2 or min(frame.shape) <= 0
            or not frame.flags.c_contiguous):
        raise ValueError('packed little-endian RGB565 image required')
    return frame


def fit_rect(shape, region):
    height, width = shape
    x, y, available_w, available_h = region
    scale = min(available_w/width, available_h/height)
    shown_w = max(1, min(available_w, round(width*scale)))
    shown_h = max(1, min(available_h, round(height*scale)))
    return (x+(available_w-shown_w)//2, y+(available_h-shown_h)//2, shown_w, shown_h)


class BoardFrontend:
    def __init__(self, asset_dir=None, *, cache_pages=2):
        self.root = Path(asset_dir) if asset_dir is not None else Path(__file__).resolve().parent/'assets'
        self.manifest = json.loads((self.root/'manifest.json').read_text(encoding='utf-8'))
        if self.manifest['screen_size'] != [WIDTH, HEIGHT] or type(cache_pages) is not int or cache_pages < 1:
            raise ValueError('invalid frontend asset contract')
        for name, expected in self.manifest['sha256'].items():
            path = (self.root/name).resolve()
            if self.root.resolve() not in path.parents or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                raise ValueError('frontend asset SHA256 mismatch: '+name)
        self.cache = OrderedDict()
        self.cache_pages = cache_pages
        self.last_layout = None

    def _page(self, name):
        if name not in self.cache:
            filename = name+'.png'
            if filename not in self.manifest['sha256']:
                raise ValueError('unknown frontend page')
            image = cv2.imdecode(np.frombuffer((self.root/filename).read_bytes(), np.uint8), cv2.IMREAD_COLOR)
            if image is None or image.shape != (HEIGHT, WIDTH, 3):
                raise ValueError('invalid frontend page pixels')
            page = bgr_to_rgb565(image)
            page.flags.writeable = False
            self.cache[name] = page
            while len(self.cache) > self.cache_pages:
                self.cache.popitem(last=False)
        self.cache.move_to_end(name)
        return self.cache[name].copy()

    @staticmethod
    def _place(screen, frame, region):
        frame = validate_frame(frame)
        x, y, w, h = fit_rect(frame.shape, region)
        # Packed RGB565 must not be interpolated as one 16-bit intensity value.
        # Nearest preserves source colors, geometry and the complete field of view.
        screen[y:y+h, x:x+w] = cv2.resize(frame, (w, h), interpolation=cv2.INTER_NEAREST)
        return (x, y, w, h)

    def render_guidance(self, original_rgb565, spec=GuidanceSpec()):
        if not isinstance(spec, GuidanceSpec):
            raise ValueError('explicit GuidanceSpec required')
        page = 'guidance_' + spec.code + (('_then_' + spec.next_code) if spec.next_code else '')
        screen = self._page(page)
        raw_rect = self._place(screen, original_rgb565, VIDEO_REGION)
        self.last_layout = dict(page='guidance', state=spec.code, raw_rect=raw_rect,
                                coordinate_space='original_capture_pixels_scaled_for_display',
                                evidence=spec.evidence, next_state=spec.next_code,
                                image_rotation_degrees=spec.image_rotation_degrees,
                                rotation_convention='positive_clockwise_image_on_screen',
                                advisory_only=True, controls_restoration=False)
        return screen

    def render_history(self, original_rgb565, history_rgb565=None, *, demo=False):
        # Only a producer-supplied historical image is displayed. No inferred
        # background or synthetic restoration is generated by this frontend.
        available = history_rgb565 is not None
        name = 'history_demo' if available and demo else ('history_available' if available else 'history_empty')
        screen = self._page(name)
        raw_rect = self._place(screen, original_rgb565, HISTORY_RAW_REGION)
        history_rect = None if not available else self._place(screen, history_rgb565, VIDEO_REGION)
        self.last_layout = dict(page='history', history_available=available, raw_rect=raw_rect,
                                history_rect=history_rect, demo=bool(demo and available),
                                controls_restoration=False)
        return screen
