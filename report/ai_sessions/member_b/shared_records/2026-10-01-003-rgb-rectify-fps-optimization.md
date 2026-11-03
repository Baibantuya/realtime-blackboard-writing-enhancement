# AI Session: 2026-10-01-003-rgb-rectify-fps-optimization
- Date: 2026-10-01
- Operator: Project owner
- Participants: Project owner, Codex
- Objective: Optimize reviewed IMX219 RGB package, validate and deploy via existing deployment script, preserve board history.
- Status: Complete (modified, physically verified and deployed; user confirmed display normal)
- Report candidate: yes
## Context Read
Root AGENTS.md and required policy/state/decisions/index from prior review, review session 002, deployment scripts/docs/config, target HLS/RTL/test/build source, current deployment PS source and manifest.
## Task and Constraints
Owner explicitly authorizes modification, deployment and board historical backups. Preserve original target and current deployment package; work in named test workspace. No credentials in logs/files. Deploy only matched artifacts with verification; do not claim measured speed without measurement.
## Contributions
Implemented HLS RGBX32/packed RGB888 DATAFLOW/cache/rotation; AE iterative divider; PS packing/capture/profile/cadence/fallback; permanent history deployment; standard constrained hardware implementation and physical acceptance.
## Decisions and Adoption
Plan cached geometry, packed memory access, AE timing repair and PS memory/profile improvements. Board installer must preserve dated history rather than delete old .previous. Decisions to be recorded with concrete ABI.
## Commands and Tools
PowerShell, rg, existing deploy_to_kv260.py. Initial plink SSH reaches host but batch authentication unavailable; user asked for login method while local work continues.
## Validation and Evidence
Completed tests/build/board deployment: see detailed progress and final acceptance below.
## Errors and Corrections
Historical F:/Vivado tool paths were not present; locating current installation before build.
## Files Changed
Candidate hls/rtl/software/tests/vivado/firmware/evidence and manifest/README; official deployment scripts/install helper/docs; local deployment config backup/current config; formal source package and internal decisions/state/index.
## Remaining Work
Requested modification/deployment/history preservation complete. Physical display observation confirmed normal by owner; optional full C/RTL simulation was stopped before completion. Further DDR/stride architecture tuning is future work.
## Handoff Notes
Previous ~1 fps measured another package; take fresh baseline on actual board before claiming improvement.

## Progress Evidence (before implementation completion)
- Board SSH authenticated; current application observed at ~1.625 fps, nonzero corners/status 0. Its source differs from historical target AE; actual board AE/clipping and AWB source retained.
- Board backup: /home/ubuntu/kv260_apps/history/whiteboard_candidate/20261001-before-fps includes current, previous, state, real firmware tree and firmware-request alias imx219-rgb-rectify.bin; SHA256SUMS verified. Initial assumption alias .bit.bin exists at /lib/firmware corrected after filesystem inspection; real alias backed up. Board clock is 2025-10-17, cannot use it as client date.
- Host optimized/legacy comparison: 8 full 1080p scenes/calls and explicit cache invalidation PASS, all RGB bytes/status/corners compared. HLS C simulation same PASS.
- HLS synthesis: render II=1, 2,073,660 cycles / 20.737 ms vs old 6,220,863 / 62.209 ms; estimate, not board throughput. Actual new registers 0x6c/0x74/0x7c verified against generated header; IP v2.0.
- AE RTL XSIM: 5 exact frame means with valid stalls PASS. Initial standalone xelab lacked common timescale; rerun with --timescale 1ns/1ps passed.
- Controller checks: packing/channel order, DMA destination boundaries, new register programming, timeout retains buffers PASS. Versioned history preserves distinct generations and verifies SHA-256 PASS. First Windows tempfile test hit inherited permissions; named workspace directory test passed without modifying permissions.
- Full HLS cosim initial generation failed due Windows path length; short R: mapping rerun in progress. Full Vivado standard OOC synthesis/implementation in progress; do not deploy without routed timing.
- Real HWH RAW8/1PPC/addresses/PS widths verified; matching DTS generated and board dtc compile exit 0 (existing graph warnings).
- Added conditional direct PL-to-DRM destination after reading board drm.py/buffer.py; full hardware pixel comparison included in smoke before live startup.
- Preserved board-measured white-point gains [1.595,1,1.579] for live startup; default time-based AE/WB controls, geometry refresh every 2 seconds.

