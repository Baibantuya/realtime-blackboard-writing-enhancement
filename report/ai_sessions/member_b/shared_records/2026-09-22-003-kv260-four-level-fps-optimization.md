# AI Session: 2026-09-22-003-kv260-four-level-fps-optimization

- Date: 2026-09-22
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 在已通过以太网连接的 KV260 上，按既有四级思路测量并优化 Jupyter `trial1` 视频处理帧率与延迟。
- Status: Completed measurement and first PS-side optimization; 30 fps decode optimization remains open
- Report candidate: Yes
- Related commits: None
- Related files: Board directory `/root/jupyter_notebooks/blackboard/trial1`; local `whiteboard/pynq/`; this record.

## Context Read

- Read root `AGENTS.md`, AI development policy, project state, decisions, AI record index, and recent 19 fps bottleneck record (2026-09-22-001).
- Current source of truth for the existing implementation is `whiteboard/pynq/kv260_threshold.py` and its notebook. Existing baseline is user-observed approximately 19 fps, not independently remeasured yet.

## Task and Constraints

- User authorized SSH access and requested hands-on optimization/testing of the KV260 notebook directory.
- The supplied password is not recorded in this session file. Board changes will be restricted to the named notebook directory, with timestamped backups before mutation.
- Four levels: (1) DMA/PL synthetic baseline, (2) camera decode-only, (3) camera plus DMA without browser preview, (4) full-path preview; compare each using the same frame size and a finite measurement window.

## Contributions

- Confirmed Ethernet SSH connectivity to `ubuntu@[private_ip]` after pinning the board's observed ED25519 host-key fingerprint. Inspected `/root/jupyter_notebooks/blackboard/trial1` without changing its existing files.
- Ran the level-2 decode-only preliminary measurement on actual UVC `/dev/video0`: 300 full-HD MJPEG frames decoded to GRAY8 in 10.97 s, or **27.35 fps**, reported CPU use 91%. This test used `ffmpeg -fflags nobuffer`; it is a decode-only baseline, not the PYNQ pipeline rate.
- Authored reproducible four-level benchmark `test_workspace/kv260_fps_optimization_2026-09-22/fps_benchmark.py`: synthetic DMA (with/without PS output copy), camera decode-only, camera+DMA without preview, and camera+DMA plus JPEG preview. The benchmark reuses its GRAY8 input buffer and includes median/p95 frame timing.
- Identified two execution-environment requirements: notebook runs under `/usr/local/share/pynq-venv/bin/python3`, not `/usr/bin/python3`; it also needs `XILINX_XRT=/usr` and `BOARD=KV260`.
- Prepared a user-upload deployment package in `test_workspace/kv260_fps_optimization_2026-09-22/deploy_trial1/`: optimized `kv260_threshold.py`, `kv260_threshold_four_level.ipynb`, and an upload/rollback README. The module reuses one UVC byte buffer, suppresses per-frame DMA-output copies, and defaults to decimated preview plus FFmpeg `nobuffer`.
- User reported that the original uploaded notebook did not expose all intended measurements. Created a complete standalone supplement `kv260_threshold_level1_level4.ipynb`, with independent imports/setup and only the missing level-1 and level-4 cases; its JSON parse was locally validated.
- User completed the supplementary measurements: level 1 synthetic DMA+PL no-copy was 120 frames/1.8337 s = **65.441 fps**, median 15.274 ms, p95 15.385 ms. Level 4 camera+DMA+PL with preview every 15 frames was 120 frames/5.1575 s = **23.267 fps**, median 33.612 ms, p95 79.896 ms; median JPEG preview encoding time was 46.513 ms. DMA buffers were released by the notebook.

## Decisions and Adoption

- The user uploaded and ran the low-copy/reusable-buffer module in a root-owned Jupyter kernel. It is adopted as the provisional PYNQ demonstration baseline: level 3 proves DMA/PL is not limiting at 30 fps, while level 4 preserves preview at 23.267 fps.
- The user's earlier approximately 19 fps used different preview cadence and copy behavior, so it is not a controlled before/after comparison. Further 30 fps work targets the MJPEG decode/capture boundary; browser preview remains optional and decimated due to its tail-latency spikes.

