"""Fixed owner-approved WB, applied to the existing 8-bit ISP gamma LUT.

Instantiate only after STREAMON (the Linux gamma driver resets LUTs there).
Do not change V4L2 gamma controls while this object owns the LUTs. No input
frame is modified/copied: PS writes 384 register words once at startup.
RGB bank order and packed u16 entries match Xilinx 5.15 gamma s_stream.
"""
import xml.etree.ElementTree as ET
import numpy as np


def gain_tables(gains):
    """Linear channel gains with a monotonic shoulder preserving highlights."""
    x = np.arange(256, dtype=np.float64)
    tables = []
    for gain in gains:
        gain = float(gain)
        if not np.isfinite(gain) or not 0.8 <= gain <= 1.9:
            raise ValueError('WB gains must be finite and in [0.8,1.9]')
        y = x * gain
        if gain > 1:
            knee = 220 / gain
            y = np.where(x <= knee, y, 220 + (x-knee)*35/(255-knee))
        tables.append(np.rint(np.clip(y, 0, 255)).astype(np.uint16))
    return np.asarray(tables)


class IspWhiteBalance:
    BANKS = (0x800, 0x1000, 0x1800)  # R, G, B

    def __init__(self, hwh, gains=(1.6838, 1.0, 1.5259), mmio=None):
        root = ET.parse(hwh).getroot()
        module = next(m for m in root.iter('MODULE') if m.get('INSTANCE') == 'v_gamma_lut_0')
        params = {p.get('NAME'): p.get('VALUE') for p in module.iter('PARAMETER')}
        depth = params.get('MAX_DATA_WIDTH')
        if depth is None or int(depth, 0) != 8:
            raise RuntimeError('WB requires the matched 8-bit gamma IP')
        addresses = {int(r.get('BASEVALUE'), 0) for r in root.iter('MEMRANGE')
                     if r.get('INSTANCE') == 'v_gamma_lut_0'}
        if addresses != {0xa0030000}:
            raise RuntimeError('WB gamma address mismatch')
        if mmio is None:
            from pynq import MMIO
            mmio = MMIO(0xa0030000, 0x2000)
        self.mmio = mmio
        if (mmio.read(0x10), mmio.read(0x18), mmio.read(0x20)) != (1920, 1080, 0):
            raise RuntimeError('WB must be configured after RGB full-HD STREAMON')
        self.original = self.read_tables()
        if not np.array_equal(self.original, np.tile(np.arange(256), (3, 1))):
            raise RuntimeError('WB expects gamma 1.0; refusing to replace an unknown curve')
        self.gains = np.asarray(gains, dtype=float)
        if self.gains.shape != (3,) or self.gains[1] != 1:
            raise ValueError('WB requires RGB gains with green=1')
        self.tables = gain_tables(self.gains)
        self.write_tables(self.tables)
        self.last = {'awb_mode': 'isp_fixed', 'awb_rgb_gains': self.gains.tolist(),
                     'awb_changed': False}

    def read_tables(self):
        tables = []
        for base in self.BANKS:
            entries = []
            for i in range(128):
                value = self.mmio.read(base + i*4)
                entries.extend((value & 0xffff, value >> 16))
            tables.append(entries)
        return np.asarray(tables, dtype=np.uint16)

    def write_tables(self, tables):
        for base, lut in zip(self.BANKS, tables):
            for i in range(128):
                self.mmio.write(base+i*4, int(lut[2*i]) | (int(lut[2*i+1]) << 16))
        if not np.array_equal(self.read_tables(), tables):
            raise RuntimeError('ISP WB LUT readback mismatch')

    def close(self):
        self.write_tables(self.original)
