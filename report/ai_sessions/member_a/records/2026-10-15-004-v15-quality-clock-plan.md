# AI Session: 2026-10-15-004-v15-quality-clock-plan
- Date: 2026-10-15
- Operator: Project owner
- AI product/model: Codex / GPT-6
- Participants: Project owner, Codex (single agent)
- Objective: 分析 200MHz、淡字连续增强、闪烁噪点、长期遮挡后无人重置及板框移动提示，提出实现思路。
- Status: Completed; analysis and documentation only
- Report candidate: no
- Related commits: none

## Context Read
根 AGENTS、AI_DEVELOPMENT_POLICY 全文；PROJECT_STATE 当前及近期状态、DECISIONS 最近条目、INDEX、session002/003。Git 全部未跟踪状态保持。
## Task and Constraints
本轮分析与设计建议；用户随后明确要求写文档。未改生产代码、未构建/部署。沿用原 DMA、两 DDR 环、PS 稀疏控制、PL 像素处理约束。语义人员检测若增加 PS 职责属于可选提案，未授权实施。
## Contributions
完成正式文档 `kv260-whiteboard-enhance/docs/v16_quality_clock_ui_plan_20261015.md`，覆盖五项方案、源代码落点、资源与接口影响、实施次序与验收。完成现有清场限制、实际量化关键路径与 host 计时口径核对。
## Decisions and Adoption
D-106 仅记录提案与证据：200MHz 分级流水目标；同色方向支持+弱字时间置信度和去噪；独立无遮挡证据驱动完整历史重建；PS提示码/PL OSD。未将建议记为已实施。
## Commands and Tools
本地源码/已留证据检查；SSH/scp只读取回最终时序报告与板端日志；查阅 AMD UG949 2021.2 Pipelining Considerations；apply_patch 编写文档与内部记录。
## Validation and Evidence
- 100MHz 后级 intra-clock WNS +0.860ns；关键路径在量化 classify，data delay9.036ns（logic2.817、route6.219ns、19级），不能以全局+0.603ns推算200MHz可用。
- 源码明确 scene_occupied / unstable 采用任何点否决，old_guard 也否决；日志 elapsed≈405s 显示 epoch0、reasons22，占用/不稳定/旧保护三项阻止重建。日志没有对应影像，不能证明该时刻无人。
- quantizer只有7×7统计和3×3同色强种子延伸，无一般时间一致性或多方向跨缺口连接。tracker 失败时保留旧坐标；无屏幕OSD提示。
- 实际报告保留 `test_workspace/v15_quality_plan_20261015/combined_timing_v15.rpt`，SHA256 `225f5da60978609c0b648a2c270b875f3b1b2a44608d006a31978f55d2af5488`；日志 `board_live_observed.log`，SHA256 `a734e175ec74446b30c8e750adb3ac874290b2f397837207dd085df237b4820e`。
- 文档与现有代码/报告交叉核对；新算法仿真、综合、实现、上板、质量复测未执行。
## Errors and Corrections
- 纠正此前把restore/quantize约189ms host时间直接当硬件绝对延迟及确定瓶颈的说法。计时在主循环观察AP_DONE时结束，含轮询延迟；9.30FPS吞吐不证明每核均饱和，具体瓶颈需硬件计数/调度等待测量。
- 纠正小帧V15_PL_FEATURES_PASS足以说明现场无人重建已解决的表述；它验证选定合成场景，现场仍可能因判据过严等无法触发。
- Windows rg通配符路径和candidate_params.json路径初查失败，随后改查实际whiteboard_ip.py及真实时序报告；未修改输入或编造不存在的参数文件。
- AMD UG1399指定旧版链接抓取超时，正式文档仅引用成功读取的UG949 2021.2，不引用未读页面作为证据。
## Files Changed
正式设计文档；本会话、DECISIONS D-106、PROJECT_STATE、INDEX。未改生产源码、硬件包或板端文件。
## Remaining Work
后续经实施指示创建新候选，先同帧证据/真实计时和无人重建，再连续增强/去噪/OSD，最终对定稿质量版做200MHz签核。小模型语义检测如采用需明确新增PS职责和性能影响。
## Handoff Notes
用户当前要求分析，不代表启动新综合或切换板上版本。
