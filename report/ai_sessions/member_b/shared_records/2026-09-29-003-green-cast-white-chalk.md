# AI Session: 2026-09-29-003-green-cast-white-chalk

- Date: 2026-09-29
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: Correct green cast and preserve white writing on a dark-green blackboard using ISP color-science guidance; deploy and verify on KV260.
- Status: Board color correction running; physical screen color after DP pixel-format switch awaiting owner observation.
- Report candidate: Yes
- Related commits: None
- Related files: `test_workspace/design_1_full_deployment_20260928/design_1_full_deployment_20260928/software/`

## Context Read

Read root AGENTS.md, AI development policy, project state, decisions, index, prior RAW8 and color-preserving AE sessions, Git status, and the user-specified ISP tutorial chapter 10. The tutorial separates luminance from chroma, describes white-point AWB with gain limits/temporal smoothing, and requires calibration for CCM.

## Task and Constraints

Use the owner's scene facts: the board is dark green, central writing is white, and current output appears green with indistinguishable writing color. Capture actual board RGB evidence before changing AE/AWB; distinguish scalar exposure errors from color-balance or RGB-order errors. Deploy and verify without inventing image-quality results.

## Contributions

- Captured one unmodified 1920x1080 `RGB3` frame from the active RAW8 pipeline, automatically resumed the candidate stream, and inspected the saved image. The white chalk, walls, and dark board were all green-tinted before PS AWB/PL processing. Old AWB sampled bright near-neutral/clipped surroundings and logged gains `[1,1,1]` despite the visible cast.
- Replaced the candidate white-point estimator with a central, local-contrast chalk detector that rejects clipped pixels. It estimates bounded red/blue gains and smooths subsequent updates; a scene-specific intensity-dependent LUT applies much more correction to bright white strokes than to the dark-green board. AE's sensor luma target, nine-patch metering, exposure/gain feedback, and RAW8 guard were not changed.
- First version used full-frame floating-point gating and visibly improved a captured frame, but board rate fell from about 1.06 to 0.89 fps. Replaced the application step with a cached 8-bit channel LUT; host frame processing dropped from about 56 ms to about 2 ms, and the resumed board pipeline returned to about 1.05 fps in its first 70 frames.
- Added optional first-frame diagnostic PNGs to `run_pipeline.py`; board saved raw, balanced, and PL-rectified images. The saved rectified image has white writing and a dark-green board. The owner then reported the physical display had red and blue swapped. Switched only the DisplayPort fourcc from `PIXEL_RGB` to `PIXEL_BGR`, leaving RGB camera/PL data untouched, and restarted the candidate again as PID 20368.

## Decisions and Adoption

- Adopted D-054 for this candidate: white-chalk reference plus luminance/intensity-separated color correction, with `PIXEL_BGR` on the observed KV260 display path. D-052's prior `PIXEL_RGB` display choice was corrected based on the owner's physical observation; post-switch physical confirmation is pending.
- The cited ISP tutorial supports luminance/chroma separation, white-point estimation, bounded gain and temporal smoothing. Its CCM section requires a calibrated color target; no calibrated CCM or color-accuracy claim is made.

## Commands and Tools

