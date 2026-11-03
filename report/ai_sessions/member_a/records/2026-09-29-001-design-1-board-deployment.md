# AI Session: 2026-09-29-001-design-1-board-deployment

- Date: 2026-09-29
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: Deploy `test_workspace/design_1_full_deployment_20260928/design_1_full_deployment_20260928` to the KV260 at `[private_ip]` and verify what actually reached/ran on the board.
- Status: Candidate `.bit/.hwh` is loaded and the continuous color pipeline is running on the KV260 as PID 14385. The five-frame headless smoke exited 0; display output is not visually verified and detector currently reports zero corners.
- Report candidate: No
- Related commits: None
- Related files: `test_workspace/design_1_full_deployment_20260928/design_1_full_deployment_20260928/`

## Context Read

- Read root `AGENTS.md`, `project_workspace/ai/AI_DEVELOPMENT_POLICY.md`, `project_workspace/PROJECT_STATE.md`, `project_workspace/DECISIONS.md`, and `project_workspace/ai/INDEX.md` in the required order.
- Read latest relevant session `2026-09-28-005-vivado-hwh-timestamp-audit.md` and reviewed the deployment package README/scripts. No earlier session specifically records deployment of this package.
- Root Git status: new empty `main` repository with untracked project/test content; no existing tracked changes to overwrite.

## Task and Constraints

- User explicitly requested board deployment and supplied SSH credentials. Do not record the password or any secret.
- Preserve the distinction between package copy, PL/overlay activation, and successful hardware smoke test.
- Existing project evidence says the candidate bitstream has negative routed slack and the user previously reported a board hang. Treat a deployment attempt and any runtime result as evidence, not as proof that the hardware is timing-safe or that the earlier hang had the same cause.
- Follow package preflight and rollback design where possible; do not claim missing or unexecuted verification passed.

## Contributions

1. Reviewed the deployment contract and verified the local `.bit`, `.hwh`, and `.dtbo` are present. The `.bit` hash is `A4E40F5EA265A44F50542303D6899CF15096D3F17130F641873D436E0CCB3FCD`; the HWH hash is `38D38F78AE64C5C4E234AB3FA6C3E967D67A923806172CA1F12CF420DFC35270`.
2. Copied the complete package to `/home/ubuntu/design_1_full_deployment_20260928/` and installed candidate firmware under `/lib/firmware/xilinx/imx219-rgb-rectify/`.
3. Corrected the deployment script's source/destination self-copy failure when run from the README-prescribed directory.
4. Loaded the candidate bitstream and RAW8 device-tree overlay and attempted its five-frame smoke test. The PYNQ entry failed during `MMIO` initialization with `RuntimeError: No Devices Found`; `xmutil listapps` had no active slot and this package has no XRT app/xclbin for registration.
5. Executed the packaged Gamma recovery. Its first attempt failed because `Full` overlay remained applied. Removed only that live-tree overlay with `fpgautil -R -n Full`, reran recovery, and verified `imx219-test` loaded, five 1920x1080 RGB frames captured at 6,220,800 bytes each, and the existing live HDMI process started.
6. Reproduced the PYNQ discovery error on the recovered Gamma app with `XILINX_XRT` unset (`Device.devices == []`), then set `XILINX_XRT=/usr` and confirmed PYNQ discovers an `EmbeddedDevice`. The deployment script was missing this environment variable after sudo. Added the export after privilege escalation.
7. Retried with `XILINX_XRT=/usr`: device discovery and MMIO succeeded, then `pynq.allocate()` failed with `Overlay is not downloaded`, confirming that raw `fpgautil` programming does not register PYNQ overlay metadata.
8. Switched the package loader to PYNQ `Overlay(.bit, dtbo=...)` with a same-basename `.bit/.hwh`. PYNQ then failed before bitstream programming while constructing its synthetic metadata xclbin: board `xclbinutil` segfaulted and left the temporary `t.xclbin` absent. Added an optional same-basename metadata-xclbin input and a preflight-only parser step so this failure is caught before unloading the current app. The candidate was not loaded during this attempt; Gamma recovery passed again.

## Decisions and Adoption

No architecture decision. The deployment flow now uses the PYNQ venv's bundled `xclbinutil`, PYNQ metadata registration from a persistent alternate-basename `.bit/.hwh`, and `fpgautil` for bit+DTBO. No external Vitis xclbin is needed for this path. Candidate acceptance remains pending because the five-frame smoke pass was not observed; the bitstream also has known negative timing slack.

