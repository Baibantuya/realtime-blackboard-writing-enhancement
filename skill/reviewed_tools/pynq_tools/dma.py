"""Explicit leases for a single-threaded host owner; no implicit allocator or reset."""
from contextlib import contextmanager
import math
import threading
import time

# Strong references prevent Python GC from freeing unresolved buffers in this process.
# This cannot preserve CMA across process death; recovery must precede process shutdown.
_unresolved = {}


class Lease:
    def __init__(self, pool, buffer):
        self.pool, self.buffer = pool, buffer
        self.state, self.held = 'free', False

    def _begin(self):
        self.state = 'in_flight'
        _unresolved[id(self)] = self

    def _complete(self):
        self.state = 'leased'
        _unresolved.pop(id(self), None)

    def _quarantine(self):
        self.state = 'quarantined'
        _unresolved[id(self)] = self


class DmaBufferPool:
    def __init__(self, buffer_shape, dtype='uint8', pool_size=3, *, allocate_fn):
        if isinstance(pool_size, bool) or not isinstance(pool_size, int) or pool_size < 1:
            raise ValueError('positive pool_size required')
        self.owner = threading.get_ident()
        self.leases = []
        self.closed = False
        try:
            for _ in range(pool_size):
                buf = allocate_fn(shape=buffer_shape, dtype=dtype)
                lease = Lease(self, buf)
                self.leases.append(lease)
                addr, size = int(buf.physical_address), int(buf.nbytes)
                if addr < 0 or size <= 0 or not all(callable(getattr(buf, m, None)) for m in ('flush', 'invalidate', 'freebuffer')):
                    raise ValueError('allocator must return a DMA buffer with explicit cache/free methods')
                if any(self.check_overlap(buf, old.buffer) for old in self.leases[:-1]):
                    raise ValueError('allocated physical regions overlap')
        except BaseException:
            # No hardware launch has happened. Retain any allocation whose free fails.
            seen = set()
            for lease in self.leases:
                if id(lease.buffer) in seen:
                    continue
                seen.add(id(lease.buffer))
                try:
                    lease.buffer.freebuffer()
                except BaseException:
                    lease._quarantine()
            raise

    def _check(self):
        if threading.get_ident() != self.owner:
            raise RuntimeError('pool requires one owner thread')
        if self.closed:
            raise RuntimeError('pool closed')

    @staticmethod
    def check_overlap(a, b):
        return int(a.physical_address) < int(b.physical_address) + b.nbytes and int(b.physical_address) < int(a.physical_address) + a.nbytes

    @contextmanager
    def acquire(self):
        self._check()
        lease = next((x for x in self.leases if x.state == 'free'), None)
        if lease is None:
            raise BufferError('no free buffer; unresolved DMA requires verified recovery')
        lease.state, lease.held = 'leased', True
        try:
            yield lease
        finally:
            lease.held = False
            if lease.state == 'leased':
                lease.state = 'free'
            elif lease.state == 'in_flight':
                lease._quarantine()

    def recover(self, *, verify_quiescent, reason):
        """Caller first stops/resets all relevant masters using a board-reviewed procedure.

        The verifier must establish no future/outstanding accesses to these buffers;
        a timeout, PID exit or generic idle bit alone is not that evidence.
        """
        self._check()
        pending = [x for x in self.leases if x.state in ('in_flight', 'quarantined')]
        if not pending or any(x.held for x in pending) or not reason.strip():
            raise RuntimeError('recovery requires released leases, unresolved DMA and evidence reason')
        if verify_quiescent(tuple(x.buffer for x in pending), reason) is not True:
            raise RuntimeError('hardware quiescence was not confirmed')
        for x in pending:
            x.buffer.invalidate()
        for x in pending:
            x._complete()
            x.state = 'free'

    def close(self):
        self._check()
        if any(x.state not in ('free', 'freed') or x.held for x in self.leases):
            raise BufferError('refusing free: leased or unresolved DMA buffers remain')
        for x in self.leases:
            if x.state != 'freed':
                try:
                    x.buffer.freebuffer()
                    x.state = 'freed'
                except BaseException:
                    x._quarantine()
                    raise
        self.closed = True


class CacheCoherentGuard:
    """ap_ctrl_hs single-shot candidate. MMIO itself must have bounded return time.

    `completion_confirmed` is an explicit hardware-contract hook. No automatic
    recovery, reset, process kill or claim of protection from blocking MMIO.
    """
    def __init__(self, ip_handle, *, completion_confirmed, timeout_seconds=2.0,
                 poll_interval_seconds=0.0005, clock=time.monotonic, sleep=time.sleep):
        if not math.isfinite(timeout_seconds) or timeout_seconds <= 0 or not math.isfinite(poll_interval_seconds) or poll_interval_seconds < 0:
            raise ValueError('positive finite timeout and nonnegative poll interval required')
        self.ip, self.confirm = ip_handle, completion_confirmed
        self.timeout, self.interval = timeout_seconds, poll_interval_seconds
        self.clock, self.sleep = clock, sleep

    @contextmanager
    def run_hardware(self, leases, *, outputs):
        leases, outputs = tuple(leases), tuple(outputs)
        if not leases or len({id(x) for x in leases}) != len(leases) or any(x not in leases for x in outputs):
            raise ValueError('unique tracked leases including every output required')
        for x in leases:
            x.pool._check()
            if x.state != 'leased' or not x.held:
                raise RuntimeError('active lease required')
        ctrl = self.ip.read(0)
        if not ctrl & 4 or ctrl & 0x80:
            raise RuntimeError('idle single-shot IP required; auto_restart is unsupported')
        # Flush outputs too: CPU dirty output lines must not later overwrite PL writes.
        for x in leases:
            x.buffer.flush()
        for x in leases:
            x._begin()  # protect before start: a write may take effect then raise
        try:
            self.ip.write(0, 1)
            deadline = self.clock() + self.timeout
            while True:
                status = self.ip.read(0)
                if status & 6 == 6 and not status & 0x80 and self.confirm(self.ip, status) is True:
                    break
                if self.clock() >= deadline:
                    raise TimeoutError('DMA completion unconfirmed; buffers quarantined, hardware may still run')
                self.sleep(self.interval)
            for x in outputs:
                x.buffer.invalidate()
            for x in leases:
                x._complete()
        except BaseException:
            for x in leases:
                x._quarantine()
            raise
        yield tuple(x.buffer for x in outputs)
