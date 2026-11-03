# Session 2026-10-20-008-v22-r4-full-release-handoff
- Date: 2026-10-20
- Operator: user
- AI: Codex
- Participants: user, Codex
- Objective: Package current 2px PS runtime v2 r4 with matching full project, generated RTL and all board artifacts; write modification and takeover guides.
- Status: Complete
- Report candidate: no
## Context Read
AGENTS, development policy, PROJECT_STATE, DECISIONS, INDEX and session007; Git status; candidate source/runtime manifests. Existing project is untracked; no commit or other AI work overwritten.
## Task and Constraints
Use current r4 source/board package, preserve signed v22 hardware and eight frozen v15 sources. Include real server Vivado project and generated RTL rather than only HLS C. Do not restart runtime or run new synthesis. Internal session history stays outside formal release.
## Contributions
Created full release directory and ZIP with exact current r4 board files, PS source/tests, matched HLS source, generated Verilog/VHDL/system RTL, real server Vivado/HLS engineering archive, Chinese change/takeover guides and verification/relocation/PS-restart helper tools.
## Decisions and Adoption
Package exact current runtime separately from original hardware-build source snapshot; identify old r7/r8 launchers as legacy dependencies, new entrypoint run_ps_runtime_v2.py authoritative.
## Commands and Tools
Read-only local and authorized server SSH inventory. First attempted source/build_release_server.sh path absent; locate actual script before documenting commands.
## Validation and Evidence
Complete ZIP1514967469bytes, SHA256 0f61f9865931e94cd7571236a4ac45a3dbe03ba6cfdca72bb41b3e8bd5a78eed.647 release file hashes + outer/inner ZIP CRC PASS. Server engineering archive1419808246bytes SHA3a545eeea0ad5d741b243641e600573602b56a16a55fc2ca33fa914bb03fed0d; downloaded archive matches server and all10412 files extracted and individually size/SHA verified.440 source/RTL files separately organized. Exact board174 bundle files match current running boardPID50374 and selectedZIP51ac1476c94f99980911f60b2f32e51a98e5390df4404539cea7174a9c2f3491. Hardware bit/bit.bin/HWH/DTBO match snapshot; hardware export source hashes and eight frozen v15 files PASS.
Recovered XPR checked24 source/IP paths after relocation, missing0. No new Vivado open/synthesis/implementation. Release-copied PC9 geometry/scheduler +3 process/content tests PASS; helper syntax/arguments PASS. Newly supplied restart helper was not executed on board. Original server tool overlays/install symlinks, .Xil and Python caches excluded, not required input design sources. All source/IP/build runs/checkpoints preserved in archive. Actual board snapshot includes transient AE-limited conditions; docs retain limitation, no unrequested algorithm change.
## Errors and Corrections
Existing candidate README still identifies r7 and deployment restore_photometry.scope describes obsolete fixed-after-init policy. Release guide must explicitly describe actual continuous SensorService behavior without silently changing already deployed sealed payload.
## Files Changed
Formal releases/v22_ps_runtime_v2_r4_20261020/ and .zip/.zip.sha256; candidate rtl/dma_rgb565_fusion_v22/README.md updated to current release; PROJECT_STATE/DECISIONS/INDEX and this session. Test/archive/assembly/seal scripts and verification reports in test_workspace/v22_r4_release_20261020. No sealed r4 payload or running source changed.
## Remaining Work
Requested packaging and handoff complete. Broader r4 visual threshold comfort, long-run cadence/content HOLD, cold-start revalidation and original dark-line/color quality remain as documented follow-up; not prerequisites invented for delivering this package.
## Handoff Notes
Current boardPID50374 confirmed at packaging snapshot; runtime left running. Complete release ZIP and SHA file under formal releases/. Handoff specifies current entrypoint and ongoing continuous AE, distinguishes legacy inherited fields and exact snapshot from live r4. No timer, synthesis, deployment/restart or private raw camera images added to package.
