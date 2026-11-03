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


class RegisterMap(dict):
    """Offset mapping with optional bit widths and register access metadata."""
    def __init__(self):
        super().__init__()
        self.widths: Dict[str, int] = {}
        self.access: Dict[str, str] = {}


def parse_hls_header(header_path: Path) -> Dict[str, int]:
    """Extract register offsets from Vitis HLS x*_hw.h header file."""
    text = header_path.read_text(encoding="utf-8", errors="ignore")
    # Matches: #define X<NAME>_ADDR_<REGNAME> 0x10 or 16
    pattern = re.compile(
        r"#define\s+[Xx][A-Za-z0-9_]+?_ADDR_([A-Za-z0-9_]+)\s+(0[xX][0-9a-fA-F]+|\d+)"
    )
    registers = RegisterMap()
    for match in pattern.finditer(text):
        raw_name = match.group(1).lower()
        if raw_name.endswith("_data"):
            name = raw_name[:-5]
        elif raw_name.endswith("_v"):
            name = raw_name[:-2]
        else:
            name = raw_name
        val_str = match.group(2)
        val = int(val_str, 16) if val_str.lower().startswith("0x") else int(val_str)
        if name in registers and registers[name] != val:
            raise ValueError(f"Conflicting header offset for {name}")
        registers[name] = val
    for raw_name, width in re.findall(r"#define\s+[Xx][A-Za-z0-9_]+?_BITS_([A-Za-z0-9_]+)\s+(\d+)",text):
        name=raw_name.lower()
        if name.endswith('_data'):name=name[:-5]
        elif name.endswith('_v'):name=name[:-2]
        if name in registers:
            if not 1 <= int(width) <= 64:raise ValueError(f"Unsupported header width for {name}")
            registers.widths[name]=int(width)
    return registers


