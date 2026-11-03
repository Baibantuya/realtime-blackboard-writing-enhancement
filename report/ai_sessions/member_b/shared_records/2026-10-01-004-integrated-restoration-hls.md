# AI Session: 2026-10-01-004-integrated-restoration-hls

- Date: 2026-10-01
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Owner and Codex; no delegation
- Objective: Port all restoration-side processing into a synthesizable full-frame HLS top accepting corrected, temporally stable frames and returning restored pixels.
- Status: Complete (local migration, validation and packaging; board integration remains future work)
- Report candidate: Yes
- Related commits: None

## Context Read
Read root AGENTS, policy, state, decisions, index, latest restoration session, Git status and guarded HLS/host sources. Prior user authorized implementation and final testing. Existing media, rectification firmware and earlier cores remain preserved.

## Task and Constraints
Preserve sampled differences, TTL/12-neighbor propagation and trusted historical replacement. Input correction/coordinate stabilization is upstream. Port sampling, state orchestration, full history/previous ownership, pixel quiet counters, fine-stroke morphology, background commits and RGB output selection. Use named root test folder; no root build artifacts. No board performance claim from simulation.

## Contributions
Implemented a complete HLS frame top and persistent DDR layout; reused guarded_state internally and moved all previous host restoration pixel operations into streaming/line-buffer code. Added native adapter/builder, full-frame oracle vectors and Vitis C/RTL TB, independent actual RTL DDR comparator, export/package/register generator, PYNQ launch controller, real corrected-video replay and integration documentation. Adoption: implemented under owner's requested scope; visual algorithm is the existing V7 candidate.

## Decisions and Adoption
Implement one memory-mapped frame IP using dense packed RGB888/BGR888 words, compatible with existing packed rectification output layout. Full frame data/history stays in caller-allocated external DDR, accessed by the IP; software allocates/initializes control and launches frames, without doing restoration pixel processing. Morphology streams and line buffers avoid on-chip full image arrays. Initial clear frame mode explicitly seeds history and states. Input/output/state buffers remain distinct and persistent across calls. Stream-only wrapper/board wiring is separate from this functional frame IP.

## Commands and Tools
Vendor MinGW GCC8.3 builds via scripts/build_whiteboard_native.py (final -O3, earlier video build -O2); actual HLS C++ sources. tb/test_whiteboard_restore.py produces binary vectors. run_whiteboard_hls.ps1/tcl uses Vitis HLS/XSIM2022.2 on xck26-sfvc784-2LV-c,10ns, Csim/synthesis/cosim/export. Final run hls_v4; earlier failures hls,hls_v2,hls_v3 preserved. compare_whiteboard_rtl.py independently parses actual AXI memory. package_whiteboard_ip.py derives registers from generated driver and exports ZIP/repository/header/reports. Vivado2022.2 check_whiteboard_ip.tcl actually discovers/creates IP and generates output products under named ip_catalog_check test folder. evaluate_whiteboard_ip.py replays source video using existing causal homography trace from the V7 upstream preprocessing; no future clear frame is used. No board commands or deployed firmware changes.

## Validation and Evidence
Final native top:38 frame calls,84335608 compared elements,zero mismatch (output/background/previous/pixel quiet/block state). Includes full1080p and maximum1920 width with partial height17. Independent properties:immediate strokes,stable save,later occlusion restoration,global history freeze,65535 TTL seed/decay and255 quiet saturation PASS;25 invalid atomic calls and12 boundary-config frames PASS. PS controller native-MMIO emulator PASS on64bit addresses,initialization/output/history/cache/overlap/timeout/disposal. Vitis C simulation41 frame vectors plus3 atomic status checks PASS; synthesis PASS126 BRAM18,42 DSP,17833 FF,32553 LUT,7.3ns estimated clock under10ns target. Full RTL44 calls PASS; independent436996 uint32 DDR outputs zero mismatch, actual statuses[1,2,2] then41 zeros verified. RTL test-set latency min216/avg48429/max507996 cycles, not full1080p measurement. IP ZIP and extracted repository exported; actual Vivado IP discovery and all output-product generation PASS, Up-to-date. Component referenced files and package hashes checked. Real6067-frame replay in progress; not yet final video result. No board/routed timing/1080p30. Evidence under test_workspace/integrated_restoration_hls_20261001 and selected report/whiteboard_restore_ip.

