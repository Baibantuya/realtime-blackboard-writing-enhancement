# AI Session: 2026-10-01-002-rgb-rectify-fps-review
- Date: 2026-10-01
- Operator: Owner
- Participants: Owner, Codex
- Objective: Review low frame rate in imx219_team_package_20260928/imx219_rgb_rectify_20260928.
- Status: In progress
- Report candidate: no
## Context Read
Root AGENTS.md, AI_DEVELOPMENT_POLICY.md, PROJECT_STATE.md, DECISIONS.md, ai/INDEX.md, package README and Git status. Relevant prior sessions will be read during review.
## Task and Constraints
Read-only code/performance review; do not change implementation or deploy. Existing root Git status has untracked project trees.
## Contributions
Pending source and report analysis.
## Decisions and Adoption
Recommendations only; no architecture decision adopted.
## Commands and Tools
PowerShell and rg source inspection.
## Validation and Evidence
Hardware profiling, synthesis, simulation and board testing: 未执行.
## Errors and Corrections
None.
## Files Changed
This internal session record only at task start.
## Remaining Work
Inspect PS loop, HLS synthesis reports and integration clocks; report evidence and prioritized optimizations.
## Handoff Notes
Do not equate synthesis estimates with measured board performance.

## Completed Review
- Status: Complete (source/report analysis only).
- Evidence: Target vitis_hls.log 838–842: output II=3 caused by three gmem0 RGB byte reads; evidence/rgb_csynth.rpt: output 62.209 ms, detector 18.859 ms, peak search 7.957 ms at 100 MHz. Schedule subtotal ~89.33 ms, not measured board latency.
- PS source serializes three copies, rotation, cache sync and display work; rectify_ms conflates several stages and omits display.
- Sensor configuration arithmetic implies 19.392 fps. Timing report identifies video-domain AE meter worst path, WNS -5.589 ns; rectify clock WNS +1.808 ns.
- Related sessions read: 2026-09-29-001-design-1-board-deployment.md and 2026-09-29-003-green-cast-white-chalk.md. Their ~1 fps belongs to another deployment package and is not a fresh result for target.
- Recommendations: staged profiling, AE meter timing repair, cached geometry/low-rate detection, packed memory reads and tile cache, actual II=1, shared-buffer/double-buffer pipeline, sensor timing after downstream readiness.
- Adoption: Suggestions only; no architecture or ABI changes adopted; DECISIONS unchanged.
- Validation: Static source/report cross-check completed. New hardware profiling, simulation, synthesis and board tests: 未执行.
- Errors/corrections: Initial broad reads truncated; followed with focused source/report sections. Do not label all low rate as Python or floating division; logs identify byte-read II constraint explicitly.
- Files changed: this session; appended PROJECT_STATE.md and ai/INDEX.md. User-facing report in Codex workspace outputs/rgb_rectify_fps_review.md. Implementation untouched.
- Remaining: obtain stage timings on the actual running package; validate optimizations and output correctness before deployment.
