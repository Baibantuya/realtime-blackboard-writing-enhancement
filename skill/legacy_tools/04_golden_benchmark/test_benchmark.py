#!/usr/bin/env python3
"""Unit tests for 04_golden_benchmark."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import tempfile
import unittest
import numpy as np
from golden_comparator import GoldenComparator
from pynq_benchmarker import PynqBenchmarker


class TestGoldenBenchmark(unittest.TestCase):
    def test_golden_comparator_exact_and_mismatch(self):
        comp = GoldenComparator(tolerance=0.0)

        # 1. Exact match
        arr1 = np.array([10, 20, 30, 40], dtype=np.uint8)
        arr2 = np.array([10, 20, 30, 40], dtype=np.uint8)
        res1 = comp.compare(arr1, arr2)
        self.assertTrue(res1.is_match)
        self.assertEqual(res1.mismatch_count, 0)
        self.assertEqual(res1.psnr_db, float("inf"))

        # 2. Mismatch with tolerance
        arr3 = np.array([10, 21, 30, 45], dtype=np.uint8) # diffs: 0, 1, 0, 5
        res_strict = comp.compare(arr1, arr3)
        self.assertFalse(res_strict.is_match)
        self.assertEqual(res_strict.mismatch_count, 2)
        self.assertEqual(res_strict.max_abs_error, 5.0)

        # Compare with tolerance=1.0 (only element 4 diff=5 should fail)
        comp_tol = GoldenComparator(tolerance=1.0)
        res_tol = comp_tol.compare(arr1, arr3)
        self.assertFalse(res_tol.is_match)
        self.assertEqual(res_tol.mismatch_count, 1)

    def test_pynq_benchmarker_metrics_and_reporting(self):
        bench = PynqBenchmarker(name="UnitTestBench")
        bench.set_metadata("board", "KV260")
        bench.set_metadata("clock_mhz", 200)

        # Simulate 10 frames
        for i in range(10):
            bench.record_frame(latency_ms=33.3 + (i % 3), is_bad=(i == 9))

        stats = bench.compute_statistics()
        self.assertEqual(stats["total_frames"], 10)
        self.assertEqual(stats["bad_frames"], 1)
        self.assertGreater(stats["mean_latency_ms"], 30.0)

        with tempfile.TemporaryDirectory() as tmpdir:
            md_path, json_path = bench.generate_report(tmpdir)
            self.assertTrue(md_path.is_file())
            self.assertTrue(json_path.is_file())
            md_content = md_path.read_text(encoding="utf-8")
            self.assertIn("UnitTestBench", md_content)
            self.assertIn("KV260", md_content)


if __name__ == "__main__":
    unittest.main()
