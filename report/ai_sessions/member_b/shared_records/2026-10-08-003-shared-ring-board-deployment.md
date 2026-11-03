# AI Session: 2026-10-08-003-shared-ring-board-deployment
- Date: 2026-10-08
- Operator: Project owner
- AI product/model: Codex / GPT-6
- Participants: Project owner, Codex (single agent)
- Objective: Deploy matched shared-ring/sparse-rectify package to owner's specified KV260, preserving old application/firmware and validating smoke/live.
- Status: In progress
- Report candidate: yes
## Context Read
Previously read AGENTS.md/policy/decisions/index; reread current state, session002 final handoff and Git status. Local candidate/ZIP previously SHA256/CRC verified.
## Task and Constraints
Owner explicitly authorizes board deployment and provides credentials. Address text192.16810.2 interpreted as[private_ip], username kept as supplied. Credentials are never recorded in files, commands or output logs. Verify host/kernel/current state, back up before hardware/application changes. Abort unsupported kernel/address/DMA mapping rather than pretending zero-copy success.
## Contributions
Connection/readiness pending.
## Decisions and Adoption
Board deployment authorized, prior owner-self-deploy boundary superseded for specified board.
## Commands and Tools
PowerShell/OpenSSH/PuTTY as appropriate; password via interactive authentication only.
## Validation and Evidence
Actual board login/module/capture/timing/display: 未执行.
## Errors and Corrections
Malformed IPv4 spelling normalized explicitly; authentication identity not assumed corrected.
## Files Changed
This session record; future evidence/backup/state metadata as needed.
## Remaining Work
Connect, kernel/capability check, backup/upload/install/check/deploy, verify smoke/live/rollback path; report actual outcome.
## Handoff Notes
Package under test_workspace/whiteboard_shared_ring_20261008; newABI4 bit/HWH/PS/DTBO/driver must remain matched, prebuiltmodulekernel5.15.0-1027-xilinx-zynqmp.

## Actual Board Deployment and Current Diagnosis (2026-10-08)
- Connected to intended board after resolving supplied address/identity spelling; no credentials stored. Preserved original application, previous application and firmware in manual backup plus installer history.
- Loaded new matched firmware; FPGA operating. Fixed actual ARM64 DMA-zone probe failure using 32-bit coherent mask with existing low-2GiB checks, rebuilt module for exact board kernel. Accepted known RGB3 one-plane capture driver's reported num_planes=0 alongside1. Candidate/formal source synchronized for these fixes.
- Three actual full-HD shared-buffer identity/restore-initialize frames completed. Capture continued concurrently. This demonstrates camera/shared-DDR/PL access, not full long-duration zero-copy/quality/performance acceptance.
- Live application never established board geometry (generation/completed/restored remained0). Visible output was raw fallback; calibration fault remains. Raw-loop frame rate must not be reported as correction/restoration performance.
- Application stopped for actual raw-frame acquisition and diagnosis. Firmware remains loaded. Saved image shows a visible tilted green board and green cast extending to nominally neutral areas.
- Owner asks to leave PL code unchanged and flags green image/exposure. PS code inspection confirms current runtime explicitly reports awb=false and has no color correction; prior version had color gains. AE controls luminance independently, with prior measured board luma near77 against target80. Green cast therefore cannot be attributed to exposure alone; missing WB is a strong candidate, while Bayer/ISP channel correctness still needs checking.
- Do not use full-frame gray-world WB: green board is real scene color. Plan neutral-reference white point correction through existing ISP from PS, retaining board green; verify Bayer/RGB channel order after sensor rotation. No new PL edit or synthesis in this diagnosis.
- Current limitations: color correction not yet implemented or accepted; detector still not locked; application stopped; local deployment ZIP predates board compatibility fixes and must be regenerated before reuse.
- Contributions: Codex deployment, DMA/capture compatibility fixes, real board smoke and failure diagnosis. Adoption: owner authorized deployment and PS diagnosis; PL edits prohibited now. Errors/corrections: successful smoke initially did not establish live geometry; explicitly corrected scope of success. Remaining work: PS color/detector repair, restart, minimal live check, synchronize final package hashes.
2026-10-08 owner requested resume: reused loaded hardware with activate(manifest,False); existing activation routine repeated three full-HD smoke frames PASS and started PID38077, live.log. No PL/PS image processing changes. Initial direct run.sh invocation failed non-executable; bash run.sh start unsupported, corrected to existing Python activation helper. Color/detection issues remain pending.
Owner now explicitly authorizes white-balance repair first. Scope: PS software/existing ISP LUT only; no PL edits/rebuild. Selected same deployment session record before edits. Inspect generated gamma ABI and actual LUT, neutral-reference sample behavior; deploy with prior files backed up and minimal live check.

