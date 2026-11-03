# AI Session: 2026-10-01-004-rgb-ddr-stability
- Date: 2026-10-01
- Operator: Project owner
- Participants: Project owner, Codex (single agent)
- Objective: Optimize indexed DDR reads; retain accepted geometry when all four corner displacements are <=16 pixels; validate and deploy preserving history.
- Status: In progress
- Report candidate: yes
## Context Read
AGENTS.md; AI_DEVELOPMENT_POLICY; PROJECT_STATE; DECISIONS; ai/INDEX; RGB sessions002/003; Git status; v2 HLS/controller/build/tests and generated AXI interfaces. No missing mandatory files.
## Task and Constraints
Owner accepts maximum corresponding corner Euclidean displacement <=16 pixels. Compare against last accepted geometry to accumulate slow motion. Refresh remains every2 seconds. Preserve working v2 and historical board versions. Credentials never recorded.
## Contributions
Investigating default AXI scheduling latency0 versus indexed reads and measured PL142.5ms. Explicit latency/outstanding and decoupling candidate require synthesis/board evidence.
## Decisions and Adoption
Threshold accepted16. New candidate isolated; v2 remains live until verified replacement.
## Commands and Tools
PowerShell/Python, GCC, Vitis HLS/Vivado2022.2; official AMD UG1399 burst/latency documentation reviewed.
## Validation and Evidence
New changes not yet tested. Prior v2 evidence is baseline, not new result.
## Errors and Corrections
None yet.
## Files Changed
This session record; candidate forthcoming.
## Remaining Work
Implement, test, synthesize, implement with timing, physical comparison and performance measurement; archive and deploy only passing candidate.
## Handoff Notes
R: belongs to v2; use distinct short mapping for v3. DDR wait attribution remains hypothesis without AXI counters.

## Scope Steering and Current Result
Owner instructed no further synthesis/deployment, added occluded-boundary hold and asked better output/text path. No combined Vivado synthesis/implementation launched. Initial HLS synthesis/export already completed before that instruction; current added failure-hold source is not regenerated into IP and must not be deployed.

Implemented edge-visibility guardian on periodic refresh; skips detector when cached boundary support lost, retains accepted reference, allows recovery. HLS failed detection now holds valid cache unless force/input interpretation change, exposes hint256; small-change hold hint512. PS masks normal hint bits and logs reasons. This is conservative boundary-support heuristic, not semantic teacher detection. Center-only person with all boundaries visible is not declared edge occlusion. No real obstruction accuracy claim.

Validated after latest source: host8fullframe legacy parity PASS; geometry threshold equality/diagonal/cumulative/reset/disabled/failure hold PASS;6 synthetic visibility/brightness/partial-left/recovery/coherent-motion/rotation tests PASS; all Python AST parses PASS. Generated fetch-only RTL request-interface test256ordered pixels with64cycle modeled response/ready/output stalls PASS:66 requests pending before first response,408cycles. It does NOT measure physical DDR or AXI adapter/system performance. Actual generated top parameter USER_MAXREQS69 vs v2=5; external read outstanding32 vs16. HLS warp initial source II1 and20.737ms estimate; board/new timing unexecuted.

## Errors and Corrections (additional)
Windows defaultGBK read failed on UTF8 Python comments; restored affected software from original with explicit UTF8, then applied changes. S: subst initially sandbox denied; approved sandbox-external mapping succeeded. Initial HLS tool MSYS signal-pipe access failed in sandbox; exited then approved external build succeeded. Fetch RTL bench initially omitted generated flow_control module; added dependency. Initial bench incorrectly capped internal request interface at external32 outstanding, causing artificial deadlock; actual internal capacity69 and returned-data adapter buffers differ. Corrected capacity and clock-edge race. Internal addresses are word indices, not external byte addresses; removed incorrect /4 model. Final bench PASS. Do not interpret66 internal requests as66 external DDR transactions.

## Files Changed (final for this stage)
Candidate hls/board_rectify_rgb.cpp, geometry_gate.h, build.tcl; software/rectify_rgb.py, run_pipeline.py, boundary_guard.py, prepare_dts.py, verify_kernel.py, verify_direct_display.py, validate_and_smoke.py; tests/test_optimized.cpp, test_geometry.cpp, test_boundary_guard.py, tb_fetch.sv; vivado/integrate_rectify.tcl; deployment.json/README; source copy kv260-whiteboard-enhance/rtl/imx219_rgb_rectify_v3; generated header evidence; internal decision/state/index/session.

## Display Architecture Findings
Current PS CPU/PYNQ frame-copy path is not essential for adding text. PL overlay in AXI-Stream can receive small PS character/location/color commands; no whole-frame CPU roundtrip. OptionA finalsharedDDR+DPDMA requires correct address/stride sharing. OptionB PS DP Live Video can bypass output DDR, needs PL native timing/pixel clock/device tree/driver configuration. Chip support confirmed officialAMD UG1449/UG1085; old-kernel bridge/newDRM differences from AMDwiki. Board5.15.0-1027-xilinx-zynqmp CONFIG_DRM_ZYNQMP_DPSUB=m andXLNX_BRIDGE/MIXER/PL_DISP enabled, live function unverified. No board display changes. Input arbitrary perspective/180rotation storage and camera/display rate matching remain independent buffering problems. Drop whole input frames at SOF; continuously scan out/repeat lastcompleteoutput, not skip displaytiming.

