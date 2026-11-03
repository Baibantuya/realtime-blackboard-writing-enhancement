# AI Session: 2026-09-17-007-pl-ps-core-interface-explanation

- Date: 2026-09-17
- Operator: Codex
- AI product/model: Codex
- Participants: 用户（成员2，PL下层流水线负责人）
- Objective: 核对并解释当前文档草案中的 PL 核心接口以及 PS/PL 数据输出边界。
- Status: Completed
- Report candidate: No
- Related commits: None

## Context Read

- 读取当前 `PROJECT_STATE.md`、`DECISIONS.md`、新仓库 `docs/spec.md`、接口/定点约定和成员2执行卡。
- 当前仓库未发现 RTL/HLS 实现，因此接口结论均来自草案，不是实测接口。

## Task and Constraints

- 用户要求确认 PL 核心接口，并说明 PL 与 PS 之间的输入输出形式。
- USB/FMC 输入路线仍未确定，接口说明需保持输入源无关。

## Contributions

- 确认草案主接口：32-bit、1 pixel/beat AXI4-Stream，BGRX 输入输出；SOF 使用 TUSER[0]，行尾使用 TLAST，TKEEP/TSTRB为4'b1111。
- 说明 PS→PL 是标准化帧像素和配置/控制，PL→PS 是处理后同尺寸帧、状态计数和错误状态。
- 区分 AXI4-Stream 像素流、AXI4-Lite 控制面、DDR/VDMA 帧搬运面和中断状态面。
- 明确接口草案未冻结，真实时钟、寄存器偏移、VDMA参数、实际输入适配仍待三人和工具确认。

## Decisions and Adoption

- 本次采用文档草案作为解释基准，不修改正式仓库代码，不宣称已有实现。
- 输入源适配层负责 MJPEG/YUYV/FMC 到标准化像素流的转换，PL 二值化核心不感知输入来源。

## Validation and Evidence

- 已验证：文档中的接口字段和信号语义已核对。
- 未执行：RTL仿真、综合、实现、寄存器导出、板端 DMA 和上板验证。

## Errors and Corrections

- 纠正“核心接口已经确认”的表述：目前只能称为待确认设计草案；尚无 RTL/HLS 端口文件。

## Files Changed

- 新增本会话记录。
- 未修改新仓库代码。

## Remaining Work

1. 三人确认 BGRX/GRAY8 核心输入选择及 AXIS 物理宽度。
2. 成员2实现 AXIS 核并由 testbench 固化实际握手行为。
3. 成员1根据实际 VDMA/缓冲和显示方案补充 PS 侧集成参数。
