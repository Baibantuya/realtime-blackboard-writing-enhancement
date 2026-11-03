"""Explicit HWH register contracts and standalone driver generation (no PYNQ import)."""
from __future__ import annotations
import argparse
import json
import keyword
from pathlib import Path
import re
import xml.etree.ElementTree as ET


def integer(value):
    if isinstance(value, bool):
        raise ValueError('boolean is not a register number')
    if isinstance(value, int):
        return value
    if not isinstance(value, str):
        raise ValueError('integer required')
    return int(value, 16 if value.lower().startswith('0x') else 10)


def tag(e):
    return e.tag.rsplit('}', 1)[-1]


def properties(e):
    result = dict(e.attrib)
    for p in e:
        if tag(p) != 'PROPERTY':
            continue
        name, value = p.get('NAME'), p.get('VALUE')
        if name in result and result[name] != value:
            raise ValueError(f'conflicting property {name}')
        result[name] = value
    return result


def parse_hwh_file(path, ip_name):
    """Match exact FULLNAME or unique exact NAME/INSTANCE; missing fields are errors."""
    modules = [m for m in ET.parse(path).getroot().iter() if tag(m) == 'MODULE']
    if ip_name.startswith('/'):
        matches = [m for m in modules if m.get('FULLNAME') == ip_name]
    else:
        matches = [m for m in modules if m.get('NAME', m.get('INSTANCE')) == ip_name]
    if len(matches) != 1:
        raise ValueError(f'exact IP match required: {ip_name!r}; found {len(matches)}')
    regs = {}
    for r in matches[0].iter():
        if tag(r) != 'REGISTER':
            continue
        p = properties(r)
        name = p.get('NAME', '').lower()
        if not name or name in regs:
            raise ValueError('missing or duplicate register name')
        if not all(k in p for k in ('ADDRESS_OFFSET', 'SIZE', 'ACCESS')):
            raise ValueError(f'{name}: ADDRESS_OFFSET, SIZE and ACCESS required')
        regs[name] = {'offset': integer(p['ADDRESS_OFFSET']), 'width': integer(p['SIZE']), 'access': p['ACCESS'].lower()}
    validate_registers(regs)
    return regs


def validate_registers(regs):
    if not regs:
        raise ValueError('empty register contract')
    occupied = set()
    for name, r in regs.items():
        if not isinstance(name, str) or not name:
            raise ValueError('register name required')
        off, width = integer(r['offset']), integer(r['width'])
        if off < 0 or off % 4 or not 1 <= width <= 32:
            raise ValueError(f'{name}: only aligned 1..32-bit MMIO words supported')
        if off in occupied:
            raise ValueError(f'{name}: overlapping MMIO word')
        occupied.add(off)
        if r['access'] not in ('read-only', 'write-only', 'read-write'):
            raise ValueError(f'{name}: unknown access')


def parse_hls_header(path):
    """Parse real HLS prefixes containing underscores; retain logical 64-bit width."""
    text = Path(path).read_text(encoding='utf-8')
    pattern = r'^\s*#define\s+(X\w+?)_(ADDR|BITS)_(\w+)\s+(0x[0-9a-fA-F]+|\d+)\b'
    addresses, widths = {}, {}
    prefixes = set()
    for prefix, kind, raw, val in re.findall(pattern, text, re.MULTILINE | re.IGNORECASE):
        prefixes.add(prefix)
        name = raw.lower()
        if name.endswith('_data'):
            name = name[:-5]
        table = addresses if kind.upper() == 'ADDR' else widths
        if name in table:
            raise ValueError(f'duplicate header macro {name}')
        table[name] = integer(val)
    if len(prefixes) != 1 or not addresses:
        raise ValueError('one nonempty HLS register bank required')
    standard = {'ap_ctrl', 'gie', 'ier', 'isr'}
    result = {}
    for name, off in addresses.items():
        width = widths.get(name, 32 if name in standard else None)
        if width not in (32, 64):
            raise ValueError(f'{name}: missing or unsupported BITS macro')
        result[name] = {'offset': off, 'width': width}
    return result


def header_words(logical):
    aliases = {'ap_ctrl': 'ctrl', 'gie': 'gier', 'ier': 'ip_ier', 'isr': 'ip_isr'}
    words = {}
    for name, r in logical.items():
        if r['width'] == 64:
            for i in (1, 2):
                words[f'{name}_{i}'] = {'offset': r['offset'] + 4 * (i - 1), 'width': 32}
        else:
            words[aliases.get(name, name)] = r
    return words


