# AI Session: 2026-09-17-003-uvc-mjpeg-feasibility

- Date: 2026-09-17
- Operator: Codex
- AI product/model: Codex
- Participants: 用户（成员2，PL下层流水线负责人）
- Objective: 评估支持 MJPEG 输出的 UVC 摄像头能否用于 USB→PS→PL→PS→显示 demo。
- Status: Completed
- Report candidate: No
- Related commits: None
- Related files: `blackboard-writing-enhance/工作空间/工作方案/02_A现场_系统集成与上板.md`、`docs/spec.md`

## Context Read

- 读取当前 `project_workspace/PROJECT_STATE.md`、`project_workspace/DECISIONS.md` 和上一条 demo 评估记录。
- 复核新仓库关于 UVC、PS 采集、DDR/VDMA、PL 标准化输入和显示路径的约定。

## Task and Constraints

- 用户确认摄像头采用 UVC 协议并支持 MJPEG 输出，询问路线可行性。
- 需要区分 UVC 传输协议、MJPEG压缩帧和PL二值化所需的未压缩像素流。

## Contributions

- 结论：可行，且 MJPEG 通常可以降低 USB 未压缩视频带宽压力。
- 明确 PS 必须先完成 MJPEG 解码和 BGRX/GRAY8 标准化，不能把压缩 JPEG 数据直接送入当前 PL 二值化核。
- 提出先验证 720p30，再验证 1080p30；必须测持续帧率、解码负载、缓冲延迟和丢帧。
- 建议不在首个 demo 内实现 PL JPEG 解码器，避免把协议/压缩解码问题与 PL 算法验证耦合。

## Decisions and Adoption

- 已写入 D-003：接受 UVC MJPEG 摄像头；PS/Linux 解码；PL 接收固定未压缩 BGRX/GRAY8。
- USB实际格式、支持的分辨率/帧率和持续运行能力仍待板端验证。

## Validation and Evidence

- 路线判断：有条件可行，基于现有项目数据通路设计；不是硬件实测结果。
- 未执行：ZCU104 UVC枚举、V4L2格式查询、MJPEG解码、720p/1080p持续采集、PS负载和显示实测。

## Errors and Corrections

- 修正潜在误解：UVC不是像素格式；MJPEG也不是PL二值化的输入格式。两者均需在PS端适配为项目标准化帧。

## Files Changed

- `project_workspace/DECISIONS.md`：新增 D-003。
- 新增本会话记录。
- `project_workspace/PROJECT_STATE.md`：待补充 UVC MJPEG 约束与验证项。

## Remaining Work

1. 成员1在板端确认 `MJPG` 模式、分辨率、帧率、stride/输出格式和持续运行情况。
2. 确认 PS 使用的 JPEG 解码路径，并分别记录解码、颜色转换和 DMA 时间。
3. 以解码后的固定 BGRX 帧接入 PL 二值化闭环。

## Handoff Notes

- 首版不要让 PL 直接处理 MJPEG 字节流；PL 算法 IP 的输入合同仍是标准化 AXI4-Stream 像素。
- MJPEG能减轻USB传输压力，但不能直接证明整机更快；解码开销必须纳入 G1/G2 端到端测量。
