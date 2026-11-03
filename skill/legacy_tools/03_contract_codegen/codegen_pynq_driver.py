#!/usr/bin/env python3
"""Contract Code Generator for PYNQ IP Cores.

Parses Vitis HLS generated C headers (x*_hw.h), Vivado HWH XML files, or
JSON register definitions, and outputs:
1. Strongly-typed, PEP 8 Python driver class.
2. Matching unit test skeleton with MockIP.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple


def parse_hls_header(header_path: Path) -> Dict[str, int]:
    """Extract register offsets from Vitis HLS x*_hw.h header file."""
    text = header_path.read_text(encoding="utf-8", errors="ignore")
    # Matches: #define X<NAME>_ADDR_<REGNAME> 0x10 or 16
    pattern = re.compile(
        r"#define\s+[Xx][A-Za-z0-9]+_ADDR_([A-Za-z0-9_]+)\s+(0x[0-9a-fA-F]+|\d+)"
    )
    registers: Dict[str, int] = {}
    for match in pattern.finditer(text):
        raw_name = match.group(1).lower()
        if raw_name.endswith("_data"):
            name = raw_name[:-5]
        elif raw_name.endswith("_v"):
            name = raw_name[:-2]
        else:
            name = raw_name
        val_str = match.group(2)
        val = int(val_str, 16) if val_str.startswith("0x") else int(val_str)
        registers[name] = val
    return registers


def parse_hwh_file(hwh_path: Path, ip_name: str) -> Dict[str, int]:
    """Extract register offsets from Vivado HWH XML file for a specific IP instance."""
    tree = ET.parse(hwh_path)
    root = tree.getroot()
    registers: Dict[str, int] = {}

    for module in root.iter("MODULE"):
        m_name = module.get("NAME") or module.get("FULLNAME", "")
        if ip_name.lower() in m_name.lower():
            for reg in module.iter("REGISTER"):
                name = reg.get("NAME", "").lower()
                off_str = reg.get("ADDRESS_OFFSET") or reg.get("OFFSET", "0")
                off = int(off_str, 16) if off_str.startswith("0x") else int(off_str)
                registers[name] = off
            break

    if not registers:
        raise ValueError(f"Could not find IP instance '{ip_name}' in HWH file: {hwh_path}")
    return registers


def generate_python_driver(registers: Dict[str, int], class_name: str = "GeneratedIPDriver") -> str:
    """Generate high-quality Python driver class."""
    lines = [
        "#!/usr/bin/env python3",
        f'"""Auto-generated PYNQ Driver for {class_name}."""',
        "",
        "from __future__ import annotations",
        "import time",
        "from typing import Any",
        "",
        f"class {class_name}:",
        f'    """Driver interface for {class_name} hardware accelerator core."""',
        "",
        "    AP_CTRL = 0x00",
        "    AP_DONE_BIT = 1 << 1",
        "    AP_IDLE_BIT = 1 << 2",
        "    AP_START_BIT = 1 << 0",
        "",
        "    def __init__(self, ip_handle: Any) -> None:",
        "        self.ip = ip_handle",
        "",
    ]

    # Detect 64-bit split pointer pairs (ending with _1 and _2)
    pointer_stems: Dict[str, Tuple[int, int]] = {}
    scalar_regs: Dict[str, int] = {}

    for reg_name, offset in sorted(registers.items(), key=lambda x: x[1]):
        if reg_name.lower() in ("ap_ctrl", "control"):
            continue
        if reg_name.endswith("_1"):
            stem = reg_name[:-2]
            high_name = f"{stem}_2"
            if high_name in registers:
                pointer_stems[stem] = (offset, registers[high_name])
                continue
        if reg_name.endswith("_2"):
            stem = reg_name[:-2]
            if stem in pointer_stems:
                continue
        scalar_regs[reg_name] = offset

    # Generate 64-bit pointer methods
    for stem, (low_off, high_off) in pointer_stems.items():
        lines.extend([
            f"    def set_{stem}_address(self, phys_addr: int) -> None:",
            f'        """Set 64-bit physical address for {stem} (low=0x{low_off:02X}, high=0x{high_off:02X})."""',
            f"        addr = int(phys_addr)",
            f"        self.ip.write(0x{low_off:02X}, addr & 0xFFFFFFFF)",
            f"        self.ip.write(0x{high_off:02X}, (addr >> 32) & 0xFFFFFFFF)",
            "",
        ])

    # Generate scalar register getters and setters
    for reg_name, offset in scalar_regs.items():
        lines.extend([
            f"    def set_{reg_name}(self, value: int) -> None:",
            f'        """Write scalar register {reg_name} (offset 0x{offset:02X})."""',
            f"        self.ip.write(0x{offset:02X}, int(value) & 0xFFFFFFFF)",
            "",
            f"    def get_{reg_name}(self) -> int:",
            f'        """Read scalar register {reg_name} (offset 0x{offset:02X})."""',
            f"        return int(self.ip.read(0x{offset:02X}))",
            "",
        ])

    # Standard handshake control methods
    lines.extend([
        "    def is_idle(self) -> bool:",
        '        """Check if hardware is in IDLE state."""',
        "        return bool(self.ip.read(self.AP_CTRL) & self.AP_IDLE_BIT)",
        "",
        "    def is_done(self) -> bool:",
        '        """Check if hardware execution has completed."""',
        "        return bool(self.ip.read(self.AP_CTRL) & self.AP_DONE_BIT)",
        "",
        "    def start(self) -> None:",
        '        """Assert ap_start to launch hardware execution."""',
        "        self.ip.write(self.AP_CTRL, self.AP_START_BIT)",
        "",
        "    def wait_done(self, timeout_seconds: float = 2.0) -> None:",
        '        """Poll for completion with watchdog deadline."""',
        "        deadline = time.monotonic() + timeout_seconds",
        "        while not self.is_done():",
        "            if time.monotonic() >= deadline:",
        '                raise TimeoutError(f"IP wait_done timed out after {timeout_seconds:.2f}s")',
        "            time.sleep(0.0005)",
        "",
    ])

    return "\n".join(lines)


def generate_test_skeleton(class_name: str) -> str:
    """Generate unit test skeleton with MockIP."""
    return f"""#!/usr/bin/env python3
