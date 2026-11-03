# AI Session: 2026-09-28-004-imx219-color-preserving-ae

- Date: 2026-09-28
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: Correct green-looking color output while retaining legible blackboard writing, informed by ISP tutorial chapter 10.
- Status: PS source correction and host checks complete; board color validation pending.
- Report candidate: No
- Related commits: None; workspace root is not a Git repository.
- Related files: `test_workspace/imx219_ps_core/package/`

## Context Read

Prior mandatory context was read in this conversation. Rechecked D-051, prior AE implementation and handoff, current source and Git status. Read the user-linked ISP chapter 10 on luminance/chrominance, white balance and color matrices. No new board frame or command line has yet been provided.

## Task and Constraints

Fix the color loss without forcing a green blackboard toward neutral gray. Preserve Linux IMX219 driver ownership of exposure/gain I²C writes. Do not claim hardware color accuracy without actual frame evidence.

## Contributions

- Inspected the code path and found two concrete color-contract errors: V4L2 requests `RGB3`, but the runner passed `bgr=True` to the PL luma kernel and used `PIXEL_BGR` for DisplayPort; the runner also defaulted to the binary output mode, which necessarily removes all color distinctions.
- Changed default output to color (`--binary` now requests the legacy black/white mode), set the PL luma selector to RGB and DisplayPort to `PIXEL_RGB`.
- Replaced equal-channel board brightness with BT.601 weighted luminance plus a clipped-channel fraction guard. Added `color_balance.py`, which estimates small, smoothed R/B corrections only from sufficiently bright near-neutral pixels and holds gains when no credible white point exists. It never treats the green board as a gray-world reference.
- Updated README and the existing internal deployment handoff for five Python modules, new CLI options, color defaults and image evidence requirements.

## Decisions and Adoption

- Adopted D-052. Chapter 10 separates luminance and chrominance, describes gray-world and white-point AWB, and recommends gain limits and temporal smoothing. A green-blackboard-dominated scene violates the gray-world premise, so white-point candidates are gated and no white point means no correction.
- No conclusion was reached on whether the reported green appearance originated in the sensor/ISP, RGB/BGR contract, default binary output or display, because the user could not provide a raw frame or command line during this turn.

## Commands and Tools

- Read `https://zsc.github.io/isp_tutorial/chapter10.html` and local PS/HLS source. Inspected `board_rectify_rgb.cpp` and confirmed `bgr` changes luma weighting only while the color byte order passes through unchanged. Used `apply_patch` to edit source and records.
- Ran `py -3 -B -m unittest discover -s test_workspace/imx219_ps_core_ae_tests -p 'test_*.py' -v` and Python AST parsing of every package `.py` file.

## Validation and Evidence

- Seven host unit tests passed: original chalk/reference and V4L2 control tests plus green-board weighted luma, clipped highlight guard, no-white-point hold, and gradual neutral-patch correction. Package Python AST parsing passed.
- Board display, captured RGB bytes, actual exposure and color response, FPS and ISP calibration: 未执行. PYNQ is unavailable on the Windows host, so the full runner was not executed there.

## Errors and Corrections

- First review established that the previous equal-channel metric was insensitive to the `RGB3` channel identity and could overexpose a green-dominant board relative to weighted luminance. This was replaced with BT.601 weighting. Added a dedicated control test to ensure clipped highlights cannot drive exposure upward; all tests passed.
- No raw image was available after requesting one; documented the causal uncertainty rather than claiming the cast is fixed on hardware.

## Files Changed

- `test_workspace/imx219_ps_core/package/auto_exposure.py`
- `test_workspace/imx219_ps_core/package/color_balance.py` (new)
- `test_workspace/imx219_ps_core/package/run_pipeline.py`
- `test_workspace/imx219_ps_core/package/README.md`
- `test_workspace/imx219_ps_core_ae_tests/test_auto_exposure.py`
- `test_workspace/imx219_ps_core_ae_tests/test_color_balance.py` (new)
- `project_workspace/ai/handoffs/imx219_ps_auto_exposure_deployment.md`
- `project_workspace/DECISIONS.md`, `project_workspace/PROJECT_STATE.md`, `project_workspace/ai/INDEX.md`, this session record

## Remaining Work

- Obtain an unmodified RGB3 frame and a photo/screenshot of the same color frame on HDMI, with the exact CLI command. Compare `--no-ae --no-awb`, AE-only, and AE+AWB, always in color mode; do not infer a PS fix from the binary image.
- Check Bayer phase, demosaic, ISP gamma/CCM and video format if raw RGB3 is already green or red/blue are swapped. Calibrate a proper CCM/white balance with a neutral/color reference if the PS white-point prototype is insufficient.
- Measure FPS and color response under dark/bright light steps on KV260; update internal evidence and state.

## Handoff Notes

- Deploy the five Python modules as a set; matching rectification bit/HWH and media graph remain prerequisites. `--binary` now explicitly selects the previous default behavior; `--color` is a compatibility alias for the new default. `--no-awb` isolates sensor AE from PS white-point correction.
