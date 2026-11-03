"""Actual event throughput; monotonic time, no nominal-rate or UI-redraw frames."""
from collections import deque
import threading
import time


class EventRate:
    def __init__(self, window=2.0, clock=time.monotonic):
        if window <= 0: raise ValueError('Positive window required')
        self.window = float(window); self.clock = clock
        self.events = deque(); self.seen = set(); self.lock = threading.Lock()

    def _prune(self, now):
        while self.events and self.events[0][0] <= now-self.window:
            _, identity = self.events.popleft(); self.seen.discard(identity)

    def add(self, identity, now=None):
        now = self.clock() if now is None else now
        with self.lock:
            self._prune(now)
            if identity in self.seen: return False
            self.seen.add(identity); self.events.append((now, identity)); return True

    def value(self, now=None):
        now = self.clock() if now is None else now
        with self.lock:
            self._prune(now)
            return len(self.events)/self.window


class ComputeRate:
    """Equivalent core rate from measured compute-only cycles, never wall FPS.

    Hardware must exclude DDR/FIFO wait cycles before supplying these values.
    Missing hardware samples are unavailable, not zero or a nominal estimate.
    """
    def __init__(self, window=2.0, clock=time.monotonic):
        self.window=float(window);self.clock=clock
        self.samples=deque();self.identities=set();self.lock=threading.Lock()

    def _prune(self,now):
        while self.samples and self.samples[0][0]<=now-self.window:
            _,identity,_=self.samples.popleft();self.identities.discard(identity)

    def add(self,identity,cycles,clock_hz,now=None):
        if not (0<int(cycles)<=0xffffffff) or not (0<float(clock_hz)<1e10):
            raise ValueError('Measured compute cycles and clock must be positive and finite')
        now=self.clock() if now is None else now
        with self.lock:
            self._prune(now)
            if identity in self.identities:return False
            self.samples.append((now,identity,float(cycles)/float(clock_hz)))
            self.identities.add(identity);return True

    def value(self,now=None):
        now=self.clock() if now is None else now
        with self.lock:
            self._prune(now)
            return len(self.samples)/sum(row[2] for row in self.samples) if self.samples else None


class PipelineMetrics:
    NAMES = ('capture_completed', 'rectify_completed', 'restore_completed',
             'quantize_completed', 'display_submitted', 'display_presented')

    def __init__(self, clock=time.monotonic):
        self.rates = {name: EventRate(clock=clock) for name in self.NAMES}
        self.rectify_compute = ComputeRate(clock=clock)
        self.coordinate_counter_available = None
        self.coordinate_samples_received = 0

    def rectify_compute_state(self, now=None):
        # Native UI ABI: -1 absent, 0 waiting, 1 measured, 2 expired.
        if self.coordinate_counter_available is False: return -1
        if self.rectify_compute.value(now) is not None: return 1
        return 2 if self.coordinate_samples_received else 0

    def add(self, name, identity, now=None):
        return self.rates[name].add(identity, now)

    def snapshot(self, now=None):
        result = {name+'_fps': rate.value(now) for name, rate in self.rates.items()}
        result['rectify_coordinate_equivalent_fps'] = self.rectify_compute.value(now)
        result['rectify_coordinate_status'] = {-1:'counter_missing',0:'waiting_for_sample',
            1:'measured',2:'sample_expired'}[self.rectify_compute_state(now)]
        return result

    def source(self, mode, now=None):
        return self.rates[('capture_completed','rectify_completed','quantize_completed')[mode]].value(now)

    def record_rectify_compute(self,identity,cycles,clock_hz,now=None):
        added = self.rectify_compute.add(identity,cycles,clock_hz,now)
        if added:
            self.coordinate_counter_available = True
            self.coordinate_samples_received += 1
        return added
