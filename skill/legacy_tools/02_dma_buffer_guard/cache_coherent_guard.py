#!/usr/bin/env python3
"""Cache Coherency Guard and Hardware Watchdog Executor.

Guarantees explicit CPU cache flush before PL execution and cache invalidation
after PL execution, preventing silent memory corruption. Enforces strict
watchdog timeouts to eliminate unkillable zombie processes.
"""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Any, Generator

logger = logging.getLogger("pynq_skill.cache_coherent_guard")


class HardwareTimeoutError(TimeoutError):
    """Raised when FPGA PL core does not complete within specified deadline."""


class HardwareNotIdleError(RuntimeError):
    """Raised when FPGA PL core is not in IDLE state prior to launch."""


class CacheCoherentGuard:
    """Manages cache synchronization and safe execution handshakes with FPGA IP."""

    AP_CTRL_OFFSET = 0x00
    AP_RETURN_OFFSET = 0x10

    BIT_AP_START = 1 << 0
    BIT_AP_DONE = 1 << 1
    BIT_AP_IDLE = 1 << 2

    def __init__(
        self,
        ip_handle: Any,
        timeout_seconds: float = 2.0,
        poll_interval_seconds: float = 0.0005,
    ) -> None:
        """Initialize guard with hardware IP handle.

        Args:
            ip_handle: PYNQ IP core instance with read() and write() MMIO methods.
            timeout_seconds: Maximum allowed execution time before raising HardwareTimeoutError.
            poll_interval_seconds: Polling sleep duration between status reads.
        """
        self.ip = ip_handle
        self.timeout = timeout_seconds
        self.poll_interval = poll_interval_seconds

    @contextmanager
    def run_hardware(
        self,
        input_buf: Any,
        output_buf: Any,
        extra_inputs: tuple[Any, ...] = (),
    ) -> Generator[Any, None, None]:
        """Execute hardware with cache safety and timeout protection.

        Workflow:
            1. Verify hardware is in IDLE state.
            2. Flush input buffer(s) to DDR so PL receives coherent data.
            3. Issue ap_start.
            4. Poll for ap_done until deadline; raise HardwareTimeoutError on expiry.
            5. Invalidate output buffer(s) so CPU reads fresh DDR data written by PL.
            6. Yield control to caller.
        """
        # Step 1: Pre-launch idle check
        ctrl_val = self.ip.read(self.AP_CTRL_OFFSET)
        if not (ctrl_val & self.BIT_AP_IDLE):
            raise HardwareNotIdleError(
                f"IP core is not idle before launch (AP_CTRL=0x{ctrl_val:08X})"
            )

        # Step 2: Flush CPU cache for all inputs
        if hasattr(input_buf, "flush"):
            input_buf.flush()
        for buf in extra_inputs:
            if hasattr(buf, "flush"):
                buf.flush()

        # Step 3: Assert ap_start
        self.ip.write(self.AP_CTRL_OFFSET, self.BIT_AP_START)
        deadline = time.monotonic() + self.timeout

        # Step 4: Watchdog protected polling
        finished = False
        while not finished:
            status = self.ip.read(self.AP_CTRL_OFFSET)
            if status & self.BIT_AP_DONE:
                finished = True
                break

            if time.monotonic() >= deadline:
                raise HardwareTimeoutError(
                    f"FPGA IP execution timed out after {self.timeout:.3f} seconds! "
                    f"Last AP_CTRL=0x{status:08X}. Check PL clock, reset, and AXI stream backpressure."
                )
            time.sleep(self.poll_interval)

        # Step 5: Invalidate CPU cache for output
        if hasattr(output_buf, "invalidate"):
            output_buf.invalidate()

        # Step 6: Hand control back to caller
        yield output_buf
