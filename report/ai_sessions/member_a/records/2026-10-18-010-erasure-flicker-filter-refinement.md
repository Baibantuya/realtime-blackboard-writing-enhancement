# AI Session: 2026-10-18-010-erasure-flicker-filter-refinement
- Date: 2026-10-18
- Operator: User
- AI product/model: Codex / GPT-6
- Participants: User, Codex (single agent)
- Objective: Refine startup erasure as repeated flicker after erasing; compare alternatives to median filtering and update the joint execution specification.
- Status: Complete (diagnosis/specification refinement only)
- Report candidate: no
- Related commits: none

## Context Read
Read root AGENTS, AI policy, current state, D-118, index and session009; git reports the formal project untracked. No nested AGENTS found in the formal project.
## Task and Constraints
Preserve all five items in the authorized joint fix scope. This turn refines the technical diagnosis and filter selection; do not claim implementation or board verification.
## Contributions
- 用户澄清启动字擦后是闪烁，更新正式v20规格4.1，优先核查display/current与content commit分离造成的旧字召回；同时保留量化阈值抖动、过期显示缓冲两种替代诊断。
- 源码复核：compose在mask=false时可显示current，commit仍可能为旧background；若下一帧mask=true且!ink则可重新展示旧background。这是存在的代码机制，尚无同源现场帧证明唯一根因。
- 补充确认后历史/相关状态同步更新与不召回不变量，局部擦除不误清未擦笔画；连续10秒及再遮挡验收。
- 扩充中值以外高斯/近似双边/导向/条件去脉冲/弱时间确认比较。首轮四组空间A/B，优先验证3x3近似双边+笔画保护，空间足够则不开时间确认；不默认将复杂guided/NLM搬进PL。
## Decisions and Adoption
- D-119：采用用户症状澄清与诊断/滤波比较顺序，更新联合修复规格；不宣称滤波已经选择最优或已上板。
- 滤波优先作用分类前的噪声/亮度证据，保护原始RGB色相；孤立强尘可能被保边保留，标点保护必测。滤波能抑制触发噪声，不能取代历史一致性修复。
## Commands and Tools
- PowerShell/rg读取Restore compose、板面返回与Quantize实现；官方OpenCV4.12滤波文档、guided filter作者项目检索。apply_patch更新正式规格及内部记录。
## Validation and Evidence
- 源码核对位置：whiteboard_restore.cpp约242-253行display/commit，约448-500行surface返回证据。正式文档新增4.1及6.1。
- 本轮未执行算法实验、实拍采集、生产代码修改、HLS/RTL/综合/时序、板端部署或性能测试；只做源码复核与方案修订。
## Errors and Corrections
- 明确此前“擦不掉”应细化为擦后闪烁，并非完全没有变化；纠正不能仅把稳定帧数/滤波强度加大就称修复。
- 无nested AGENTS的rg返回1表示未找到，不是源码读取失败。
## Files Changed
- 正式docs/v20_quality_motion_display_execution_plan_20261018.md；本session、DECISIONS D-119、PROJECT_STATE、ai/INDEX。
## Remaining Work
- 五项联合实现仍待执行；按同源序列诊断擦除闪烁层级，再做空间滤波四组对照，按已授权v20完整流程推进。
## Handoff Notes
Startup erasure flickers rather than remaining uniformly unchanged. Distinguish history resurrection, threshold toggling and stale output buffers without claiming a unique field cause.
