# AI Session: 2026-10-18-009-v20-system-fix-plan
- Date: 2026-10-18
- Operator: User
- AI product/model: Codex / GPT-6
- Participants: User, Codex (single agent)
- Objective: 将五项联合修复及底层缓冲帧率需求整理成系统、可执行的方案。
- Status: Complete (execution plan delivered; production implementation not performed)
- Report candidate: no
- Related commits: none
- Related files: v19/source; docs/v20_quality_motion_display_execution_plan_20261018.md

## Context Read
按序复核AGENTS/AI政策、状态、D-117、INDEX、session008及Git状态。
## Task and Constraints
用户要求统一修复并给出可执行方案；本轮明确工程步骤、接口、指标、验证及实施边界，不把规划写成已经修复。不改运行中程序或伪造新性能结果。
## Contributions
- 创建正式docs/v20_quality_motion_display_execution_plan_20261018.md，覆盖全部五项，明确同版联合修复/分阶段验证/统一匹配封包。
- 帧率按camera worker有效DQBUF、Rectify/Restore/Quantize完成、KMS提交和pageflip确认分别计数；F1/F2/F3展示对应源缓冲FPS及真实显示FPS，历史和提示页不冒充视频。
- 对现有capture worker、FrameRing、UI Rate/合成、Scanout代码复核，明确PS观测的完成吞吐仍受运行调度影响，不能用目标30/DP60/阶段倒数伪造底层FPS。
- 增加每Ring B槽QualityMeta方案，保证Restore和Quantize并行时状态属于相同sequence/geometry/history代次；板面参考、擦除、色相和噪声规则共享可信证据。
- 采用PS运动状态/代次门控、PL板材参考和局部擦除、种子笔画定色、条件空间滤波+弱时间确认，以及原生C显示复制/混合。包含资源上限、模块列表、量化目标和完整场景矩阵。
- 板端缺少modetest/drm_info，改用libdrm只读探针查询card0 planes，未设置mode/FB/plane或master。plane39不支持RG16/ARGB，plane40同时支持RG16和AR24；因此不能假定当前565视频+ARGB UI分平面直接成立。只确认格式能力，未进行双plane commit或格式转换试验。
## Decisions and Adoption
- D-118：用户将五项统一纳入修复范围，本轮交付执行规格。此规格未实施，不能写成已修复。采用同一v20候选分阶段验证、一次匹配发布，保留v19运行/回退。
- 第一版必做FPS正确性与原生C显示优化；独立UI平面/原缓冲直接scanout受格式和生命周期约束，不作为五项修复的默认前提。CPU缓存同步不等于设备完成或引用释放。
- 块级元数据不是第三个像素DDR环；新算法ABI/导出寄存器必须更新HWH、控制软件和参考模型，帧池驱动ABI6原则保持。
- 各验收百分比/延迟与95%吞吐保留均是待验证工程目标，不是用户已确认的承诺或实测结果；旧200MHz时序FAIL与资源拥挤透明保留。
## Commands and Tools
- 本地源码/manifest/时序报告核对；Linux官方DMA-BUF/KMS文档检索。
- SSH只读工具发现与plane查询；SCP上传/tmp/probe_drm_planes_v20_20261018.py，调用drmModeGetPlaneResources/GetPlane及per-fd universal client cap。未停止/切换显示或视频程序。
- 本地test_workspace/v20_execution_plan_20261018/probe_drm_planes.py、drm_planes.json、plan_review.json。
## Validation and Evidence
- 显示平面格式只读实查完成；结果保存在drm_planes.json。
- 文档完整性检查PASS：五工作包、六帧率事件、逐帧元数据、发布门、明确双plane限制及Markdown围栏一致。此检查只验证规划文本，不代表算法通过。
- 代码事实：capture是独立DQBUF worker；F1/F2当前全帧copy；UI NumPy混合每新帧分配多份uint32区；Ring B像素流水和全局恢复状态有不同生命周期，新增元数据必须逐槽绑定。
- 未执行：生产源码改动、原生C显示实现、运动/擦除/颜色/滤波新算法、HLS/RTL/综合/时序、新板包/部署或新FPS对比。上一轮10.58FPS不是本方案性能承诺。
## Errors and Corrections
- Windows rg文件通配路径再次未展开，改目录加glob。
- DECISIONS首次占位补丁因锚点不匹配未生效，随后以UTF-8精确追加D-118并检查；未产生部分内容改动。
- 板卡无modetest/drm_info，改libdrm只读查询。未绕过权限或进行任何KMS状态提交。
- 纠正潜在方案风险：不能把RGB565/YUYV内存载体机制照搬到显示解码；不能让Quantize读下一帧全局block_state；不能仅更改FPS标签宣称实际显示提速。
## Files Changed
- 正式docs/v20_quality_motion_display_execution_plan_20261018.md。
- 内部本记录、D-118、PROJECT_STATE、ai/INDEX；独立测试目录的能力探针/记录/文档审查结果。
- 无生产PS/HLS/RTL、板包或运行进程改动。
## Remaining Work
方案已交付。实施时按P0同源基线与诊断、P1 PS运动/FPS/原生显示、P2联合PL、P3 fresh HLS/整机、P4匹配上板、P5现场量化逐步执行；五项范围统一，不需要重开需求讨论。规划不等于修复已经完成。
## Handoff Notes
用户要求能显示底层实际缓冲FPS，须区分生产/处理完成与实际屏幕新帧，不用更改标签掩盖显示瓶颈。