## WB Repair Implementation
- Added board_package/isp_white_balance.py and integrated startup/update/cleanup into run_pipeline.py; synchronized formal software/. Existing ISP identity curves read on actual hardware (all3banks), 1920x1080/RGB/8bit ABI validated.
- Neutral sampling every3s, old gains bootstrap, inverse-LUT feedback, limited gain changes, highlights shoulder and original LUT cleanup. No input mutation or fullframe WB transform. No PL or sensor Bayer code edit.
- Meaningful small test PASS: green-reference rejection; known neutral biased reference converges after inverse feedback; monotonic LUT; no input mutation; readback/reset. Python syntax checks PASS.
- Regenerated driver source archive and matched local28-file automatic-deployer ZIP to include prior board compatibility fixes and WB module; ZIP CRC, bundle SHA and system manifest SHA checks PASS. Original bit/HWH unchanged.
- Board application stopped; prior scripts additionally backed up to history/20261008-before-wb. Original installer archived previous/current again before installing refreshed ZIP. No hardware reload requested. Board preflight26files PASS; activation pending at record write.
- Files: candidate board_package/isp_white_balance.py/run_pipeline.py/system_manifest.json/kernel_sources.tar.gz; candidate prepare_wb_package.py/test_isp_white_balance.py/ZIP; formal software/run_pipeline.py/isp_white_balance.py/v4l2_rgb.py; internal session/decisions/state/index.
WB live PID39144 ran >930 frames with readback checks passing; neutral sampling roughly3540-4305 pixels and gains1.6838/1/1.5259. Owner explicitly requests these gains fixed permanently. Removed WB feedback update method and all pipeline periodic WB calls; initial/default/deployment explicit arguments now1.6838/1/1.5259. AE remains independent. Fixed-LUT test PASS for exact gains/no update method/green preserved/neutral correction/monotonic/readback/reset. Refreshed matched ZIP CRC and both checksum manifests PASS; fixed WB deployment pending. Visual quality not independently captured/confirmed. D-074 adaptive portion superseded by owner freeze.
## Fixed WB Result and Handoff
- Final fixed runtime restarted without FPGA reload, PID39638. Actual frame260 log: awb_mode=isp_fixed, gains=[1.6838,1.0,1.5259], awb_changed=false, bad_frames0, board_luma85 against target80; LUT startup readback passed. Program continues running.
- Geometry generation remains0, completed/restored0. WB repair/freeze completed; board detection/rectify quality remains unresolved. Raw display rate is not corrected/restored performance. Visual color acceptance not independently captured by agent.
- Local finalized28-file ZIP SHA25671140550b316d2f7f4a693f0d59896daa429ffca6306d4c2840edef87e05cfce; CRC/bundle+system hashes passed. Software/formal defaults and deployment arguments all fixed. Board installer preserved history before both WB revisions. Original bit/HWH reused.
- Error corrections: missing PYNQ environment in diagnostic MMIO subprocess corrected using deployment environment; HWH MAX_DATA_WIDTH actual name used after inspection. Fixed-gain owner request superseded adaptive implementation before final handoff.
- Remaining work: blackboard geometry lock repair under PS-only constraint; assess actual visual correction and long-run operation separately. No further changes in this turn.
