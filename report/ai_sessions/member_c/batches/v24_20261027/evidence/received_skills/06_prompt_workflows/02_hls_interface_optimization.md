# 提示词工作流 02: HLS 综合报告 -> 瓶颈定位与约束收敛

## 1. 适用场景
- 队伍在完成 Vitis HLS C/C++ 代码编写后，执行 `csynth_design` 综合，发现启动间隔（II > 1）无法达成满流水，或者时钟时序违例（WNS < 0），或者 BRAM / DSP 资源超标。

## 2. 提示词模板 (Prompt Template)

```markdown
你是一位精通 AMD Vitis HLS (2020.1~2026.1) 与 UltraFast 设计方法学的顶尖 FPGA 优化专家。
我的 HLS 加速核在综合后未能达到性能/资源预期，请根据我提供的源码与综合报告帮我深度定位根因并给出精确的 pragma 修复方案。

【硬件与时钟目标】：
- 目标器件：<填写器件型号，如 Zynq UltraScale+ xck26-sfvc784-2LV-c>
- 目标时钟频率：<如 200MHz，时钟周期 5.0ns>
- 目标性能指标：<如要求主循环 Initiation Interval II=1>

【HLS 核心算法源码片段】：
<粘贴涉及内层循环或大数组读写的 C/C++ 代码>

【Vitis HLS 综合报告关键输出】：
<粘贴 csynth.rpt 中的 Timing Summary、Loop Latency & II、以及 Memory/Resource 统计部分>

请按以下逻辑为我提供诊断与代码重构方案：

1. **流水线停顿（Pipeline Stall）根因分析**：
   - 指出导致 II > 1 的具体数据依赖性（True RAW Dependency / Loop-Carried Dependency）；
   - 分析是否存在多端口存储器争用（Dual-Port BRAM bank conflict），具体哪一行代码在同一周期试图访问同一数组的多个地址。
2. **时钟时序违例（Timing Slack Violation）根因分析**：
   - 提取报告中组合逻辑最长路径（Critical Path），指出是由于深层三元运算、长位宽乘除法，还是未打拍的多路选择器导致延迟超过 5.0ns。
3. **精准 HLS 指令与代码级重构**：
   - 给出重构后的完整 C/C++ 函数，精准插入 `#pragma HLS PIPELINE II=1`、`#pragma HLS ARRAY_PARTITION` 或 `#pragma HLS BIND_STORAGE`；
   - 如有时序违例，示范如何在循环内部插入打拍寄存器或将复杂条件判断展开；
   - 保证接口使用 `#pragma HLS INTERFACE s_axilite` 与 `#pragma HLS INTERFACE m_axi offset=slave`，且 64 位指针地址对齐符合 AXI 突发规范。
```

## 3. 典型应用范例与产出效果
- **在白板项目中的实际应用**：在 200MHz（5.0ns）高频时序收敛中，Restore 模块最初存在 7.2ns 组合路径且 II=3。通过本工作流引导，重构滑动窗口行缓存为 `ARRAY_PARTITION complete dim=1`，并在跨像素时域状态机间插入硬件打拍流水级，成功将 II 降至 1（满吞吐），时钟达成 200MHz 零违例。
