# AI Session: 2026-10-20-001-v22-fusion-presynthesis
- Date: 2026-10-20 (Asia/Shanghai)
- Operator: User
- AI product/model: Codex / GPT-6
- Participants: User and Codex; single agent, no delegation
- Objective: Implement the agreed v20/v21 fusion plan and stop before synthesis.
- Status: Complete for source/native checkpoint; STOPPED_BEFORE_SYNTHESIS
- Report candidate: no
- Related commits: none; formal project and tests initially untracked
- Related files: handoffs/2026-10-19-v20-v21-fusion-plan.md

## Context Read
Root AGENTS.md, AI_DEVELOPMENT_POLICY.md, current PROJECT_STATE.md, relevant DECISIONS D-125..135, INDEX.md, sessions021/022 and both glare/fusion handoffs; Git status; v21 Q/tracking/build scripts. No nested AGENTS.md found. Historical state/log sections not relevant to this task are not claimed as fully reviewed.

## Task and Constraints
Independent v22 source candidate; sealed v21 r5 rollback unchanged. Freeze eight v15 sources, two-core architecture, same-frame ownership and visible-only Canvas admission. Native C++/software regression and real-frame replay allowed; HLS synthesis, Vivado synthesis/implementation, deployment and board operations not performed. Stop before any synthesis. Real13426 includes a person and is never trusted startup material; true hue annotations/trusted additional captures are unavailable locally.

## Contributions
Created independent formal dma_rgb565_fusion_v22 source, retaining sealed r5. Integrated 7x7 positive local contrast, strong/weak directional stroke evidence, symmetric red/blue confidence/neutral-hole propagation, dim-material thresholds and nonoverlapping dim erasure evidence. Local PS material retains broad illumination. Added continuous 5x3 zonal exposure normalization and admission coordination after user clarified scene/light changes. Frozen eight v15 files, two-core and A/B ownership contracts remain.
## Decisions and Adoption
Adopted D-136 within user authorization. User initially accepted bright v22_7 but identified missing dark writing and blue-to-black/missing blue (both options). User then requested continuous PS exposure to a relatively fixed PL input effect, superseding the initial choice to keep AE frozen after lock; final candidate continuously meters/controls and holds new input during normalization. User explicitly required red to receive the blue corrections too; implemented shared red/blue logic rather than a blue-only final patch. No autonomous synthesis/deployment authorization inferred.
## Commands and Tools
Native: python -B -X utf8 kv260-whiteboard-enhance/rtl/dma_rgb565_fusion_v22/source/scripts/validate_local.py --output test_workspace/v22_fusion_20261020/red_blue_ae_verified

Actual C++ Q A/B: python -B -X utf8 kv260-whiteboard-enhance/rtl/dma_rgb565_fusion_v22/source/scripts/compare_fusion.py --input test_workspace/v21_glare_color_20261019 --output test_workspace/v22_fusion_20261020/red_blue_ae_compare

Audit: python -B -X utf8 test_workspace/v22_fusion_20261020/audit_presynthesis.py