def parse_hwh_file(hwh_path: Path, ip_name: str) -> Dict[str, int]:
    """Read an exact, unambiguous instance; never default missing offsets to zero.

    Vivado stores register offsets in direct PROPERTY children. FIELD offsets
    are relative bit-field metadata and must not be interpreted as registers.
    Attribute-style and PROPERTIES-wrapped metadata are also accepted when
    their values agree. The returned contract is for 32-bit AXI-Lite registers.
    """
    tag = lambda node: node.tag.rsplit("}", 1)[-1]
    query = ip_name.strip().strip("/").casefold()
    if not query:
        raise ValueError("An exact IP instance name is required")
    matches = [node for node in ET.parse(hwh_path).getroot().iter()
               if tag(node) == "MODULE" and query in {
                   node.get(key, "").strip("/").casefold()
                   for key in ("INSTANCE", "NAME", "FULLNAME")}]
    if len(matches) != 1:
        raise ValueError(f"Expected one exact IP instance '{ip_name}', found {len(matches)}")
    registers = RegisterMap()
    owners: Dict[int, str] = {}
    for reg in matches[0].iter():
        if tag(reg) != "REGISTER":
            continue
        name = reg.get("NAME", "").lower()
        if not re.fullmatch(r"[a-z_][a-z0-9_]*", name) or name in registers:
            raise ValueError(f"Missing, invalid or duplicate register name: {name!r}")
        values = [reg.get(key) for key in ("ADDRESS_OFFSET", "OFFSET") if reg.get(key) is not None]
        properties = [child for child in reg if tag(child) == "PROPERTY"]
        properties += [prop for child in reg if tag(child) == "PROPERTIES"
                       for prop in child if tag(prop) == "PROPERTY"]
        values += [prop.get("VALUE") for prop in properties
                   if prop.get("NAME") in ("ADDRESS_OFFSET", "OFFSET")]
        offsets = []
        for value in values:
            value = (value or "").strip()
            if not re.fullmatch(r"(?:0[xX][0-9a-fA-F]+|[0-9]+)", value):
                raise ValueError(f"Invalid address offset for {name}: {value!r}")
            offsets.append(int(value, 16 if value.lower().startswith("0x") else 10))
        if not offsets or len(set(offsets)) != 1:
            raise ValueError(f"Missing or conflicting address offset for {name}")
        off = offsets[0]
        if off % 4 or off > 0xFFFFFFFC:
            raise ValueError(f"Offset is outside aligned 32-bit AXI-Lite addressing: {name}={off}")
        if off in owners:
            raise ValueError(f"Unsupported register alias at {off:#x}: {owners[off]} and {name}")
        owners[off] = name
        registers[name] = off
        sizes = [prop.get('VALUE') for prop in properties if prop.get('NAME') == 'SIZE']
        if sizes and (len(set(sizes)) != 1 or not (sizes[0] or '').isdigit()):
            raise ValueError(f"Invalid or conflicting size for {name}")
        width = int(sizes[0]) if sizes else 32
        if not 1 <= width <= 64:
            raise ValueError(f"Unsupported register width for {name}: {width}")
        registers.widths[name] = width
        access = [prop.get('VALUE') for prop in properties if prop.get('NAME') == 'ACCESS']
        if access and (len(set(access)) != 1 or access[0] not in ('read-only','write-only','read-write')):
            raise ValueError(f"Unsupported or conflicting access for {name}")
        registers.access[name] = access[0] if access else 'read-write'
    if not registers:
        raise ValueError(f"No registers in IP instance '{ip_name}'")
    locations = {}
    for name, off in registers.items():
        for word in range((registers.widths[name]+31)//32):
            address = off+4*word
            if address > 0xFFFFFFFC or address in locations:
                raise ValueError(f"Overlapping or out-of-range register storage: {name}")
            locations[address] = name
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

    widths = getattr(registers, 'widths', {})
    access = getattr(registers, 'access', {})
    # Legacy contracts may describe 64-bit pointers as adjacent low/high pairs.
    pointer_stems: Dict[str, Tuple[int, int]] = {}
    scalar_regs: Dict[str, int] = {}

    for reg_name, offset in sorted(registers.items(), key=lambda x: x[1]):
        if offset == 0 and reg_name.lower() in ("ap_ctrl", "control", "ctrl"):
            continue
        if reg_name.endswith("_1"):
            stem = reg_name[:-2]
            high_name = f"{stem}_2"
            if (high_name in registers
                    and widths.get(reg_name,32) == widths.get(high_name,32) == 32
                    and access.get(reg_name,'read-write') != 'read-only'
                    and access.get(high_name,'read-write') != 'read-only'):
                if registers[high_name] != offset+4:
                    raise ValueError(f"Non-adjacent split pointer: {stem}")
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
            '        if not 0 <= addr < (1 << 64): raise ValueError("Address outside 64-bit range")',
            f"        self.ip.write(0x{low_off:02X}, addr & 0xFFFFFFFF)",
            f"        self.ip.write(0x{high_off:02X}, (addr >> 32) & 0xFFFFFFFF)",
            "",
        ])

    # Generate scalar register getters and setters
    for reg_name, offset in scalar_regs.items():
        width = widths.get(reg_name,32)
        permission = access.get(reg_name,'read-write')
        if permission != 'read-only':
            lines.extend([f"    def set_{reg_name}(self, value: int) -> None:",
                          f'        """Write {width}-bit {reg_name} at 0x{offset:02X}."""',
                          '        value = int(value)'])
            if width > 32:
                lines.append(f'        if not 0 <= value < (1 << {width}): raise ValueError("Value outside {width}-bit range")')
            lines.append(f"        self.ip.write(0x{offset:02X}, value & 0xFFFFFFFF)")
            if width > 32:
                lines.append(f"        self.ip.write(0x{offset+4:02X}, (value >> 32) & 0xFFFFFFFF)")
            lines.append('')
        if permission != 'write-only':
            lines.extend([f"    def get_{reg_name}(self) -> int:",
                          f'        """Read {width}-bit {reg_name}; multiword reads are not atomic."""',
                          f"        value = int(self.ip.read(0x{offset:02X})) & 0xFFFFFFFF"])
            if width > 32:
                lines.append(f"        value |= (int(self.ip.read(0x{offset+4:02X})) & 0xFFFFFFFF) << 32")
            lines.extend([f"        return value & {(1<<width)-1}",''])

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


def generate_test_skeleton(class_name: str, module_name: str = None) -> str:
    """Generate unit test skeleton with MockIP."""
    return f"""#!/usr/bin/env python3
\"\"\"Unit test skeleton for {class_name}.\"\"\"

import unittest
from {module_name or class_name.lower()} import {class_name}

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
        test_code = generate_test_skeleton(args.class_name, out_file.stem)
        test_file.write_text(test_code, encoding="utf-8")
        print(f"Generated test skeleton: {test_file}")


if __name__ == "__main__":
    main()
