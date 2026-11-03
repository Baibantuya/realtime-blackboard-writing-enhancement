# AI Session: 2026-10-01-001-real-video-hls-restoration

- Date: 2026-10-01
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: Prepare/run a real blackboard/teacher occlusion restoration case locally before board integration, using actual HLS arithmetic results.
- Status: Complete: real video rendered, C/RTL numerical PASS, visual restoration quality not accepted
- Report candidate: No
- Related commits: None
- Related files: C delivery snapshot and `test_workspace/hls_c_handoff_20260930/`.

## Context Read

Read root instructions and development policy; reviewed current state, recent decisions/index and 2026-09-30-010 local HLS simulation record, Git status and source inventory. Previous covered-test arithmetic PASS does not establish real restoration quality.

## Task and Constraints

User wants actual teacher-occluded blackboard restoration testing locally before going to the board. Read-only video inventory under workspace found no mp4/avi/mov/mkv source videos. Request original input path and a user-confirmed unobstructed background frame. Preserve supplied source and raw media.

## Contributions

Confirmed that supplied reference composes each output using pre-commit background where M is true, then updates background only where W is true. HLS supplies only sampled differences and block-state masks; decoding, sampling, full-frame history storage, composition and video encoding must be supplied by an offline test adapter. The original delivery's real `测试视频1.mp4` is referenced by relative path but absent; only statistics and textual time annotations are included. Documentation describes first-observed-then-occluded writing, and never-yet-visible writing; these must not be treated as equivalent restoration cases.

Prepared execution scope once media arrives: sequential HLS C++ arithmetic calls and explicit state/background submission for complete local output video, plus representative continuous real-frame C/RTL arithmetic checks. Produce original / history-restored / M-mask video panels and representative PNGs; include background contamination, writing-delay and erosion/ghosting observations. State whether each visible result comes from HLS C simulation or RTL; do not present software frame composition as an already integrated hardware compositor.

## Decisions and Adoption

No new architecture decision. Restoration uses previously observed pixels; no claim of generating unseen writing.

## Commands and Tools

Context/source reads, recursive media-path inventory under the entire workspace, relevant delivery video-evaluation/source-note reads and `BlockForegroundReference.process` source inspection. Required video path and confirmed unobstructed initialization were requested through asynchronous user input.

## Validation and Evidence

Real teacher-video restoration and board test: 未执行. Previous session's synthetic RTL tests are not a real video test.

## Errors and Corrections

No runtime failure; required media absent from inspected workspace.

## Files Changed

This internal record, `project_workspace/ai/INDEX.md` and `project_workspace/PROJECT_STATE.md`. No raw-media or algorithm change.

## Remaining Work

Obtain original video path and confirmed background initialization; implement/run a sequential test which submits background/state using HLS outputs, then render raw/restored/mask views. Compare C/RTL outputs for representative consecutive real frames. Board integration remains separate.

## Handoff Notes

Waiting for video path and a user-confirmed unobstructed background frame/time. Previously observed writing can be restored from stored history if detection and write control succeed; writing that has never been visible cannot be recovered by this historical-background method. Avoid using later clear frames to fabricate earlier restoration. Real restoration quality and all board tests remain unexecuted.

## Input Received and Ongoing Execution

The owner placed `4626a491a5a409bc1f8a84ffae5c42e8.mp4` in the original C delivery directory after the initial inventory. SHA256 `92aa53739e7cef05ce74a91980db2bd82ad9b4ba750ac00be24aee3a29566581` exactly matches the historical delivery test video. OpenCV reports 1920x1080, 6351 frames, 30.03946 fps and about 211.42 seconds. Visually reviewed the contact sheet and the unobstructed 6-second initialization candidate; original delivery annotations identify 6–8 seconds as clear. No future frame is used for initialization.

Created `test_workspace/real_video_hls_20261001/`. Vendor GCC 8.3.0 from Vitis HLS 2022.2 compiled unmodified `block_diff_w1` and `block_state` into a native DLL; hashes match original sources. Sequential W0/W1 engines use actual HLS outputs for state/history commits. All six difference and five state outputs are checked against Python on every processed frame. Full-frame state processes every frame, while presentation video is downsampled threefold. Full input sampling adapter was checked against the original packer at initialization. C execution is not RTL video integration.

Locally installed imageio-ffmpeg 0.6.0 under the named test directory. Initial configured-index and proxy attempts failed; isolated PyPI installation with proxy variables removed only from the child process succeeded. No global Python environment or original delivery files were modified. Ordinary sandbox vendor GCC execution had the known MSYS signal-pipe restriction; authorized elevated execution succeeded.