## Commands and Tools

- Read-only PowerShell inventory and SHA-256 checks for the package; read root project context and prior relevant hardware record.
- OpenSSH `ssh.exe` / `scp.exe` to copy the package, inspect the KV260 and run the deployment/recovery scripts. Credentials were not recorded.
- `Test-NetConnection`: board TCP/22 reachable; TCP/445 not reachable.
- Local `bash -n` was attempted but WSL failed to start with `E_ACCESSDENIED`; remote Bash executed the deployment and recovery scripts.
- On-board read-only checks: Linux `5.15.0-1027-xilinx-zynqmp`; 44 GB free; PYNQ Python 3.10; inspect `xmutil listapps`, FPGA manager state, overlay status, device nodes, and kernel log.
- On-board read-only PYNQ comparison: with `env -u XILINX_XRT`, `Device.devices == []` and `Device.active_device` raises; with `XILINX_XRT=/usr`, `Device.devices` contains `EmbeddedDevice` and `Device.active_device` succeeds.
- On-board PYNQ 3.0.1 source inspection: `Overlay` requires matching `.bit/.hwh`, consumes an optional same-basename `.xclbin`, and `EmbeddedDevice` synthesizes a metadata-only xclbin from the HWH memory topology when none exists. Its helper invokes `xclbinutil` with `EMBEDDED_METADATA` and `MEM_TOPOLOGY` sections.
- On-board `/usr/bin/xclbinutil --version` segfaulted in `/usr/bin/unwrapped/xclbinutil`; PYNQ's `Overlay(..., download=False)` failed during metadata construction before programming with missing temporary `/tmp/.../t.xclbin`.
- Local host tool inventory found Vivado 2022.2 but no `xclbinutil`, `v++`, or Vitis executable; no XSA exists for this candidate build, so no compatible xclbin was generated in this session.
- The final deployment script check-only run repeated that parser failure at step 2, before step 3 could stop the Gamma preview or unload `imx219-test`. Final read-only check showed `imx219-test` still active in slot 0, FPGA manager `operating`, baseline overlays applied, preview process PID 8192 alive, and candidate files only staged.
- AMD fpgautil documentation was consulted to confirm `fpgautil -R -n Full` removes the matching live-tree overlay before reconfiguration.

## Validation and Evidence

- Board SSH login and package copy succeeded. Remote SHA-256 values matched the local bit/HWH/DTBO values.
- Candidate deploy steps 1-6 completed: HWH/firmware structural preflight passed; `fpgautil` reported the bitstream loaded successfully; RAW8 media format setup reported RGB3 1920x1080 and VTS/vertical blanking 1648.
- Candidate step 7 failed before capturing any frame: PYNQ warned no XRT devices were found, then `pynq.MMIO` raised `RuntimeError: No Devices Found`. At that point `xmutil listapps` showed both known apps at active slot `-1`; the board had no `/dev/xclmgmt*`, while `zocl` and `/dev/dri/renderD128` existed. The package contains no XRT app/xclbin registration artifact.
- On the recovered Gamma app, PYNQ device discovery fails when `XILINX_XRT` is unset and succeeds with `/usr`. The second candidate attempt with this environment fix passed device discovery and MMIO, then `allocate()` failed because no PYNQ Overlay was registered.
- The PYNQ Overlay loader then reached HWH parsing but failed because target `xclbinutil` segfaults while generating its synthetic metadata xclbin. The final check-only deployment attempt reproduced this before stopping Gamma. No candidate frame was processed in any attempt.
- First recovery attempt failed to load `imx219-test` because the `Full` overlay still occupied the full FPGA region. Kernel log stated `Region already has overlay applied` and the region overlay create failed with `-22`.
- Recovery after `sudo fpgautil -R -n Full` passed: `imx219-test` loaded in slot 0; FPGA manager state `operating`; `imx219-test_image_1` and baseline `pynq` overlays applied; five camera frames captured, each 1920x1080 RGB / 6,220,800 bytes; live HDMI process PID 5718 started. Visual DP/HDMI output was not inspected.
- Candidate firmware remains staged under `/lib/firmware/xilinx/imx219-rgb-rectify/`; final remote hashes match local hashes, but candidate bit/overlay are not active.
- Existing build evidence still reports WNS -5.589 ns and TNS -66.917 ns; this deployment attempt does not change that result or establish timing safety.

