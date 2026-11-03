# 模块 04: 黄金参考比对与性能自动化报表工具 (04_golden_benchmark)

## 1. 适用范围与功能职责

### 适用场景
- 软硬件协同验证全生命周期（C/C++ 仿真、RTL 联仿、板端 Smoke 与长周期稳态压测）；
- 任何需要将 PL 硬件加速输出与软件纯 CPU 算法黄金真值（Golden Reference）进行数值比对的场景；
- 自动化测量并输出规范的吞吐帧率（FPS）、帧间隔抖动（Jitter）、首帧延迟、坏帧数（Bad Frames）以及性能报告。

### 核心功能
1. **多维度黄金参考比对（Golden Comparator）**：
   - 支持逐像素/逐元素绝对精确匹配（Exact Bit-Accurate Match）；
   - 支持容差比对（MAE、Max Error、PSNR、SSIM），输出不匹配点位统计与错误热力掩膜；
   - 自动生成符合赛题提交要求的差异摘要 JSON。
2. **端到端三级性能压测报表生成器（PYNQ Benchmarker）**：
   - **第 1 级（算法级）**：单帧/多帧软硬件数值等价性比对（验证功能正确性）；
   - **第 2 级（冒烟级）**：3 帧端到端连通性测试（验证寄存器、DMA 与缓存闭环）；
   - **第 3 级（稳态级）**：1000 帧长周期压测，自动化统计稳态 FPS、首帧耗时、坏帧率与异常计数；
   - 自动导出规范的 Markdown 实验报告，可直接粘贴进比赛报告。

### 失效条件
- 比对的两组数据维度或形状（Shape）不一致；
- 输入数据包含未定义的 `NaN` 或 `Inf`。

---

## 2. 核心 API 与使用范式

### 2.1 黄金参考比对
```python
from skill.golden_benchmark.golden_comparator import GoldenComparator

# 比对硬件输出与纯软件真值
comparator = GoldenComparator(tolerance=0) # 0 表示要求位精确匹配
result = comparator.compare(hardware_output, golden_reference)

print(f"Match: {result.is_match}")
print(f"Max Absolute Error: {result.max_abs_error}")
print(f"Mismatch Pixels: {result.mismatch_count} ({result.mismatch_ratio:.2%})")
```

### 2.2 性能自动压测与报告生成
```python
from skill.golden_benchmark.pynq_benchmarker import PynqBenchmarker

benchmarker = PynqBenchmarker(name="Video_Pipeline_Benchmark")

for frame_idx in range(1000):
    start = time.monotonic()
    # 执行一次软硬件迭代
    output = process_frame(frame)
    latency_ms = (time.monotonic() - start) * 1000
    
    # 记录该帧延迟与健康状态
    benchmarker.record_frame(latency_ms=latency_ms, is_bad=False)

# 自动生成完整报告
benchmarker.generate_report(output_dir="report/benchmark_results")
```

---

## 3. 经验来源与失败复盘

本模块直接源自项目中的以下排查实证：
1. **口头宣称 30FPS 但实际存在偶发丢帧**：仅靠单次平均耗时评估吞吐会掩盖偶尔发生的长延迟抖动。压测工具引入首帧延迟独立统计、百分位延迟（P95/P99）与连续 1000 帧无坏帧严格门禁，为项目提供无可辩驳的实测铁证。
2. **色度通道细微溢出排查**：定点化 HLS 算法在个别边界像素出现 ±1 溢出。通过容差热力图分析，快速区分是算法定点误差还是总线错位，极大加速算法收敛。
