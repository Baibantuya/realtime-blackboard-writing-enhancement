"""Executable example with real V24 contract and a fake MMIO object only."""
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parents[1]
W = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
from pynq_tools.codegen import parse_hwh_file, generate_python_driver
from pynq_tools.benchmark import PynqBenchmarker


def main():
    hwh = W/'evidence/20261027/runtime_v24/hardware/imx219-fusion-v24.hwh'
    registers = parse_hwh_file(hwh, '/board_quantize_rgb_0')
    pointers = json.loads((PACKAGE/'examples/scene_pointers.json').read_text(encoding='utf-8'))
    namespace = {}
    exec(generate_python_driver(registers, 'SceneIP', pointers), namespace)
    class FakeIP:
        def __init__(self): self.writes = []
        def write(self, offset, value): self.writes.append((offset, value))
        def read(self, offset): return 0
    ip = FakeIP()
    driver = namespace['SceneIP'](ip)
    driver.write_pointer('src', 0x12345000)
    driver.write_register('control', 3)
    assert ip.writes == [(0x18, 0x12345000), (0x68, 3)]
    ticks = iter((0, 10, 11, 12))
    b = PynqBenchmarker(event_name='presented_content', latency_scope='PS content stage', start_event='process entry', clock=lambda: next(ticks))
    for latency in (1, 9, 1): b.record_frame(latency)
    print(json.dumps({'mock_writes': ip.writes, 'metrics': b.compute_statistics(), 'hardware_access': False}, indent=2))


if __name__ == '__main__':
    main()
