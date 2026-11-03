# AI Session: 2026-10-19-017-v15-frozen-restore-external-foreground-plan
- Date: 2026-10-19 (Asia/Shanghai)
- Operator: User
- AI product/model: Codex / GPT-6
- Participants: User, Codex (single agent)
- Objective: 整理v15至v20演变，提出保持v15恢复核不改、独立区分人物遮挡与板书写擦的统一算法及代码接入方案。
- Status: Complete; proposal only
- Report candidate: no
- Related commits: none

## Context Read
承接session016按规定顺序读取的AGENTS、AI policy、PROJECT_STATE、DECISIONS、INDEX、相关会话和Git状态；本轮重读最新状态/决策/索引、session016及Git状态。审查正式v15及已保存的匹配v16/v18发布源和当前v19/v20主HLS源码。v17无完整匹配发布源，未推断其算法细节。
## Task and Constraints
用户明确要求先方案与算法，并强调不修改恢复逻辑；本轮不实施生产代码，不综合，不部署。将边界落实为正式v15 Restore/guarded源码、寄存器与内部状态机冻结；外置模块负责最终画布和字迹事件。
## Contributions
- 逐项核查五版Restore/guarded/Quantize源码哈希与diff。v15/v16/v18 guarded_state完全一致，v19/v20同版。v16取消ink显示writes门控，v18恢复；v19增加局部板面/粗字/白物体例外，v20增加板材状态/逐槽meta及滤波色传播。
- 确认v15不导出完整像素人物mask，原background只按trusted/ink更新，不能可靠提交初始字擦除。故不能只调v15参数满足用户新要求；外置Canvas必须作为唯一最终画面与写擦历史，v15输出仅作遮挡参考和回归。
- 提出对象身份→露出认证→板书ADD/ERASE的链路；Canvas、Surface、ObjectMask、UNKNOWN/OCCLUDED/REVEAL_PENDING/VISIBLE及短候选状态；人物静止不释放，坐标实际露出后才接纳新字/擦除。颜色和噪声从对象判断剥离。
- 说明PS低分辨率有序快照与v15读Ring A并行，同序号/代次mask接入外置像素核；过期时UNKNOWN。保留v20 UI/几何防护与原校正意见。
- 正式方案 docs/v15_frozen_restore_scene_algorithm_20261019.md；旧v20核心重写方案加替代标记并保留诊断证据。
## Decisions and Adoption
- D-125是本轮AI方案，尚未实施。用户的v15基线/不修改恢复逻辑约束已反映在规格中；D-124重写恢复核心路线被本方案取代。
- 现有model_sidecar只作诊断且严格等效未解决，不作为现成可信人物mask。单目RGB不可无条件恢复从未观测的隐藏原字；此类区域保持UNKNOWN。
## Commands and Tools
PowerShell/rg/Python读取发布源、哈希和diff；apply_patch写方案及内部记录。无新编译、SSH、板端或子代理。
## Validation and Evidence
- 源码核查：v15/v16/v18 guarded_state SHA256前缀均545152f6620e，v19/v20均8e1227c90402；v15正式源于session016与发布ZIP快照一致，v18先前与发布清单匹配。
- session016既存native反例和session015已存11快照仅被引用，不算本轮新实验。
- 新算法native/真实视频/板测、HLS/RTL、综合/时序/FPS均未执行。
## Errors and Corrections
- 此前交接文档把bulk_white_blocks描述为连通域，源码实为全ROI计数；旧文档“当前运行v16”已过时。本轮以发布源码与最新状态为准。
- 初次以PowerShell管道提交含中文长Python脚本出现stdin编码SyntaxError，未写入任何文件；改用apply_patch编辑并检查结果。
- 对用户“不修改恢复逻辑”明确落地为v15核冻结；外置最终画布是避免继续修改该核所需的架构变化，不把它说成参数调整。
## Files Changed
- 正式docs/v15_frozen_restore_scene_algorithm_20261019.md；旧docs/v20_occlusion_content_redesign_plan_20261019.md替代说明。
- 本记录、DECISIONS D-125、PROJECT_STATE、ai/INDEX。
- 未修改生产算法、固件、运行板卡。
## Remaining Work
本次方案任务已完成。实际同源v15现场回归、外置算法实现、真实画质及硬件资源/时序/FPS均待后续任务。
## Handoff Notes
先取得人物进入/静止/离开及写擦的同源真实事件序列；通过v15遮挡基线后才接入Canvas更新。若人物长期污染Canvas必须回到遮挡模块修正，不在v15恢复核加例外。现运行板卡状态本轮未重新核查。
