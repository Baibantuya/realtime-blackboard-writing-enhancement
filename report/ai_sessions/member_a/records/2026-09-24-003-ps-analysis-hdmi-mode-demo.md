# AI Session: 2026-09-24-003-ps-analysis-hdmi-mode-demo

- Date: 2026-09-24
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 给出 PS 调用分析帧、发布遮挡框、把 PL 结果输出到 HDMI 的 demo，并预留黑板/白板模式控制寄存器。
- Status: 文档 demo 和接口基线完成；自定义驱动/PL 实现与板测待完成
- Report candidate: No
- Related commits: None
- Related files: `kv260-whiteboard-enhance/docs/ps_analysis_hdmi_mode_demo.md`; `kv260-whiteboard-enhance/docs/pl_ps_interface_spec.md`; D-040。

## Context Read

- 按根目录规范重新读取 `AGENTS.md`、AI 开发策略、项目状态、决策记录、索引和最新会话记录。
- 阅读 `pl_ps_interface_spec.md`、`whiteboard/pynq/run_camera_dp.py`、`whiteboard/pynq/kv260_threshold.py` 和 `whiteboard/pynq/README.md`。
- 两次 `git status`（工作区根及正式目录）均报告不是 Git 仓库，无法核对版本状态。

## Task and Constraints

- 需要解释分析帧到 PS 的调用、检测框回传、PL 输出 HDMI 和 PS 模式控制。
- 当前已有的 PYNQ DisplayPort runner 只证明 PS 给 DisplayPort frame 写入 RGB 图像的 API 模式；自定义分析/结果驱动、生产 VDMA display ring 和 DRM/KMS DMA-BUF import 并不存在，示例不得声称可直接运行。
- 新正式文档写入 `kv260-whiteboard-enhance/`；内部决策和流水记入 `project_workspace/`。

## Contributions

- 绘制分析/控制/显示流图，提供 PS 主循环示例：取分析 DMA-BUF、推理跟踪、发布 ABI v1 ROI、归还槽位、读取 PL 合成输出。
- 给出 PYNQ `DisplayPort.newframe()/writeframe()` 的 bring-up 显示路径；明确逐帧 PS copy 仅用于功能点亮。目标性能路径为 PL 输出 VDMA DMA-BUF 经 DRM/KMS import 直接扫描到 PS DisplayPort/HDMI。
- 在 AXI-Lite 预留白板/黑板模式 shadow、commit、active、ack 和 error 寄存器 `0x58–0x68`，PL 下一 SOF 原子切换 profile，视频不停顿。
- 更新规范到 v0.3，登记 D-040 并更新项目状态。

## Decisions and Adoption

- 用户要求预留 PS 向 PL 传入黑板/白板模式控制；D-040 作为接口实现基线采纳。
- HDMI 先用已存在的 PYNQ API 作为 bring-up 路径，正式连续显示目标为共享 DMA-BUF 的 DRM/KMS scanout。

## Commands and Tools

- 使用 PowerShell/`rg` 读取并交叉核对项目规范和已有 runner；使用补丁编辑 Markdown 规格、demo 和内部记录。

## Validation and Evidence

- 文档/API 静态核对。未运行 Python demo，因为 `WhiteboardVideoDevice` 驱动、PL result/analysis DMA 接口、模式寄存器硬件和输出帧 VDMA 尚未实现。
- 未执行测试、仿真、综合、时序或板端 HDMI/模式切换验证。

## Errors and Corrections

- 初稿方向写成“框给 PS 拼合”；校正为 PL→PS 只送 2 fps 分析帧，PS→PL 回传 ROI，PL 执行 clean-board 更新/合成。
- 区分功能 demo 与生产显示：PYNQ `writeframe()` 路径要 PS copy；DRM/KMS 共享帧缓冲是未实现的性能目标。

## Files Changed

- `kv260-whiteboard-enhance/docs/ps_analysis_hdmi_mode_demo.md`（新增调用/显示/模式切换 demo）
- `kv260-whiteboard-enhance/docs/pl_ps_interface_spec.md`（版本升至 0.3，加入 HDMI 与模式控制契约）
- `project_workspace/DECISIONS.md`（D-039 修订、增加 D-040）
- `project_workspace/PROJECT_STATE.md`
- `project_workspace/ai/INDEX.md`
- `project_workspace/ai/sessions/2026-09-24-003-ps-analysis-hdmi-mode-demo.md`（本记录）

## Remaining Work

1. 实现 Linux `WhiteboardVideoDevice` 驱动 API：分析 DMA-BUF queue、输出帧 queue、result mailbox、所有权/cache sync。
2. 实现 PL `MODE_SHADOW/MODE_COMMIT` 和跨 SOF 应用/ACK。
3. 先用 PYNQ copy runner 点亮 HDMI，再完成 VDMA 输出 DMA-BUF 到 DRM/KMS scanout import。
4. 上板核对持续 HDMI 帧率/丢帧、模式切换无撕裂、结果帧号和分析 ring 满时主路不中断。

## Handoff Notes

调用示例与两条显示路径见 `kv260-whiteboard-enhance/docs/ps_analysis_hdmi_mode_demo.md`；接口地址和 mode enum 见 `pl_ps_interface_spec.md` 与 D-040。示例中 `WhiteboardVideoDevice` 及 detector 是明确待实现的适配层。
