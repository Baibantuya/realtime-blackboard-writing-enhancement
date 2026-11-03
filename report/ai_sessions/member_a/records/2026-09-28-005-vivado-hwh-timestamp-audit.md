# AI Session: 2026-09-28-005-vivado-hwh-timestamp-audit

- Date: 2026-09-28
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: Explain whether the generated `design_1.hwh` predates the afternoon Vivado bitstream build and determine whether it describes the same integrated BD.
- Status: Completed; the `.hwh` is from the same BD build as the `.bit`, though emitted earlier.
- Report candidate: No
- Related commits: None
- Related files: `test_workspace/imx219_team_package_20260928/imx219_rgb_rectify_20260928/build/`

## Context Read

Read `AGENTS.md`, `project_workspace/ai/AI_DEVELOPMENT_POLICY.md`, `project_workspace/PROJECT_STATE.md`, `project_workspace/DECISIONS.md`, `project_workspace/ai/INDEX.md`, the relevant prior Vivado build session `2026-09-27-009-imx219-bitstream-test-handoff.md`, and the recent Git setup record. Workspace root is not a Git repository; `kv260-whiteboard-enhance/` is a new empty Git repository with untracked project files. The isolated test package is not a Git repository.

## Task and Constraints

Determine the provenance and consistency of the `.hwh` relative to the final `.bit`; do not represent mismatched timestamps alone as proof of a stale design. No source or architecture changes are in scope.

## Contributions

1. Correlated the `.hwh`, source BD, bitstream, build orchestration log, and final synth/implementation logs.
2. Confirmed the timestamp gap reflects Vivado's build stages: `generate_target all` exported the BD handoff before the long implementation/bitgen run.
3. Recorded that the routed timing gate failed and prevented XSA export; this does not mean the `.hwh` predates a different design revision.

## Decisions and Adoption

No design decision.

## Commands and Tools

 - PowerShell `Get-Item` for BD/HWH/bit/timing timestamps and sizes.
 - `rg` against `combined_build.log`, synth run log, implementation run log, and HWH XML for target generation, bitgen completion, and `board_rectify_rgb_0` presence.
 - Read-only Git status: `E:/code/fpga-competition` is not a Git repository; `kv260-whiteboard-enhance/` is a new repository with expected untracked files; isolated test package is not a Git repository.

## Validation and Evidence

- `build/system/imx219_system.srcs/sources_1/bd/design_1/design_1.bd`: 143,620 bytes, 2026-09-28 16:22:40.
- `build/system/imx219_system.gen/sources_1/bd/design_1/hw_handoff/design_1.hwh`: 717,491 bytes, 2026-09-28 16:23:51; SHA-256 `38D38F78AE64C5C4E234AB3FA6C3E967D67A923806172CA1F12CF420DFC35270`. HWH XML identifies KV260 K26 and contains `/board_rectify_rgb_0` (`whiteboard.org:hls:board_rectify_rgb:1.0`).
- `combined_build.log` shows `generate_target all` followed by export of `design_1.hwh`; later it records `synth_1 finished` at 16:51:06 and `impl_1 finished` at 17:31:40. The implementation log links `design_1_board_rectify_rgb_0_0.dcp` as `board_rectify_rgb_0` and reports `Bitgen Completed Successfully`.
- `design_1_wrapper.bit`: 7,797,812 bytes, 2026-09-28 17:31:22; SHA-256 `A4E40F5EA265A44F50542303D6899CF15096D3F17130F641873D436E0CCB3FCD`.
- Routed summary: WNS -5.589 ns, TNS -66.917 ns, 191 setup endpoints failing; WHS +0.009 ns, no hold endpoints failing. DRC: 0 errors, 441 warnings, 128 advisories. No board test was run.
- Conclusion: HWH timestamp is earlier because BD handoff generation precedes synthesis and implementation. Its topology matches the BD used by synthesis/implementation. XSA export was skipped by the build script's negative-slack guard.

## Errors and Corrections

- Initial timestamp inventory used the wrong generated BD path (`...imx219_system.gen/.../design_1.bd`), which does not exist. Corrected to `...imx219_system.srcs/sources_1/bd/design_1/design_1.bd`; no project files were changed by the failed read.

## Files Changed

- `project_workspace/PROJECT_STATE.md` — recorded the HWH/bitstream provenance and timing caveat.
- `project_workspace/ai/INDEX.md` — indexed this session record.
- This internal session record.

## Remaining Work

- Timing closure remains open (WNS -5.589 ns); current bitstream is not timing-accepted or board-validated.
- XSA was not exported because the build script refused the negative-slack design.

## Handoff Notes

Do not touch the HWH timestamp or copy it as if it had been emitted at bitgen time. Vivado generated it from the integrated block design in `generate_target all`; the bitstream was written after implementation. The HWH resides under the generated BD `hw_handoff/` directory rather than beside the `.bit`.

## Hardware Follow-up

- User report: KV260 became stuck during board use; restarting did not recover it. This symptom has not been independently observed or diagnosed.
- The routed timing failure (WNS -5.589 ns) makes the bitstream a plausible contributor to malfunction, not a proven cause. A reboot can reload the same bitstream if the boot flow loads it from QSPI/eMMC/SD; if it was only loaded to PL over JTAG, a true full power removal should clear that volatile PL configuration.
- Suggested isolation: remove power fully and disconnect nonessential peripherals; then boot known-good media/image if the normal boot path reloads the suspect image. Capture boot method, status LEDs and UART log before changing flash contents. Do not use this bitstream as a known-good baseline.
