#!/usr/bin/env python3
"""Auto-generated PYNQ Driver for ExampleAcceleratorIP."""

from __future__ import annotations

import time
from typing import Any


class ExampleAcceleratorIP:
    """Driver interface for ExampleAcceleratorIP hardware accelerator core."""

    AP_CTRL = 0x00
    AP_DONE_BIT = 1 << 1
    AP_IDLE_BIT = 1 << 2
    AP_START_BIT = 1 << 0

    def __init__(self, ip_handle: Any) -> None:
        self.ip = ip_handle

    def set_src_addr_address(self, phys_addr: int) -> None:
        """Set 64-bit physical address for src_addr (low=0x20, high=0x24)."""
        addr = int(phys_addr)
        self.ip.write(0x20, addr & 0xFFFFFFFF)
        self.ip.write(0x24, (addr >> 32) & 0xFFFFFFFF)

    def set_dst_addr_address(self, phys_addr: int) -> None:
        """Set 64-bit physical address for dst_addr (low=0x28, high=0x2C)."""
        addr = int(phys_addr)
        self.ip.write(0x28, addr & 0xFFFFFFFF)
        self.ip.write(0x2C, (addr >> 32) & 0xFFFFFFFF)

    def set_width(self, value: int) -> None:
        """Write scalar register width (offset 0x10)."""
        self.ip.write(0x10, int(value) & 0xFFFFFFFF)

    def get_width(self) -> int:
        """Read scalar register width (offset 0x10)."""
        return int(self.ip.read(0x10))

    def set_height(self, value: int) -> None:
        """Write scalar register height (offset 0x18)."""
        self.ip.write(0x18, int(value) & 0xFFFFFFFF)

    def get_height(self) -> int:
        """Read scalar register height (offset 0x18)."""
        return int(self.ip.read(0x18))

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
