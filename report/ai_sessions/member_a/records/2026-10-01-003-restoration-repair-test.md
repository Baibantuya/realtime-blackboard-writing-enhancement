# AI Session: 2026-10-01-003-restoration-repair-test

- Date: 2026-10-01
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: Implement paper-preserving restoration repairs and finally test real video and HLS C/RTL.
- Status: Local implementation and tests complete; complete scene restoration not accepted
- Report candidate: Yes
- Related commits: None
- Related files: Prior baseline and paper-guided proposal; new formal restoration module and named tests.

## Context Read

Read AGENTS, policy, state, decision log, index, previous session, Git status and causal video test adapter. Original C delivery and video remain preserved. User authorized implementation and tests.

## Task and Constraints

Preserve block sampling/difference/timers/spatial propagation/history composition. Reproduce original baseline alongside guarded candidate. No future frames or generated writing. Real-video visual improvements and C/RTL arithmetic consistency are separate gates.

## Contributions

Added a separate guarded candidate, reproducible native/Vitis runners, numerical oracles, real-video comparison and visual checks. Corrected missing new writing, skin-pixel pollution and camera-induced blurred history through iterations. V7 registers the board to its clear initialization and preserves raw unmasked pixels. No subagents or board deployment.

## Decisions and Adoption

D-064 proposal and D-065 refinements guide this candidate. V7 is adopted for the supplied video's tested writing improvements; whole-scene teacher removal is not accepted because residual history contamination remains. Original delivery/media unchanged.

## Commands and Tools

Python/OpenCV/NumPy, vendor GCC and Vitis HLS/XSIM 2022.2.

## Validation and Evidence

V7:6067 consecutive1080p frames,445560480 actual HLS C++/NumPy scalar comparisons, zero mismatch. Current unchanged cores C/synthesis/RTL PASS:69 calls across directed units and registered193/199s full-frame cases; independent actual AXI-output comparison153106 values, zero mismatch. 21 directed/random native properties plus protected-neighbor writing/save/reocclusion, warm skin/broad white region rejection/global freeze and registration tests PASS. Source hashes match executed manifest; MP4 source hash unchanged. Full video2022 preview frames10.01fps and240-frame key clip decoded at start/middle/end. 40/63/76/113/150s unoccluded circuit crop pixel-exact with raw.199s crop886/886 bright strokes present at exact display positions; saved background886/886 within2px,795/886 exact-position bright pixels after inverse resampling. No whole-scene accuracy claim. Board/IP export/full PL compositor/routed timing/1080p30 performance 未执行.

## Errors and Corrections

See iteration history below. Initial thumbnail claim of new writing preservation was wrong and corrected after owner feedback. Rejected guard-only, whole-block release and coarse pixel-gated variants. V5 skin pollution and V6 blurred repeated history rejected. Registered V7 fixes the tested blur; residual teacher speckles remain. First RTL TB arrays below declaredAXI depth caused instrumented SIGSEGV; fixed full-depth allocations. Independent dump decoder needed Vitis-renamed quiet_r port; fixed and validated actual outputs. PowerShell stdin sometimes encoded Chinese text asGBK; moved Unicode file edits toapply_patch. No false hardware/runtime claims.

## Files Changed

Formal software:guarded_restoration.py,guarded_native.py,board_stabilization.py; RTL:guarded_diff.cpp,guarded_state.cpp; TB:guarded_tb_io.h,guarded_diff_tb.cpp,guarded_state_tb.cpp,test_guarded_restoration.py,test_guarded_writing_pixels.py,test_board_stabilization.py; scripts:build_guarded_native.py,evaluate_guarded_restoration.py,run_guarded_hls.ps1,run_guarded_hls.tcl,compare_guarded_rtl.py; docs/guarded_restoration.md and selected report/restoration_v7 evidence. Named tests undertest_workspace/restoration_repair_20261001; internal session/decisions/state/index updated.

## Remaining Work

Residual teacher speckles/history contamination still need stronger trustworthy-background/person discrimination. Registration, full-frame history/pixel compositing remain host software; hardware video interfaces, performance, timing and deployment are future work. Supplied-video calibration is not a guarantee for other clothing, colors, dense writing or camera motion. No work remains for the completed local test run itself.

## Handoff Notes

Prior W1 has substantial artifacts despite zero arithmetic mismatches. Do not claim complete recovery without evidence.

## Follow-up: Integrated IP Completion Audit

2026-10-01: Owner clarifies final target: input already corrected frames to one IP and output frames with occluded content replaced. Reuse this session for read-only source/interface audit and readiness conclusion. No new implementation/tests authorized by this status question alone; inspect current kernel signatures and host processing boundaries, then update the handoff state. Participants: owner and Codex; no delegation.

Audit result: guarded_diff receives packed samples (index*48,16 samples per16x16 block), not full image pixels, and returns occupied/motion/quiet/changed counts. guarded_state returns TTL/q/seed and block M/W arrays, not restored RGB pixels. Both use m_axi arrays/s_axilite control; no integrated restoration frame/stream top or export_design in the current guarded HLS runner. Host Engine performs sampling, full previous/history memory, per-pixel writing recognition/quiet counters, background commits and RGB replacement. These remain required hardware work for the clarified target. Prior RTL/video results validate the two arithmetic cores and a hybrid software composition, not a complete restoration IP. Separate existing rectification firmware is upstream functionality and does not fill these restoration gaps. If upstream correction also fixes temporal board coordinates, ORB/LK registration can remain upstream or be omitted; per-frame perspective correction alone does not establish that guarantee. No percentage estimate assigned. New tests/implementation/export/board work:未执行. This readiness assessment is adopted for handoff; no selected report case added.

