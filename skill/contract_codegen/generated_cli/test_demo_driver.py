#!/usr/bin/env python3
"""Unit test skeleton for DemoIP."""

import unittest
from demo_driver import DemoIP

class MockIP:
    def __init__(self):
        self.mem = {0x00: 0x04} # Initially IDLE

    def read(self, offset: int) -> int:
        return self.mem.get(offset, 0)

    def write(self, offset: int, value: int) -> None:
        self.mem[offset] = value
        if offset == 0x00 and (value & 0x01): # ap_start
            self.mem[0x00] = 0x06 # Set IDLE + DONE

class TestDemoIP(unittest.TestCase):
    def setUp(self):
        self.mock_ip = MockIP()
        self.driver = DemoIP(self.mock_ip)

    def test_idle_and_start(self):
        self.assertTrue(self.driver.is_idle())
        self.driver.start()
        self.assertTrue(self.driver.is_done())

if __name__ == "__main__":
    unittest.main()
