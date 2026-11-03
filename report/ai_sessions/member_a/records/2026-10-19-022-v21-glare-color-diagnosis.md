# AI Session: 2026-10-19-022-v21-glare-color-diagnosis
- Date: 2026-10-19
- Participants: user / Codex, no delegation
- Objective: determine whether PS alone can fix bright-board glare, thick strokes and blue/black mixture; record PL work for tomorrow if required.
- Status: In progress
- Report candidate: no
- Related commits: uncommitted workspace

## Context Read
Root AGENTS and policy, PROJECT_STATE, DECISIONS, INDEX, session021, Git state and current quantizer/PS source inspected. r5 remains running with matched unchanged hardware.

## Task and Constraints
User reports bright central reflection classified as white chalk (black output), thick strokes and blue mixed with black. Prior basic acceptance does not cover this lighting failure. No PL edits or synthesis today; PS changes only if evidence supports them.

## Contributions / Decisions and Adoption
Pending diagnostics. Preserve v15 Restore and two-core architecture.

## Validation and Evidence
Requested safe SIGUSR2 frame from current r5 PID29285. Local evidence directory: test_workspace/v21_glare_color_20261019. No repair claimed yet.

## Errors and Corrections
None yet.

## Files Changed
This internal record; subsequent evidence and state updates pending.

## Remaining Work
Inspect actual raw/output/material metadata; replay existing C++ with PS-accessible surface/noise/threshold settings. Adopt PS only if glare and genuine strokes/colors remain separable; otherwise record exact PL limitations and next-day plan.

## Outcome / handoff
- Read actual frame13426 raw/output/meta, visibly confirmed broad central black patches and thick strokes. Ran actual unmodified C++ four fresh-canvas parameter replays:26/24 white45152 blue1316;26/8 white41561 blue4932;40/8 white27365 blue4810;56/8 white14550 blue4490 in fixed central crop. Lower margin visibly recolors neutral strokes; high delta visibly loses fine writing. These counts are not annotated accuracy.
- PL neutral-first hardcoded range24/brightness64 cannot be overridden by PS color_margin. Half-threshold edge bridging and broad-support acceptance are potential glare/thickness mechanisms; PS global-bright-outlier inpaint can underestimate bright material. PS-only scalar tuning not accepted. Current raw contains a person and must not initialize a reference.
- User instruction respected: no production PS parameter write/redeployment, no PL source edit, no synthesis. r5 remains running. Captured 448.9-second log shows 3421outputs cumulative7.62FPS, bad_frames0; picture quality remains partial/failed under glare. Existing95 tests were not rerun because production source unchanged; four real-frame native diagnostic runs executed.
- Exact next-day algorithm/work/validation handoff written to project_workspace/ai/handoffs/2026-10-19-v21-glare-color-next-day.md. No new build or scheduled wake started; existing automation remains paused.
- Files changed: internal session022, handoff, state/decisions/index and formal README status; only test scripts/evidence under named test folder, no algorithm changes.
- Status: Diagnosis complete; repair deferred per user to next day. Main unresolved items: glare/material, thin-stroke thickness, coherent white/blue/red discrimination; large camera movement and long-run validation remain open.

## AE / v20 comparison follow-up
用户提出分区曝光且v20无此问题。实际检查：r5 auto_exposure.py九块测光仅位于归一化板框40/50/60%中心区，输出单一sensor exposure/analogue_gain；不是每区独立曝光。主入口255行条件只在warmup/未锁框/重新校准时ae.update，锁定后photometry_frozen=True，当前不是持续自动曝光。不能声称AE已经能补后续光照。
v20量化N7，逐像素计算AREA*channel-center邻域sum的正局部对比，并方向结构/强弱判据；v21用相对PS冻结tile材料的绝对residual，失去对平滑反光的局部背景抑制。代码差异支持这是v21回归风险，v20现场对比仍来自用户反馈，未跑匹配条件A/B。后续应保留v15恢复/新Canvas前景机制，只恢复/评估v20局部对比与方向结构方法，而非整套回滚v20恢复。
AE后续方案：全板分区测光、剔除人物/字迹/反光，高亮分位/饱和约束，驱动当前单曝光，局部光照归一化另做；低频限幅AE并携带photometric状态/暂缓Canvas提交/保持人物与内容，禁止直接解冻造成旧参考失配。真正不同区域不同曝光当前软件路径不支持；多曝光融合额外吞吐/运动重影，不作为第一路线。今天仍不改PL/不部署。

## Fusion plan recorded at user request
新增handoffs/2026-10-19-v20-v21-fusion-plan.md，明确v15恢复冻结、v21前景及写擦保留、v20局部对比/方向/强弱笔画和色相兼容机制评估接入、PS分区测光与参考协调；D-135。修改STATE/INDEX/原交接链接。仅文档记录，核对文件存在与关键章节；未改代码/未运行综合或硬件测试。

