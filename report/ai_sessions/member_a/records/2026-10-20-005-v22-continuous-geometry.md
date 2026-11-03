# Session 2026-10-20-005-v22-continuous-geometry
- Date: 2026-10-20
- Participants: user, Codex
- Status: In progress
- Objective: User explicitly requires low-frequency PS movement/board checks, update matrix while frame remains visible, search when absent; resolve blank deep-view initialization UX.
## Context Read
AGENTS, policy/state/decisions/index from current sessions, session004, runtime BoardAnalyzer/GeometryTracker/main and scene geometry transport.
## Findings
r2 froze recognition while locked; edge-loss watchdog cannot implement in-frame tracking and user reports no reliable loss trigger. This is an architectural PS control error, not accepted behavior.
## Contributions
Pending.
## Decisions and Adoption
Replace permanent lock with bounded2Hz board measurements, update validated moved quadrilateral, invalidate admission/search on missing frame. Keep quiescent geometry commit and material/Canvas reprojection. No PL or clock change.
## Validation and Evidence
Pending. SSH probe currently delayed; do not infer board state.
## Errors and Corrections
Previous r2 change incomplete and did not meet in-frame motion requirement.
## Files Changed
Pending.
## Remaining Work
Implement/validate PS detector control, initialization UI/preview, deploy independently if board reachable.

## User refinements and corrective work
User explicitly states startup assumes no person; automatic initialization required, no mandatory F7. Later explicitly requests F7 optional manual reset/initialization button to right of F6 in existing style. User emphasizes FPS regression was introduced by PS changes and repeated false board-search transitions; do not attribute it to PL frequency.
R3 continuous2Hz geometry updates actually observed generations1..19, with initialized content transported across generations; r4 rejects partially clipped frames. These initial changes used full detection every sample and single-miss search, causing CPU/performance/false-search problems. R4 actual CPU143%,10threads, camera24.5FPS/output5.5FPS diagnostic. Preserve all earlier packages/logs.
Revised PS controller uses1Hz small grayscale physical-frame motion check, full detector only on movement or3s refresh, three consecutive missing measurements before search. Brief stationary detector misses preserve known geometry; moved-but-unverified frames revoke admission pending recheck. Disable redundant10Hz optical-flow worker; bound OpenCV/OpenBLAS to1thread. No PL/clock change. Source tests cover real synthetic board/move/absence, missing debounce/recovery, lighting, cached static measurements.
Default startup now automatic under explicit user's no-person assumption. F7 optional request revokes admission/drains leases then resets PS reference and Canvas; geometry-only updates transport existing references. UI source copied into independent v22 source/software/ui_native and archive_ui.py. Added native F7 button right ofF6, expanded mouse/keyboard navigation queue to8buttons. Existing Noto subset contains every requested glyph; no font substitution. New ARM UI bridge compiled with existing verified unchanged LVGL static library, new build receipt retained. Actual keyboard queue, rendered UI visual inspection, mouse click PASS; f7_ui.png.
R5 PS performance observed CPU91.1%/4threads vs prior143%/10threads; camera30FPS, sampled output7.5..8FPS, cached recognition6.4ms vs full185..206ms. These are diagnostic windows with moving/initialization sections, not controlled identical-frame benchmark or guaranteed stable throughput. Content auto initialized without F7.
Actual live F7 test on r5 exposed RuntimeError Cannot admit unsafe geometry after manual_scene_reset: a loop iteration could have revoked gate but stale is_safe admitted a camera frame. Preserved r5 failure log/package. Fixed generated main needs_guidance to include not gate.safe, preventing any unsafe mid-loop frame admission. R6 compiled from same UI lib, no new FPGA load. Current PID33947, whiteboard_fusion_v22_r6_20261020. Final ZIP SHA5589002b35050d243da58f5b2cd4d965044e9c13fc2faaca07d9f9f3e67d5a71. Repeated live F7 lifecycle validation pending at this checkpoint.
Local assembler initially used a nonexistent marker; corrected and retained failed runtime. Windows os.set_blocking unavailable in input unit fixture; used event-read mock. Fixture import/name corrections retained. No false PASS claim for those failed runs. Documentation SCP to root-owned directory denied; corrected via sudo extracting only metadata from verified ZIP, keeping running code unchanged. R5 final corrected-doc ZIPb3e57d2603c233250e9e794395cb4f4aad0d9b202023c94ed903dff5041a1f6d, old pre-doc ZIP retained.

## R6 actual validation and R7 button style
R6 live log contains five reset events and zero pipeline_failure at109.65s; content resumed needs_bootstrap=false, geometry15, recent Q7..8FPS/display6.5..8FPS, no bad frames. Later user reports F7 appears to act likeF6; source maps F6 save and F7 reset distinctly, actual manual_scene_reset events observed. This perceived behavior is not declared resolved by event mapping alone. User then narrows current request to darker F7 border.
R7 changes only native F7 background0xD7C7B8 and2px fully opaque border0xA58A73 with existing18px round corners; function logic identical toR6. New ARM bridge compile with same LVGL static lib PASS, key queue and mouse F7 click PASS; f7_ui_r7.png visually inspected, visible separate button right ofF6. ARM library SHAf8f356f2f9e800905faf81fd1b29275596989686c35e0176c7684450b0f6d909. ZIP45210ad585b2d478bfac19786b502196df0a79ba00a7df55811873f4c9854262. Deploy independent whiteboard_fusion_v22_r7_20261020; no FPGA/clock/algorithm change.
