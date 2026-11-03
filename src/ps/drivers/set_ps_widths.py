#!/usr/bin/env python3
"""Configure R6 active AXI ports only, after unload and before FPGA load.

HP1 AFIFM addresses/encoding verified against installed PYNQ embedded_device.py
on kria, 2026-10-21. Never invoke while video/DMA is running.
"""
import mmap
import os
import struct
import sys
import xml.etree.ElementTree as ET

EXPECTED = {
    'C_MAXIGP0_DATA_WIDTH': '128', 'C_MAXIGP2_DATA_WIDTH': '32',
    'C_SAXIGP2_DATA_WIDTH': '128', 'C_SAXIGP3_DATA_WIDTH': '128', 'C_SAXIGP4_DATA_WIDTH': '128',
    'PSU__USE__S_AXI_GP2': '1', 'PSU__USE__S_AXI_GP3': '1', 'PSU__USE__S_AXI_GP4': '1',
}
WRITES = (
    (0xfd615000, 0x300, 0x200), (0xff419000, 0x300, 0),
    (0xfd380000, 3, 0), (0xfd380014, 3, 0),  # HP0 read/write
    (0xfd390000, 3, 0), (0xfd390014, 3, 0),  # HP1 read/write (Restore)
    (0xfd3a0000, 3, 0), (0xfd3a0014, 3, 0),  # HP2 read/write (camera)
)


def validate_hwh(path):
    root = ET.parse(path).getroot()
    ps = [m for m in root.iter('MODULE') if m.get('MODTYPE') == 'zynq_ultra_ps_e']
    if len(ps) != 1:
        raise RuntimeError('Expected exactly one Zynq UltraScale PS in HWH')
    params = {p.get('NAME'): p.get('VALUE') for p in ps[0].iter('PARAMETER')}
    for key, value in EXPECTED.items():
        if params.get(key) != value:
            raise RuntimeError('HWH mismatch: %s=%r, expected %s' % (key, params.get(key), value))


def configure(path):
    validate_hwh(path)  # All checks precede /dev/mem access.
    fd = os.open('/dev/mem', os.O_RDWR | os.O_SYNC)
    try:
        for address, mask, value in WRITES:
            with mmap.mmap(fd, 4096, flags=mmap.MAP_SHARED,
                           prot=mmap.PROT_READ | mmap.PROT_WRITE, offset=address & ~4095) as page:
                offset = address & 4095
                old = struct.unpack_from('<I', page, offset)[0]
                new = (old & ~mask) | value
                struct.pack_into('<I', page, offset, new)
                actual = struct.unpack_from('<I', page, offset)[0]
                if actual != new:
                    raise RuntimeError('PS width readback failed at %#x' % address)
                print('%#010x: %#010x -> %#010x' % (address, old, actual))
    finally:
        os.close(fd)


if __name__ == '__main__':
    configure(sys.argv[1])
