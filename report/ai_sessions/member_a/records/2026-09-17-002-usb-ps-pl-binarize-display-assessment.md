# AI Session: 2026-09-17-002-usb-ps-pl-binarize-display-assessment

- Date: 2026-09-17
- Operator: Codex
- AI product/model: Codex
- Participants: 用户（成员2，PL下层流水线负责人）
- Objective: 评估 USB→PS→PL二值化→PS→显示 demo 的路线可行性，并梳理执行流程。
- Status: Completed
- Report candidate: No
- Related commits: None
- Related files: `blackboard-writing-enhance/工作空间/工作方案/02_A现场_系统集成与上板.md`、`docs/spec.md`、`工作空间/工作方案/05_接口与定点算法约定.md`

## Context Read

- 读取根目录当前 `PROJECT_STATE.md`、`DECISIONS.md` 及上一条新项目会话记录。
- 读取新仓库 A 现场系统集成方案、首版规格、接口/定点约定和性能预算。
- 新仓库当前未发现 RTL/HLS/Python 实现文件；尚无板卡运行证据。

## Task and Constraints

- 评估 demo：USB 摄像头进入 PS，PS 送入 PL，PL 做二值化，再回 PS，输出到显示器。
- 用户要求后续按成员2工作范围推进 PL 下层流水线算法。
- 不得把路线评估写成已完成硬件测试；所有未执行项目必须明确标记。

## Contributions

- 判断该 demo 适合作为第一条系统可行性闭环。
- 明确建议链路：UVC/V4L2 → PS 格式标准化 → DDR/CMA → VDMA/视频 DMA → AXI4-Stream PL 二值化 → 输出缓冲 → PS 显示。
- 明确分阶段流程：PS采集显示基线、固定单帧 DMA 闭环、PL 二值化比对、720p30 连续流、显示合入、再扩展1080p30。
- 识别主要风险：USB格式/解码、物理连续缓冲与cache sync、VDMA帧/行协议、显示路径和DP/HDMI授权边界。

## Decisions and Adoption

- 采用 D-002 作为 demo 工作路线和初步验收边界。
- 首档选择 1280×720、30 fps；固定帧正确后再连续流。
- PL 输出保持 32 位 BGRX、原尺寸；二值结果编码为黑白像素，避免 PS 额外重排显示格式。
- 允许 demo 阶段一次显式 PS 缓冲复制；不把零拷贝作为前置条件。
- ZCU104 显示优先 DisplayPort；HDMI 显示器只在 DP-to-HDMI 转接已验证时使用，不为 demo 引入 HDMI RX/TX 输入 IP。

## Commands and Tools

- 读取项目方案和规格文档。
- 检查仓库源码扩展名：未发现 `.sv`、`.v`、`.vhd`、`.cpp`、`.h`、`.py`、`.tcl` 实现文件。

## Validation and Evidence

- 路线评估：基于文档和典型数据通路的工程判断，结论为“有条件可行”。
- 已验证：新仓库无现有实现代码，且分支为 `b/pl-lower-pipeline`。
- 未执行：板卡、UVC、V4L2、VDMA、AXIS仿真、综合、时序、连续帧和显示实测。

## Errors and Corrections

- 用户口述 HDMI 输出；新仓库规范以 ZCU104 DisplayPort 为主要显示路径。因此将显示端修正为 DisplayPort 或已验证的 DP-to-HDMI 转接，不直接假定 HDMI IP 可用。
- USB 摄像头可能输出 MJPEG/YUYV 等格式；不把摄像头输出直接假定为 BGRX，要求 PS 先记录并标准化。

## Files Changed

- `project_workspace/DECISIONS.md`：新增 D-002。
- `project_workspace/PROJECT_STATE.md`：登记 demo 路线与未验证边界。
- `project_workspace/ai/INDEX.md`：本会话索引待同步。
- 新增本会话记录。

## Remaining Work

1. 成员1确认板卡、Linux/PYNQ、USB设备格式和显示路径。
2. 成员2建立 AXIS 二值化 IP 与随机背压/复位 testbench。
3. A/B 联调固定单帧 DMA 闭环，再进入连续 720p30。

## Handoff Notes

- 当前 demo 不是最终增强算法；它是验证系统接口、缓冲、协议和显示的最小闭环。
- 首个可复现证据应包含输入帧、PL输出帧、逐像素差异/CRC、配置、frame_id、超时/丢帧统计和显示截图或录像。
