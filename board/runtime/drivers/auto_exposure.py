"""Blackboard-centered IMX219 exposure feedback through the Linux V4L2 driver.

The IMX219 driver owns I2C. Its exposure and analogue_gain controls write the
sensor registers; this module must not access the camera I2C bus directly.
"""
import re
import math
import subprocess
import time
from pathlib import Path

import numpy as np


def zonal_board_stats(frame, patch_size=48, corners=None, excluded=None):
    """Sparse 5x3 whole-board metering; one global exposure, no frame copy.

    Optional exclusion mask uses camera coordinates (e.g. a projected trusted
    foreground mask). No mask is inferred from color alone. Saturation includes
    highlights even when their zone is an outlier for the luminance target.
    """
    if frame.ndim != 3 or frame.shape[2] != 3 or frame.dtype != np.uint8:
        raise ValueError("Expected an HxWx3 uint8 camera frame")
    height, width = frame.shape[:2]
    if patch_size < 4 or patch_size > min(width, height) // 4:
        raise ValueError("AE patch size must fit inside the center of the frame")
    means = []
    clipped = 0
    sampled = 0
    zone_clipping=[]
    half = patch_size // 2
    points=None if corners is None else np.asarray(corners,dtype=float)
    if points is not None and (points.shape!=(4,2) or not np.all(np.isfinite(points))):raise ValueError('Invalid AE board corners')
    if excluded is not None and (excluded.shape!=(height,width) or excluded.dtype!=np.bool_):
        raise ValueError('AE exclusion must be a camera-coordinate bool mask')
    for fy in (0.2, 0.5, 0.8):
        for fx in (0.12, 0.31, 0.5, 0.69, 0.88):
            if points is None:cy,cx=round(height*fy),round(width*fx)
            else:
                xy=(1-fy)*((1-fx)*points[0]+fx*points[1])+fy*((1-fx)*points[3]+fx*points[2])
                cx,cy=map(lambda value:int(round(value)),xy)
                cx=max(half,min(width-half,cx));cy=max(half,min(height-half,cy))
            tile = frame[cy-half:cy-half+patch_size:2,
                         cx-half:cx-half+patch_size:2]
            if excluded is not None:
                valid=~excluded[cy-half:cy-half+patch_size:2,cx-half:cx-half+patch_size:2]
                if np.count_nonzero(valid)<max(4,valid.size//3):continue
                tile=tile[valid].reshape(-1,1,3)
            # V4L2 RGB3 is R,G,B. Separate luminance from chroma (BT.601),
            # and preserve the green board's real color rather than treating
            # its channels as a neutral gray reference.
            rgb = tile.astype(np.uint16)
            luma = (77*rgb[:, :, 0] + 150*rgb[:, :, 1]
                    + 29*rgb[:, :, 2]) / 256.0
            low,cutoff = np.percentile(luma, (20,70))
            means.append(float(luma[(luma>=low)&(luma<=cutoff)].mean()))
            # A saturated chroma channel is not a blown-out board patch.
            # Meter brightness clipping; blue chalk may legitimately have a
            # high B channel while its luminance and surrounding board are dark.
            zone_clip=int(np.count_nonzero(luma >= 245))
            clipped += zone_clip
            sampled += tile.shape[0] * tile.shape[1]
            zone_clipping.append(zone_clip/(tile.shape[0]*tile.shape[1]))
    if len(means)<3:raise ValueError('Insufficient exposed zones for AE')
    values=np.asarray(means)
    middle=np.median(values);spread=np.median(np.abs(values-middle))
    good=np.abs(values-middle)<=max(12,3*spread)
    # A local reflection/bright chalk patch must not hold the entire dark board
    # below target. Reduce exposure for widespread clipping (at least a quarter
    # of the board zones), rather than the single brightest sampled zone.
    clip=float(np.percentile(zone_clipping,75))
    return float(np.mean(values[good])),clip


def center_board_stats(frame, patch_size=48, corners=None):
    """Compatibility entry point, now meters the whole board."""
    return zonal_board_stats(frame,patch_size,corners)


def center_board_luma(frame, patch_size=48):
    return center_board_stats(frame, patch_size)[0]


def sensor_node(explicit=None):
    if explicit:
        return explicit
    matches = []
    for entry in sorted(Path("/sys/class/video4linux").glob("v4l-subdev*")):
        try:
            name = (entry / "name").read_text().strip().lower()
        except OSError:
            continue
        if "imx219" in name:
            matches.append("/dev/" + entry.name)
    if len(matches) != 1:
        raise RuntimeError("Expected one IMX219 subdevice; use --ae-sensor after checking media-ctl -p")
    return matches[0]


def _control_specs(node):
    result = subprocess.run(["v4l2-ctl", "-d", node, "--list-ctrls"],
                            check=True, capture_output=True, text=True, timeout=5)
    specs = {}
    for line in result.stdout.splitlines():
        match = re.match(r"\s*(exposure|analogue_gain|digital_gain)\s+.*?min=(\d+)\s+max=(\d+)"
                         r"\s+step=(\d+)\s+default=\d+\s+value=(\d+)", line)
        if match:
            name, low, high, step, value = match.groups()
            specs[name] = tuple(map(int, (low, high, step, value)))
    if "exposure" not in specs:
        raise RuntimeError("IMX219 subdevice has no readable exposure control: " + node)
    return specs


class BlackboardAutoExposure:
    def __init__(self, sensor=None, target=80, deadband=6, patch_size=48,
                 control_interval=.3, settle_seconds=.2, stable_observations=3):
        if (not 8<=target<=200 or not 1<=deadband<=32 or
                not math.isfinite(control_interval) or control_interval<=0 or
                not math.isfinite(settle_seconds) or settle_seconds<0 or not 2<=stable_observations<=16):
            raise ValueError('Invalid exposure normalization policy')
        self.sensor = sensor_node(sensor)
        self.specs = _control_specs(self.sensor)
        self.target = target
        self.deadband = deadband
        self.patch_size = patch_size
        self.exposure = self.specs["exposure"][3]
        self.gain = self.specs.get("analogue_gain", (0, 0, 1, 0))[3]
        self.digital_gain = self.specs.get("digital_gain", (256, 256, 1, 256))[3]
        self.digital_spec=None
        if "digital_gain" in self.specs:
            dlow,dhigh,dstep,dvalue=self.specs['digital_gain']
            # IMX219 digital gain is Q8 (256 = 1x). Bound electronic
            # amplification to 2x without changing frame length or VBLANK.
            cap=dlow+max(0,(min(dhigh,512)-dlow)//dstep)*dstep
            self.digital_spec=(dlow,cap,dstep,dvalue)
        self.last = None
        self.control_interval=control_interval;self.settle_seconds=settle_seconds
        self.stable_observations=stable_observations;self.stable_count=0
        self.next_control=0.;self.settle_until=0.;self.ready_for_pl=False
        self.previous_luma=None

    @staticmethod
    def _clamp_step(value, spec):
        low, high, step, _ = spec
        return max(low, min(high, low + round((value-low) / step) * step))

    def update(self, frame, corners=None, now=None):
        now=time.monotonic() if now is None else now
        if not math.isfinite(now):raise ValueError('Invalid AE clock')
        luma, clipped_fraction = center_board_stats(frame, self.patch_size,corners)
        exposure, gain, digital = self.exposure, self.gain, self.digital_gain
        low, high, step, _ = self.specs["exposure"]
        control_due=now>=self.next_control and now>=self.settle_until
        if control_due and self.digital_spec is not None and digital>self.digital_spec[1]:
            digital=self.digital_spec[1]
        elif control_due and luma < self.target - self.deadband and clipped_fraction <= 0.02:
            # Limit each update so sensor latency cannot cause large overshoot.
            candidate = self._clamp_step(round(exposure * min(1.25, self.target / max(luma, 1))),
                                         self.specs["exposure"])
            exposure = self._clamp_step(min(high, max(exposure + step, candidate)),
                                        self.specs["exposure"])
            if exposure == self.exposure and "analogue_gain" in self.specs:
                gain = self._clamp_step(gain + max(4, round((self.target-luma)/3)),
                                        self.specs["analogue_gain"])
            analogue_max="analogue_gain" not in self.specs or self.gain>=self.specs['analogue_gain'][1]
            if self.exposure>=high and analogue_max and self.digital_spec is not None:
                candidate=round(digital*min(1.25,self.target/max(luma,1)))
                digital=self._clamp_step(max(digital+self.digital_spec[2],candidate),self.digital_spec)
        elif control_due and (luma > self.target + self.deadband or clipped_fraction > 0.02):
            # Remove digital amplification first when the lights return, then
            # analogue gain, and finally exposure. Never trade away sensor
            # exposure while keeping unnecessary digital noise amplification.
            if self.digital_spec is not None and digital>self.digital_spec[0]:
                ratio=.9 if clipped_fraction>.02 else max(.75,self.target/max(luma,1))
                digital=self._clamp_step(min(digital-self.digital_spec[2],round(digital*ratio)),self.digital_spec)
            elif "analogue_gain" in self.specs and gain > self.specs["analogue_gain"][0]:
                gain = self._clamp_step(gain - max(4, round((luma-self.target)/3)),
                                        self.specs["analogue_gain"])
            else:
                ratio = 0.9 if clipped_fraction > 0.02 else max(0.75, self.target/luma)
                candidate = self._clamp_step(round(exposure * ratio),
                                             self.specs["exposure"])
                exposure = self._clamp_step(max(low, min(exposure - step, candidate)),
                                            self.specs["exposure"])
        changes = []
        if exposure != self.exposure:
            changes.append("exposure=%d" % exposure)
        if gain != self.gain:
            changes.append("analogue_gain=%d" % gain)
        if digital != self.digital_gain:
            changes.append("digital_gain=%d" % digital)
        if changes:
            subprocess.run(["v4l2-ctl", "-d", self.sensor,
                            "--set-ctrl=" + ",".join(changes)],
                           check=True, capture_output=True, text=True, timeout=5)
            self.exposure, self.gain, self.digital_gain = exposure, gain, digital
            self.next_control=now+self.control_interval
            self.settle_until=now+self.settle_seconds
        normalized=abs(luma-self.target)<=self.deadband and clipped_fraction<=.02
        limited=bool(control_due and not normalized and not changes)
        # At the sensor's real exposure/gain limits, waiting for an impossible
        # target held Q forever. Accept stable *measured* limited exposure after
        # the same confirmation period; retain the limited flag in diagnostics.
        steady=self.previous_luma is not None and abs(luma-self.previous_luma)<=max(2.,self.deadband/2.)
        stable=(normalized or (limited and steady)) and not changes and now>=self.settle_until
        self.stable_count=min(self.stable_observations,self.stable_count+1) if stable else 0
        self.ready_for_pl=self.stable_count>=self.stable_observations
        self.previous_luma=luma
        self.last = {"board_luma": round(luma, 1), "ae_target": self.target,
                     "ae_metering": "whole_board_5x3", "ae_control": "single_global",
                     "ae_clip_fraction": round(clipped_fraction, 4),
                     "exposure_lines": self.exposure, "analogue_gain": self.gain,
                     "digital_gain":self.digital_gain if self.digital_spec is not None else None,
                     "digital_gain_limit":None if self.digital_spec is None else self.digital_spec[1],
                     "digital_gain_factor":None if self.digital_spec is None else round(self.digital_gain/256.,3),
                     "ae_changed": bool(changes),"ae_ready_for_pl":self.ready_for_pl,
                     "ae_stable_observations":self.stable_count,
                     "ae_normalizing":not self.ready_for_pl,
                     "ae_limited":limited,
                     "ae_limit_reason":('digital_gain_cap' if self.digital_spec is not None and self.digital_gain>=self.digital_spec[1] and luma<self.target-self.deadband else 'sensor_controls') if limited else None,
                     "ae_ready_reason":('target_stable' if normalized else 'sensor_limit_stable') if self.ready_for_pl else 'settling',
                     "ae_clip_policy":"luma245_zone_p75"}
        return self.last