- Read the user-specified [ISP tutorial chapter 10](https://zsc.github.io/isp_tutorial/chapter10.html), current AE/AWB/runner/PL controller source, related project sessions, board media controls, candidate logs, and an older RAW10-derived frame.
- `capture_and_resume.sh` stopped the live Python process, captured one raw RGB3 PNG with `V4l2RgbStream`, and resumed the same candidate. `pscp` copied it to `test_workspace/green_cast_white_chalk_2026-09-29/`; local OpenCV scripts analyzed and previewed the frame.
- Host `py -3 -B -m unittest discover` ran the scene-specific regression checks. `preflight_chalk.py` executed on the board before each restart. Board `bash -n`, SHA-256, V4L2 format/control readback, process/log checks, and captured output PNGs were used for deployment verification. Credentials were not written to files.

## Validation and Evidence

- Baseline frame `/home/ubuntu/design_1_full_deployment_20260928/diagnostics/before_color_rgb3.png` and local copy `test_workspace/green_cast_white_chalk_2026-09-29/before_color_rgb3.png` were captured from `RGB3` 1920x1080 under sensor `SRGGB8_1X8`. Whole-frame median RGB was `[88,149,102]`; central median `[59,103,73]`. Central high-contrast chalk samples retained strong G bias, explaining why scalar AE could not restore their white color.
- Host regression: two checks passed on a synthetic green board and the captured real RGB3 frame. The real-frame test found more than 80 chalk samples, R gain >1.4 and B gain >1.2, chalk chroma imbalance reduced by >3x, and board green preserved. Board preflight accepted the same image with 1116 chalk samples and gains `[1.631,1,1.403]`.
- First deployed floating-point version produced PID 19741 and saved `diagnostics/after_chalk/{raw_rgb3,balanced_rgb3,rectified_rgb3}.png`; actual first-frame gains `[1.657,1,1.398]` and nonzero PL corners. Matched raw/balanced sample statistics: chalk median `[123,198,142]` to `[202,198,198]`, chalk median channel imbalance 129 to 17; quiet board median `[61,108,77]` to `[69,108,83]`, preserving G-R=39. The saved PL rectified PNG visibly presents white writing on a green board. Physical screen was not directly inspected by AI.
- The owner reported red/blue reversal on the display. PYNQ source showed `PIXEL_RGB` fourcc `RG24` and `PIXEL_BGR` fourcc `BG24`. After switching to `PIXEL_BGR` and deploying the LUT version, PID 20368 started and reached frame 70 without exception, about 1.05 fps and `rectify_ms` about 317 ms. Sensor still reported RAW8 1920x1080; DRM connector was connected. Logs showed AE gain change during a lighting variation (211 down to 188, then up to 232) while target remained 80, confirming feedback remained active. Post-switch physical red/blue and chalk appearance: awaiting owner observation.
- Full timing closure, calibrated color accuracy, and controlled low-light performance: 未执行. Existing bit timing violation remains WNS -5.589 ns / TNS -66.917 ns; bit/HWH/DTBO were not reloaded during these Python-only changes.

## Errors and Corrections

- Initial assumption that AWB white candidates were usable was corrected after inspecting the raw frame: many high-brightness wall pixels were clipped and supplied `[1,1,1]` gains. Chalk was identified by local contrast inside the board region instead.
- The first corrected image looked good but full-frame floating-point gain maps slowed the board pipeline. Replaced them with a cached 8-bit LUT and retested both image metrics and frame rate.
- The earlier `PIXEL_RGB` display choice was inconsistent with the owner's observed red/blue output. Kept RGB order for capture/PL and changed only DisplayPort's pixel format; direct physical confirmation of the revised mapping is still pending.

## Files Changed

- Candidate `software/color_balance.py`, `software/run_pipeline.py`, and `README.md` under `test_workspace/design_1_full_deployment_20260928/design_1_full_deployment_20260928/`.
- Named diagnostic workspace `test_workspace/green_cast_white_chalk_2026-09-29/`: capture/restart/preflight helpers, real-frame regression and comparison scripts, and captured PNG evidence.
- Board candidate `software/color_balance.py`, `software/run_pipeline.py`, `README.md`, current PID/log, diagnostic PNGs, and retained pre-change backup files/logs.
- `project_workspace/DECISIONS.md`, `project_workspace/PROJECT_STATE.md`, `project_workspace/ai/INDEX.md`, and this session record.

## Remaining Work

- Obtain the owner's physical-screen confirmation after `PIXEL_BGR`; if still reversed, compare a known-color test pattern and adjust only the display buffer ordering.
- Test a deliberate dark/bright illumination step and a second scene with white chalk in the center to assess convergence and false white-point selection. Board AE can saturate at exposure 2724 and gain 232 under low light; this limits attainable luma without changing sensor timing/illumination.
- Promote the accepted candidate source and reproduction notes into the formal project directory after physical acceptance; current experiment and evidence remain in `test_workspace`.

## Handoff Notes

Current candidate process is PID 20368, log `/home/ubuntu/design_1_full_deployment_20260928/candidate_live.log`; current files' board hashes can be checked before any later reload. The prior AE and AWB/runner variants plus pre-restart logs remain under the board work directory. Do not record credentials. `--no-awb` isolates scalar AE from this scene-specific white-chalk color stage; `--dump-first-dir PATH` saves RGB diagnostic frames.