## Current Status / Handoff
Source/local validation completed for this stage. Architecture exploration documented; character overlay/live display not implemented or adopted. Further HLS/full synthesis/implementation/board deployment deliberately deferred at owner's instruction. Existing v2 PID23845/FPGAoperating confirmed read-only, current/state31files preserved and hashed at history/whiteboard_candidate/20261001-before-ddr-stability. Local deployment config still points workingv2. Newformalv3 hasno firmware and current sourcesdoNOTmatchinitialexport. Remaining: realvideo boundary tests/algorithm calibration; selectsharedDDRvsDPlive with validtiming/buffers; specifyfonts; onlythen combined rebuild/timing/physical differential/performance and authorized deployment. No newFPS claim.

## Architecture Evaluation Follow-up (started)
Owner proposes startup/manual calibration, initial camera-direction OSD, color normalization to white/black/red/blue, teacher-history restoration IP and directHDMI, PScontrol. This turn evaluates feasibility only; no further synthesis/deployment remains binding. Existing session004 selected before substantive evaluation. Read rootpolicy/state/decisions/index/session and Git, officialAMDvideo/display docs. Need distinguish calibration detection vs per-framewarp, preserveRGB/luma evidence beforepalette, historyvalidity/erasure/reset and displayratebuffering. No new measuredperformance.

## Startup Calibration / Palette / Restoration / HDMI Evaluation (complete)
Feasible target architecture, not implemented/adopted as final architecture. Calibration detector/H fitting can run until consecutive valid stable observations then lock; per-frame perspective warp continues with fixedH. ExistingcachedPL142.5ms andrefreshed187.7ms demonstrate lockingdetectordoesnotremove dominantwarp/readcost; periodicv2 alreadycachesH. No speedup estimate promised. Manual recalibration needs transactional frame-boundarymatrix switch and historycoordinate reset/generation; camera/boardmotion may produce warning withoutautomaticHupdate.

Recommend PLcapture/ISP -> addressablegeometrycache+fixedwarp -> illumination/colorfeatures -> paletteclassification plus retainedluma/chroma/foregroundconfidence -> guardedhistoryIP -> white/black/red/blue palette -> OSD -> displaybuffer/timing/output. PSstate/controlonly. Do not quantize allRGB tofourcolorsbeforeforegroundmask: skin/clothes becomeclasslabels and rawmotion/colorevidence islost. Guardteacher/staticforegroundupdates using observedvalidmask/confidence/quiettimestamps; newwriting immediately visible but backgroundcommits delayed. Genuineerasuremustupdatehistoryafterunoccludedconfirmation. Never-in-view/occluded-firstbackground cannotrestoreunknownwriting; do not use futureframes. ReuseguardedV7coreideasonly; completePLcompositorunverified, teachercontaminationstillknown.

Packed4classhistorytheoretical2bits/pixel=518400bytes1080p (vsRGB8886220800bytes,12xrawpayloadreduction); addingvalidity/confidence/age/previousstateandDMAalignmentincreasestorage. Class+statebytefirstimplementation2073600bytes/frameplausibleproposal; notresource/performanceverification. Geometry/inputandhistorybuffermemoryremainsnecessary; sequentialbursthistory canbeefficientwithoutCPUframecopy. 1080p30active62.208Mpixel/s,100MHzII1sufficientarithmetictheorybutmemory/multiplepasses/blankingtimingstillneedmeasuring.

KV260hasHDMIJ5andDPJ6. AMDKriaFAQstatesbothdrivenbyPSDPcontrollerthroughcarrierDP/HDMIsplitter; cannotassumebarePLAXISdirecttoHDMIpins. EvaluatePLnativevideo/VTC->PSDP live->carrierHDMIorfinalbuffers->DPDMA->HDMI. Currentdrivers/livepathunverified. Needcontinuousdisplaytimingandlast-completeframerepeatforlowerprocessrate; droponlywholeinputframesatSOF.

Primarysources: https://xilinx.github.io/kria-apps-docs/faq/build/html/docs/faq.html ; https://docs.amd.com/r/en-US/ug1089-kv260-starter-kit/Interfaces ; https://docs.amd.com/r/en-US/ug934_axi_videoIP/Video-Subsystem-Bandwidth-Requirements ; AMDUG1449DPandLinuxwiki referencedabove. Localguarded_restoration.md/reportrestoration_v7andwhiteboard_restore.hchecked.

Validation this follow-up: staticcode/designreviewandprimarydocumentationonly. No codechanges,newtests,synthesis,boardwritesorperformanceexperiment. Remainingimplementation scopeunchanged; ownerhasaskedfeasibilityevaluation, notresumedbuilds.