No network/board/automation tools, no Vitis/Vivado tools invoked. Guard refusals were tested using prepare_system/export_hardware/seal_package only; they refused before accessing nonexistent hardware inputs. All experiment outputs stayed in named test_workspace/v22_fusion_20261020 children. No subagents or other human collaborators beyond user/Codex.
## Validation and Evidence
- Final actual 130 native/software checks: 0 failures/errors/skips. Bounded 64-word reader/scan/writer C++ testbench errors=0, 1920x33/padding/HOLD/erase cases. 100-frame synthetic v15+Q+tracker replay: zero initial/person-interval/final mismatches; old white448→0 at second reveal observation.
- Eight frozen files match both locked hashes and formal v15; r5 ZIP remains SHA256152b8c5d12ac1b9f28a1642ca79404ba24cc4836c410d853793cb9cf9d4c63f9. Source audit55files/3expected guard refusals PASS, tested C++/headers match final candidate; generated runtime software hashes match source. Formal curated evidence/source_manifest.json identifies all19 added/changed source files relative to v21.
- Same raw13426, cookies/visible domain/frozen material: four reviewed bare rectangles19100px have v21 false ink1269, v20 raw28, final v22_7 zero. 5x5 probe fails synthetic width1..5 suite; 7x7 passes. Actual v20 restored-B variant is separately identified as a different pixel input; v20 quality ABI/Canvas are not equivalent to v21.
- Dark text crop diagnostic ink771→2081, blue0→369 compared with pre-dark revision. Blue outline crop black400→102 / blue792→1090 compared with pre-hue revision. These counts are not accuracy/recall: remaining ambiguous samples, actual red hue truth and complete stroke annotations remain unresolved. User identified remaining mixture; no overall color acceptance claimed.
- Continuous AE tests use mocked sensor controls and explicit lighting response, including dark→bright→other levels, rate/settle/stability gating, saturation and limits. Actual assembled main test verifies AE-paused inputs plus A/B ownership/three-stage overlap. Geometry can still obtain its existing bounded-rate snapshots during normalization. AE never learns transient/person frames into trusted material; post-lock control uses PS target80±6 by default, not a fixed sensor value. Real convergence/FPS NOT_RUN.
- Formal candidate evidence/presynthesis_validation.json, same_frame_comparison.json, annotated_regions.png, dark_detail.png, blue_detail.png, preview.png. Full logs/replays stay under named test workspace. All new HLS Csim/csynth/RTL, Vivado/route/resources/timing, board test/FPS NOT_RUN.
## Errors and Corrections
Large combined context output truncated; reread task-relevant files individually. No project result inferred from truncation.
- real_compare1 bare rectangles crossed an existing white vertical stroke; its false-ink aggregate is invalid. Retained original annotated input/report, corrected rectangles in real_compare2 onward; final used the reviewed independent top glare gap and three true gaps.
- First dim-threshold relaxation added10 top-gap noise pixels. Added broad-neighborhood illumination-rise guard; final four gaps return0 while dim writing improves.
- First hue expansion failed two low-signal white/white-next-to-blue tests (adaptive_verified1). RGB565 expansion turned an8-level input tint into9-level observed spread; increased confirmed-white tolerance to12 before propagation. All final white/red/blue/crossing tests pass. Failed evidence retained.
- Initial copied validation date and inherited hardware_status were stale; corrected to2026-10-20/source-only v22. An initial exposure-frozen plan became obsolete after direct user clarification; final code/docs use continuous normalization and preserve that change of requirement here.
- Review caught the risk that an early AE continue could starve geometry discovery. Refactored normalization through existing discovery/release path, keeping PL admission blocked while geometry acquisition continues; runtime integration rerun PASS. No real hardware was used to claim this correction.
## Files Changed
New formal candidate rtl/dma_rgb565_fusion_v22: README/STOP,55source files (36 unchanged copies,19 added/changed listed in source_manifest.json), curated validation evidence. Principal changes: Q cpp, local material, continuous auto_exposure.py, runtime assembler, candidate identity/export/sealer/verification, local test builders/validators/comparison, quality/exposure/runtime tests. New named experiment workspace. Internal session/handoff/STATE/DECISIONS/INDEX. No old production source/package/launcher or auxiliary files modified.
## Remaining Work
Human-confirmed real red/blue/white truth and trustworthy startup captures; actual AE across occlusion/scene/flicker/color changes and sensor limits; remaining blue/black ambiguity; broad lettering and local material scale. Future authorized HLS II/storage/AXI, route/nonnegative timing/device capacity, matching package and sustained FPS/field checks. Global exposure does not normalize every pixel or arbitrary color-temperature changes; projected foreground exclusions in camera metering are not integrated yet. Large residual reference changes can still require explicit trusted initialization.
## Handoff Notes
Preserve r5 release; no automatic build, wake or deployment is authorized by this task.
Final handoff: ai/handoffs/2026-10-20-v22-presynthesis-checkpoint.md. Six Q line buffers are23040 logical bytes (+7680vs5x5), not measured BRAM. DDR/canvas layout/ABI unchanged; source changes still need freshly matching hardware. Build target remains100MHz and real K26 capacity/nonnegative setup/hold. Future permission to synthesize must be explicit; this turn ends before synthesis.
