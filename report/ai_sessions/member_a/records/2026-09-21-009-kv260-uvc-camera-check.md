# AI Session: 2026-09-21-009-kv260-uvc-camera-check

- Date: 2026-09-21
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 通过 KV260 串口检查新接入的免驱 USB UVC 摄像头是否正确枚举、支持哪些视频格式，并进行短时间连续采集验证。
- Status: Completed
- Report candidate: No
- Related commits: None
- Related files: `project_workspace/ai/sessions/2026-09-21-009-kv260-uvc-camera-check.md`, `project_workspace/PROJECT_STATE.md`, `project_workspace/ai/INDEX.md`

## Context Read

已读取根目录入口规范、AI 开发政策、项目状态、决策流水、内部索引和上一轮 KV260 串口板测记录。已知有效串口参数为 COM11、115200-8-N-1、XON/XOFF；板卡为 KV260 revB、Ubuntu 22.04.4。

## Task and Constraints

- 用户已将免驱 USB 摄像头连接至 KV260，并要求检查。
- 优先执行只读枚举和 V4L2 能力检查；连续采集输出到 `/dev/null`，不保存图像、不修改摄像头固件或板卡配置。
- 真实执行结果必须与未执行项区分；登录凭据不写入记录。

## Contributions

- 摄像头枚举为 Realtek `HDR CAMERA-A`，USB ID `0bda:5180`，制造商字符串 `BLC-260423-J`，UVC 1.00；通过板载 USB 2.0 high-speed hub 连接，`uvcvideo` 和 `snd-usb-audio` 均已绑定。
- 创建 `/dev/video0`（Video Capture）、`/dev/video1`（Metadata Capture）和 `/dev/media0`；用户属于 `video` 组，可直接访问采集节点。
- `/dev/video0` 的 MJPEG 模式在 1920×1080、2592×1944、2048×1536、1280×1024、1280×960、1280×720、1024×768、800×600、640×480、320×240 均声明 30 fps。
- YUYV 4:2:2 模式：1920×1080/1280×1024/1280×960/1280×720 为 5 fps，2592×1944/2048×1536 为 2 fps，1024×768 为 10 fps，800×600 为 15 fps，640×480/320×240 为 30 fps。
- 控制项包括亮度、对比度、饱和度、色调、自动白平衡、gamma、50/60 Hz 电源频率、锐度、背光补偿、自动/手动曝光等。
- USB 描述符为 USB 2.01、`MaxPower 500mA`；摄像头麦克风枚举为 ALSA `card 1, device 0`。

## Decisions and Adoption

- 暂无。

## Commands and Tools

- 已读取项目上下文并建立本次会话记录。
- 通过 Plink 使用 COM11、115200-8-N-1、XON/XOFF 接入已有 `ubuntu@kria` shell。
- 执行 `lsusb`、`lsusb -t`、`v4l2-ctl --list-devices/-D/--list-formats-ext/--list-ctrls-menus`、设备节点检查、USB 描述符检查、`arecord -l` 和内核日志筛选。
- 将视频流直接输出到 `/dev/null`，分别测试 1280×720 MJPEG 30 fps 300 帧、640×480 YUYV 30 fps 150 帧、1920×1080 MJPEG 30 fps 150 帧。

## Validation and Evidence

- 1280×720 MJPEG：参数成功设为 30 fps，300 帧在 10.399 秒完成；包含启动阶段的总平均约 28.85 fps，稳态显示达到 29.98 fps。
- 640×480 YUYV：参数成功设为 30 fps，150 帧在 5.410 秒完成；包含启动阶段的总平均约 27.73 fps，测试过程无采集错误。
- 1920×1080 MJPEG：参数成功设为 30 fps，150 帧在 5.430 秒完成；包含启动阶段的总平均约 27.62 fps，测试过程无采集错误。
- 三次采集均完成请求帧数；测试后内核日志未出现 USB reset、disconnect、overflow、overrun、timeout 或 video error。
- 未执行 MJPEG 软件解码、画面内容/色彩视觉验证、长时间 300 帧以上压力、音频实际录制、PL/VDMA/HDMI 视频闭环。

## Errors and Corrections

- 内核在麦克风枚举时报告 `cannot get freq at ep 0x86` 和异常大的音量范围警告；视频 UVC 枚举和三组采集未受影响。麦克风仅验证到 ALSA 枚举，未验证真实录音质量。

## Files Changed

- `project_workspace/ai/sessions/2026-09-21-009-kv260-uvc-camera-check.md`
- `project_workspace/PROJECT_STATE.md`
- `project_workspace/ai/INDEX.md`

## Remaining Work

1. 以 720p30 MJPEG 为首个高帧率输入基线，实测 A53/硬件解码到 BGRX/GRAY8 的负载与延迟。
2. 保存并目视检查代表性帧，确认色彩、曝光、对焦、白板细节与畸变；本次数据输出到 `/dev/null`。
3. 完成摄像头→PS 解码/标准化→AXIS/PL→DDR→HDMI/DP 闭环及长时间稳定性测试。

## Handoff Notes

摄像头作为 UVC 视频源可用。若目标是 720p30 或 1080p30，应采用 MJPEG 后在 PS/硬件侧解码；YUYV 在 720p 仅 5 fps，不适合作为项目的 720p30 输入，但 VGA YUYV 30 fps 可作为无需 JPEG 解码的低分辨率 bring-up 模式。
