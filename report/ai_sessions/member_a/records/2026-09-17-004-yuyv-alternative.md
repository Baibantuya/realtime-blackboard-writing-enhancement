# AI Session: 2026-09-17-004-yuyv-alternative

- Date: 2026-09-17
- Operator: Codex
- AI product/model: Codex
- Participants: 用户（成员2，PL下层流水线负责人）
- Objective: 评估摄像头同时提供 YUYV/YUY2 时对首个 PL 二值化 demo 的影响。
- Status: Completed
- Report candidate: No
- Related commits: None

## Context Read

- 读取当前 `PROJECT_STATE.md`、`DECISIONS.md` 及 UVC/MJPEG 评估会话。
- 复核新仓库首版规格、A现场系统链路和成员2 PL算法方案。

## Task and Constraints

- 用户补充摄像头也支持“yuv2”；按常见摄像头格式解释为 `YUYV` 或 `YUY2`，实际 FourCC 需以 V4L2 查询为准。
- 需要评估其是否比 MJPEG 更适合 USB→PS→PL 二值化 Demo。

## Contributions

- 结论：YUYV/YUY2 很适合首个二值化 bring-up，因为未压缩且亮度 Y 已直接存在。
- 明确字节排列：每两个像素通常为 `Y0 U Y1 V`；PL 可丢弃 U/V，仅处理 Y0/Y1。
- 建议当目标模式稳定时优先用 YUYV；MJPEG 作为降低 USB 带宽或设备实际更稳定时的备选。
- 给出未含协议/对齐的理论数据量：720p30约55.3 MB/s，1080p30约124.4 MB/s。

## Decisions and Adoption

- 新增 D-004：YUYV/YUY2 稳定时优先用于首个二值化 bring-up。
- PL 输出仍统一为 32 位黑白 BGRX，便于返回 PS 显示。
- 摄像头实际 FourCC、stride、分辨率和持续帧率仍未验证。

## Validation and Evidence

- 路线判断：工程上有条件可行，未进行板端实测。
- 未执行：V4L2格式查询、USB持续带宽、PL YUYV解析仿真、DMA、显示和性能测试。

## Errors and Corrections

- 将用户的“yuv2”标记为待确认名称；不能直接假定是 YUYV，需以 `v4l2-ctl --list-formats-ext` 的 FourCC 为准。

## Files Changed

- `project_workspace/DECISIONS.md`：新增 D-004。
- `project_workspace/PROJECT_STATE.md`：待补充 YUYV 优先策略。
- 新增本会话记录。

## Remaining Work

1. 在板端查询实际 `YUYV`/`YUY2` 格式和可用分辨率/帧率。
2. 优先完成 YUYV 720p30 固定帧和连续流验证。
3. PL 输入接口决定采用 YUYV 解析入口，或由 PS 先抽取/标准化 Y 后再送入通用核。