\"\"\"Unit test skeleton for {class_name}.\"\"\"

import unittest
from {class_name.lower()} import {class_name}

class MockIP:
    def __init__(self):
        self.mem = {{0x00: 0x04}} # Initially IDLE

    def read(self, offset: int) -> int:
        return self.mem.get(offset, 0)

    def write(self, offset: int, value: int) -> None:
        self.mem[offset] = value
        if offset == 0x00 and (value & 0x01): # ap_start
            self.mem[0x00] = 0x06 # Set IDLE + DONE

class Test{class_name}(unittest.TestCase):
    def setUp(self):
        self.mock_ip = MockIP()
        self.driver = {class_name}(self.mock_ip)

    def test_idle_and_start(self):
        self.assertTrue(self.driver.is_idle())
        self.driver.start()
        self.assertTrue(self.driver.is_done())

if __name__ == "__main__":
    unittest.main()
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Input C header (.h), Vivado HWH (.hwh), or JSON")
    parser.add_argument("--ip", help="IP instance name (required for HWH files)")
    parser.add_argument("--class-name", default="GeneratedIPDriver", help="Generated Python class name")
    parser.add_argument("--output", default="generated_driver.py", help="Output Python file path")
    parser.add_argument("--generate-test", action="store_true", help="Also generate matching test skeleton")
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.is_file():
        print(f"Error: Input file '{in_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    suffix = in_path.suffix.lower()
    if suffix in (".h", ".hpp"):
        registers = parse_hls_header(in_path)
    elif suffix in (".hwh", ".xml"):
        if not args.ip:
            print("Error: --ip argument is required when parsing HWH files.", file=sys.stderr)
            sys.exit(1)
        registers = parse_hwh_file(in_path, args.ip)
    elif suffix == ".json":
        data = json.loads(in_path.read_text(encoding="utf-8"))
        registers = data.get("registers", data)
    else:
        print(f"Error: Unsupported input file type '{suffix}'", file=sys.stderr)
        sys.exit(1)

    if not registers:
        print("Error: No registers extracted from input file.", file=sys.stderr)
        sys.exit(1)

    driver_code = generate_python_driver(registers, args.class_name)
    out_file = Path(args.output)
    out_file.write_text(driver_code, encoding="utf-8")
    print(f"Generated driver with {len(registers)} registers: {out_file}")

    if args.generate_test:
        test_file = out_file.parent / f"test_{out_file.name}"
        test_code = generate_test_skeleton(args.class_name)
        test_file.write_text(test_code, encoding="utf-8")
        print(f"Generated test skeleton: {test_file}")


if __name__ == "__main__":
    main()
