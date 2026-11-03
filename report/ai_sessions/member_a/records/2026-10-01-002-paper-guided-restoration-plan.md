# AI Session: 2026-10-01-002-paper-guided-restoration-plan

- Date: 2026-10-01
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: Read articles/41_40094_zh.pdf and propose repairs preserving the paper's core restoration method.
- Status: Complete: paper-grounded repair proposal; not implemented or validated
- Report candidate: No
- Related commits: None
- Related files: Original paper, C handoff block_foreground/HLS kernels, prior real-video evidence.

## Context Read

Root AGENTS, AI policy, state, decisions, INDEX, recent real-video session, Git status. No algorithm modifications or tests authorized by this planning request.

## Task and Constraints

Preserve historical background restoration; separate original paper requirements, current implementation choices, observed failures and proposed changes. Preserve source PDF and C delivery.

## Contributions

Pending paper/code comparison.

## Decisions and Adoption

Recommendations only; no production algorithm change adopted.

## Commands and Tools

PDF skill for reading text and inspecting formula/flow pages. Bundled runtime discovered.

## Validation and Evidence

New algorithm tests/synthesis/board execution: 未执行.

## Errors and Corrections

None at creation.

## Files Changed

Internal session record; subsequent state/index/decision updates to follow.

## Remaining Work

Read paper and actual state formulas, identify priority fixes and evaluation gates.

## Handoff Notes

Prior numerical parity does not establish restoration quality.

## Paper and Implementation Findings

Read all 15 pages via extracted text and visually inspected Chinese pages 2/3/4 and original pages 9/10/14 (figures 4/5 and limitations). Source PDF is unchanged. The method retains sampled block background/frame differences, a waiting timer, 12-neighbor cross-frame propagation and immediate sparse/fine-line background updates, then overlays a translucent silhouette. Default 16-pixel blocks, step 4, RGB delta10 and 13/16 changed samples are original implementation choices; waiting time is scene-dependent (example10 seconds). The paper explicitly acknowledges shadows/similar foreground colors, persistent false regions under propagation and fine structures of people entering the background. Its 35-person display-preference experiment used depth segmentation, so it is not a quantitative guarantee for the RGB-only software detector.

Current reference lines 177–182: W1 stability uses previous-frame comparisons over four consecutive quiet frames, adds an E-rising-edge TTL seed, and still derives M from E & TTL>0. W0 writes !M; W1 writes !M & stable. Lines 272–273 compose pre-commit background then update entire allowed blocks. Low-change person edges can therefore pass the same fast-background criterion as fine writing; previous-frame stability alone is not proof of clear board. B1 uses decaying maximum old-neighbor TTL. The paper does not disclose enough exact propagation pseudocode to assert this numeric recurrence is proven identical to the original. Observed remnants may combine leaked current person pixels, contaminated history and persistent false foreground; no per-block causal trace has established their proportions.

## Proposed Repair Sequence (Recommendations, Not Adopted Production Rules)

1. Establish paper-aligned B0/B1 baseline and log E/D/seed/TTL/Q/M/W, stored background, each background write and propagation origin on the known failure segments. Separate raw-person leakage, stored-person contamination and maintained false foreground before tuning. Check propagation eligibility/timing against paper figures; do not claim unpublished implementation reproduced.
2. Stabilize input conditions: board ROI, fixed image geometry, measured quiet-board temporal noise and global brightness shifts; calibrate E/D thresholds separately. Detect frame-wide disturbance and freeze background commits; use actual processing cadence for hold duration. Registration/color normalization if traces show a need. Any HSV-style or chroma/luminance rule remains an explicit subsequent engineering proposal supported as a possibility in the paper, not a proven fix.
3. Separate display mask M from trusted-background commit W. Keep the last trusted background; permit sparse changed candidate patches only outside confirmed/suspected person boundary and after short confirmation. Freeze writes in uncertain person-edge/shadow regions; stable person is not automatically trusted. Selective commit or guarded sparse write is a proposed extension of original fine-line fast path. Avoid blanket delay for all blocks, which would worsen fresh writing.
4. Preserve 12-neighbor, old/new double-buffer, cross-frame propagation. Restrict relay to plausible occluder candidates and track age since a genuine local movement seed; neighbor relay alone cannot continually certify background-independent freshness. Clear regions matching trusted background, and release confirmed sparse stationary writing separately. Such modifications trade false foreground against stationary-person leakage and must be evaluated separately, not guaranteed.
5. Maintain separate release/update paths for exposed sparse new writing and large foreground. Follow known real writing through first visible frame to later occlusion, measure update delay and survival in history. New dense pictures/erasures need controlled waiting. Never-observed content and indefinitely motionless person versus permanently changed background remain inherent ambiguities of the available RGB history evidence.

Implementation order: reference diagnosis and one-variable changes on same causal video, before/after raw/output/background/masks; manually label or select historical-only already-visible writing and unobstructed negative controls; score ghosts, lost strokes, update delay and overwritten person pixels. Only improvements passing visual gates are transferred to HLS, then C/RTL comparisons. Candidate logic is primarily block counters, masks, neighbor comparators; resource/timing and interfaces must be measured after implementation. No fixed new threshold, hold or stability duration has been selected. No additional simulation, synthesis or board test executed for this proposal.

## Adoption, Files, Corrections and Handoff

AI contribution: PDF extraction/visual review, code/paper distinction, failure-mechanism hypotheses and ordered repair/evaluation proposal. Owner requested a plan; production changes remain unadopted. No subagents or conflicts. Files: this session, INDEX/STATE and proposed D-064; named test folder holds paper text/relevant page PNGs. Original PDF/C sources unchanged. Initial console print hit Windows GBK UnicodeEncodeError after extraction already succeeded; read the saved UTF-8 extraction and rendered relevant pages instead. Next step is cause tracing and paper-aligned baseline, followed by guarded history writes/fast fine-line handling; no effectiveness result claimed.
