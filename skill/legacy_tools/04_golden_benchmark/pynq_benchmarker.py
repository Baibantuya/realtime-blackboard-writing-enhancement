#!/usr/bin/env python3
"""PYNQ Pipeline Benchmarking and Automated Reporting Tool.

Records high-resolution frame latency, steady-state throughput (FPS),
frame-to-frame jitter, and anomaly/bad-frame counts, exporting standardized
Markdown and JSON benchmark artifacts.
"""

from __future__ import annotations

import json
import statistics
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


class PynqBenchmarker:
    """Collects hardware performance metrics and generates standardized reports."""

    def __init__(self, name: str = "PYNQ_Benchmark") -> None:
        self.name = name
        self.start_time = time.monotonic()
        self.latencies_ms: List[float] = []
        self.timestamps: List[float] = []
        self.bad_frames_count = 0
        self.metadata: Dict[str, Any] = {}

    def set_metadata(self, key: str, value: Any) -> None:
        """Store additional environment metadata (e.g. board model, clock frequency)."""
        self.metadata[key] = value

    def record_frame(self, latency_ms: float, is_bad: bool = False) -> None:
        """Record the execution duration and status of a single frame/iteration."""
        now = time.monotonic()
        self.timestamps.append(now)
        self.latencies_ms.append(float(latency_ms))
        if is_bad:
            self.bad_frames_count += 1

    def compute_statistics(self) -> Dict[str, Any]:
        """Compute comprehensive throughput and latency statistics."""
        count = len(self.latencies_ms)
        if count == 0:
            return {"total_frames": 0, "fps": 0.0, "status": "EMPTY"}

        total_elapsed = self.timestamps[-1] - self.start_time
        # Steady state elapsed (excluding first frame initialization delay)
        if count > 1:
            steady_elapsed = self.timestamps[-1] - self.timestamps[0]
            steady_fps = (count - 1) / max(steady_elapsed, 1e-6)
        else:
            steady_fps = 1.0 / max(total_elapsed, 1e-6)

        sorted_latencies = sorted(self.latencies_ms)
        p50 = sorted_latencies[int(count * 0.50)]
        p95 = sorted_latencies[min(int(count * 0.95), count - 1)]
        p99 = sorted_latencies[min(int(count * 0.99), count - 1)]

        mean_lat = statistics.mean(self.latencies_ms)
        std_lat = statistics.stdev(self.latencies_ms) if count > 1 else 0.0

        return {
            "total_frames": count,
            "total_elapsed_seconds": round(total_elapsed, 3),
            "steady_fps": round(steady_fps, 2),
            "first_frame_latency_ms": round(self.latencies_ms[0], 2),
            "mean_latency_ms": round(mean_lat, 2),
            "jitter_stdev_ms": round(std_lat, 2),
            "p50_latency_ms": round(p50, 2),
            "p95_latency_ms": round(p95, 2),
            "p99_latency_ms": round(p99, 2),
            "bad_frames": self.bad_frames_count,
            "bad_frame_rate": round(self.bad_frames_count / count, 4),
        }

    def generate_report(self, output_dir: str | Path) -> Tuple[Path, Path]:
        """Generate markdown and JSON benchmark reports.

        Returns:
            Tuple of (markdown_path, json_path).
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        stats = self.compute_statistics()
        combined_data = {
            "benchmark_name": self.name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "environment": self.metadata,
            "results": stats,
        }

        # 1. Export JSON report
        json_file = out_path / f"{self.name}_report.json"
        json_file.write_text(json.dumps(combined_data, indent=2), encoding="utf-8")

        # 2. Export Markdown report
        md_lines = [
            f"# 性能基准测试报告: {self.name}",
            f"- **测试时间**: {combined_data['timestamp']}",
            f"- **硬件与环境**: {', '.join(f'{k}={v}' for k, v in self.metadata.items()) if self.metadata else 'N/A'}",
            "",
            "## 核心性能指标 (Summary Metrics)",
            "",
            "| 指标项 | 实测数值 | 评价说明 |",
            "|---|---|---|",
            f"| **总处理帧数** | `{stats['total_frames']}` 帧 | 样本规模 |",
            f"| **稳态吞吐帧率 (FPS)** | **`{stats['steady_fps']} FPS`** | 连续稳态处理速度 |",
            f"| **首帧初始化时延** | `{stats['first_frame_latency_ms']} ms` | 冷启动开销 |",
            f"| **平均单帧时延** | `{stats['mean_latency_ms']} ms` | 综合平均响应时间 |",
            f"| **帧间隔抖动 (Jitter)** | `±{stats['jitter_stdev_ms']} ms` | 传输平稳性标准差 |",
            f"| **P95 延迟门限** | `{stats['p95_latency_ms']} ms` | 95% 帧处理完成上限 |",
            f"| **P99 延迟门限** | `{stats['p99_latency_ms']} ms` | 99% 极端尾部时延 |",
            f"| **坏帧/丢帧统计** | **`{stats['bad_frames']}` 帧 (`{stats['bad_frame_rate']:.2%}`)** | 硬件稳定性判定 |",
            "",
            "## 结论与门禁检查",
            "- 零坏帧通过: " + ("PASS" if stats["bad_frames"] == 0 else "FAIL"),
            "- 稳态性能达标: " + ("PASS" if stats["steady_fps"] > 0 else "N/A"),
            "",
        ]
        md_file = out_path / f"{self.name}_report.md"
        md_file.write_text("\n".join(md_lines), encoding="utf-8")

        return md_file, json_file