## Errors and Corrections

- First SSH launch used outer `sudo -A` before the script exported `SUDO_ASKPASS`; sudo exited before changing hardware. Corrected by invoking the package script directly.
- The documented package location equals its internal `WORK` path, so `cp -a software/. WORK/software/` attempted a self-copy and exited after installing candidate files but before changing the running app. Added a guard to skip that copy when `$ROOT == $WORK`; transferred the corrected script.
- Candidate bit/DTBO loaded but smoke could not initialize PYNQ because no XRT device/app was active. No candidate frame was processed.
- First Gamma rollback did not remove the `Full` overlay and `xmutil loadapp` failed. Consulted AMD fpgautil usage, removed the named overlay, and reran recovery successfully.
- Local shell syntax check was unavailable because the WSL service returned `E_ACCESSDENIED`; board Bash execution verified the corrected script parsed and ran through its steps.
- Initial interpretation that the candidate required an xclbin was too strong. Later on-board comparison showed PYNQ discovery depends on `XILINX_XRT=/usr` in this runtime. Corrected the package README and deployment script; candidate-specific XRT/MMIO/DMA operation still needs a retest.
- The XRT environment fix alone was insufficient: PYNQ `allocate()` also needs downloaded overlay metadata. Updated deployment to use `Overlay`; the board's xclbinutil segfault revealed the next blocker. The optional package artifact must be a compatible PYNQ/XRT metadata xclbin matching the bit/HWH, not an arbitrary renamed file.
- PYNQ `Overlay` construction calls the board `xclbinutil`; its wrapper masked the child segfault as exit 0, so PYNQ reported the missing temp file. Added a preflight-only metadata parse before any app stop and optional same-basename xclbin staging so failure leaves the known Gamma app active.

## Files Changed

- `test_workspace/design_1_full_deployment_20260928/design_1_full_deployment_20260928/deploy_new_design.sh` — skip the redundant software copy, set `XILINX_XRT=/usr`, stage optional xclbin, and preflight PYNQ metadata before stopping the app.
- `test_workspace/design_1_full_deployment_20260928/design_1_full_deployment_20260928/software/load_pynq_overlay.py` — load the PYNQ overlay and optionally check metadata without programming.
- `test_workspace/design_1_full_deployment_20260928/design_1_full_deployment_20260928/software/board_preflight.py` — require the same-basename `.bit` file.
- `test_workspace/design_1_full_deployment_20260928/design_1_full_deployment_20260928/README.md` — record current PYNQ/XRT findings, timing caveat, and rollback sequence.
- Board `/home/ubuntu/design_1_full_deployment_20260928/` — staged deployment package; corrected script and README synchronized.
- Board `/lib/firmware/xilinx/imx219-rgb-rectify/` — candidate bit/HWH/DTBO and generated SHA256SUMS remain staged but inactive.
- Board runtime — restored known `imx219-test` app in slot 0; captured five frames and restarted the existing live preview process.
- `project_workspace/ai/sessions/2026-09-29-001-design-1-board-deployment.md` — this completed record.
- `project_workspace/ai/INDEX.md` — add this session to the index.
- `project_workspace/PROJECT_STATE.md` — record the deployment attempt, recovery, evidence, and blockers.

## Remaining Work

- Candidate run is active. Remaining checks are visible DP output and real-scene detection; the current scene yields zero corners and the pipeline runs at about 1.28 fps. Timing closure remains a separate design concern.
- The candidate bitstream has known negative timing slack; resolve timing before treating any retry as an accepted design. Any limited smoke attempt is not timing closure or performance proof.
- Add a cleanup/recovery path to the deployment procedure so failure after applying the full overlay removes `Full` before calling `xmutil loadapp`.
- After the candidate retest, verify frame processing plus visible output. Candidate deployment has not passed.

## Handoff Notes

Do not record user-supplied credentials. `/usr/bin/xclbinutil` still segfaults, but `/usr/local/share/pynq-venv/bin/xclbinutil` works and is selected by the updated deployment `PATH`; a separate Vitis `.xclbin` is not required for PYNQ's HWH metadata path. PYNQ configfs DTBO insertion failed, so the loader registers `.bit/.hwh` from a persistent alternate-basename copy and applies bit+DTBO via `fpgautil`. After correcting the order to apply via `fpgautil` first and generate PYNQ metadata cache afterward, the five-frame headless test exited 0 and continuous color processing started. The current board runs the candidate; see the latest follow-up below.

