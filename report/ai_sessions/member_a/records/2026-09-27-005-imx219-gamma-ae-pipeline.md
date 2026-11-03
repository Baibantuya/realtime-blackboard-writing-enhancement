# AI Session: 2026-09-27-005-imx219-gamma-ae-pipeline

- Date: 2026-09-27
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: Create an isolated KV260-oriented IMX219 CSI-2 to gamma/auto-exposure and PS/HDMI pipeline starter project under test_workspace.
- Status: Completed as an RTL/integration scaffold; implementation unverified
- Report candidate: No
- Related commits: None; workspace root is not a Git repository.
- Related files: `test_workspace/imx219_gamma_ae/`; tutorial `21_ov5645_mipi_hdmi`; root `IMX219_datasheet.pdf`.

## Context Read

Read AGENTS.md, `project_workspace/ai/AI_DEVELOPMENT_POLICY.md`, PROJECT_STATE.md, DECISIONS.md, INDEX.md, and the two most recent related session records (2026-09-27-003 and -004). Root `git status` failed with “not a git repository”. Tutorial source inventory and IMX219 datasheet presence were confirmed. The root `.Xil` folder is unrelated and untouched.

## Task and Constraints

Build a new isolated project in `test_workspace/imx219_gamma_ae`: IMX219 CSI-2 RAW10 → gamma, PL exposure feedback via sensor configuration registers, AXI-stream/VDMA to PS, PS HDMI output. Do not board test. Provide a staged verification plan. Mark uncertain sensor settings as provisional.

## Contributions

- Added self-contained SystemVerilog modules for an open-drain IMX219 I²C write FSM, reset/init/runtime sensor control, AXI-stream RGB gamma mapping, frame luma meter, frame-rate negative-feedback exposure controller, and a combined RGB stream core.
- Wrote a Chinese README with topology, all module contracts, upstream Linux 2-lane/1080p30 reference choices, explicit board-dependent assumptions, Vivado integration steps, PS V4L2→PYNQ display invocation, and a staged verification plan.
- Added Vivado project creation Tcl (source project only; no BD/IP/bitstream generation) and a PS V4L2 RGB capture/DisplayPort script copied from the existing IMX219 display reference.
- The CSI receiver and demosaic remain AMD Vivado IP blocks to be configured for the actual device/tool version; AXI VDMA, Linux V4L2 device tree/driver, and board constraints are integration work documented in README.

## Decisions and Adoption

D-045 records the isolated architecture: CSI RX → demosaic → custom PL RGB gamma/AE → sensor I²C feedback, with VDMA DDR buffering to PS V4L2 and HDMI via PYNQ DisplayPort. This is an experimental scaffold and does not change D-042/D-043 project-level CSI readiness and incompatible overlay restrictions. Sensor initialization values reference upstream Linux IMX219 common/2-lane values, FLL=1763 for the 1080p30 mode, and datasheet register definitions; exact module and board match remains unknown.

## Commands and Tools

PowerShell file/source inspection and project authoring. Read the local IMX219 PDF register definitions; browsed the primary upstream Linux IMX219 driver for mode/PLL reference: https://github.com/torvalds/linux/blob/master/drivers/media/i2c/imx219.c . No external communication or board operation.

## Validation and Evidence

Source review only. No RTL lint/elaboration, simulation, Vivado project creation, synthesis, implementation, timing, VDMA/V4L2 integration, performance measurement, or board capture was executed. Verification steps and expected checks are in project README.

## Errors and Corrections

- Initially used a 1125-line frame-length placeholder and a short sensor init list; reviewed upstream Linux mode values and replaced these with the 1080p30 FLL=1763 and 2-lane PLL/common reference values. The module INCK and wiring remain to confirm.
- Manual interface review caught a stale AXI luma meter port connection and corrected it.
- Manual I²C transaction review caught an ACK counter that would STOP before sending the sensor data byte; corrected the transaction to send slave address `0x20`, register high, register low, and data, with ACK after all four bytes. This is not test evidence; I²C simulation is explicitly a next validation step.
- Removed generated plaintext extraction of the local datasheet from the project; the source PDF remains at workspace root.

## Files Changed

- `test_workspace/imx219_gamma_ae/README.md`
- `test_workspace/imx219_gamma_ae/rtl/ae_controller.sv`
- `test_workspace/imx219_gamma_ae/rtl/axis_gamma_rgb24.sv`
- `test_workspace/imx219_gamma_ae/rtl/axis_luma_meter.sv`
- `test_workspace/imx219_gamma_ae/rtl/imx219_i2c_write.sv`
- `test_workspace/imx219_gamma_ae/rtl/imx219_sensor_ctrl.sv`
- `test_workspace/imx219_gamma_ae/rtl/imx219_video_core.sv`
- `test_workspace/imx219_gamma_ae/software/display_v4l2_dp.py`
- `test_workspace/imx219_gamma_ae/vivado/create_project.tcl`
- `project_workspace/DECISIONS.md` (D-045)
- `project_workspace/PROJECT_STATE.md`
- `project_workspace/ai/INDEX.md`
- This session record.

## Remaining Work

1. Confirm exact module/board wiring, INCK, XCLR/I²C, CSI lane pins, board XDC and Bayer phase.
2. Create/verify CSI RX + demosaic + VDMA block design for installed Vivado version; connect compatible Linux DT/V4L2 frame capture.
3. Run planned simulation, synthesis/timing and staged hardware tests; adjust AE and display format/stride from evidence.

## Handoff Notes

All values called out as provisional are software reference defaults, not board-verified configuration. Avoid using tutorial OV5645 I²C values. Do not load an overlay until it matches the installed KV260 Linux/firmware stack (D-043). `README.md` contains the complete validation plan; all such validation is currently unexecuted.
