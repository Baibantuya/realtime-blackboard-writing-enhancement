#!/usr/bin/env python3
"""Unit tests for 03_contract_codegen."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import tempfile
import unittest
from codegen_pynq_driver import generate_python_driver, parse_hls_header


class TestContractCodegen(unittest.TestCase):
    def test_parse_hls_header_and_generate_code(self):
        c_header_sample = """
        // ==============================================================
        // Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2021.2
        // ==============================================================
        #define XMYIP_ADDR_AP_CTRL 0x00
        #define XMYIP_ADDR_WIDTH_DATA 0x10
        #define XMYIP_ADDR_HEIGHT_DATA 0x18
        #define XMYIP_ADDR_SRC_ADDR_1_DATA 0x20
        #define XMYIP_ADDR_SRC_ADDR_2_DATA 0x24
        #define XMYIP_ADDR_DST_ADDR_1_DATA 0x28
        #define XMYIP_ADDR_DST_ADDR_2_DATA 0x2C
        """

        with tempfile.NamedTemporaryFile("w", suffix="_hw.h", delete=False) as f:
            f.write(c_header_sample)
            tmp_path = Path(f.name)

        try:
            regs = parse_hls_header(tmp_path)
            self.assertIn("width", regs)
            self.assertEqual(regs["width"], 0x10)
            self.assertEqual(regs["src_addr_1"], 0x20)
            self.assertEqual(regs["src_addr_2"], 0x24)

            # Generate driver code
            code = generate_python_driver(regs, "TestIPDriver")
            self.assertIn("class TestIPDriver:", code)
            self.assertIn("def set_src_addr_address(self, phys_addr: int) -> None:", code)
            self.assertIn("def set_width(self, value: int) -> None:", code)
            self.assertIn("def wait_done(self, timeout_seconds: float = 2.0) -> None:", code)

            # Verify generated code compiles without syntax errors
            compiled = compile(code, "<string>", "exec")
            self.assertIsNotNone(compiled)
        finally:
            tmp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
