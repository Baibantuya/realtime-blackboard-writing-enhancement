# AI Session: 2026-09-22-007-kv260-hybrid-ps-pl-board-recovery-architecture

- Date: 2026-09-22
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 依据《板书增强 技术路线》并适配 KV260，重新规划光照/黑板自适应、教师遮挡检测、历史板书恢复和 UI 所需的 PS/PL 协同数据流。
- Status: Completed architecture recommendation; not implemented
- Report candidate: Yes
- Related commits: None
- Related files: `板书增强_技术路线_v1.docx`; D-035; this record.

## Context Read

- Read `板书增强_技术路线_v1.docx` through OOXML text extraction. Its renderer could not run because bundled LibreOffice was unavailable; no visual layout claim is made. The document specifies v1 PL ISP-lite/correction/illumination/pen enhancement, while teacher segmentation, temporal recovery, and DPU are v2/v3 scope.
- Read current KV260 four-level evidence: UVC MJPEG decode is the bottleneck, while PL/DMA supports the required stream rate. D-035 selects a future CSI-2 PL-first route for stable 1080p30.

## Task and Constraints

- User requires adaptive light/blackboard location correction, teacher occlusion localization, historical-frame board recovery, and a simple UI. These require PS control/state assistance but must not reintroduce PS full-frame decode/copy into the real-time path.

## Contributions

- Defined a three-plane hybrid architecture: PL fast pixel plane, PS/DPU analysis/control plane, and PL/DDR temporal board-state plane.
- Assigned PS to low-rate scene interpretation, DPU scheduling, tracking, parameter/version control, history safety policy, UI and telemetry; assigned PL to every-frame pixel transforms, mask application, temporal blend/composition, frame-buffer IO and HDMI output.
- Defined required contracts: frame IDs/timestamps join asynchronous segmentation mask to its input frame; stale/low-confidence masks cause conservative history update; recovered pixels must have a visible indicator as required by the source document.

## Decisions and Adoption

- Proposed D-036: do not let PS process full-resolution frame pixels in the hot path. Use a PL-produced decimated analysis branch and control messages returning via AXI-Lite/DDR.
- The historical clean-board update is a per-pixel DDR/PL operation, not a PS NumPy/OpenCV loop. PS controls whether/where it may update and preserves provenance.

## Commands and Tools

- Read the route document with bundled Python/docx OOXML text extraction; local search/read of prior KV260 architecture records.

## Validation and Evidence

- Architecture review only. No DPU model, segmentation accuracy, mask latency, VDMA multi-buffer path, CSI camera, HDMI output, or end-to-end recovery validation executed.

## Errors and Corrections

- The source DOCX explicitly classifies recovery/DPU as v2/v3; describing it as currently delivered v1 would be inaccurate. The recommendation is a staged architecture that permits those features without moving the pixel hot path to PS.

## Files Changed

- `project_workspace/ai/sessions/2026-09-22-007-kv260-hybrid-ps-pl-board-recovery-architecture.md` (created).

## Remaining Work

1. Freeze the AXI4-Stream Video and DDR buffer contracts, including frame IDs and stale-mask behavior.
2. Choose/deploy a teacher segmentation model and establish latency/accuracy targets at a decimated resolution.
3. Implement and test the PL temporal clean-board engine, provenance overlay, UI control plane, and safety fallbacks.

## Handoff Notes

PS participates continuously, but as an asynchronous state/control service; it is not on the per-pixel/per-frame display critical path.