## Follow-up: Board Runtime Path Repair

- Root cause correction: the PYNQ venv contains its own working `xclbinutil`; sudo's default `PATH` selected the older system XRT utility instead. Added `/usr/local/share/pynq-venv/bin` to the deployment script's root `PATH` while keeping `XILINX_XRT=/usr` for device discovery.
- Confirmed PYNQ `Overlay(..., download=False)` now parses the same `.bit/.hwh` and prints `PYNQ_OVERLAY_METADATA_READY` without a Vitis `.xclbin`.
- PYNQ's auto-detected same-basename DTBO failed via this board's configfs readback. The loader now uses a persistent `pynq_runtime/overlay.bit` + `.hwh` copy with no `.dtbo` sidecar, then invokes `fpgautil -b ... -o ...` for the candidate bit and DTBO. Persistence is required because PYNQ reopens the bit file when it allocates buffers.
- Candidate PYNQ load, CMA allocation (`0x28c2000`), and `fpgautil` bit/DTBO load succeeded. `run_pipeline.py` printed frame 1 (status 1, downward hint, zero corners, 3.08 fps, rectify 142.6 ms); this run did not yield the deployment success marker, so five-frame completion is unverified.
- During troubleshooting, recovery restored `imx219-test` and its five-frame capture passed. After the owner clarified the required final state, the candidate was reloaded and left running as PID `14385`.
- Modified local package files: `deploy_new_design.sh`, `software/load_pynq_overlay.py`, and `README.md`. No password was recorded. Candidate timing remains WNS -5.589 ns / TNS -66.917 ns; no timing or long-run claim is made.
- Remaining: verify visible DP/HDMI output and detection after positioning a board in the camera view; the pipeline is currently active and timing closure remains failed.

## Latest: Explicit Candidate Run

- The project owner clarified that the candidate must remain deployed and running. Reloaded the candidate `.bit/.hwh` and DTBO with the corrected PYNQ/XRT flow; updated the helper order so `fpgautil` programs the bit+DTBO first, followed by `Overlay(download=False, gen_cache=True)` to persist PYNQ metadata for the separate processing process.
- The five-frame headless `run_pipeline.py --frames 5 --no-display --no-ae --no-awb --binary` exited with code 0.
- Started continuous color pipeline with DisplayPort enabled as PID `14385`; board log is `/home/ubuntu/design_1_full_deployment_20260928/candidate_live.log`; PID file is `/home/ubuntu/design_1_full_deployment_20260928/candidate_live.pid`.
- Read-only follow-up showed process `14385` still running and FPGA manager state `operating`. Log reached frame 100 at approximately 1.28 fps; `rectify_ms` about 137 ms. Current image produced zero corners and a downward/unreliable-direction hint. DisplayPort output was not visually checked.
- Board is left with the candidate active and processing. Existing timing report remains WNS -5.589 ns / TNS -66.917 ns; no claim of timing closure or detection correctness.

## Follow-up: Live Exposure, Format, and Display Geometry

- Objective: answer whether the current candidate run uses IMX219 auto exposure, whether its IP input is exposed and 1080p, and why the displayed image has black bars. Participants: project owner and Codex. This was read-only inspection; no code or board setting was changed.
- Process `14385` remained active with `run_pipeline.py --color`, without `--no-ae` or `--no-display`. The loop captures a frame, calls `BlackboardAutoExposure.update(frame)` every five frames by default, applies white balance, and then calls `kernel.process(frame)`. AE changes sensor `exposure` and `analogue_gain` controls, so subsequent captured frames entering the IP reflect those settings; it does not apply a separate pixel exposure transform to the just-captured frame.
- Board log showed live AE values changing: at frame 760 `ae_changed=true` and `analogue_gain=177`; later luma approached target 80. Live IMX219 V4L2 controls read `exposure=2724`, `analogue_gain=171`, `vertical_blanking=1648`. The code does not claim a fixed exposure on every frame.
- Read-only `media-ctl` reported IMX219 and RAW8 media pads at `SRGGB8_1X8/1920x1080`; `/dev/video0` reported `RGB3` 1920x1080 after the ISP. The IP receives the captured 1920x1080 RGB frame after optional white balance and rotation, with sensor exposure already reflected in it.
- DRM `card0-DP-1` reported `connected`, `enabled`, and modes 1024x768, 800x600, 848x480, and 640x480; framebuffer was 1024x768. The script selects the largest mode and letterboxes 16:9 video: 1920x1080 → 1024x576, leaving 96 black pixels at top and bottom. The project owner reported seeing these bars. No display mode was changed.
- Adoption: factual current-state verification only. Files changed: this session and `project_workspace/PROJECT_STATE.md`. Validation: live log and board controls/media/DRM queried; no new visual inspection or test run. Error/correction: previous record's display-unverified statement now has a user report of visible output with bars; AI has not independently viewed the physical screen. Remaining: target detection still yields zero corners in the observed scene; timing closure and performance remain unresolved.

