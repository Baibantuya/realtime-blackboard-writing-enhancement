# AI Session: 2026-10-08-002-shared-ring-rectify-build
- Date: 2026-10-08
- Operator: Project owner
- AI product/model: Codex / GPT-6
- Participants: Project owner, Codex (single agent)
- Objective: SSH leisheng@[private_ip], clone /data1/leisheng_codex/wb_restore_system_roi_scalar_20261007 into new independent project, implement update.md001/002/003, validate/synthesize/route and deliver matched bit/HWH/DTBO/PS automatic deployment package locally for owner board use.
- Status: Complete (matched local delivery; owner board acceptance pending)
- Report candidate: yes
- Related commits: none yet
## Context Read
Previously read root AGENTS.md, AI_DEVELOPMENT_POLICY, state/decisions/index and related RGB sessions. This turn reread current state/decisions/index, update.md and Git state. All mandatory local files exist. Remote rules/source pending inspection.
## Task and Constraints
User explicitly authorizes new project/implementation/synthesis, superseding prior no-synthesis constraint for this isolated candidate. Preserve supplied previous project/firmware. Deliver under local test_workspace new folder; user performs board deployment. Formal source/reproduction delivery copied to kv260-whiteboard-enhance as required. No board modifications/loads assumed authorized. Do not record secrets or claim board performance before owner tests.
## Contributions
SSH authenticated via existing key; remote base exists. New source/build/deployment work pending.
## Decisions and Adoption
update.md001/002/003 are authorized implementation scope. Architecture/register/kernel/interface changes recorded as concretized.
## Commands and Tools
PowerShell/OpenSSH; first sandbox network denied (port22Permissiondenied), reran with approved escalation and connected. No password needed/recorded.
## Validation and Evidence
Remote host and base directory read successfully. New tests/build/timing/board: 未执行.
## Errors and Corrections
Network sandbox denied firstSSH; approved externalSSH worked.
## Files Changed
This session; later source/project/evidence and state/index/decisions/update expected.
## Remaining Work
Inspect exact remote rectifier/base/tool/boardpackage, isolate project, implement and test all3changes, HLS/Vivado route/timing/export, verify package local delivery.
## Handoff Notes
Source baseline is supplied Oct7 ROI-scalar restore system, current Oct1 v2/v3 source is reference only. zero-copy compatibility/cache/ownership and sensor Bayer afterflip need actual kernel contract, package capability gates. User retains final physical validation.

## Implementation Progress
- Created remote independent /data1/leisheng_codex/wb_shared_ring_rectify_20261008; copied only baseline RTL/Vivado source/unchanged restore IP, not previous routed bit/DCP as the new result. Local candidate test_workspace/whiteboard_shared_ring_20261008.
- Sensor initialization now uses driver hflip/vflip before capture, queries actual RAW8 Bayer format and propagates it to CSI/demosaic; no PS cv2 rotation.
- Shared capture uses actual rectifier-platform device low31-bit contiguous DMA allocation exported as DMA-BUF, V4L2_MEMORY_DMABUF(4), four frames, read-only CPU mapping. Exporter checks camera DMA mappings equal contiguous expected address, rejecting IOMMU/bounce/alias rather than implicit copies. Separate descriptor-only drain worker preserves one PL-held, one newest-complete and at least two camera slots; no live ingress copy. CPU READ sync and PL start/done lease gates; source released after rectifier, not after restore. Driver not loaded on actual board.
- Minimal sparse8+8profiles/green-difference/innerboundary/4linefit tracking implemented in PS; periods2s/gate16px/confirm3 default. AcceptedH/canvas/ROI hold onsmallchange; explicit manualglobalrecalibration confirms even small changes; uncertainmotion suspendsrestore untilconfirmed/resolved; truegeneration updates resetrestore history.
- New HLS packedRGB888 uint32src/dst uses external20-word acceptedgeometry plus four64-byte inputcachelines reset percall and DATAFLOW coordinate/fetch/pack/write stages. Legacy mesh/detector removed. Preserved3master bundles/top/controlbase; generated32-bit pointer registerlayout differs fromold64bitpointers: src0x10,dst0x18,status0x20,hint0x28,corners0x30,binary0x38,mode0x40,threshold0x48,bgr0x50,geometry0x58. PS updated from generated header, not old offsets.
- Native20full1920x1080 cases PASS (primary40validoutput comparisons inclsourceaddressreuse, atomicinvalid20); HLSCSIM/CSYNTH and VerilogCOSIM60calls32x24PASS. Not fullHDRTL/board claim.13LinuxsoftwaretestsPASS includingshadow/slanted/occluded synthetic detection, acceptedreferenceaccumulation, manualgeneration, uncertainmotion, brightgreenintegeroverflow regression, actualregisterprogramming, timeoutpinning, streamworker ownership and sensorflip/Bayer commandorder.
- Framepoolmodulecrosscompiled ARM64 against Ubuntu5.15.0-1027-xilinx-zynqmp.31headers+Module.symvers; ELF/vermagic verified; no actual insmod/board test. OlderGCC10 vs kernelGCC11warning recorded; no kernelupgradeperformed.
- Automaticdeploy packaging now supports opt-in package_board_runner/package_overlay_helper/package_readme, allowing matchingDMA-safeversionedhelpers; validation_files carries KO/sourcearchive. Legacypackages keep defaults. No existing local deployment config/auth modified and no board upload/load.
- Fullstandard2021.2 systeminitialbuild failed6vendorHLSIPexports due signeddecimal-date core_revision overflow. Local generated mainIPrevision bounded; inheritedofficialY2K22patch sourced in candidate6failedHLSruns, all6manualexportsPASS. CandidateprivateHLSlauncherpatch and standard recovery nowresetsunfinishedOOCs and reruns; no sharedtoolinstallation edits/oldcheckpointstitching. Initialfailedlogs retained.
## Errors and Corrections (progress)
2021.2 open_project absolute path rejected; cd build/open simpleprojectname fixed. InitialPS pointeroffsetassumption64bits corrected toactual generated32-bitheader. Windowsruntime test cannotimportfcntl; movedLinux tests to isolatedservervenv. Kernel dev_is_dma_coherent neededdma-map-ops include. PrivateHLSwrapper stringformat nestedpercent bug corrected. One inlineSSHpythonquoting probe failed, replacedwithfile-basedinspection. Detectorint16luma overflow atbrightgreen correctedint32 andtested. Manualrecalibration anduncertainmotionhistory gates added/tested. No failedresult omitted.
## Current Verification Limits
No remote boardlogin/programming, physicalsensorcontrol/Bayer/imagequality, DMA-BUFcameraimport/alias, coldboot/longrun/FPS test. User performs boardacceptance; package includesfullframeidentity+restoreinitialization smoke. Fullsystem routedtiming/bit/HWH/DTBO export andlocalarchivehash verification stillpending.

