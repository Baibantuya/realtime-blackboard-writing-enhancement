import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import unittest
from register_map_inspector import RegisterMapInspector


class MockRegister:
    def __init__(self, name: str, address: int):
        self.name = name
        self.address = address


class MockIP:
    def __init__(self):
        # Emulate HLS generated registers including 64-bit split pointer
        self.register_map = [
            MockRegister("AP_CTRL", 0x00),
            MockRegister("width", 0x10),
            MockRegister("height", 0x18),
            MockRegister("src_addr_1", 0x20),
            MockRegister("src_addr_2", 0x24),
            MockRegister("dst_addr_1", 0x28),
            MockRegister("dst_addr_2", 0x2C),
        ]
        self.mem = {reg.address: 0 for reg in self.register_map}
        # Initially set AP_CTRL idle bit (bit 2)
        self.mem[0x00] = 0x04

    def read(self, offset: int) -> int:
        return self.mem.get(offset, 0)

    def write(self, offset: int, val: int) -> None:
        self.mem[offset] = val


class TestRegisterMapInspector(unittest.TestCase):
    def setUp(self):
        self.ip = MockIP()
        self.inspector = RegisterMapInspector(self.ip)

    def test_discovery_and_verification(self):
        # Verify valid contract
        self.assertTrue(
            self.inspector.verify_registers(
                required_scalars=["width", "height"],
                required_pointers=["src_addr", "dst_addr"],
            )
        )
        # Verify missing register raises KeyError
        with self.assertRaises(KeyError):
            self.inspector.verify_registers(required_scalars=["non_existent_reg"])

    def test_64bit_pointer_write(self):
        # Physical address > 32-bit: 0x00000008_76543210
        test_addr_64 = 0x876543210
        self.inspector.write_pointer_64("src_addr", test_addr_64)

        # src_addr_1 should receive low 32-bit: 0x76543210
        self.assertEqual(self.ip.read(0x20), 0x76543210)
        # src_addr_2 should receive high 32-bit: 0x8
        self.assertEqual(self.ip.read(0x24), 0x8)

    def test_handshake_state(self):
        self.assertTrue(self.inspector.is_idle)
        self.assertFalse(self.inspector.is_done)

        # Start IP
        self.inspector.start()
        self.assertEqual(self.ip.read(0x00), 0x01)


if __name__ == "__main__":
    unittest.main()
