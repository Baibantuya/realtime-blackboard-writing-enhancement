# AI Session: 2026-09-21-011-kv260-1080p30-mjpeg-decode-feasibility

- Date: 2026-09-21
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 评估 KV260 上 1080p30 UVC MJPEG 的 PS 解码压力和端到端流程可行性。
- Status: Completed
- Report candidate: No
- Related commits: None
- Related files: `project_workspace/ai/sessions/2026-09-21-011-kv260-1080p30-mjpeg-decode-feasibility.md`, `project_workspace/PROJECT_STATE.md`, `project_workspace/ai/INDEX.md`

## Context Read

已读取项目规范、项目状态和最近 UVC 枚举/单帧会话。实测摄像头支持 1920×1080@30 MJPEG；KV260 为 4 核 Cortex-A53、3.8 GiB RAM，未验证过 MJPEG 解码吞吐。

## Task and Constraints

- 用户拟采用 1080p30，询问 PS 解码压力及整链路可行性。
- 先检查现有 FFmpeg/GStreamer/硬件解码能力，再执行短时间 MJPEG→原始像素丢弃解码测试与 CPU 观测。
- 不安装软件、不更改摄像头控制或系统配置；输出仅到 `/dev/null`。

## Contributions

- 板端提供 FFmpeg 4.4.2 和 GStreamer 1.20.3 的通用 MJPEG/JPEG 软件解码器；未发现可用于 MJPEG 的 KV260 VCU 节点或 GStreamer 硬件加速插件。FFmpeg 列出的 `vaapi/drm` 等通用 hwaccel 名称不构成 MJPEG 硬解码证据。
- 1920×1080@30 MJPEG → 原生 YUV 解码 → null：300 帧的媒体时间为 10.20 秒、FFmpeg 稳态 `speed=1.02x`；进程实际耗时 10.85 秒，CPU 85%（用户态 8.91 秒、内核态 0.33 秒），峰值 RSS 178,536 KiB。
- 1920×1080@30 MJPEG → `bgr0` → rawvideo null：300 帧媒体时间为 10.00 秒但仅 `speed=0.892x`，进程实际耗时 12.03 秒、CPU 98%，FFmpeg 报告 53 个输出重复帧；不满足实时 BGRX 输入要求。
- 1920×1080@30 MJPEG → `gray` → rawvideo null：300 帧 `speed=1.02x`、进程耗时 10.62 秒、CPU 95%；随后 900 帧连续测试耗时 30.63 秒、CPU 96%、RSS 181,368 KiB。温度约 29.9–32.1 °C，测试后无新增内核 error。

## Decisions and Adoption

- 用户提出下一阶段按 1080p30 推进。基于实测，采纳为**临时 bring-up 基线**：`1080p30 MJPEG → PS 软件解码 → GRAY8 → PL/帧缓冲/显示`。
- 不在 PS 侧将 1080p30 转换为 BGRX；该路线实测低于实时。若后续显示/接口强制 BGRX，应将颜色展开移入 PL 或改用受验证的硬件加速/降低分辨率。
- 此决定只覆盖采集到 PL 前的数据格式和性能约束，尚未完成 AXIS/VDMA/显示集成，需在完整链路实测后确认最终接口。

## Commands and Tools

- 已读取上下文并建立会话记录。
- 检查 FFmpeg/GStreamer 解码器、hwaccel 列表、设备节点和可能的 VCU sysfs 节点。
- 使用 `/usr/bin/time` 和真实 `/dev/video0`，在 1080p30 MJPEG 输入下分别测量 YUV 解码、BGRX 转换和 Gray8 转换；输出始终为 `/dev/null`。
- 对 Gray8 进行 900 帧长测，并检查温度和近两分钟内核 error。

## Validation and Evidence

- 证据来自真实 KV260、真实 UVC 摄像头和实际 MJPEG 流，不是离线样本或推算。
- 纯解码和 Gray8 转换可跟随 30 fps 媒体时间；Gray8 的长测仅约 2%–4% 处理余量，实际耗时包含约 0.6 秒的初始化/收尾开销。该余量不足以承受额外的大型 PS 像素操作。
- 300 帧 Gray8 试验中 FFmpeg 报告 6 个输出重复帧，未观察到 UVC/内核错误；未据此宣称零丢帧，仍需完整 VDMA/显示链路的帧计数验证。
- 未执行硬件 MJPEG 解码、PS→PL DMA、缓存同步、PL 算法、DRM/KMS 显示或端到端延迟测试。

## Errors and Corrections

- BGRX 转换时 FFmpeg 提示 `No accelerated colorspace conversion found from yuv422p to bgra`，与低于实时的实测结果一致；将其从 1080p30 PS 侧基线路径中排除。
- Gray8/BGRX 转换均出现 FFmpeg 关于 deprecated full-range pixel format 的提示；本次仅测吞吐，尚未完成全/限范围映射和显示颜色正确性校准。

## Files Changed

- `project_workspace/ai/sessions/2026-09-21-011-kv260-1080p30-mjpeg-decode-feasibility.md`
- `project_workspace/PROJECT_STATE.md`
- `project_workspace/DECISIONS.md`
- `project_workspace/ai/INDEX.md`

## Remaining Work

1. 建立 PS 的 Gray8 零/少拷贝缓冲到 AXI DMA/VDMA 的最小链路，计数验证 30 fps、丢帧与端到端延迟。
2. 明确 AXIS 核是否以 Gray8 作为 1080p30 输入格式；如必须 BGRX，优先在 PL 展开或调整目标分辨率。
3. 在真实白板上完成自动曝光预热、透视校正和照度补偿前后对比；不要仅凭桌面场景的吞吐结论声称板书效果。

## Handoff Notes

1080p30 对 KV260 **可行但紧张**：MJPEG 解码加 Gray8 标准化约占一个 A53 核的 95%–96%，系统还有其他核但该单线程热点几乎没有余量。把灰度化后尽快交给 PL，避免 PS 侧 BGRX、形态学、逐像素增强或额外多次拷贝；首版显示/算法应使用灰度或二值输出。