def validate_pointers(regs, pointers):
    """Pointer semantics supplied by a reviewed interface, never inferred from CPU width."""
    used = set()
    for name, p in pointers.items():
        if not isinstance(name, str) or not name:
            raise ValueError('pointer name required')
        width, words = p.get('width'), p.get('words')
        if width not in (32, 64) or not isinstance(words, list) or len(words) != width // 32:
            raise ValueError(f'{name}: explicit 32/64-bit ordered words required')
        for word in words:
            if word not in regs or regs[word]['width'] != 32 or regs[word]['access'] == 'read-only' or word in used:
                raise ValueError(f'{name}: invalid or overlapping pointer word {word}')
            used.add(word)
        if width == 64 and regs[words[1]]['offset'] != regs[words[0]]['offset'] + 4:
            raise ValueError(f'{name}: split words must be consecutive low/high')


def generate_python_driver(regs, class_name='GeneratedIPDriver', pointers=None):
    validate_registers(regs)
    pointers = pointers or {}
    validate_pointers(regs, pointers)
    if not class_name.isidentifier() or keyword.iskeyword(class_name):
        raise ValueError('class name must be a Python identifier')
    # repr of data only; no source file expressions or register names are interpolated as code.
    return f'''"""Generated explicit register access; offline mock tested, board use pending."""
class {class_name}:
    REGISTERS = {regs!r}
    POINTERS = {pointers!r}

    def __init__(self, ip_handle):
        self.ip = ip_handle

    def write_register(self, name, value):
        r = self.REGISTERS[name]
        if r['access'] == 'read-only':
            raise PermissionError(name)
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value < (1 << r['width']):
            raise ValueError('register value out of range')
        self.ip.write(r['offset'], value)

    def read_register(self, name):
        r = self.REGISTERS[name]
        if r['access'] == 'write-only':
            raise PermissionError(name)
        return int(self.ip.read(r['offset']))

    def write_pointer(self, name, address):
        p = self.POINTERS[name]
        if isinstance(address, bool) or not isinstance(address, int) or not 0 <= address < (1 << p['width']):
            raise ValueError('pointer address out of range')
        for i, word in enumerate(p['words']):
            self.write_register(word, (address >> (32 * i)) & 0xffffffff)
'''


def generate_test_skeleton(class_name, filename):
    return f'''"""Standalone generated smoke test: all IO is MockIP."""
import importlib.util
from pathlib import Path
import unittest
spec = importlib.util.spec_from_file_location('generated_under_test', Path(__file__).with_name({filename!r}))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class MockIP:
    def __init__(self): self.mem = {{}}
    def write(self, off, val): self.mem[off] = val
    def read(self, off): return self.mem.get(off, 0)

class TestContract(unittest.TestCase):
    def test_writable_words(self):
        ip = MockIP()
        driver = module.{class_name}(ip)
        for name, reg in driver.REGISTERS.items():
            if reg['access'] != 'read-only':
                driver.write_register(name, 1)
                self.assertEqual(ip.mem[reg['offset']], 1)
    def test_readonly_rejected(self):
        driver = module.{class_name}(MockIP())
        for name, reg in driver.REGISTERS.items():
            if reg['access'] == 'read-only':
                with self.assertRaises(PermissionError): driver.write_register(name, 0)

if __name__ == '__main__': unittest.main()
'''


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=Path, required=True, help='HWH XML, not a C header')
    p.add_argument('--ip', required=True, help='Exact FULLNAME (preferred) or unique NAME')
    p.add_argument('--pointers', type=Path, help='Reviewed JSON: pointer name -> width and ordered words')
    p.add_argument('--class-name', default='GeneratedIPDriver')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--generate-test', action='store_true')
    a = p.parse_args()
    regs = parse_hwh_file(a.input, a.ip)
    pointers = json.loads(a.pointers.read_text(encoding='utf-8')) if a.pointers else {}
    source = generate_python_driver(regs, a.class_name, pointers)
    test_path = a.output.with_name('test_' + a.output.name)
    if a.output.suffix != '.py' or a.output.exists() or (a.generate_test and test_path.exists()):
        raise ValueError('new .py output required; existing files are never overwritten')
    a.output.write_text(source, encoding='utf-8')
    if a.generate_test:
        test_path.write_text(generate_test_skeleton(a.class_name, a.output.name), encoding='utf-8')
    print(json.dumps({'registers': len(regs), 'output': str(a.output), 'hardware_access': False}))


if __name__ == '__main__':
    main()
