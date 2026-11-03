# AI Session: 2026-10-20-006-ps-algorithm-and-framerate-redesign
- Date: 2026-10-20
- Operator: why
- AI product/model: Gemini 3.8 Flash (Antigravity)
- Participants: user, Antigravity
- Objective: Diagnose PS board detection conflicts (loss, exit, micro-movement, occlusion) and display frame rate drops; propose a clean decoupled architectural redesign.
- Status: In progress
- Report candidate: yes (covers foundational PS/PL pipeline decoupling, multi-modal board tracking state machine, and root-cause throughput analysis)
- Related commits: None yet
- Related files:
  - `kv260-whiteboard-enhance/rtl/dma_rgb565_fusion_v22/board_package_r7/scene_board_recognition.py`
  - `kv260-whiteboard-enhance/rtl/dma_rgb565_fusion_v22/board_package_r7/board_detector.py`
  - `kv260-whiteboard-enhance/rtl/dma_rgb565_fusion_v22/board_package_r7/run_stage_pipeline_archive.py`
  - `kv260-whiteboard-enhance/rtl/dma_rgb565_fusion_v22/board_package_r7/scene_live.py`
  - `kv260-whiteboard-enhance/rtl/dma_rgb565_fusion_v22/board_package_r7/archive_ui.py`

## Context Read
- `AGENTS.md`
- `project_workspace/ai/AI_DEVELOPMENT_POLICY.md`
- `project_workspace/PROJECT_STATE.md`
- `project_workspace/DECISIONS.md`
- `project_workspace/ai/INDEX.md`
- Recent sessions 005, 004, 003, and live run log `live_r6.log`.

## Task and Constraints
- Analyze the 4-way conflict in current PS board recognition:
  1. No board found (initial calibration/search guidance).
  2. Board exited field of view (must reliably trigger re-search, not freeze on stale geometry).
  3. Slight board movements (homography matrix should continuously update, not ignore small moves).
  4. Person occludes whiteboard (writing or walking past must NOT cause false loss of board or re-detection).
- Analyze the root cause of extremely low display frame rate and severe frame dropping.
- Formulate a clean, thoroughly decoupled PS algorithm redesign where PS acts as a true asynchronous bypass/coprocessor without blocking the video flow.

## Contributions
- Identified the coupling mechanisms in the current PS implementation:
  1. False occlusion-triggered search: `_movement` monitors border intensity differences, triggered whenever a person crosses the board edge. Occlusion breaks 4-edge detection, setting `safe = False`, which immediately invokes `gate.revoke()`, dropping all pending frames and freezing the video.
  2. Deadzone & drain blocking on micro-movement: `delta <= 4` freezes matrix; when matrix changes, main loop stalls until Ring A/B are completely drained.
  3. Synchronous CPU intervention per frame: `quantizer.prepare` and `quantizer.restore_done` read/process DDR frames synchronously in the main loop; heavy CPU copies (4MB per snapshot and display copy) congest the shared DDR bus.
  4. Video flow gated on PS state: Camera frames are dropped if PL rings are waiting on PS CPU processing or if `safe == False`.

## Decisions and Adoption
- (Pending user discussion and confirmation)

## Commands and Tools
- `git status`
- Code inspection via `view_file` and directory inspection via PowerShell commands.

## Validation and Evidence
- Inspected `live_r6.log`: Camera captures at 30 FPS, but `camera_dropped_before_admission` reached 674 frames, output FPS was 3.5~5.5 FPS, and stage latencies showed huge spikes (rectify up to 332ms, quantize up to 313ms) caused by bus contention and gate revocation.

## Errors and Corrections
- Clarified that low display FPS is not caused by PL clock frequency alone, but by PS CPU bus contention, synchronous frame processing in the main loop, and aggressive `gate.revoke()` on occlusion.

## Files Changed
- (Session record created)

## Remaining Work
- Present complete architectural redesign proposal to user.
- Detail the decoupled state machine for board detection (multi-hypothesis edge tracking + Kalman/exponential smoothing + area/keypoint verification for exit vs occlusion).
- Detail the asynchronous bypass pipeline architecture to restore full framerate.

## Handoff Notes
- All diagnostic findings and proposed algorithm structures are grounded in exact lines of code in v22_r7.
