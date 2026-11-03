# AI Session: 2026-09-21-012-kv260-pl-first-camera-architecture

- Date: 2026-09-21
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 根据 1080p30 MJPEG 实测，确定以 PL 为主要像素处理位置、PS 仅承担必要采集/解码/缓冲职责的相机架构，并评估是否立即转向 CSI-2。
- Status: Completed
- Report candidate: No
- Related commits: None
- Related files: `project_workspace/ai/sessions/2026-09-21-012-kv260-pl-first-camera-architecture.md`, `project_workspace/DECISIONS.md`, `project_workspace/PROJECT_STATE.md`, `project_workspace/ai/INDEX.md`

## Context Read

已读取项目规范、项目状态、D-027 和 1080p30 实测记录。已知：UVC MJPEG→YUV 纯解码约占一个 A53 核的 85%，软件 Gray8 标准化约 95%–96%，BGRX 标准化低于实时；当前 UVC 摄像头和 1080p30 MJPEG 已实测可用。

## Task and Constraints

- 用户希望最大化利用 PL，PS 仅保留基础任务，并允许在必要时转向 CSI 摄像头。
- 不将“PS 仍需做 JPEG 解码”误表述为完整 PS 图像增强；不把尚未实测的 DMA/CSI 链路表述为已完成。

## Contributions

- 采用 PL-first 架构：PS 只完成 V4L2/UVC 管理、MJPEG 解码、DMA/CMA 缓冲分配与同步；PL 完成亮度提取（如需要）、透视/裁切、照度补偿、二值化、形态学和输出格式处理。
- 对 UVC MJPEG，优先使用解码器的 YUV `Y` 平面直接作为 GRAY8 源，避免 FFmpeg 的额外 BGRX 或软件 Gray8 色彩空间转换；实际 API 的 stride、CMA/DMA 导入和 cache 同步仍需板测。
- 不立即切换到 CSI-2：已验证的 UVC 可最快完成 1080p30 PL 闭环。MIPI CSI-2/IMX219 是更符合“PS 最小化”的第二阶段/正式低延迟路线，但需要新增相机、CSI RX/D-PHY、传感器控制和 RAW Bayer→Gray 路线验证。

## Decisions and Adoption

- D-028 记录为用户偏好的 PL-first 临时架构基线。

## Commands and Tools

- 基于已完成的真实 UVC 采集和解码基准进行架构裁决；本次未运行新板端命令。

## Validation and Evidence

- 1080p30 MJPEG→YUV/GRAY8/BGRX 的吞吐数据来自上一会话的真实板测。
- PS→CMA/DMA→PL、Y 平面零/少拷贝、CSI-2 输入和 PL 视频闭环尚未验证。

## Errors and Corrections

- 修正了“Gray8 必须由 PS 颜色转换生成”的过强表述：MJPEG 原生解码结果为 YUV，软件接入可优先引用其中的亮度平面；是否能无额外拷贝进入 DMA 取决于实际缓冲分配和驱动接口。

## Files Changed

- `project_workspace/ai/sessions/2026-09-21-012-kv260-pl-first-camera-architecture.md`
- `project_workspace/DECISIONS.md`
- `project_workspace/PROJECT_STATE.md`
- `project_workspace/ai/INDEX.md`

## Remaining Work

1. 实现 PS 端 V4L2/libavcodec 原型：MJPEG 解码后取 Y plane，复制/导入到 DMA 安全 GRAY8 缓冲，记录 CPU、copy、cache-sync 与帧计数。
2. 将 GRAY8 AXIS 输入接入 PL，完成 1080p30 下亮度增强/二值化和帧缓冲显示。
3. 并行准备 J9 CSI-2 IMX219 路线，待 UVC 闭环完成后以端到端延迟、CPU占用、图像质量和开发风险比较是否迁移。

## Handoff Notes

UVC 不应在 PL 内尝试 JPEG 解码；这会把通用图像编解码问题引入首版 FPGA 工程。PL 的价值应集中在流式像素算法和低延迟处理。CSI-2 是长期 PL-first 最优输入，但不是当前已验证 UVC 路线的必要前置条件。
