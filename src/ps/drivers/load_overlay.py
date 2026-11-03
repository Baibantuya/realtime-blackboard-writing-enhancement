#!/usr/bin/env python3
"""Load a matching PYNQ .bit/.hwh overlay and optional device-tree overlay."""
import argparse
import json
import shutil
import subprocess
from pathlib import Path

from pynq import Overlay
from pynq.pl_server.global_state import STATE_DIR, clear_global_state


def clear_stale_pynq_state():
    state_file = Path(STATE_DIR) / "global_pl_state.json"
    if not state_file.is_file():
        return
    try:
        bitfile = Path(json.loads(state_file.read_text()).get("bitfile_name", ""))
    except (OSError, ValueError, TypeError):
        bitfile = Path()
    if not bitfile.is_file():
        clear_global_state()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bit", required=True, help=".bit file with same-basename .hwh")
    ap.add_argument("--dtbo", required=True, help="matching Linux device-tree overlay")
    ap.add_argument("--check-only", action="store_true",
                    help="parse overlay metadata without programming the FPGA")
    args = ap.parse_args()

    bitfile = Path(args.bit)
    dtbo = Path(args.dtbo)
    if not bitfile.is_file() or not dtbo.is_file():
        raise FileNotFoundError("matching .bit and .dtbo files are required")

    bitbin = bitfile.with_suffix(".bit.bin")
    if not bitbin.is_file():
        raise FileNotFoundError(f"matching FPGA manager bitstream is missing: {bitbin}")

    # Recover from an earlier interrupted PYNQ load that left a state record
    # pointing at a temporary bit file which has since been removed.
    clear_stale_pynq_state()

    # PYNQ auto-detects a same-basename .dtbo next to the bit file and uses a
    # configfs readback path that this KV260 kernel rejects. Keep a persistent
    # copy under a different basename, program bit+DTBO with fpgautil, then
    # rebuild PYNQ's metadata cache without reprogramming the PL. The cache must
    # be generated after fpgautil because programming through fpgautil clears
    # PYNQ's downloaded-overlay state.
    pynq_dir = bitfile.parent / "pynq_runtime"
    pynq_dir.mkdir(parents=True, exist_ok=True)
    pynq_bit = pynq_dir / "overlay.bit"
    pynq_hwh = pynq_bit.with_suffix(".hwh")
    shutil.copy2(bitfile, pynq_bit)
    shutil.copy2(bitfile.with_suffix(".hwh"), pynq_hwh)
    source_xclbin = bitfile.with_suffix(".xclbin")
    if source_xclbin.is_file():
        shutil.copy2(source_xclbin, pynq_bit.with_suffix(".xclbin"))
    else:
        pynq_bit.with_suffix(".xclbin").unlink(missing_ok=True)

    if args.check_only:
        overlay = Overlay(str(pynq_bit), download=False)
        print("PYNQ_OVERLAY_METADATA_READY", flush=True)
        return

    remove = subprocess.run(["fpgautil", "-R", "-n", "Full"], check=False,
                            text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if remove.stdout:
        print(remove.stdout, end="", flush=True)
    load = subprocess.run(
        ["fpgautil", "-b", str(bitbin), "-o", str(dtbo), "-f", "Full", "-n", "Full"],
        check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    if load.stdout:
        print(load.stdout, end="", flush=True)
    failure_markers = ("failed to apply overlay", "loading through fpga manager failed", "failed to create overlay")
    if load.returncode != 0 or any(marker in load.stdout.lower() for marker in failure_markers):
        raise RuntimeError("fpgautil failed to load bitstream/DTBO; refusing to register metadata")
    manager_state = Path("/sys/class/fpga_manager/fpga0/state")
    if manager_state.is_file() and manager_state.read_text().strip() != "operating":
        raise RuntimeError("FPGA manager is not operating after fpgautil: " + manager_state.read_text().strip())

    # Register metadata after FPGA manager programming so the state persists
    # for the separate run_pipeline.py process, without changing the PL again.
    overlay = Overlay(str(pynq_bit), download=False, gen_cache=True)
    print("PYNQ_METADATA_REGISTERED", flush=True)

    print("PYNQ_OVERLAY_LOADED", flush=True)


if __name__ == "__main__":
    main()
