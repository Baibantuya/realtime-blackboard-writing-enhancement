# AI Session: 2026-09-17-006-source-agnostic-development-plan

- Date: 2026-09-17
- Operator: Codex
- AI product/model: Codex
- Participants: 用户（成员2，PL下层流水线负责人）
- Objective: 在摄像头未到货、USB与FMC路线未确定时，制定未来两天的低返工开发计划。
- Status: Completed
- Report candidate: No
- Related commits: None

## Context Read

- 读取当前项目状态、D-002至D-005和新仓库成员2 PL执行方案、接口约定、规格及验收文档。

## Task and Constraints

- 当前无摄像头，无法进行 UVC/MJPEG/YUYV 实测。
- USB 与 FMC 输入路径尚未决策，不能提前冻结板级输入 IP、引脚、时钟和 XDC。
- 用户负责成员2的 PL 下层流水线算法开发。

## Contributions

- 建议两日开发重点放在输入源无关的 PL 核、AXIS 协议、参考模型和合成测试向量。
- 建议用合成 BGRX/GRAY8/YUYV 原始数据模拟输入，不实现摄像头驱动或 JPEG/FMC 接收。
- 提出两日节奏：Day 1 数学/合同/向量/testbench；Day 2 可综合核心/随机背压/复位/边界验证。
- 明确 USB/FMC 只通过前端适配层接入统一像素合同，降低路线变更返工。

## Decisions and Adoption

- 采用 D-006：暂不冻结 USB 或 FMC，优先推进平台无关 PL 逻辑。
- 两日不做 UVC 驱动、MJPEG 解码、FMC/HDMI/MIPI 接收 IP、具体引脚/XDC、最终 VDMA 地址和板端性能结论。

## Validation and Evidence

- 当前仅完成开发计划评估；未执行 RTL 仿真、综合、实现、时序、上板或摄像头测试。

## Errors and Corrections

- 避免把 Demo 输入路线误当作 PL 算法接口：PL 应接收统一标准化像素流，输入源差异留在 PS 或视频接收适配层。

## Files Changed

- `project_workspace/DECISIONS.md`：新增 D-006。
- `project_workspace/PROJECT_STATE.md`：待补充两日计划。
- `project_workspace/ai/INDEX.md`：新增会话索引。
- 新增本会话记录。

## Remaining Work

1. 在新仓库建立英文源码目录和仿真入口。
2. 由成员2与成员3确认最小输入/输出合同和阈值定义。
3. 完成最小 PL 二值化闭环后，再根据实际输入路线新增 USB/FMC 适配器。