## Errors and Corrections
1. Found and corrected a potential C++ short-circuit stream read before compiling: broad flags must be consumed even for non-neutral pixels.
2. First Csim failed62 words because generated expected background vectors retained references to subsequently modified NumPy history. Snapshot arrays now copied; native/Vitis C rerun PASS.
3. First synthesis rejected frame_in reads in both neutral and composition DATAFLOW processes. Replaced duplicate full-frame AXI read with one reader and delayed pixel FIFO depth16384 (seven morphology rows at1920 plus slack). Native rerun PASS; synthesis PASS.
4. First RTL compilation rejected weak as a SystemVerilog keyword. Renamed the scalar weak_threshold; added explicit pointer s_axilite pragmas to eliminate a second accidental control bundle. Final build uses one control interface. Native arithmetic normalized hash identical to the running video's earlier interface spelling; source_equivalence.json records this and identical final/RTL vectors.
5. Compose's nonpipelined outer groups yield a static1080p estimate176ms; functional migration is not realtime30 acceptance. No board results fabricated.

## Files Changed
Formal:rtl/whiteboard_restore.cpp,whiteboard_restore.h,whiteboard_stream.h; software/whiteboard_native.py,whiteboard_ip.py,whiteboard_registers.json; scripts/build_whiteboard_native.py,evaluate_whiteboard_ip.py,run_whiteboard_hls.ps1,run_whiteboard_hls.tcl,compare_whiteboard_rtl.py,package_whiteboard_ip.py,check_whiteboard_ip.tcl; tb/test_whiteboard_restore.py,whiteboard_restore_tb.cpp,test_whiteboard_properties.py,test_whiteboard_controller.py; docs/whiteboard_restore_ip.md; README.md; ip/whiteboard_restore/ exported ZIP/repository/header/reports/manifest; report/whiteboard_restore_ip/ selected evidence. Internal:session004,index,state,decisions D-067. Tests/builds/test media in test_workspace/integrated_restoration_hls_20261001. Existing original C handoff,PDF,raw video,deployed correction firmware and guarded arithmetic sources unchanged.

## Remaining Work
Complete ongoing real video replay, inspect selected visible results and finalize records. Future system integration:Vivado DDR/control/clock/reset wiring,bitstream/HWH,board deployment and routed timing/performance. Performance optimization required before realtime30 acceptance; qualitative person-removal limitations remain.

## Handoff Notes
V7 visual residuals remain algorithm limitations; migrating it must not claim those are automatically fixed.

## Final Packaging and Results
Real video replay completed:6067 consecutive1080p frames,125854818720 pixel/state elements compared,zero mismatch;240 encoded frames form a24-second visible clip. Earlier in-progress references above are superseded by this final result. Selected199s comparison was visually reviewed. Production PS controller no longer imports the OpenCV reference algorithm.

Delivered two ZIPs under kv260-whiteboard-enhance/handoff/:whiteboard_restore_source_20261001.zip (4988315 bytes) and whiteboard_restore_ip_20261001.zip (916478 bytes), with unpacked source_project and ip_core under whiteboard_restore_20261001. Source includes HLS sources,69 generated RTL/header/ROM files, vectors, software, scripts, documentation and selected video evidence. IP includes plain RTL, explicit AXI interface metadata, rebuild_ip.tcl, register/controller material and2022.2 reference IP. Each package has a SHA256 manifest.

Recipient's2021.1/2021.2 version is unknown. Adopt local Vivado RTL repackaging instead of importing higher-version component metadata. rebuild_ip.tcl actually passed in installed Vivado2022.2;69 RTL/header/ROM files preserved and output products generated. Vivado2021 was not available and was not tested. Separate source-project creation Tcl scripts were not independently executed. User requested immediate packaging and no repeated checks; no further tests performed after that instruction.

Packaging corrections: initial ROM file-type assignment rejected; corrected to IPX mif entries. Long Windows paths corrected using short project/instance names. One earlier Vivado run accidentally placed owned log/journal/cache at workspace root; moved only its identified files to the named test folder's root_artifact_correction, preserving unrelated caches.

Additional changed formal files:scripts/rebuild_whiteboard_rtl_ip.tcl,create_whiteboard_rtl_project.tcl,create_whiteboard_hls_project.tcl;docs/whiteboard_handoff.md;handoff deliverables. Final records updated. Owner requested R/S release:removed SUBST mappings R->test_workspace/rgb_rectify_fps_20261001 and S->test_workspace/rgb_rectify_ddr_stable_20261001 successfully with elevated subst /D after sandbox access denial. Original directories/files preserved.

Remaining work is system DDR/control integration,bitstream/HWH,board testing,routed timing and performance optimization; current functional IP does not establish1080p30 or perfect teacher removal. Requested packaging and drive-map release are complete.
