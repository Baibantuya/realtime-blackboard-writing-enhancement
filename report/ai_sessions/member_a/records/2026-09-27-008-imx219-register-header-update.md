# AI Session: 2026-09-27-008-imx219-register-header-update

- Date: 2026-09-27
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: Read the supplied IMX219 1080p30 register header and align the project's register defaults with it.
- Status: Standalone RTL sequence and AE startup exposure updated; integrated Linux sensor mode table and hardware behavior remain unverified.
- Report candidate: No
- Related commits: None; root is not a Git repository.
- Related files: `test_workspace/imx219_gamma_ae/imx219_1080p30_regs(1).h`, `test_workspace/imx219_gamma_ae/rtl/imx219_sensor_ctrl.sv`, `test_workspace/imx219_gamma_ae/rtl/ae_controller.sv`, `test_workspace/imx219_gamma_ae/README.md`, `project_workspace/DECISIONS.md`, `project_workspace/PROJECT_STATE.md`

## Context Read

Read the root instructions, AI development policy, project state, decision log, internal index, recent IMX219 sessions, and the supplied H file. Confirmed the integrated block design uses Linux's IMX219 V4L2 driver as the sole sensor I²C master; `imx219_sensor_ctrl.sv` is the standalone direct-I²C prototype and is not instantiated into that integrated BD.

## Task and Constraints

Use the supplied `imx219_1080p30_regs(1).h` values and order in the standalone sensor sequencer. Keep the optional live HDMI gain reference distinct from the default runtime table. Do not claim synthesis, camera readback, or board validation without running it.

## Contributions

- Replaced the standalone initialization sequence with the header's mode, RAW10 and runtime settings, preserving order; appended stream-on after the header sequence because its arrays stop before stream start.
- Changed the standalone sequencer's initial exposure and the shared PL AE controller reset value from 1600 to the header's 600 lines. FLL remains 1763 lines; analogue gain starts at zero; standalone digital gain starts at `0x0100`.
- Updated README to identify the header as a provisional register source and explain the integrated Linux-driver boundary. The optional `reference_live_hdmi_gain_regs` values are not applied at startup.

## Decisions and Adoption

- Adopted the supplied header as the standalone RTL table baseline (D-048).
- Did not change the kernel IMX219 driver's mode table or claim the integrated CSI system now initializes with the header's mode. That requires a separate Linux driver/device-tree configuration, and the driver remains the bus owner under D-047.
- `0x012A/0x012B=0x1800`, module input clock, lane setup, and link frequency remain provisional until checked against the actual module and CSI receiver setup.

## Commands and Tools

- Read the H file, RTL, README, candidate DTS, project state, decisions, index, and prior pipeline session.
- Used `apply_patch` to update the RTL, README, and internal records.
- `git status --short` could not run because `E:\code\fpga-competition` is not a Git repository.

## Validation and Evidence

- Static source review only. No Vivado build, simulation, register readback, or board test was executed.
- Source values in the sequencer were transcribed from the user-specified H file; the H file itself was not modified.

## Errors and Corrections

- The previous standalone table used a different crop window and set register `0x012A` to `0x0C`; it also started exposure at 1600 lines. These were replaced with the supplied table's values and 600-line runtime default.
- The previous 1600-line default remains in historical session D-047 as the state at that time; D-048 supersedes it for the current standalone/AE startup value.

## Files Changed

- `test_workspace/imx219_gamma_ae/rtl/imx219_sensor_ctrl.sv`
- `test_workspace/imx219_gamma_ae/rtl/ae_controller.sv`
- `test_workspace/imx219_gamma_ae/README.md`
- `project_workspace/DECISIONS.md`
- `project_workspace/PROJECT_STATE.md`
- `project_workspace/ai/INDEX.md`
- `project_workspace/ai/sessions/2026-09-27-008-imx219-register-header-update.md`

## Remaining Work

- Confirm the input clock, CSI lane/rate configuration, Bayer phase, and register compatibility for the exact IMX219 module.
- If the integrated system must use this exact table, configure/patch the Linux driver path rather than enabling the standalone PL I²C sequencer alongside it.
- Run Vivado synthesis and a controlled camera register/readback and capture check when requested and available.

## Handoff Notes

The source header's runtime defaults specify 600 integration lines, FLL 1763, analogue gain code 0, and digital gain `0x0100`. Its separate live HDMI example uses different gain values and was intentionally left unapplied. No validation result should be inferred from this source edit.
