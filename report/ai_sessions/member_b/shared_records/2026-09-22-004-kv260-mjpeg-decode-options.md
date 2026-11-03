# AI Session: 2026-09-22-004-kv260-mjpeg-decode-options

- Date: 2026-09-22
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 在确认 HDMI 输出不使用浏览器预览后，评估并实测 KV260 1080p MJPEG 解码优化空间，以及是否需要转 CSI-2 摄像头。
- Status: Completed; CSI-2 recommended for a stable 1080p30 production path
- Report candidate: Yes
- Related commits: None
- Related files: Board `/dev/video0`; `project_workspace/PROJECT_STATE.md`; `project_workspace/DECISIONS.md`; this record.

## Context Read

- Read the completed four-level result in session 2026-09-22-003 and decision D-035. User's board evidence: L1 65.441 fps, L2 24.769 fps, L3 25.150 fps, L4 23.267 fps.

## Task and Constraints

- HDMI output removes browser JPEG/widget overhead, but it does not remove UVC MJPEG software decode.
- Use controlled board-side FFmpeg decode-only measurements before recommending a camera-interface change. Do not change the active overlay or existing notebook files.

## Contributions

- Confirmed the board FFmpeg build exposes a software `mjpeg` decoder and an irrelevant Nvidia `mjpeg_cuvid` decoder. Its advertised generic hwaccel methods are VDPAU/CUDA/VAAPI/DRM/OpenCL, but the board has only `/dev/video0` and `/dev/video1`; no board-accessible MJPEG hardware decoder is present.
- Ran actual-board 1080p30 UVC MJPEG→GRAY8 decode-only measurements for 300 frames with FFmpeg `-threads 1`, `-threads 2`, and `-threads 4`, all with `-fflags nobuffer`: 10.86 s (27.62 fps, CPU 92%), 10.88 s (27.57 fps, CPU 90%), and 10.87 s (27.60 fps, CPU 90%), respectively. Decoder threading has no useful effect.
- Rechecked UVC formats: 1080p30 is MJPEG only; 1080p YUYV is limited to 5 fps. Therefore changing this UVC camera from MJPEG to uncompressed input cannot meet 1080p30.

## Decisions and Adoption

- HDMI output should replace the browser preview for display latency and removes its JPEG/widget stalls, but it cannot lift the current camera pipeline above the MJPEG decode ceiling.
- For a stable 1080p30 final route, prefer a MIPI CSI-2 camera delivering raw Bayer/YUV pixels into PL (then PL ISP/gray/threshold/HDMI) over continuing to optimize the existing USB MJPEG path.
- Do not implement a PL JPEG decoder in the current competition schedule: it is a substantially larger compression/bitstream-integration task than using the KV260 native CSI-2 input and offers less predictable integration risk. Keep UVC MJPEG as a usable ~25 fps bring-up/fallback path.

## Commands and Tools

- Board read-only capability checks: `ffmpeg -decoders`, `ffmpeg -hwaccels`, `/dev/video*` inventory, and `v4l2-ctl --list-formats-ext`.
- Three board-side decode runs using `/usr/bin/time` and FFmpeg decoder thread counts 1/2/4. A first shell-loop invocation was invalidated by Windows/remote shell quoting; the three independent runs above are the accepted evidence.

## Validation and Evidence

- Accepted measurements: 27.62 fps (thread 1), 27.57 fps (thread 2), and 27.60 fps (thread 4), all 300 frames. This is consistent with the user-run PYNQ notebook decode-only result of 24.769 fps after accounting for different measurement wrappers.
- No CSI-2 camera has been connected or tested in this session. The CSI-2 recommendation is an engineering inference from the measured UVC decoder limit and the KV260's native camera interface, not a CSI throughput measurement.

## Errors and Corrections

- The initial combined remote loop produced only decoder-list output due to cross-shell quoting. It was not recorded as a performance result; independent commands were used instead.

## Files Changed

- `project_workspace/ai/sessions/2026-09-22-004-kv260-mjpeg-decode-options.md` (created).

## Remaining Work

1. Select a CSI-2 module with available KV260/PYNQ driver and PL capture reference path.
2. Define CSI-2→PL→HDMI architecture and measure it on board before retiring UVC fallback.
3. If retaining UVC for demonstration, configure HDMI output and present it as an approximately 25 fps path, not 30 fps.

## Handoff Notes

The full-HD UVC camera exposes only MJPEG at 30 fps; its YUYV mode is 5 fps. FFmpeg decoder threads 1/2/4 do not improve its MJPEG decode rate. Do not spend further time tuning thread count.
