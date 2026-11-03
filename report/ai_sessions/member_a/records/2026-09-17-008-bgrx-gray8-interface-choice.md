# AI Session: 2026-09-17-008-bgrx-gray8-interface-choice

- Date: 2026-09-17
- Operator: Codex
- AI product/model: Codex
- Participants: 用户（成员2，PL下层流水线负责人）
- Objective: 在 USB 摄像头暂定的前提下，决定 BGRX 与 GRAY8 的接口分工，并确定其他 PL/PS 核心接口基线。
- Status: Completed
- Report candidate: No
- Related commits: None

## Context Read

- 读取当前项目状态、D-001至D-006、接口/定点约定、首版规格、A系统集成方案和成员2 PL执行卡。
- 当前仓库仍无 RTL/HLS实现和硬件验证证据。

## Task and Constraints

- 摄像头暂定 USB，可能输出 MJPEG/YUYV；FMC 暂不作为当前输入实现。
- 用户要求在 BGRX 与 GRAY8 之间做选择，并由 AI 决定其余接口内容、说明理由。

## Contributions

- 决定 PL 边界使用 32-bit BGRX8888，PL 内部即时生成 GRAY8 亮度信号；首版输出黑白 BGRX。
- 决定首个核心使用 1 pixel/beat AXI4-Stream、AXI4-Lite控制、输入输出独立帧buffer。
- 决定连续视频优先 VDMA/视频DMA，固定帧可用 AXI DMA 做最小闭环。
- 决定首个简单核心使用 SystemVerilog RTL，避免同时维护 RTL和HLS两套实现。
- 保留 USB 输入适配层：MJPEG 在 PS 解码，YUYV 在 PS 标准化或后续增加解析器；PL 核心不感知 UVC格式。

## Decisions and Adoption

- 已写入 D-007，作为当前工作接口基线，仍需团队确认后冻结。
- 选择 BGRX 的理由：与现有4字节视频/VDMA/显示合同一致，输入输出格式稳定，并为未来彩色笔迹保护保留信息。
- 选择内部 GRAY8 的理由：二值化只需要亮度，避免独立灰度帧带来的额外 DDR buffer、DMA 和 PS 重组；算法上保留清晰的灰度信号。
- 不选择全链路 GRAY8 的理由：PS仍需保存或恢复颜色，显示前增加转换；后续彩色增强会再次改接口。

## Validation and Evidence

- 这是基于数据通路和后续算法需求的设计判断。
- 未执行：带宽测量、RTL仿真、综合、时序、资源、USB采集、DMA和显示验证。

## Errors and Corrections

- 纠正“BGRX和GRAY8必须二选一”的问题：应区分 PL 边界格式与 PL 内部算法格式，外部BGRX、内部GRAY8能减少整体返工。

## Files Changed

- `project_workspace/DECISIONS.md`：新增 D-007。
- 新增本会话记录。
- `PROJECT_STATE.md` 和 `ai/INDEX.md`：待同步。

## Remaining Work

1. 与成员1/3确认BGRX字节序、stride、VDMA和显示要求。
2. 实现 SystemVerilog BGRX→GRAY8→binary AXIS核心和testbench。
3. 仿真通过后再冻结 Vivado IP、AXI-Lite物理寄存器和板级 DMA 参数。