## Commands and Tools

- Read-only board inspection: hostname/OS, V4L2 UVC capability, FPGA manager state, board files, CPU count, and filesystem capacity.
- Decode baseline: `/usr/bin/time ... ffmpeg ... -frames:v 300 -pix_fmt gray -f rawvideo - >/dev/null`.
- Attempted temporary benchmark execution with system Python (missing PYNQ), then notebook venv (requires root for PYNQ clock/MMIO access). Neither attempt successfully loaded or modified the overlay.

## Validation and Evidence

- UVC is 1920x1080 MJPEG at 30 fps and FPGA manager reports `operating`.
- Actual measured level-2 decode-only result: 10.97 s/300 frames = 27.35 fps; CPU 91%.
- User executed the uploaded optimized notebook's level-2 case: 120 frames in 4.8448 s = **24.769 fps**, median 33.716 ms/frame, p95 34.287 ms/frame. This is the current controlled decode-only result; it confirms that full-HD MJPEG→GRAY8 decode alone is below 30 fps but has low frame-time jitter. It supersedes the prior CLI result for notebook-comparison purposes because its code path and finite sample definition match the four-level notebook.
- User executed level 3 in the same notebook: 120 camera+DMA+PL frames without preview in 4.7715 s = **25.150 fps**, median 33.634 ms/frame, p95 34.125 ms/frame. Its 0.082 ms lower median than level 2 is within separate-run source timing variation, not evidence that DMA accelerates decode. The data establishes that the DMA/PL path adds no measurable frame-time cost at this resolution and sample size; it is not the cause of the approximately 19 fps old full-path result.
- Local delivery validation: optimized module passed `py_compile` and a threshold-boundary smoke test; notebook JSON parses successfully.
- Full board validation is now complete via user-run notebooks: L1 65.441 fps; L2 24.769 fps; L3 25.150 fps; L4 23.267 fps. Level-4 p95 is 79.896 ms because JPEG/widget work occurs on 8 of 120 frames, and its 46.513 ms median JPEG cost is synchronous in the loop.

## Errors and Corrections

- Initial direct upload to `trial1` failed with permission denied; no existing board file was overwritten.
- Initial benchmark used `/usr/bin/python3`, where OpenCV and NumPy binary versions conflict and PYNQ is absent. Inspection of the Jupyter service corrected the interpreter to the PYNQ virtual environment.
- PYNQ venv initially reported no device until its Jupyter environment variables were restored. It then reached overlay download but correctly stopped at root-only MMIO access.

## Files Changed

- `project_workspace/ai/sessions/2026-09-22-003-kv260-four-level-fps-optimization.md` (created).
- `test_workspace/kv260_fps_optimization_2026-09-22/fps_benchmark.py` (created; local reproducible test artifact).
- `test_workspace/kv260_fps_optimization_2026-09-22/deploy_trial1/kv260_threshold.py` (created; user-upload candidate).
- `test_workspace/kv260_fps_optimization_2026-09-22/deploy_trial1/kv260_threshold_four_level.ipynb` (created; user-upload benchmark).
- `test_workspace/kv260_fps_optimization_2026-09-22/deploy_trial1/README.md` (created; upload/rollback instructions).
- `test_workspace/kv260_fps_optimization_2026-09-22/deploy_trial1/kv260_threshold_level1_level4.ipynb` (created; independent supplemental benchmark).

## Remaining Work

1. Compare FFmpeg MJPEG decode with explicitly configured decoder thread counts and determine whether the installed build can use more than one A53 core.
2. If decode remains below 30 fps, evaluate a lower-resolution UVC mode or a non-MJPEG/accelerated decode capture path while preserving GRAY8 at the PL boundary.
3. For lowest display latency, separate browser preview from the capture/DMA loop or keep it at a lower cadence; use a bounded latest-frame queue rather than accumulating camera frames.

## Handoff Notes

The Jupyter service is root-owned; user ran the uploaded notebooks through its kernel. Future controlled testing should start a fresh kernel and avoid a concurrent `/dev/video0` reader.
