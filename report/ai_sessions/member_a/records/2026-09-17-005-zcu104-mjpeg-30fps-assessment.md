# AI Session: 2026-09-17-005-zcu104-mjpeg-30fps-assessment

- Date: 2026-09-17
- Operator: Codex
- AI product/model: Codex
- Participants: 用户（成员2，PL下层流水线负责人）
- Objective: 评估 YUY2 分辨率受限时，是否可在 ZCU104 上使用 MJPEG 30fps 作为输入。
- Status: Completed
- Report candidate: No
- Related commits: None

## Context Read

- 读取当前项目状态、D-002至D-004、UVC/MJPEG与YUYV评估记录。
- 复核新仓库关于 ZCU104、PS采集、PL处理、DMA和显示的规划边界。

## Task and Constraints

- 用户补充摄像头 YUY2 仅支持 480p30、768p10，询问 ZCU104 上 MJPEG 30fps 的可行性。
- 必须区分摄像头模式能力、USB传输、A53解码能力和PL/显示吞吐。

## Contributions

- 结论：可以评估，且 MJPEG 30fps 是合理候选；建议先以实际支持的 720p30 为目标。
- 指出 MJPEG 30fps 不能由 YUY2 分辨率表直接推出，必须查询实际 MJPG FourCC 的分辨率/帧率组合。
- 指出瓶颈更可能是 A53 JPEG 解码、颜色转换、缓存和显示链路，而不是 USB nominal bandwidth。
- 建议使用 NEON优化的 libjpeg-turbo 或已验证的视频 pipeline；不把 VCU 默认当作 MJPEG 解码器。
- 建议连续至少300帧分项测量，并在 720p30 通过后再尝试1080p30。

## Decisions and Adoption

- 新增 D-005：允许把 ZCU104 MJPEG 30fps 作为候选输入；720p30优先，1080p30待验证。
- MJPEG 解码仍放 PS/Linux，PL 只处理解码后的标准化像素；首版不实现 PL JPEG decoder。

## Validation and Evidence

- 路线判断：有条件可行，当前没有 ZCU104、摄像头或解码基准实测。
- 未执行：MJPG格式查询、实际码率、A53解码性能、300帧连续运行、DMA/PL/显示联调。

## Errors and Corrections

- 修正“USB3足够所以30fps可行”的简化判断：USB带宽只是必要条件，PS解码和端到端持续处理必须单独测量。

## Files Changed

- `project_workspace/DECISIONS.md`：新增 D-005。
- `project_workspace/PROJECT_STATE.md`：补充 MJPEG 30fps 评估状态。
- `project_workspace/ai/INDEX.md`：新增会话索引。
- 新增本会话记录。

## Remaining Work

1. 查询实际 MJPG 分辨率/帧率列表并确认目标模式。
2. 在板端分别测试纯采集、纯解码、解码加颜色转换。
3. 再接 DMA、PL二值化和显示，统计端到端帧率与丢帧。
