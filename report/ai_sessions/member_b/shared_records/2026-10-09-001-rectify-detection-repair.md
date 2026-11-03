# AI Session: 2026-10-09-001-rectify-detection-repair
- Date: 2026-10-09 (Asia/Shanghai client)
- Operator: Owner
- Participants: Owner and Codex
- Objective: Diagnose/fix sparse PS detector using yesterday's actual frame; update previous project/package and remote project, white display before valid calibration.
- Status: Completed offline; board validation pending (disconnected)
- Report candidate: yes
- Related commits: None; working tree currently untracked project files.

## Context Read
Read AGENTS.md, policy, current state/decisions/index, deployment session003 and current detector/runtime. Existing fixed WB1.6838/1/1.5259 retained. Root policy unchanged.
## Task and Constraints
Board disconnected; use saved actual rawRGB npy/png. Prior no-PL-edit restriction retained. Remote Oct8 candidate allowed for edits. No claim of new board execution or synthesis. Test in test_workspace/rectify_detection_20261009; preserve pre-repair detector and matched ZIP.
## Contributions
Diagnosis and edits pending.
## Decisions and Adoption
Owner explicitly authorizes rectify repair; no-calibration display should be white based on prior clarification. Preserve shared DMA ring, fixed WB and accepted-H/history interface.
## Commands and Tools
Python/NumPy/OpenCV offline and SSH existing Vivado server.
## Validation and Evidence
Not yet executed; board validation 未执行 (disconnected).
## Errors and Corrections
Pending.
## Files Changed
This record; preserved test snapshots.
## Remaining Work
Trace real failure, bounded detector correction, image/sequence negative checks, offline warp preview, runtime white fallback, package/hash/server synchronization and state/index update.
## Handoff Notes
No board commands. Candidate local test_workspace/whiteboard_shared_ring_20261008; server /data1/leisheng_codex/wb_shared_ring_rectify_20261008.

## Completed Diagnosis and Changes
- Original detector returnsNone on raw and fixed-WB modeled frame. Raw top samples included wall boundaries such as(480,94)/(617,72), inconsistent with actual frame; original all-point fit rejected even remaining valid line points. Exact fixed-WB modeled board medianRGB91/94/102 cannot satisfy G-B>=10; original detector had zero edge points. Fixed WB remains unchanged per owner.
- New bounded relative-luminance/weak-color profiles, deterministic <=28 pair support checks per edge then line refit, inner-directed transitions. Initial radius64/track32 avoids selecting outer shadow after coarse bright metal gap merge. Kept geometry matrix ABI/cache/generation/hysteresis.
- run_pipeline initializes a white cached display frame once and has no raw camera snapshot on calibration failure; PL is only called after accepted geometry. Existing valid geometry remains held across temporary detection loss. Logs include detector stage/edge point counts/failure reason.
- Candidate/formal PS sources and server software synchronized, exact detector/runtime hashes compared. Previous local detector+matched ZIP preserved in test_workspace/rectify_detection_20261009; remote previous detector/runtime saved in evidence/detection_repair_20261009. No board connection or writes.

## Actual Verification
- Saved actual raw and exact ISP-LUT modeled WB frame detection PASS. Modeled brightness0.7/0.85/1.1/1.2, noise +/-2, four blank colors and shifted scene checks PASS. These are generated variants of ONE captured frame, not new camera captures or general accuracy statistics.
- Initial3confirm locks, unchanged scene holds generation1, shifted24/-8 confirms3checks before generation2. Approximate manual corner landmarks differ <=19.55px; landmarks are visual estimates, not calibrated ground truth. Final WB corners approx(130.92,457.69),(1642.56,231.86),(1732.23,657.09),(199.43,934.22).
- Existing13Linuxruntime tests PASS on server. Dedicated real-pipeline/fake-device fallback test PASS:3white frames/no raw snapshot/no uncalibrated PL; its synthetic timing values are not performance evidence.
- Unchanged HLS C compiled natively on server; actual saved-image geometry processed full1920x1080RGB output matches float32 reference in all6220800bytes, status/hint/corners correct. This is native C execution, not FPGA timing or new RTL simulation. Preview visually inspected; board straight, canvas outside white, chalk content visible.
- Full ZIP28files refreshed; ZIP CRC/bundleSHA/systemSHA PASS. SHA0973aa27daff76fd04cd8e852a7426ec0671d33fc83412c8d850c75a82dc4b38. BIT SHA29f456b0ad380ab838338162a1fd68069ef02a79503f0634c857847b459db06b/HWH SHAf4f402c14b49cfd7750a7c073e130adb37759d70725870d887d621aa7a70edbd remain unchanged.

## Errors and Corrections
- First luminance version passed actual picture but2old synthetic tests showed outer-shadow detection45px off. Expanded bounded refinement and preferred inside transition; both tests then PASS. No failed expectation relaxed.
- Windows full Linux capture tests cannot importfcntl; run on existing isolated server dependencies/runtime_env. Server barepython lacksnumpy, corrected interpreter.
- White fallback harness initially lackedWindowsSIGUSR1 and hit low-resolution Windows clock divide-by-zero; mocked signal and deterministic clock in TEST ONLY. Final real pipeline exercised unchanged ARM behavior; no fake timing claimed.

## Deliverables and Remaining Work
- Candidate board_package/board_detector.py/run_pipeline.py/README.md/system_manifest.json; matching ZIP. Formal software same plus tests/replay_saved_frame.py and test_white_fallback.py; source/tests copies; prepare_wb_package.py updated to sync detector and preserve offline validation.
- Evidence: test_workspace/rectify_detection_20261009/replay/{server_summary.json,native_corrected.png,detected_overlay.png}; raw/model arrays, geometry and preserved baseline under named test directory. Internal decisions/state/index updated.
- Remote /data1/leisheng_codex/wb_shared_ring_rectify_20261008/software updated; tests/evidence replay available; final ZIP in board_artifacts/whiteboard_shared_ring_20261009_ps_repair.zip matches local SHA.
- Adopted: PS repair and white initial fallback. PL unchanged; no new synthesis, bitstream, board deployment, cold-start/long-run/latency/quality acceptance. Task completed offline; next board connection must confirm geometry_generation>0 and completed/restored advance, visually inspect correction and verify ownership/performance separately.
- Participants: owner requirement/approval; Codex diagnosis, implementation, validation and packaging. No subagents.
