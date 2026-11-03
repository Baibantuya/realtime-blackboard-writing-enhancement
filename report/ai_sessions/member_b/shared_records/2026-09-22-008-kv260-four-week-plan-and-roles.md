# AI Session: 2026-09-22-008-kv260-four-week-plan-and-roles

- Date: 2026-09-22
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, two on-site members, one remote member, Codex
- Objective: 基于现有 KV260 验证管线，形成四周开发计划、现场/远程分工和团队可读的数据流摘要。
- Status: Completed plan; owner review required before execution
- Report candidate: Yes
- Related commits: None
- Related files: `kv260-whiteboard-enhance/docs/kv260_four_week_plan.md`; D-035; D-036.

## Context Read

- Read root project policy/current state, D-035/D-036, the four-level performance evidence, and the current hybrid PS/PL recovery architecture record.

## Task and Constraints

- Four-week horizon; two members can access the board, one member is remote.
- Must preserve the real-time PL path while adding PS-assisted calibration, teacher localization, historical recovery and UI.

## Contributions

- Created the four-week execution plan in the formal KV260 submission directory. It stages platform spine, adaptive enhancement/UI, teacher-mask/historical recovery, and system evidence rather than scheduling by individual clock time.
- Assigned two on-site roles to board I/O and PL integration, and the remote role to independently testable reference algorithms, segmentation evaluation, UI and metrics.
- Defined frame-ID/time/validity contracts so asynchronous PS/DPU results cannot corrupt PL historical recovery.

## Decisions and Adoption

- Plan applies D-035/D-036 and is a proposed execution baseline. The project owner should confirm the priority order and the CSI-2/HDMI hardware availability before work starts.
- User clarified the immediate goal: first run HDMI output, then optimize PL and PS algorithms. Recommended sequencing is HDMI test-pattern/known-frame bring-up first, followed immediately by CSI-2 integration in the same first platform phase; do not postpone CSI-2 until after algorithm development.
- Updated the formal four-week plan and role matrix accordingly: on-site A owns HDMI-first then CSI-2 bring-up; on-site B owns the video/DDR/algorithm PL path against the frozen interface; remote C starts software references, segmentation evaluation and UI in parallel from week 1.

## Commands and Tools

- Read current project context and created `kv260-whiteboard-enhance/docs/kv260_four_week_plan.md`.

## Validation and Evidence

- The Markdown plan was manually reviewed for the staged deliverables and role/interface consistency. No hardware implementation or performance validation occurred in this planning session.

## Errors and Corrections

- None.

## Files Changed

- `project_workspace/ai/sessions/2026-09-22-008-kv260-four-week-plan-and-roles.md` (created).
- `kv260-whiteboard-enhance/docs/kv260_four_week_plan.md` (created).

## Remaining Work

1. Owner confirms CSI-2/HDMI availability and assigns named people to A/B/C roles.
2. Start with HDMI test pattern, then insert CSI-2 into the already verified HDMI path; develop algorithms against the frozen AXI4-Stream contract in parallel.

## Handoff Notes

The plan deliberately preserves UVC/PYNQ as a fallback/algorithm verification route while avoiding a false claim that it is the final 1080p30 input path.
