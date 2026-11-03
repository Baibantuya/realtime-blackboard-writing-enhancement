# AI Session: 2026-10-12-007-restoration-optimization-assessment
- Date: 2026-10-12
- Operator: Project owner
- AI product/model: Codex / GPT-6
- Participants: Project owner, Codex (single agent)
- Objective: 评估局部恢复、RTL DDR burst搬运、低开销卡尔曼思路对帧率和近静止人物/阴影遮挡的作用。
- Status: Complete (assessment only; not implemented)
- Report candidate: no
- Related commits: 无
## Context Read
已按序阅读AGENTS、政策、状态、决策、索引和近期B32/565会话及Git状态；长历史输出部分截断，当前相关记录完整读取。质量会话首次路径错误，已发现正确文件名待补读。
## Task and Constraints
用户要求先评估不修改；不修改代码、配置、固件或正式报告，仅按项目规范写内部记录。算法/架构建议不等于采用。
## Contributions
待补齐代码证据、瓶颈边界和建议。
## Decisions and Adoption
待评估，未采用新实现。
## Commands and Tools
PowerShell只读代码/记录/Git审查；必要官方技术资料核对。
## Validation and Evidence
仿真、综合、实现、上板、性能测试：未执行。
## Errors and Corrections
初次质量会话文件名猜错，发现正确路径后纠正；长历史输出截断不声称完整读取。
## Files Changed
本记录；完成后更新内部索引/状态/决策提案。
## Remaining Work
完成评估与交接记录。
## Handoff Notes
最新565会话尚在部署恢复，不能假定已运行；B32历史7.5927FPS日志host耗时不能当独立IP上限。


## Final Assessment (Recommendations Only)
- Source reviewed: latest formal RGB565/B16 source/hls/whiteboard_restore.cpp, guarded_state.cpp, whiteboard_restore.h, build_restore_quality.tcl and runtime whiteboard_ip.py/pipeline_stages.py; related v6 quality and paper-guided historical assessment read. Formal/source algorithms not modified.
- Local ROI currently means board participation; render_frame still processes the complete frame. compose reads/writes background, previous and per-pixel quiet over every pixel even when history values remain unchanged. Merely narrowing roi or gating output replacement does not remove these costs.
- Proposed architecture: board-wide sparse block detection/state update -> active row-span descriptors -> RTL burst transport with bounded FIFOs -> local pixel morphology/compose -> complete output via direct input bypass for inactive pixels. Active work includes actual occlusion, suspicious boundary, reveal/exit confirmation and visible new-writing/erasures awaiting trusted commit. Preserve normal-region history maintenance through a dirty/periodic scan policy; step4 sparse samples can miss thin new strokes, so sparse-only maintenance is not equivalent. Previous sparse samples must advance for all blocks; per-pixel previous/quiet state must be refreshed/reset upon ROI entry, not compared with stale skipped frames. Requires new scheduling/state contract and reference validation.
- Keep distinct true replacement mask, computational region and transport expansion. Align/merge horizontal spans to AXI beats/burst units, not a single giant person bounding rectangle or automatic longest256-beat bursts. Current RGB565 16x16 block has only32 contiguous bytes per row; neighboring blocks can merge into128/256byte spans. 64-bit16beats=128B=64pixels is an illustrative proposed interface, not a verified existing bus. With current32-bit packed interface,16/32/64beats=64/128/256bytes=32/64/128pixels. AXI4 burst cannot cross4KB; real route/HP/interconnect widths and arbitration determine best size. Padding loaded for transfer must not expand logical replacement/history commit.
- Local filters need halo: local_ink radius3; broad path erosion3+dilation3+dilation1 has total spatial dependence radius7. Crop processing must preserve7pixel halo and original frame-edge padding, in addition to block-level mask/protection expansion. Read halo, write core only.
- Logical RGB565 steady compose traffic = N*(input2+output2+background4+previous4+quiet2)=14N=29.0304MB/frame for1080p. Sparse block feature stage roughly129600 samples*3 arrays*4bytes=1.5552MB useful32bit reads, excluding bus fetch amplification. State metadata additional. Hypothetical unchanged-cost active pixels plus full input/output bypass: N*(4+10r), r=25% yields13.4784MB before sampling/halo/dirty work. This is arithmetic/model, not measured bytes, guaranteed reduction or speedup; no skipping-history parity claimed.
- Near-static failure evidence: guarded_state lines41/45/63/68 seeds require dense weak plus motion/new occupancy; TTL decrements and core requiresTTL>0. Runtime defaulthold6. Sustained background difference alone does not refreshTTL. Thus absent new seeds/neighbor seeds, a stationary occluder can lose replacement despite history not contaminated. whiteboard_restore lines176/181/182 prove protected history writes do not independently preserve display mask; thin-ink exception may expose/commit person edge texture. Global dense>=75% special path outputsM=0,W=0, freezing history but not forcing restored display. These are code mechanisms, not confirmed scene root causes.
- Quality priority: evidence-gated persistent occlusion, explicit clear-board/reveal confirmation and separate thin-writing/erasure release, rather than only extendingTTL. Continuous difference is not sufficient by itself because new dense drawing/erasure can also differ from history. Release observations combine background agreement, sparse/thin writing evidence and bounded temporal/neighborhood plausibility; RGB-only ambiguous long stationary objects remain a limit. Separate M display from W trusted commit, including fine-path ownership.
- Kalman idea: valuable for block-level confidence/noise/illumination smoothing; cannot create occlusion observations or distinguish static person by itself. First candidate fixed-gain integer filter C += (Z-C)>>k with rounding/saturation plus fast-entry/slow-exit hysteresis, gate unreliable measurements and background commits. This is Kalman-inspired/IIR, not full covariance-updating Kalman. One8bit score per8160blocks =8160bytes logical additional state, can use packed existing/external state and sequential engine; actual BRAM/area must be synthesized.
- True scalar Kalman optionally estimates trusted clear-board illumination with x/P and K=P/(P+R); do not feed stationary foreground into background estimator. x16+P16 per8160blocks=32640bytes logical state before packing. LUT gain or shared fixed-point reciprocal avoids independent floating division perblock; Q/R and elapsed-time behavior require calibration. No per-pixel RGB Kalman or whole-frame covariance buffers recommended. Actual resources not measured.
- Latest565 session004 reports routed79775LUT/120BRAM/239DSP/CLB99.13%; B32 historicalCLB99.80%. No current board throughput measurement in this assessment; deployment is independently underway/blocked onmedia in other records. Design should replace existing DDR adapters/full-frame work, share small engine/FIFOs, avoid replicated neighborhood buffers or many outstanding bursts. LUT percentage alone does not prove placement headroom.
- Proposed validation order: same-frame rectified/restored/quantized/background and blockO/M/TTL/W trace for enter->stand->leave/shadow; independent completion timing and actual acceptedAXIbeats/stalls; quality-only latch/filter A/B; then locality/burst A/B. Include newthin/colorwriting,erasure,reocclusion,ROIboundary/halo,slowframe/drop/geometryreset and contaminatedinitialbackground. No tests executed in this session.