## Full Build Recovery
First full standard Vivado build retained successful runs but failed hsc/vsc compile_c import because absolute Windows paths exceeded limits. Read-only open via R: confirmed actual project/run directories resolve to R:. Original combined build exited with synthesis failure at 11:52 client host time; no bit produced or deployed. Short recovery waits for still-running custom synthesis (which completed with 0 errors/0 critical warnings), preserves completed runs, and launches only the two scaler children and wrapper. Reports and generated clocks remain in the ordinary Vivado implementation flow; no checkpoint stitching or timing downgrade used.

## Implementation Progress
Short-path scaler children/wrapper and complete top synthesis passed (top 0 errors/0 critical warnings). Standard implementation now reads all normal IP checkpoints and XDC constraints and performs logic optimization. Launching top/implementation refreshed scaler dependency checkpoints again; no bypass of dependency generation. Board remains legacy application at ~1.626 FPS. Hardware differential gate extended to five cases including cached changed image, explicit invalidation and BGR cache-key change. Full routed timing and board gate remain pending.

## Final Acceptance and Adoption
Adopted and deployed via existing deploy_to_kv260.py twice; final PID 23845, FPGA operating, 1010 frames at 3.417587 FPS vs 1.625717 before (2.102x). Stable sampled status 0. SHA-256 of actual board bit and run_pipeline.py match candidate. Five physical full-frame differential cases and camera gate PASS both times. Cached PL median 142.530 ms, refresh 187.735 ms. Direct DRM rejected because strides=(5888,3,1), address=0x1017f5000; fallback remains active. AE/WB cadence changed from initial0.25 to0.75 seconds after profiling; split-channel LUT trial slower (43.1 vs31.0 ms), rejected.
Clock Wizard TIMING-2/4 found at final methodology despite positive setup; corrected exported complete routed XDC via reset_timing/read_xdc, removing exactly duplicate primary/jitter and retaining true PS clock with same jitter. Corrected WNS0.384/WHS0.010/WPWS0.164, all violation totals0, internal no-clock/unconstrained0, method no critical warnings. DRC ordinary IP warnings remain. Physical placement/routing unchanged, no constraint severity downgrade. Standard bit/XSA build completed. Optional full RTL cosim was terminated at2h17m; resulting tool FAIL caused by termination; not claimed pass. Only verified own xsim processes25352/34864 stopped. R: short mapping retained for existing project reproducibility.
History initial backup plus installer generations retained with hashes; final .previous is first optimized runtime, original legacy remains initial backup and permanent archives. Board clock inaccurate. Read-only state path corrected from state.json to whiteboard_candidate.state.json. SCP multi-remote-source invocation rejected, corrected to single observed wildcard. No credentials stored. Formal sources rtl/imx219_rgb_rectify_v2; outputs report, benchmark and source/firmware ZIP. Original E: packages untouched.

Owner physical confirmation: display is normal (direction/color/rectification/chalk writing). All requested work complete; no approval pending. Final report generation UTF-8 read setting corrected after Windows default GBK error; rerun succeeded.

## Bottleneck Explanation Follow-up
2026-10-01: Owner asks what the bottleneck specifically is. Reviewed existing benchmark, render/read_pixel/store_rgb and serial PS loop; no new hardware test or operational source change. Confirmed largest measured stage is PL (~142.5 ms cached/~187.7 ms refresh); remaining sampled medians capture/copy46.8 ms, white balance28.6 ms, display copy/submit54.2 ms, packing2.1 ms. Display measurement includes submission/vsync, capture includes waiting; these are not pure memcpy costs and medians are not additive exact per-frame timing. Source computes perspective addresses then individual uint32 input reads, while output is sequential; burst/outstanding settings do not prove actual transaction utilization. DDR latency/transaction efficiency/backpressure is a leading hypothesis for ideal20.737 versus measured142.5 ms; AXI counters/ILA and pipeline stall measurements were NOT executed, so exact attribution to DDR versus compute/output is unproven. Serial capture -> WB -> PL -> display also constrains end-to-end FPS. DRM stride5888 vs packed5760 and reported address outside allowed low-DDR window explain why zero-copy path was rejected. No new deployment requested or performed.
