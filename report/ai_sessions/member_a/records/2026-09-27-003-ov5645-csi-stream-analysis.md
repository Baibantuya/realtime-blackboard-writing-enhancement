# AI Session: 2026-09-27-003-ov5645-csi-stream-analysis

- Date: 2026-09-27
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: Analyze the supplied OV5645 CSI example and map its register, stream, demosaic, and PS output paths to the IMX219 KV260 project.
- Status: Completed source-level analysis; hardware unverified
- Report candidate: No
- Related commits: None; workspace is not a Git repository.
- Related files: tutorial 21_ov5645_mipi_hdmi; current KV260 rectifier.

## Context Read

Read root AGENTS.md, AI policy, project state, decisions, index, recent IMX219 and rectifier sessions. `git status` reports no Git repository.

## Task and Constraints

Analysis and design guidance only; do not modify tutorial or formal project code.

## Contributions

- Traced OV5645 I2C sequencer, two-lane RAW10 CSI-2 RX IP, AXI4-Stream Video demosaic/gamma chain, and custom DDR4/HDMI backend.
- Confirmed misleading `rgb565` config filename: file itself says RAW10 1920x1080, CSI IP is configured RAW10, and demosaic is 10-bit.
- Identified migration hazards: OV5645 register table is not IMX219-compatible; example stream2native bridge has an 8-word counter without frame reset; CSI controller transaction input is tied low; video stream is converted to standalone DDR4/HDMI, not PS; existing rectifier uses AXI memory masters and cannot be directly spliced into streaming path.
- Recommended KV260 combined overlay with IMX219 control, CSI RX, RAW processing, frame buffering around the existing rectifier or redesign of that rectifier, then AXI4-Stream Video to frame-buffer write/PS DDR. Distinguish stream entering PL from PS consuming frames in DDR.

## Decisions and Adoption

Analysis and recommended architecture only; no new owner decision adopted. Do not copy tutorial unchanged.

## Commands and Tools

PowerShell `Get-Content`/`rg` source inspection; official AMD AXI4-Stream Video and demosaic protocol documentation; Linux IMX219 driver lookup. Git status unavailable: no Git repository.

## Validation and Evidence

Source inspection only; simulation, synthesis, and board capture: 未执行.

## Errors and Corrections

Initially searched a nonexistent tutorial `bd` source path; located generated CSI RX block design and IP XCI instead. Avoided treating filename `rgb565` as actual output format.

## Files Changed

This session record, internal index and project state only. No tutorial or formal project code changed.

## Remaining Work

Verify IMX219 mode table and Bayer order against actual module, integrate camera-compatible PL/device-tree with installed KV260 kernel, simulate AXI4-Stream Video, capture one real frame, and choose frame-based rectifier adaptation or rewrite based on measured needs.

## Handoff Notes

The existing rectifier's `m_axi` source/destination and random DDR access require a frame boundary; a mere AXIS wrapper is insufficient for its current perspective warp. Current board CSI stack is absent and prior third-party overlay caused kernel Oops (D-043).
