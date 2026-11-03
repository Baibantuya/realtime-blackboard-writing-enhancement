# AI Session: 2026-09-21-010-kv260-uvc-single-frame

- Date: 2026-09-21
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 从 KV260 的 USB UVC 摄像头采集一帧 1280×720 MJPEG 图像，取回并进行目视质量检查，提出下一步方案。
- Status: Completed
- Report candidate: No
- Related commits: None
- Related files: `project_workspace/ai/sessions/2026-09-21-010-kv260-uvc-single-frame.md`, `project_workspace/PROJECT_STATE.md`, `project_workspace/ai/INDEX.md`

## Context Read

已读取项目规范、项目状态、内部索引和上一轮 UVC 摄像头实测记录。摄像头已确认 720p30 MJPEG 可连续采集，串口参数为 COM11、115200-8-N-1、XON/XOFF。

## Task and Constraints

- 用户要求实际采一帧并展示照片，同时给出基于画面的后续方案。
- 采集目标为 `/dev/video0`、1280×720 MJPEG；板端使用 `/tmp` 临时文件，取回后保留内部证据副本。
- 不调整曝光/白平衡等摄像头控制，先检查默认自动参数的真实效果。

## Contributions

- 从 `/dev/video0` 以 1280×720、MJPEG、30 fps 配置采集一帧，板端临时文件为 baseline JPEG、8-bit、3 components，大小 70,433 字节。
- 通过串口 Base64 传回图像并保存为 `project_workspace/evidence/kv260_uvc/first_frame_1280x720.jpg`；本地与板端 SHA-256 均为 `96cba79efcfa41f478d9a9f23b92da2120b636239a6f63efc7feac60f0f5843c`。
- 目视检查：场景为桌面/书架/显示器，不是白板。中心物体和远处轮廓可辨，色彩基本正常，广角视场足够；右上显示器和右下白色键盘明显高光剪切，左侧明显偏暗，动态范围与照明均匀性不足。画面存在轻微冷/青倾向，边缘和远处细节清晰度一般；当前低机位、斜向构图和杂乱背景不适合评估板书识别。

## Decisions and Adoption

- AI 建议（待用户确认）：首版继续采用 720p30 MJPEG 输入；正式白板采集前先改善安装角度和照明，再做自动曝光预热、曝光/白平衡锁定和透视校正。当前单帧只证明真实图像可采集，不证明白板文字增强效果。

## Commands and Tools

- 已读取上下文并建立会话记录。
- 通过 Plink 登录 KV260，使用 `v4l2-ctl` 配置 `/dev/video0` 为 1280×720 MJPEG 30 fps 并采集一帧。
- 使用 `file`、`stat`、`sha256sum` 校验板端 JPEG；经 Base64 串口传输到本机，解码后再次验证 SHA-256，并进行原始分辨率目视检查。
- 板端 `/tmp/codex_kv260_uvc_20260921.jpg` 在本地证据校验完成后已删除，可恢复副本保存在内部证据目录。

## Validation and Evidence

- 图像可正常解码为 1280×720 JPEG，文件哈希在传输前后一致，排除串口传输损坏。
- 已实际目视检查曝光、亮暗分布、颜色、视场、构图与清晰度；未对照片做缩放、增强或内容修改。
- 未执行白板场景拍摄、客观清晰度/畸变标定、曝光参数扫描或 PL 图像增强。

## Errors and Corrections

- 首次唤醒串口时输入被登录程序解释为无效凭据，出现一次 `Login incorrect`；随后使用正确账号登录，不影响板端或摄像头状态。

## Files Changed

- `project_workspace/ai/sessions/2026-09-21-010-kv260-uvc-single-frame.md`
- `project_workspace/evidence/kv260_uvc/first_frame_1280x720.jpg`
- `project_workspace/PROJECT_STATE.md`
- `project_workspace/ai/INDEX.md`

## Remaining Work

1. 将摄像头安装在白板中心高度附近，光轴尽量垂直白板，白板占画面 70%–85%，避开显示器和灯具等强亮源。
2. 先运行约 30 帧让自动曝光/白平衡稳定，再根据白板高光情况降低曝光；在现场光照固定后锁定曝光和白平衡，并保持 50 Hz 防闪烁。
3. 采集一张完整白板、一个角落小字和一张斜拍图，比较原图、灰度/二值化和透视校正结果，再确定最终增强参数。

## Handoff Notes

当前摄像头和串口取图链路可用。照片暴露的首要问题不是分辨率，而是机位和高光：若不先控制强亮源及透视，后续二值化会把过曝区域丢成纯白、暗区文字噪声放大。建议下一次直接对准真实白板再采一帧，用同一证据流程评估。
