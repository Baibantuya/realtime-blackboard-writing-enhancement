# AI Session: 2026-09-27-007-imx219-complete-vivado-pipeline

- Date: 2026-09-27
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: Complete the IMX219 CSI-2 → demosaic → gamma/AE → PS DDR/framebuffer → HDMI Vivado system in the isolated test project.
- Status: Partial integration complete; system synthesis blocked; no bitstream.
- Report candidate: No
- Related commits: None; root is not a Git repository.
- Related files: `test_workspace/imx219_gamma_ae/`; local prior IMX219 reference sources under `test_workspace/imx219_reference_2026-09-24/`; KV260 rectifier BD.

## Context Read

Read required root AGENTS.md, AI policy, project state, decisions, index, and related sessions 005/006. Root Git status unavailable: workspace is not a repository. Discovered a previous IMX219 reference design source tree (2023.1) and a separate KV260 rectifier Vivado project; these are inspection sources only. Prior binary overlay produced a kernel Oops on the current image (D-043), so do not deploy that binary or DTBO.

## Task and Constraints

Integrate a complete CSI/Demosaic/AXIS gamma+AE/VDMA-to-PS output design. Use only verified board pin/clock data; retain provisional sensor mode values. Run Vivado 2022.2 validation, and generate bitstream only if the physical design passes DRC with real constraints. No board test requested.

## Contributions

- Adapted the inspected KV260 CSI reference block design to Vivado 2022.2 and the correct `xck26-sfvc784-2LV-c` K26 part. Added the source Tcl, board interface XDC and helper Tcl under the isolated project.
- Integrated a PL AXIS luma meter/AE status module on the demosaic output, a PS-readable AXI GPIO register at `0xA00C0000`, and a Python bridge that sends the desired exposure/analogue-gain through the Linux IMX219 V4L2 driver. This is the adopted I²C ownership plan; the standalone direct-PL-I²C sensor controller is not instantiated in the system BD.
- Kept AMD Gamma LUT, CSC/scaler and frame-buffer writer IP, with the frame writer connected to PS HP2/DDR. Added a candidate DTS and capture/HDMI/AE instructions. Old `.bin` and `.dtbo` files were not copied/deployed.
- Corrected stale workspace documentation that described the board target as XCZU5EV; the KV260 target is K26/XCK26.

## Decisions and Adoption

- Adopted integrated AE through PL statistics/controller → AXI GPIO → Linux V4L2 exposure/gain controls. Reason: the board camera uses a PCA9546 I²C mux and Linux sensor driver; this preserves a single bus master.
- AE defaults remain provisional: 24 MHz INCK, two lanes, link frequency 456 MHz, 1080p30/FLL 1763, 1600 exposure lines, target mean 112 DN, ±3 deadband, gain codes 0–232.
- AMD Gamma LUT remains the configurable gamma block. HDMI is PS-side PYNQ DisplayPort framebuffer output through the KV260 carrier route, not a PL HDMI transmitter.
- See D-047. This supersedes D-045's direct PL I²C ownership proposal for the integrated system.

## Commands and Tools

- Vivado 2022.2 `build_system.tcl`: created block design, generated outputs and ran `validate_bd_design`.
- Vivado 2022.2 `synth_ae_status.tcl`: standalone AE meter/controller synthesis.
- Vivado 2022.2 `run_synthesis.tcl`, `synth_all_sources.tcl`, and retries: system synthesis attempts; see logs below.
- Python AST parse of `software/run_ae_v4l2.py`.

## Validation and Evidence

- **Passed:** Vivado block-design validation in `build/system_generate_verified.log`; all AXI address segments include AXI GPIO at `0xA00C0000`. Generated top RTL shows `ae_status` connected to GPIO and the K26 part.
- **Passed:** Standalone synthesis of `axis_ae_status` with `axis_luma_meter` and `ae_controller`: 0 errors, 0 critical warnings, generic parallel-synthesis warning; see `build/ae_status_synth.log` and `build/ae_status_utilization.rpt`.
- **Passed:** Python parser syntax check for `software/run_ae_v4l2.py`.
- **Failed / unresolved:** Full system synthesis. Initial direct run needed BD-generated HDL; after `generate_target all`, top synthesis found missing `xlconstant_v1_1_7_xlconstant` and `sc_exit_v1_0_13_top` in the nested SmartConnect hierarchy. Adding the local constant HDL exposed the SmartConnect protected-source include/library dependency (`sc_util_v1_0_4_constants.vh` / package). System logs: `build/system_synth_after_gen.log`, `build/system_synth_xlconstant.log`, `build/system_synth_smartconnect.log`.
- **Not run:** system implementation, timing analysis, bitstream generation, DTS compilation, RTL simulation, hardware/board capture, sensor I²C probing and HDMI runtime.

## Errors and Corrections

- Original part ID in the old RTL-only run was XCZU5EV; changed the integrated project to KV260 K26 `xck26-sfvc784-2LV-c`.
- Adapted IP VLNVs to Vivado 2022.2 (`mipi_csi2_rx_subsystem:5.2`, `zynq_ultra_ps_e:3.4`).
- First AE GPIO base `0xA00A0000` overlapped the scaler's `0xA0080000–0xA00BFFFF` range; moved GPIO to `0xA00C0000` and BD validation passed.
- First BD validation lacked AE monitor clock/reset; tied both to the 200 MHz video clock/reset and validation passed.
- Vivado module-reference rejected the AE module as SystemVerilog top source; changed that single module file to `.v`, after which the module reference was accepted.
- Full synthesis remains blocked by missing/unenlisted nested IP HDL-library/checkpoint inputs; no result was labeled successful and no bitstream was forced.

## Files Changed

- `test_workspace/imx219_gamma_ae/README.md`
- `test_workspace/imx219_gamma_ae/rtl/axis_ae_status.v`
- `test_workspace/imx219_gamma_ae/vivado/build_system.tcl`
- `test_workspace/imx219_gamma_ae/vivado/design_1_bd_kv260.tcl`
- `test_workspace/imx219_gamma_ae/vivado/design_1_pin.xdc`
- `test_workspace/imx219_gamma_ae/vivado/add_fan_enable.tcl`
- `test_workspace/imx219_gamma_ae/vivado/*.tcl` build and validation scripts
- `test_workspace/imx219_gamma_ae/software/README.md`
- `test_workspace/imx219_gamma_ae/software/run_ae_v4l2.py`
- `test_workspace/imx219_gamma_ae/software/device_tree/imx219_camera_overlay.dts` (candidate only)
- `project_workspace/DECISIONS.md`, `project_workspace/PROJECT_STATE.md`, `project_workspace/ai/INDEX.md`

## Remaining Work

1. Resolve nested SmartConnect/other Vivado IP OOC/library integration so the complete BD synthesizes in Vivado 2022.2.
2. After successful synthesis, run implementation, timing and DRC; generate bitstream/HWH/XSA only if all checks pass.
3. Regenerate/validate device tree against final XSA and current KV260 kernel; confirm actual IMX219 V4L2 subdevice controls and mode parameters before use.
4. Provide staged board plan: sensor bind/I²C → media graph → CSI packets/RAW10/Bayer phase → one DDR RGB frame → HDMI continuous display → AE light-step response. Board validation was not performed.

## Handoff Notes

Do not use or load the failed prebuilt CSI overlay; compatible PL image, bitstream and kernel device tree must be rebuilt together. Current system BD is validated, but its full synthesis is blocked by IP-library generation and it has no bitstream. D-047 supersedes the earlier direct-PL-I²C control approach for the integrated system.
