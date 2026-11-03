# AI Session: 2026-10-15-005-v15-requirements-analysis-and-implementation-strategy
- Date: 2026-10-15
- Operator: Project owner
- AI product/model: Gemini 3.8 Flash
- Participants: Project owner, Gemini 3.8 Flash (single agent)
- Objective: 深入分析用户提出的关于 dma_rgb565_color_cache_clear_v15 的五项关键工程问题（200MHz时钟可行性、淡色笔迹连续性、背景闪烁去噪、无人重置历史消除遮挡重影、屏幕显示黑板移出移动提示），并给出切实可行的FPGA/HLS/PS系统级实现思路与架构方案。
- Status: Completed; analysis and architecture recommendations
- Report candidate: yes
- Related commits: none
- Related files:
  - `kv260-whiteboard-enhance/rtl/dma_rgb565_color_cache_clear_v15/`
  - `kv260-whiteboard-enhance/docs/v16_quality_clock_ui_plan_20261015.md`
  - `project_workspace/PROJECT_STATE.md`
  - `project_workspace/DECISIONS.md`

## Context Read
- `AGENTS.md`
- `project_workspace/ai/AI_DEVELOPMENT_POLICY.md`
- `project_workspace/PROJECT_STATE.md`
- `project_workspace/DECISIONS.md`
- `project_workspace/ai/INDEX.md`
- `project_workspace/ai/sessions/2026-10-15-004-v15-quality-clock-plan.md`
- `kv260-whiteboard-enhance/docs/v16_quality_clock_ui_plan_20261015.md`
- v15 源码：`board_quantize_rgb.cpp`, `whiteboard_restore.cpp`, `scene_rebase.h`, `board_detector.py`

## Task and Constraints
- 针对用户提出的 5 点具体问题进行工程化深度分析并给出实现思路。
- 严禁空穴来风或伪造时钟收敛结果，严格基于 v15 实际时序报告（WNS +0.860ns / 100MHz / 9.036ns关键路径）和板端日志进行客观论证。
- 严禁擅自修改已冻结的核心数据流架构（保留两 DDR 环、保留原 vendor queued DMA、保留 PS 稀疏控制和 PL 像素处理边界）。

## Contributions
- 详细剖析了 200MHz 的瓶颈根因（量化 classify 关键路径 19 级逻辑延迟 9.036ns），指明不能盲目拉高时钟，提出滑动窗口列累加与 4~5 级流水线重构方案。
- 提出“4向线性支持度 + 定向微缺口桥接”的淡字连续性增强方案，解决弱阈值缺乏邻近强种子即被吞没的问题。
- 提出“空间孤立点抑制 + 时域确认（2帧生效）+ 动态噪声底估计”联合去噪方案，消除空板闪烁噪点。
- 深度诊断 v15 自动清场在实际场景无法触发的原因（全画面 12.96 万采样点单点一票否决、且受污染的历史旧保护自我死锁），提出“容错面积比 + 纯当前输入真实黑板一致性判据 + 帧边界原子级全历史重置”方案，彻底根治人员离开后的残影重影。
- 针对黑板移出板框提示，分析了 PS 边框检测状态码映射逻辑，并对比了“PL 硬件轻量点阵 OSD”与“PS 待机直刷 DRM 引导图”两种可行路径。
- **硬件开销与现有结构分析**：测算新增逻辑主要为 LUT/FF（预计增加 2k~3.5k，占 2~3%），BRAM 几乎不增（若采用方案 B 则 OSD 0 开销）；揭示芯片剩余 56 个 URAM（可用超 2MB 存储）尚未被利用的优化空间；明确 BRAM/DSP 未被也不应被强制限制在单一物理连续区域（因芯片物理硅柱分布及流水线局部就近原则，强制集中会导致严重布线死锁）。
- **浅色衣服遮挡去除失败的根本代码根因**：精确定位到 `whiteboard_restore.cpp` 中 `o += db>=delta && !cc`：算法将所有亮色中性（`cc = chalk()`）强行判定为“粉笔字”，导致浅色衣服在遮挡检测阶段被 `!cc` 直接过滤，`occupied` 恒为 0，掩码 `mask` 无法置位，恢复核将浅色衣服直接透传输出到屏幕；且大面积浅色还触发了 `white_changed` 假阳性。
- **BRAM 手动例化与集中合并可行性分析**：明确不需要且强烈不建议手动例化底层 RAMB36/18 原语或强行将多数组打包到单个 BRAM。原因包括：(1) 单个 RAMB36 仅 4.5KB，一整行 1080p 565 即占 3.84KB，容量无法容纳多行；(2) BRAM 仅有两个物理读写端口（双端口），而 II=1 的 7x7 流水线每拍需要并行并发访问 7 行数据，强行合并到单 BRAM 必因端口争用摧毁流水线；(3) HLS/XPM 显式绑定是 AMD 推荐的最佳实践，手写底层原语破坏编译器流水调度与寄存器重平衡。小数组应优先推断为 LUTRAM。
- **用户对“显式例化 BRAM IP 彻底杜绝 reg 展开”的核心关切解析**：
  - 用户的担忧极为精准：本项目历史版本 B32 就曾因纯行为级 `reg` 数组加组合读写导致 Vivado 无法推断为 BRAM，退化为数万触发器导致 CLB 爆到 99.80%。
  - 纯 Verilog 模块（如 Rectify Fetch）：采用 AMD 官方参数化存储宏 XPM（`xpm_memory_sdpram`）或 Block Memory Generator (BMG) IP 核，直接锁定物理 Block RAM，彻底杜绝编译器退化为 reg。
  - Vitis HLS 模块（如 Quantize/Restore）：无法直接在 C++ 中写 Verilog module 例化语句，但必须使用硬性绑定指示 `#pragma HLS BIND_STORAGE ... impl=bram/impl=uram`，强制 HLS 编译器调用其内置的专用 RAM IP 发生器（HLS 版 BMG），生成确定性的物理 RAM 子模块，杜绝编译器猜测。若需完全挂接外部 Vivado BMG IP，可通过 `#pragma HLS INTERFACE bram` 引出标准 BRAM 物理总线在 BD 中连线。