## Sources Checked
- AMD UG1399 2021.1 Summary https://docs.amd.com/r/2021.1-English/ug1399-vitis-hls/Summary : burst inference, pipelining, width and arbitration distinctions.
- AMD UG1448 2021.2 Burst Inference Failure10 https://docs.amd.com/r/2021.2-English/ug1448-hls-guidance/Burst-Inference-Failure-10 : conditional access can block inference.
- Arm AMBA AXI/ACE IHI0022H https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/IHI0022H_amba_axi_protocol_spec.pdf :4KB/256INCR protocol constraints (search extract).
- Kalman1960 original research available via Duke https://people.duke.edu/~hpgavin/SystemID/References/Kalman-JBE-1960.pdf (search extract). UNC Welch/Bishop directfetch unavailable; not used as fetched full text evidence.

## Final Decisions and Adoption
D-091 proposal only; no algorithm/interface/parameter/tool adoption approved or implemented. User asked assessment only.
## Final Validation and Evidence
Static source/records and official documentation reviewed. Traffic/state sizes are analytical calculations. New simulation, synthesis, implementation, board tests, FPS and recovery-quality measurements: 未执行.
## Final Errors and Corrections
Generated IP/evidence guessed subpaths absent locally; no generatedAXI or new resource verification claimed. Discovered concurrent session005 board-deployment and session006 same-topic initial record; renamed our new record to007 to avoid duplicate sessionID. Did not alter either record or message other chat. State/decision/index updates are append-only to preserve concurrent work.
## Final Files Changed
project_workspace/ai/sessions/2026-10-12-007-restoration-optimization-assessment.md; project_workspace/ai/INDEX.md; project_workspace/PROJECT_STATE.md; project_workspace/DECISIONS.md. No formal/source/config/firmware/test modifications.
## Final Remaining Work and Handoff
1. Isolate actual near-static failure across aligned frame stages and M/W/TTL history.
2. Validate persistent occlusion and low-cost block filter without hidingnewwriting/erasure.
3. Design row-span transport and history maintenance contract, then synthesize/profile ROI and burst sweeps; no FPS promise before real measurements.
## Final Status
Complete: read-only restoration optimization assessment; suggestions not implemented. No subagents used.


## Follow-up: Concrete Modification Handoff
- 用户要求生成可交给另一对话的明确修改文件；沿用本会话记录。
- 本次只创建内部交接说明，不实施恢复IP/PS/固件修改。
- 读取最新状态：独立565部署存在media/内核恢复问题，不能假定565实时链路可用；交接将明确离线开发与实际板测依赖。
- Planned file: project_workspace/ai/handoffs/restore_optimization_modification_spec_20261012.md。

## Follow-up Completed: Concrete Modification Handoff
- Created project_workspace/ai/handoffs/restore_optimization_modification_spec_20261012.md，包含基线文件映射、M1～M8修改项、P0～P4实施顺序、历史有效性/halo/burst/完整输出所有权、低开销置信度、质量/RTL/性能验收及未完成事项。
- 用户要求的文件已生成；内容明确仅文档交接，不把建议当已实施，也不替另一个对话推定部署授权。
- 文件存在/章节/阶段完整性检查完成；未执行代码测试、仿真、综合、上板或新性能测量。
- 本次文件修改：上述handoff、本会话、INDEX、PROJECT_STATE、DECISIONS（D-091交接补充）。正式代码/配置/固件未修改。
- 遗留：用户将文件交给另一对话；接手按实际授权、最新版本/板端状态和工程记录继续。
