#!/usr/bin/env python3
"""Universal robust PYNQ Overlay Loader.

Supports seamless loading across AMD Zynq-7000, Zynq UltraScale+ (KV260, KR260,
ZCU104), and Versal. Decouples fpgautil Linux DTBO programming from PYNQ
metadata registration to avoid Configfs crashes.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

logger = logging.getLogger("pynq_skill.overlay_loader")


class UniversalOverlayLoader:
    """Robust overlay loader with multi-platform compatibility guards."""

    @staticmethod
    def clear_stale_pynq_state() -> None:
        """Clear orphaned PYNQ global state files left by previously crashed processes."""
        try:
            from pynq.pl_server.global_state import STATE_DIR, clear_global_state

            state_file = Path(STATE_DIR) / "global_pl_state.json"
            if state_file.is_file():
                try:
                    data = json.loads(state_file.read_text(encoding="utf-8"))
                    bitfile = Path(data.get("bitfile_name", ""))
                    if not bitfile.is_file():
                        logger.warning(
                            "Found stale PYNQ state pointing to missing bitfile: %s. Clearing.",
                            bitfile,
                        )
                        clear_global_state()
                except Exception as err:
                    logger.debug("Failed parsing state file (%s), resetting state.", err)
                    clear_global_state()
        except ImportError:
            # Running in non-PYNQ host environment (e.g., simulation or test mock)
            pass

    @classmethod
    def load(
        cls,
        bitfile_path: str | Path,
        dtbo_path: str | Path | None = None,
        download: bool = True,
        check_operating_state: bool = True,
    ) -> Any:
        """Load overlay with safety checks.

        Args:
            bitfile_path: Path to the .bit file (must have matching .hwh in same dir).
            dtbo_path: Optional path to Linux device-tree overlay (.dtbo).
            download: If False, only register/parse metadata without touching PL.
            check_operating_state: Check /sys/class/fpga_manager/fpga0/state after load.

        Returns:
            pynq.Overlay instance.
        """
        bitfile = Path(bitfile_path).resolve()
        if not bitfile.is_file():
            raise FileNotFoundError(f"Bitstream file not found: {bitfile}")

        hwh_file = bitfile.with_suffix(".hwh")
        if not hwh_file.is_file():
            raise FileNotFoundError(f"Matching HWH metadata file not found: {hwh_file}")

        # Clear any stale PYNQ state
        cls.clear_stale_pynq_state()

        from pynq import Overlay

        # If check-only / no download requested, register metadata directly
        if not download:
            logger.info("Registering PYNQ overlay metadata without programming PL: %s", bitfile)
            return Overlay(str(bitfile), download=False)

        # Detect Zynq UltraScale+ FPGA Manager subsystem
        manager_state = Path("/sys/class/fpga_manager/fpga0/state")
        is_zynqmp_linux = manager_state.exists()

        if is_zynqmp_linux and dtbo_path is not None:
            dtbo = Path(dtbo_path).resolve()
            if not dtbo.is_file():
                raise FileNotFoundError(f"DTBO file not found: {dtbo}")

            bitbin = bitfile.with_suffix(".bit.bin")
            if not bitbin.is_file():
                raise FileNotFoundError(
                    f"ZynqMP fpgautil requires matching .bit.bin format: {bitbin}"
                )

            logger.info("Programming PL via fpgautil: bit=%s dtbo=%s", bitbin.name, dtbo.name)

            # Step 1: Remove existing active overlay via fpgautil if necessary
            subprocess.run(
                ["fpgautil", "-R", "-n", "Full"],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            # Step 2: Program hardware and device tree together
            load_proc = subprocess.run(
                ["fpgautil", "-b", str(bitbin), "-o", str(dtbo), "-f", "Full", "-n", "Full"],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            failure_patterns = (
                "failed to apply overlay",
                "loading through fpga manager failed",
                "failed to create overlay",
            )
            if load_proc.returncode != 0 or any(p in load_proc.stdout.lower() for p in failure_patterns):
                raise RuntimeError(f"fpgautil overlay programming failed:\n{load_proc.stdout}")

            # Step 3: Verify hardware manager state
            if check_operating_state and manager_state.is_file():
                state_str = manager_state.read_text(encoding="utf-8").strip()
                if state_str != "operating":
                    raise RuntimeError(
                        f"FPGA Manager failed to reach 'operating' state (current: {state_str})"
                    )

            # Step 4: Register PYNQ metadata without reprogramming hardware
            logger.info("Registering PYNQ metadata cache after fpgautil load")
            overlay = Overlay(str(bitfile), download=False, gen_cache=True)
            return overlay

        # Standard PYNQ Overlay loading (e.g. PYNQ-Z2, PCAP or simulated)
        logger.info("Programming PL via native PYNQ Overlay: %s", bitfile)
        overlay = Overlay(str(bitfile), download=True)
        return overlay