## Decisions and Adoption
- 维持既有架构约束，将上述方案作为 v16 候选的实施指导建议。未修改生产源码或启动综合。

## Validation and Evidence
- 依据 v15 真实实现数据：后级 100MHz 域最长路径延迟 9.036ns（布线占 6.219ns），当前物理结构无法直接支持 200MHz（5ns）。
- 依据 v15 板端实测日志：`epoch=0, reasons=22` 证实原有清场条件过于严苛导致现场完全无法触发。
- 依据 `board_detector.py` 内部 `clipped` 与 `fit` 边缘样本逻辑，证实 PS 能够准确提炼出左右上下偏移状态。
- 依据 `whiteboard_restore.cpp` 第 387 行源码：`o+=db>=int(delta)&&!cc&&!chalk(b,chalk_min,chalk_spread);`，实证浅色衣物导致 `!cc == 0`，致使遮挡检测完全失效。

## Planned Code Modifications (v16 Proposal)
1. `whiteboard_restore.cpp`:
   - 移除 `o += db>=delta && !cc` 中的 `!cc` 盲目豁免，引入大面积亮白（Broad White）强遮挡检测，解决浅色/白衣服无法消除遮挡的问题；
   - 重构 `auto_clear` 判定：将全屏 12.96 万点单点一票否决改为容忍面积比（$\ge 97\%$ 区域无大面积遮挡），解除 `old_guard` 永久否决权；
   - 连续确认无人后，在两帧间隙执行原子重置：以当前可信帧覆写 `background`/`previous`，清零 `TTL`/`confidence`/`pixel_quiet`，清除历史残影；
   - 对行 Burst Buffer 施加 `#pragma HLS BIND_STORAGE ... impl=uram`，利用 56 个闲置 URAM 释放 BRAM。
2. `board_quantize_rgb.cpp`:
   - 增加 4 向（水平/垂直/对角）线性支持度计算，让无强种子的整段淡字能正常输出；
   - 增加 1~2 像素定向微缺口桥接与笔画颜色语义继承；
   - 增加空域孤立点滤除与双帧时域确认，消除背景闪烁噪点；
   - 重构 `classify` 函数：7x7 累加改为滑动列和，单拍拆分为 4~5 级流水寄存器（目标 200MHz / 150MHz 稳健过渡）；
   - 所有行缓存硬绑定 `impl=bram`，FIFO 绑定 `impl=lutram`，杜绝 reg 展开。
3. `board_detector.py` & PS 显示调度:
   - 提炼 `LEFT_CLIPPED`, `RIGHT_CLIPPED`, `TOP_CLIPPED`, `BOTTOM_CLIPPED`, `TOO_CLOSE`, `LOCKED` 等提示状态码；
   - 方案 B（PS 旁路刷 DRM 待机图）：黑板移出时 PS 直接向显示缓冲刷入带箭头的静态引导图，重新锁定后切回 PL 硬件流（0 PL 硬件开销）；或方案 A（PL 硬件轻量 OSD）。
4. `config_resources.json` & Vivado 约束:
   - 更新候选版本为 v16，更新时钟目标与 URAM/BRAM 绑定配置。

## Remaining Work
- 用户授权后，建立独立的 `kv260-whiteboard-enhance/rtl/dma_rgb565_color_cache_clear_v16`（或在指定候选目录）落地实施上述代码修改并执行仿真验证。