## Final Delivery
- Complete owner-requested candidate implementation/build/local delivery. User's latest steering stops expanded experiments; only matched package assembly/checksum completion performed afterwards. Board deployment remains owner action.
- Final corrected-clock routed timing WNS+0.464/WHS+0.010/WPWS+0.164ns, violation totals0, no_clock/unconstrained_internal_endpoints/multiple_clock0, no methodology Critical Warning. Clock Wizard duplicateprimary andjitter removed fromfullroutedXDC; truePSprimary jitter0.100 retained, generated100/200/200MHz validated; placement/routing unchanged. BitgenDRC0errors (ordinary vendorwarnings retained). Final56723LUT/68581FF/78.5BRAMtiles/158DSP. No power/FPS claim.
- Originalstandardrecovery hit missingopenBD atwrite_bd_tcl afterroute; fixedwith explicitopenBD beforeexport and directbitgen fromclock-verified routeddesign. XSA successfully generatedbyVivado include_bit, no hand-built fakeXSA.
- Matchbit/HWH/DTBO/rawBootgenbin/XSA exported; unchanged restoration IP67files byte-identical tobaseline. HWHtimestamp precedesbit because it isgeneratedBDmetadata; actualABI/pointerwidth/registeroffsets checked. Compiledoverlay externalphandle warnings are baseline standalone-overlayfixups, compiledfixup/newnode/firmwarename verified. Actualloadingunverified.
- Delivered E:/code/fpga-competition/test_workspace/whiteboard_shared_ring_20261008/board_package and whiteboard_shared_ring_20261008_board.zip,27flatZIPfiles/4643158bytes. Native25board-artifact/runtime SHA256 plus allbundle entries verified; ZIPCRC PASS. BIT29f456b0ad380ab838338162a1fd68069ef02a79503f0634c857847b459db06b; HWHf4f402c14b49cfd7750a7c073e130adb37759d70725870d887d621aa7a70edbd.
- Finalsource/PS copiedto formal rtl/imx219_shared_ring_rectify_v4; opt-inhelper supportin scripts/deploy_to_kv260.py; update.md001/002/003 markedimplementedcandidate/unverifiedboard. Originalremoteproject andlocaldeploymentconfig untouched.
## Additional Errors and Corrections
PrivateHLSlauncher firstinheritedvendorPYTHONHOME andfailedPythonencodings; shebang -E fixed, originalfailedlogs retained. InlinePowerShell-expanded remotePATH causedvivado-not-found; replacedbyfile-basedrun_recovery.sh. FirstautoZIPdeployment.json hash mismatch due WindowsCRLF vs archiverLF serialization; generatedflatmanifest bytes normalizedLF andZIP rebuilt/reverified. No failedtest orbuild accepted aspass.
## Final Validation Limits / Remaining Work
Actual moduleinsmod, V4L2DMABUFcameraimport/physicalsharing, sensorregisterBayer/color/direction, display, coldboot, longrun, realdetectoraccuracy/restorationquality/FPS: 未执行. Driverprebuilt targets5.15.0-1027-xilinx-zynqmp/ARM64; deliveredsource foranotherkernel. HLSmaxlatency bound1.348s is a dynamic/cache-miss worst-case estimate, not boardperformance; smallRTLtests cannotprovefullHDlatency. Userrun.sh deploy performsidentity/restore-init smoke, then live; no boardconnectedwrites byagent.
## Files Changed / Handoff (final)
Candidate source, board_package, evidence andZIP; formal rtl/imx219_shared_ring_rectify_v4 and scripts/deploy_to_kv260.py; update.md; session/decisions/state/index. Source trees containcode/reproduction, notinternalconversationlogs. No new simulation/profiling afterownerrequestsjustpackaging.
- Status: Complete (build and matched local delivery; owner board acceptance pending)