Observed 63-second actual comparison: W1 partially restores historical board text but leaves teacher head/arm/edge artifacts; W0 has prominent block fragments and background contamination. Arithmetic parity must not be confused with restoration-quality acceptance. No frame-level clean ground truth was supplied, so no recovery accuracy percentage will be invented.

Prepared real-snapshot RTL runner, independent AXI memory-dump comparator, video report and reproduction README. RTL validation is pending completion of full-video execution at this checkpoint. Board execution remains 未执行.

## Full Video Completed

Processed 6067 consecutive frames after source frame 182 at 6.0295667 seconds, stopping before 208 seconds. Runtime 824.916 seconds is host C-adapter runtime, not FPGA throughput. Compared 1,089,147,840 HLS C/Python scalar outputs with zero mismatches across two policies and eleven fields per 8160-block frame. Encoded 2022 presentation frames, 1920x340 at about 10.01 fps, 36,153,747 bytes. OpenCV reopened video and successfully decoded frames 0/300/1000/1800/2021; frame count matches summary.

Visually inspected actual 40/63/180/193/199-second comparison PNGs. W0 has severe spatial block ghosts, including regions outside the current person. W1 restores portions of previous board content but retains person colors/head/edges and, at 199 seconds, suppresses some newly exposed writing. Current restoration quality is not accepted; fix detection/history update and newly exposed writing behavior before board integration. Numerical parity establishes matching arithmetic only.

Real RTL snapshots are source frames 5799/5800 at 193.0001/193.033411 seconds, each W0 and W1. C simulation and synthesis completed with four real cases per kernel; RTL simulation still running at this checkpoint. First RTL launch failed because Windows PowerShell read a UTF-8 Chinese path without BOM as ANSI. Added UTF-8 BOM to the runner, reran in new ASCII output folders, preserving failed-attempt directories. No C++ modifications were required. HLS reports loop constraints unmet; this is not a post-route timing-closure result.

## Final Result, Adoption and Handoff

Vitis HLS / XSIM 2022.2 completed both unmodified kernels through C simulation, synthesis and Verilog co-simulation. Difference kernel: 8 directed + 4 real golden cases, 12 RTL calls; independent RTL AXI-memory extraction compared 195840 real-case scalar outputs, zero mismatch. State kernel: 10 directed + 4 real golden cases, 14 RTL calls; 163200 real-case outputs, zero mismatch. Combined actual RTL: 359040 outputs, zero mismatch. Sources remain hash-identical to original delivery. These are two arithmetic subcores; not a complete RTL video compositor or board result. No physical deployment, post-route timing closure or FPGA performance test performed (未执行).

Created full comparison video, 24-second key clip (176–200s), selected full-resolution original/W0/W1/mask PNGs, playback HTML, JSON source/build/video/decode/RTL metadata and compressed actual/expected RTL arrays. Key clip first/last frames decoded successfully. Full playback video already checked at five locations. Reviewed 40/63/180/193/199s visible comparisons. Current default W0 has severe ghosts; W1 partially restores historical content but retains body/head/edge remnants and suppresses some newly exposed writing. Adopted local causal test harness as evaluation evidence; did not adopt current visual behavior as satisfactory restoration. Recommendation: repair background contamination and new-writing visibility before board integration.

AI contribution: media identity/initialization audit, unmodified native HLS bridge, per-frame Python comparison and causal compositor, real snapshot collection, actual C/synthesis/RTL runs, independent RTL memory parser, visible report and evidence records. Participants were owner and Codex; no delegated agents, no collaboration conflicts. Owner supplied raw video; Codex reviewed and integrated all results.

Files changed/created: `test_workspace/real_video_hls_20261001/{inspect_video.py,build_native.py,run_video.py,run_rtl.ps1,compare_rtl.py,make_video_report.py,README.md}`, copied unmodified C++ sources/DLL/build manifest, local `tools/`, `rtl_runs/`, source metadata/contact sheet and `results/`; internal session, INDEX, PROJECT_STATE and D-063. No original delivery media/source files or formal production algorithms modified. No Git commit made. Prior waiting/pending checkpoints above are superseded by this completed result.

Reproduction starts with this test directory's README. Results: `results/report.html`, `key_case_176_200.mp4`, `restoration_comparison.mp4`, `video_summary.json`, `rtl_summary.json`. Real-case snapshots preserve pre-commit state at frames 5799 and 5800. Remaining tasks: diagnose/refine detection/history write control and newly exposed writing behavior, collect frame-level recovery truth, then integrate sampling/state/background storage/composition/memory interfaces on board. This task did not tune thresholds to hide failures or reconstruct never-observed writing.
