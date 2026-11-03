#!/usr/bin/env python3
"""Auto-generated PYNQ Driver for DemoIP."""

from __future__ import annotations
import time
from typing import Any

class DemoIP:
    """Driver interface for DemoIP hardware accelerator core."""

    AP_CTRL = 0x00
    AP_DONE_BIT = 1 << 1
    AP_IDLE_BIT = 1 << 2
    AP_START_BIT = 1 << 0

    def __init__(self, ip_handle: Any) -> None:
        self.ip = ip_handle

    def set_value(self, value: int) -> None:
        """Write 32-bit value at 0x10."""
        value = int(value)
        self.ip.write(0x10, value & 0xFFFFFFFF)

    def get_value(self) -> int:
        """Read 32-bit value; multiword reads are not atomic."""
        value = int(self.ip.read(0x10)) & 0xFFFFFFFF
        return value & 4294967295

    def is_idle(self) -> bool:
        """Check if hardware is in IDLE state."""
        return bool(self.ip.read(self.AP_CTRL) & self.AP_IDLE_BIT)

    def is_done(self) -> bool:
        """Check if hardware execution has completed."""
        return bool(self.ip.read(self.AP_CTRL) & self.AP_DONE_BIT)

    def start(self) -> None:
        """Assert ap_start to launch hardware execution."""
        self.ip.write(self.AP_CTRL, self.AP_START_BIT)

    def wait_done(self, timeout_seconds: float = 2.0) -> None:
        """Poll for completion with watchdog deadline."""
        deadline = time.monotonic() + timeout_seconds
        while not self.is_done():
            if time.monotonic() >= deadline:
                raise TimeoutError(f"IP wait_done timed out after {timeout_seconds:.2f}s")
            time.sleep(0.0005)
