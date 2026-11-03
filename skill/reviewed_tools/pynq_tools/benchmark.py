"""Event-defined observations, never automatic claims of cold boot or steady state."""
import json
import math
from pathlib import Path
import re
import statistics
import time


class PynqBenchmarker:
    def __init__(self, *, event_name, latency_scope, start_event, clock=time.monotonic, warmup_frames=0):
        if not all(isinstance(x, str) and x.strip() for x in (event_name, latency_scope, start_event)):
            raise ValueError('event, latency scope and start event must be named')
        if isinstance(warmup_frames, bool) or not isinstance(warmup_frames, int) or warmup_frames < 0:
            raise ValueError('nonnegative warmup frame count required')
        self.clock, self.start = clock, clock()
        if not math.isfinite(self.start):
            raise ValueError('finite start time required')
        self.event, self.scope, self.start_event = event_name, latency_scope, start_event
        self.warmup, self.frames = warmup_frames, []

    def record_frame(self, latency_ms, is_bad=False):
        t = self.clock()
        if not math.isfinite(latency_ms) or latency_ms < 0 or not math.isfinite(t):
            raise ValueError('finite nonnegative latency and finite monotonic timestamp required')
        if t < self.start or (self.frames and t <= self.frames[-1][0]):
            raise ValueError('event timestamps must strictly increase')
        self.frames.append((t, float(latency_ms), bool(is_bad)))

    def compute_statistics(self, *, thresholds=None):
        thresholds = thresholds or {}
        if set(thresholds) - {'min_observed_fps', 'max_bad_frame_rate'}:
            raise ValueError('unknown threshold')
        if any(not math.isfinite(v) or v < 0 for v in thresholds.values()) or thresholds.get('max_bad_frame_rate', 0) > 1:
            raise ValueError('invalid threshold')
        window = self.frames[self.warmup:]
        times, lat = [x[0] for x in window], [x[1] for x in window]
        intervals = [(b - a) * 1000 for a, b in zip(times, times[1:])]
        count = len(window)
        bad = sum(x[2] for x in window)
        fps = (count - 1) / (times[-1] - times[0]) if count > 1 else None
        bad_rate = bad / count if count else None
        checks = {}
        for key, target in thresholds.items():
            val = fps if key == 'min_observed_fps' else bad_rate
            ok = val is not None and (val >= target if key == 'min_observed_fps' else val <= target)
            checks[key] = 'NOT_CHECKED' if val is None else ('PASS' if ok else 'FAIL')
        return {'event_name': self.event, 'latency_scope': self.scope, 'start_event': self.start_event,
                'total_recorded_events': len(self.frames), 'warmup_excluded': min(self.warmup, len(self.frames)),
                'window_events': count, 'window_start_s': times[0] if times else None, 'window_end_s': times[-1] if times else None,
                'observed_fps': fps, 'start_to_first_event_ms': (self.frames[0][0] - self.start) * 1000 if self.frames else None,
                'first_event_stage_latency_ms': self.frames[0][1] if self.frames else None,
                'mean_stage_latency_ms': statistics.mean(lat) if lat else None,
                'stage_latency_stdev_ms': statistics.stdev(lat) if count > 1 else None,
                'frame_interval_stdev_ms': statistics.stdev(intervals) if len(intervals) > 1 else None,
                'p95_stage_latency_ms': sorted(lat)[math.ceil(.95 * count) - 1] if count else None,
                'bad_frames': bad, 'bad_frame_rate': bad_rate, 'dropped_frames': 'NOT_MEASURED',
                'thresholds': thresholds, 'checks': checks, 'performance_evaluation': 'NOT_EVALUATED' if not thresholds else
                ('FAIL' if 'FAIL' in checks.values() else ('NOT_CHECKED' if 'NOT_CHECKED' in checks.values() else 'PASS')),
                'limits': 'Observation window only; no automatic cold-boot, steady-state or end-to-end interpretation.'}

    def generate_report(self, output_dir, *, name='benchmark', thresholds=None):
        if not re.fullmatch(r'[a-zA-Z0-9_-]+', name):
            raise ValueError('simple report name required')
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        stats = self.compute_statistics(thresholds=thresholds)
        js, md = out / (name + '.json'), out / (name + '.md')
        js.write_text(json.dumps(stats, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        md.write_text('# Observed event metrics\n\n' + '\n'.join(f'- {k}: {v}' for k, v in stats.items()) + '\n', encoding='utf-8')
        return md, js


def compare_golden(expected, actual, *, tolerance=0, mask=None):
    """Finite, nonempty numeric arrays only; tolerance and mask are explicit."""
    import numpy as np
    a, b = np.asarray(expected), np.asarray(actual)
    if a.shape != b.shape or a.size == 0 or not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError('same nonempty shape and finite nonnegative tolerance required')
    if a.dtype.kind not in 'buif' or b.dtype.kind not in 'buif':
        raise ValueError('real numeric arrays required')
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError('nonfinite samples are not accepted as matches')
    if mask is None:
        selected = np.ones(a.shape, dtype=bool)
    else:
        selected = np.asarray(mask)
        if selected.shape != a.shape or selected.dtype.kind != 'b':
            raise ValueError('boolean mask with exact shape required')
    if not selected.any():
        raise ValueError('empty selected region')
    # Pixel/metadata use only. Large 64-bit integers cannot be compared exactly via float64.
    if any(x.dtype.kind in 'iu' and np.any(np.abs(x.astype(object)) > 2**53) for x in (a, b)):
        raise ValueError('integer magnitude beyond exact float64 comparison scope')
    diff = np.abs(a.astype('float64')[selected] - b.astype('float64')[selected])
    wrong = int(np.count_nonzero(diff > tolerance))
    return {'is_match': wrong == 0, 'compared_values': int(diff.size), 'mismatches': wrong, 'max_abs_diff': float(diff.max()), 'tolerance': tolerance}