## Implemented Candidate and Corrections

Formal code added under software/, rtl/, scripts/ and tb/. Candidate retains sampled block differences, TTL, old/new 12-neighbor propagation and historical composition. Added sampled bright-neutral exclusion to separate chalk-like changes, lower-density occluder support, distinct display/write guards, ROI, global >=75% dense ROI disturbance freeze and parameter validation. Native DLL built from formal HLS files. Original baseline/delivery/media are preserved.

First Python probe (delta24, chalk floor130) visibly reduced teacher body/edge ghosts. Initial thumbnail review incorrectly inferred new writing retention at 199s; owner correctly pointed out missing new writing. Full-resolution crop [945,385,1085,450] showed 0/886 retained bright stroke samples, versus 369/886 in original W1 with 2px tolerance. This candidate was NOT accepted as solving new-writing visibility. It processed 6067 full frames, 396053760 numeric outputs with zero C/Python mismatches, but that does not fix visual failure. All stage2 results preserved in stage2_no_fine_release/. Correction explained to owner.

V2 changes: lower chalk-like floor100 to include antialiased strokes; add raw background-change count to the diff interface; allow stable low-occupancy sparse changes (<=8/16 raw changed samples) to release neighbor-only display protection and commit writing. Core detected person remains protected. New vector magic GDFVEC02/GSTVEC02 distinguishes changed ABI. Old ROI/color heuristics remain dataset-calibrated; identical-color or bright clothing, dense writing and persistent camera motion remain potential limitations.

A preliminary pre-freeze native run was interrupted to incorporate the global disturbance guard; partial evidence preserved in pre_freeze_attempt/. First unit test relay fixture incorrectly removed the source from the current weak region; corrected fixture, then tests passed. First RTL attempt: C simulation and synthesis passed, but co-simulation instrumented testbench failed (state DUMP_OUTPUTS SIGSEGV). Cause was test buffers smaller than m_axi declared depth on small/invalid cases. Updated testbench allocations to full declared input/output depths without changing kernel math; reran, instrumented C TB now generates RTL simulations successfully. Original failed runs retained.

V2 native complete-video test is running. V2 directed/native test passes 21 properties, with 25 difference /34 state vectors, including independently computed scalar color counts, partial bottom blocks, parameter/status handling, ROI/global freeze, full-frame history commit and new visible writing saved then restored under later occlusion. No V2 RTL result yet; prior intermediate V1 RTL runs still tracked separately. No board test or routed timing closure performed.

V2 complete: 6067 frames /445560480 scalar outputs, zero arithmetic mismatches, but real 63s frame shows renewed teacher edge contamination. Rejected whole-block fine release. V3 restores floor130 and strict whole-block guards, adds only stable sparse neutral-bright pixel display/history commit (min100, spread55, <=8/16 raw changes, below weak occupancy); sampled background repacked from committed full history. This extra pixel compositor is host software, not implemented in HLS cores. V1 RTL completed PASS:31 diff/40 state calls including directed status cases; these are historical V1 only.

V3 run interrupted to refine adjacent-teacher writing confirmation. V4 keeps HLS cores unchanged from V3; fine-writing host eligibility uses a separate brightness100 sampled occupancy plus <=8/16 raw changes, with per-pixel 3-frame quiet confirmation instead of block quiet. This avoids moving neighboring pixels suppressing exposed static strokes. Full background writes remain protected. Compositor uses equivalent OpenCV masked copy for runtime cost. V4 full-video acceptance pending.

Owner again reports partial strokes. Reject block eligibility for visible ink: V5 keeps strict HLS guards but displays ROI neutral thin pixels immediately (min90/spread65; broad-region opening7 then dilation3 excludes broad bright areas), saves stable3-frame pixels only and prohibits all commits during global freeze. This is host-only pixel compositor extension. V4 partial run preserved. Numeric and visual V5 acceptance pending; cannot guarantee semantic discrimination of thin bright clothing/skin fragments.

V5 63s visual review exposed accumulated orange skin contamination, rejected despite admitting all 886 new-writing bright pixels. V6 tightens fine-pixel color: min100/spread55 and R<=B+6/R<=G+6, calibrated to supplied video neutral chalk; raw199 selected strokes have R-B between -23 and -14, so all886 still admitted. Keep broad exclusion and pixel quiet confirmation. V5 partial and full-frame40 RTL vectors preserved; those vectors belong to V5 context only, although kernel sources unchanged. V6 full sequential test pending.

Owner reports blurred board writing; V6 rejected as final. Matched initial/current board features show camera drift about15px at40s and21px at63s. V7 adds causal ORB + subpixel LK/RANSAC board-plane registration to clear initialization, checked spatial inlier coverage/reprojection/corner drift; updates every3 frames and holds last transform if rejected. HLS block algorithm unchanged. Process canonical board; inverse-warp only recovered masked pixels back into raw coordinates, leaving unmasked original pixels intact. New registration and inverse composite are host preprocessing, not HLS hardware. V6 evidence preserved.

V7 actual 63s unoccluded circuit crop [550,150,830,310] is pixel-exact against raw (100% RGB equality, mean absolute channel error0), versus rejected V6 39.1987% exact /12.93796 mean error. Sharpness zoom/JSON generated from actual output, not illustrative images. Synthetic registration mapping error0.03854px, unmasked pixel equality PASS. Full run still pending later new-writing scenes; do not extrapolate this local equality to whole-frame recovery accuracy.
