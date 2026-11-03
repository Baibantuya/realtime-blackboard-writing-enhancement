# 模块 06: 大模型协同设计提示词工作流 (06_prompt_workflows)

## 1. 适用范围与功能职责

### 适用场景
- 队伍在与各类通用大模型（Claude、ChatGPT、Gemini 等）协同开展嵌入式 FPGA / PYNQ 软硬件协同设计时；
- 避免散乱提问与“幻觉代码”，通过结构化提示词（Structured Prompts）引导大模型给出符合工程约束与硬件可综合规范的技术方案；
- 覆盖软硬件划分、HLS 时序资源优化、PS 端嵌入式瓶颈排查三大阶段。

### 核心工作流清单
1. [`01_algorithmic_hardware_partition.md`](01_algorithmic_hardware_partition.md)：**算法描述 -> 软硬件边界划分工作流**（基于计算密度、访存带宽与实时性预算进行定量推导）；
2. [`02_hls_interface_optimization.md`](02_hls_interface_optimization.md)：**HLS 综合报告 -> 瓶颈定位与约束收敛工作流**（根据 II 流水延迟、BRAM/LUT 资源报警精准调优 pragma）；
3. [`03_arm_cpu_bottleneck_audit.md`](03_arm_cpu_bottleneck_audit.md)：**PS 嵌入式瓶颈 -> ARM/NEON 优化工作流**（排查低算力 ARM 上的 Python 算力黑洞）。

---

## 2. 提示词使用最佳实践原则

在将提示词发送给大模型时，请遵循以下由本项目 180 篇 AI 会话沉淀的工程经验：
1. **带入明确的物理器件型号与时钟约束**（如 `AMD Zynq UltraScale+ xck26-sfvc784-2LV-c, 200MHz, 1080p@30FPS`），避免模型给出适用于 GPU 的无约束矩阵方案；
2. **强制区分物理地址与虚拟地址**，要求模型生成符合 AXI4 总线与缓存一致性规范的代码；
3. **附带实测耗时数据与综合报告具体行**，促使大模型基于确凿事实而非抽象推测进行纠错。
