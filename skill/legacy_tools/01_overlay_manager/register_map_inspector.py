#!/usr/bin/env python3
"""Register Map Inspector and Safe MMIO Accessor.

Handles HLS / Vivado register maps, automatic 64-bit address splitting
(address_1 low 32-bit, address_2 high 32-bit), and AP_CTRL handshake checks.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("pynq_skill.register_map_inspector")


class RegisterMapInspector:
    """Introspects and accesses PYNQ IP core registers with contract verification."""

    # Standard Xilinx HLS AXI-Lite control register offsets
    AP_CTRL_OFFSET = 0x00
    AP_RETURN_OFFSET = 0x10

    # AP_CTRL bitmasks
    BIT_AP_START = 1 << 0
    BIT_AP_DONE = 1 << 1
    BIT_AP_IDLE = 1 << 2
    BIT_AP_READY = 1 << 3
    BIT_AUTO_RESTART = 1 << 7

    def __init__(self, ip_handle: Any) -> None:
        """Initialize inspector with a PYNQ DefaultIP or custom MMIO handle."""
        self.ip = ip_handle
        self._register_cache: Dict[str, int] = {}
        self._pointer_pairs: Dict[str, Tuple[int, int]] = {}
        self._introspect_registers()

    def _introspect_registers(self) -> None:
        """Discover register names, offsets, and detect 64-bit split pairs."""
        # Check if ip has register_map (standard PYNQ 2.5+)
        if hasattr(self.ip, "register_map"):
            for reg in self.ip.register_map:
                name = reg.name
                offset = reg.address
                self._register_cache[name.lower()] = offset

        # Detect 64-bit split pointer pairs:
        # e.g., 'src_addr_1' (low) and 'src_addr_2' (high), or 'src_addr_data'
        seen_stems: set[str] = set()
        for name in list(self._register_cache.keys()):
            if name.endswith("_1"):
                stem = name[:-2]
                high_name = f"{stem}_2"
                if high_name in self._register_cache:
                    low_off = self._register_cache[name]
                    high_off = self._register_cache[high_name]
                    self._pointer_pairs[stem] = (low_off, high_off)
                    seen_stems.add(stem)

        logger.debug(
            "Discovered %d registers and %d 64-bit pointer pairs",
            len(self._register_cache),
            len(self._pointer_pairs),
        )

    def print_register_map(self) -> None:
        """Pretty-print the active register map and current live values."""
        print(f"{'Register Name':<28} | {'Offset':<10} | {'Current Value'}")
        print("-" * 55)
        for name, offset in sorted(self._register_cache.items(), key=lambda x: x[1]):
            try:
                val = self.ip.read(offset)
                val_str = f"0x{val:08X} ({val})"
            except Exception as e:
                val_str = f"<read failed: {e}>"
            print(f"{name:<28} | 0x{offset:04X}     | {val_str}")

    def verify_registers(
        self,
        required_scalars: Optional[List[str]] = None,
        required_pointers: Optional[List[str]] = None,
    ) -> bool:
        """Verify that the IP contains all required registers according to contract.

        Raises:
            KeyError: if any mandatory register is missing.
        """
        missing: List[str] = []

        if required_scalars:
            for s in required_scalars:
                if s.lower() not in self._register_cache:
                    missing.append(f"scalar:{s}")

        if required_pointers:
            for p in required_pointers:
                p_lower = p.lower()
                # A pointer is satisfied if either:
                # 1. A split pair exists (e.g. p_1 and p_2)
                # 2. Direct register exists (e.g. p)
                if p_lower not in self._pointer_pairs and p_lower not in self._register_cache:
                    missing.append(f"pointer_64:{p}")

        if missing:
            raise KeyError(
                f"IP interface contract verification failed! Missing registers: {missing}"
            )
        return True

    def write_reg(self, name: str, value: int) -> None:
        """Write a 32-bit scalar register by name."""
        name_lower = name.lower()
        if name_lower not in self._register_cache:
            raise KeyError(f"Register '{name}' not found in IP register map")
        offset = self._register_cache[name_lower]
        self.ip.write(offset, int(value) & 0xFFFFFFFF)

    def read_reg(self, name: str) -> int:
        """Read a 32-bit register by name."""
        name_lower = name.lower()
        if name_lower not in self._register_cache:
            raise KeyError(f"Register '{name}' not found in IP register map")
        offset = self._register_cache[name_lower]
        return int(self.ip.read(offset))

    def write_pointer_64(self, pointer_name: str, physical_address: int) -> None:
        """Safely write a 64-bit physical address into split 32-bit registers.

        Handles both HLS split registers (e.g. ptr_1 low, ptr_2 high) and
        standard contiguous 8-byte pointer offsets.
        """
        addr = int(physical_address)
        low_word = addr & 0xFFFFFFFF
        high_word = (addr >> 32) & 0xFFFFFFFF
        p_lower = pointer_name.lower()

        if p_lower in self._pointer_pairs:
            low_off, high_off = self._pointer_pairs[p_lower]
            self.ip.write(low_off, low_word)
            self.ip.write(high_off, high_word)
        elif p_lower in self._register_cache:
            # Fallback: assume offset+0 is low, offset+4 is high
            base_off = self._register_cache[p_lower]
            self.ip.write(base_off, low_word)
            self.ip.write(base_off + 4, high_word)
        else:
            raise KeyError(
                f"64-bit pointer register '{pointer_name}' not discovered in IP register map"
            )

    @property
    def is_idle(self) -> bool:
        """Check if IP is currently in IDLE state (bit 2 of AP_CTRL)."""
        ctrl = self.ip.read(self.AP_CTRL_OFFSET)
        return bool(ctrl & self.BIT_AP_IDLE)

    @property
    def is_done(self) -> bool:
        """Check if IP has completed execution (bit 1 of AP_CTRL)."""
        ctrl = self.ip.read(self.AP_CTRL_OFFSET)
        return bool(ctrl & self.BIT_AP_DONE)

    def start(self) -> None:
        """Issue ap_start pulse/assert (bit 0 of AP_CTRL)."""
        self.ip.write(self.AP_CTRL_OFFSET, self.BIT_AP_START)
