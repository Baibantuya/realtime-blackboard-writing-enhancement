# AI Session: 2026-09-27-004-imx219-fpga-github-examples

- Date: 2026-09-27
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: Locate public IMX219 FPGA examples covering sensor configuration, CSI reception, demosaic, and exposure adjustment.
- Status: Completed source review; no project implementation
- Report candidate: No
- Related commits: None; workspace is not a Git repository.
- Related files: GitHub repositories cited below.

## Context Read

Continued from session 003 after required root policy, project state, decisions, index, and recent camera sessions were read. Current Git status was checked in session 003 and no repository was found.

## Task and Constraints

Research and compare public examples; no changes to formal source or board state.

## Contributions

- Located `gtaylormb/ultra96v2_imx219_to_displayport`, which explicitly targets KV260 and includes 1080p30, IMX219 I2C table in `software/src/imx219.c`, Xilinx CSI RX/demosaic/gamma/VDMA and demosaic register setup. Exposure uses a fixed analogue gain write; no automatic exposure loop found in inspected code.
- Located `ikwzm/RasPi-Camera-V2-KV260`, a Linux/V4L2 KV260 pipeline with IMX219 RAW10, CSI RX, demosaic, gamma, VPSS, frame-buffer writer. Its prebuilt overlay already failed on this project's installed image (D-043); do not retry unchanged.
- Located Enclustra ZynqMP MIPI example with IMX219, demosaic/gamma, CPU capture, and documented manual V4L2 exposure/analogue/digital gain controls.
- Located CircuitValley legacy and newer Lattice FPGA camera projects with IMX219 and FPGA ISP. Legacy README explicitly says manual exposure only. Newer project includes portable ISP concepts but not a verified KV260 automatic exposure implementation.
- Linux Xilinx IMX219 driver supplies authoritative register mapping and mode/control implementation for the relevant software stack.

## Decisions and Adoption

Recommendation only: prioritize Greg Taylor KV260 design for baremetal hardware/I2C/AXIS structure, Linux driver and Enclustra for exposure controls, ikwzm as Linux media-graph reference, and implement the missing AE feedback loop separately. No owner adoption yet.

## Commands and Tools

Web search and read-only inspection of public GitHub repository READMEs, source files, and Linux driver.

## Validation and Evidence

Public source and documentation review only. Build, simulation, board capture, and auto-exposure verification: 未执行.

## Errors and Corrections

Avoid interpreting presence of exposure controls as an automatic exposure algorithm. Avoid applying incompatible third-party KV260 binary/DTBO after recorded kernel Oops.

## Files Changed

This internal session record, index, and project state only.

## Remaining Work

Inspect full source/BD versions and licensing before reuse; create one compatible KV260 overlay; validate I2C ID, RAW10 frame, Bayer phase, and exposure changes on board; add and test AE loop.

## Handoff Notes

Key links: https://github.com/gtaylormb/ultra96v2_imx219_to_displayport ; https://github.com/ikwzm/RasPi-Camera-V2-KV260 ; https://github.com/enclustra/ZynqMpVideoAppNote/tree/master/example4-mipi ; https://github.com/circuitvalley/mipi_csi_receiver_FPGA ; https://github.com/circuitvalley/USB_C_Industrial_Camera_FPGA_USB3 ; https://github.com/Xilinx/linux-xlnx/blob/master/drivers/media/i2c/imx219.c .