## Follow-up: 1080p Display Mode and Standalone AE Comparison

- Objective: explain why the current display cannot select 1920x1080 and identify the running AE file and reasons its visual result differs from the earlier standalone preview. Participants: project owner and Codex. This was read-only inspection; no process, board setting, or candidate source was changed.
- Board process PID 14385 remained active at the check (20 minutes elapsed), running the candidate `software/run_pipeline.py --color`. It imports the colocated `software/auto_exposure.py` and invokes `BlackboardAutoExposure.update(frame)` every five captured frames before white balance, rotation, and `RectifyRGB.process`. Live log reached frame 1410 at average 1.18 fps with `board_luma=77.5`, exposure 2724 lines, analogue gain 211, and nonzero detected corners. No direct physical-screen inspection was performed by AI.
- Current PYNQ `DisplayPort` exposes DRM modes 1024x768, 800x600, 848x480, and 640x480. `/sys/class/drm/card0-DP-1/edid` returned 0 bytes. PYNQ `DrmDriver.configure()` explicitly raises `ValueError` when the requested `VideoMode` is absent from `display.modes`; candidate selects the largest enumerated mode. Thus 1920x1080 is unavailable to this runtime under the present display handshake. Hardware or monitor inability is not established. The selected 1024x768 mode displays 16:9 content as 1024x576 plus 96 black pixels at top and bottom.
- Board SHA-256 of current candidate `auto_exposure.py` and prior `/home/ubuntu/imx219_probe_2026-09-24/auto_exposure.py` are identical: `b98288d10015610d9e297fb845cc7c90fa2e843771fb272698fc2d1b862c6009`. The algorithm file did not change. This comparison assumes the owner's earlier standalone preview is that `imx219_probe_2026-09-24` run; the exact user-referenced file has not been independently confirmed.
- Prior preview `run_imx219_dp_mmap.py` meters hardware-scaled 1024x576 RGB frames and outputs directly to DisplayPort with `PIXEL_BGR`. Its `configure_media_scaled.sh` uses RAW10 at 1920x1080 before scaler. Current candidate meters full 1920x1080 RGB frames, uses RAW8 media format with `vertical_blanking=1648`, then applies AWB, rotation, PL rectification, and `PIXEL_RGB` output. Both AE instances use target 80 and default five-frame updates with 48-pixel patches; those patches cover different fractions of the input. RAW format/ISP and RGB/BGR output also affect measured and displayed color.
- Prior `hdmi.log` at frame 8670 reported 27.26 fps, luma 75.2, exposure 1759, gain 83. Current candidate log at frame 1410 reported about 1.18 fps, luma 77.5, exposure 2724, gain 211. At five-frame cadence this is roughly 0.18 s versus 4.2 s between AE updates, using long-run average frame rates; instantaneous cadence was not measured. The prior preview's vertical blanking was not read, so no claim about its exact exposure ceiling is made.
- Adoption: factual comparison only. Modified files: this session and `project_workspace/PROJECT_STATE.md`. Validation: board source, modes/EDID, process, SHA-256, logs, and local candidate source inspected; no mode override or end-to-end visual quality test executed. Error/correction: earlier suggestion that current script alone allows a longer exposure is narrowed to confirmed current RAW8 VTS configuration and observed exposure value; the prior sensor control limit was not verified. Remaining: restore readable EDID or establish a supported DRM mode override if 1080p scanout is required; compare captured reference frames from both pipelines under the same scene to isolate RAW format, ISP, and AE sampling effects.
