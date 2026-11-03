#!/usr/bin/env python3
"""Unit tests for 02_dma_buffer_guard."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import unittest
from cache_coherent_guard import CacheCoherentGuard, HardwareNotIdleError, HardwareTimeoutError
from dma_buffer_pool import DmaBufferPool


class MockBuffer:
    def __init__(self, phys_addr: int, nbytes: int):
        self.physical_address = phys_addr
        self.nbytes = nbytes
        self.flush_count = 0
        self.invalidate_count = 0
        self.freed = False

    def flush(self):
        self.flush_count += 1

    def invalidate(self):
        self.invalidate_count += 1

    def freebuffer(self):
        self.freed = True


class MockIPForGuard:
    def __init__(self, behaves_well: bool = True):
        self.ctrl = 0x04  # IDLE bit set
        self.behaves_well = behaves_well
        self.starts = 0

    def read(self, offset: int) -> int:
        if offset == 0x00:
            return self.ctrl
        return 0

    def write(self, offset: int, val: int) -> None:
        if offset == 0x00:
            if val & 0x01:  # ap_start
                self.starts += 1
                if self.behaves_well:
                    # Instantly set DONE bit and clear START
                    self.ctrl = 0x06  # IDLE + DONE
                else:
                    # Hang: clear IDLE and never assert DONE
                    self.ctrl = 0x00


class TestDmaGuard(unittest.TestCase):
    def test_buffer_pool_acquire_and_overlap(self):
        counter = 0

        def mock_alloc(shape, dtype):
            nonlocal counter
            counter += 1
            return MockBuffer(phys_addr=0x1000 * counter, nbytes=0x1000)

        pool = DmaBufferPool(buffer_shape=(100,), dtype="uint8", pool_size=2, allocate_fn=mock_alloc)

        # Acquire 2 buffers
        with pool.acquire() as b1:
            with pool.acquire() as b2:
                self.assertFalse(pool.check_overlap(b1, b2))
                # Attempting to acquire 3rd should fail
                with self.assertRaises(BufferError):
                    with pool.acquire():
                        pass

        # Check overlapping logic directly
        buf_a = MockBuffer(0x1000, 0x1000)  # 0x1000..0x2000
        buf_b = MockBuffer(0x1800, 0x1000)  # 0x1800..0x2800 (overlaps)
        buf_c = MockBuffer(0x2000, 0x1000)  # 0x2000..0x3000 (contiguous, no overlap)

        self.assertTrue(DmaBufferPool.check_overlap(buf_a, buf_b))
        self.assertFalse(DmaBufferPool.check_overlap(buf_a, buf_c))

        pool.close()

    def test_cache_guard_normal_execution(self):
        ip = MockIPForGuard(behaves_well=True)
        guard = CacheCoherentGuard(ip, timeout_seconds=0.1)

        in_buf = MockBuffer(0x1000, 0x100)
        out_buf = MockBuffer(0x2000, 0x100)

        with guard.run_hardware(in_buf, out_buf):
            pass

        # In-buf must have been flushed
        self.assertEqual(in_buf.flush_count, 1)
        # Out-buf must have been invalidated
        self.assertEqual(out_buf.invalidate_count, 1)
        # IP must have received ap_start
        self.assertEqual(ip.starts, 1)

    def test_cache_guard_timeout(self):
        # Hardware hangs (never asserts done)
        ip = MockIPForGuard(behaves_well=False)
        guard = CacheCoherentGuard(ip, timeout_seconds=0.05, poll_interval_seconds=0.005)

        in_buf = MockBuffer(0x1000, 0x100)
        out_buf = MockBuffer(0x2000, 0x100)

        with self.assertRaises(HardwareTimeoutError):
            with guard.run_hardware(in_buf, out_buf):
                pass

    def test_cache_guard_not_idle(self):
        ip = MockIPForGuard(behaves_well=True)
        ip.ctrl = 0x00  # Busy, not idle
        guard = CacheCoherentGuard(ip, timeout_seconds=0.1)

        in_buf = MockBuffer(0x1000, 0x100)
        out_buf = MockBuffer(0x2000, 0x100)

        with self.assertRaises(HardwareNotIdleError):
            with guard.run_hardware(in_buf, out_buf):
                pass


if __name__ == "__main__":
    unittest.main()
