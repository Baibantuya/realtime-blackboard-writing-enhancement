# AI Session: 2026-10-19-016-v20-root-cause-redesign-plan
- Date: 2026-10-19 (Asia/Shanghai)
- Operator: User
- AI product/model: Codex / GPT-6
- Participants: User, Codex (single agent)
- Objective: 分析v20静止人物红残影、新字不出现、擦除慢及校正输出低帧率；以正式v15遮挡效果为回归基线，提出简化架构与代码修改方案。
- Status: Complete; assessment and proposal only
- Report candidate: no
- Related commits: none; project/test trees are untracked

## Context Read
已依序读取AGENTS、AI policy、PROJECT_STATE最新检查点、DECISIONS近期条目、INDEX、session011/014/015及v18对照分析session2026-10-17-001。状态/决策历史全文过长，使用最新分段和任务相关历史，不声称逐字读取全部历史。相关代码与当前Git状态正在核查。
## Task and Constraints
用户要求先方案及代码修改思路。本轮不修改生产算法，不综合、不部署、不重启板卡；仅阅读现有源码/已保存证据，必要时独立本地诊断并记录。现场现象为用户报告，不视为已有同源可重现序列。
## Contributions
- 用户补充白字应输出黑色但夹杂蓝色，已纳入颜色设计及共同验收。
- 读取正式v15恢复源，并确认与session2026-10-17-001从发布ZIP提取的v15快照逐字一致；检查当前v20恢复/遮挡/量化/PS调度/监测RTL。
- 确认v19/v20校正HLS、取数RTL及integration wrapper逐字一致；普通guarded_state也一致。v20仍有多重占用清零、可见性和历史提交特例。
- 汇总session015已有11快照：host校正中位39.329ms、恢复234.787ms、量化106.982ms，11/11Ring A无FREE。校正FPS受下游反压的证据强，不证明校正本体新退化。
- 编译当前v20恢复/量化C++，执行128×96 native探针：新增112像素暗蓝字30次后显示/历史均0，白/浅蓝/红均112；合成红条纹第1次放行512/历史0，120次后512/512。机制探测而非真实人物语义验收。
- 颜色探针中3/4中性候选+1/4蓝色候选，检查80像素全部变蓝；源码允许一个近邻种子达到染色门槛。不能仅凭该合成输入判定物理颜料白/蓝，现场需同帧原始ROI。
- 正式方案：docs/v20_occlusion_content_redesign_plan_20261019.md。以v15为遮挡回归门槛，统一Visibility/Canvas/Surface/Candidate，唯一历史提交，颜色判定与可见性分离；保留已验证基础链路/UI。
## Decisions and Adoption
- D-124为AI建议，未实施；用户仅要求方案。已实施的v20保持。
- 物体静止不学习为板面；图像坐标可通过可信露出释放。新字/擦除不能与人物同归永久前景；UNKNOWN不能等同背景。
- 性能先测同源单核/并发/UI差异，再减恢复重复板材估计、量化逐像素metadata及多模式开销；不先重写校正器。
- 白字中性保护与蓝字连续性同时验收，禁止单邻居跨色传播；先空间证据，不默认增加永久颜色锁/模型/整帧状态。
## Commands and Tools
PowerShell/rg/Git、Python3统计哈希与日志；g++ -std=c++11 -O2 -DWHITEBOARD_NATIVE本地编译探针；apply_patch编辑方案和内部记录。无SSH/板卡/服务器操作，无子代理。
## Validation and Evidence
- `test_workspace/v20_redesign_assessment_20261019/static_and_saved_log_audit.json`：源码比较与已存日志统计。
- 同目录quality_probe.cpp/exe/txt：实际恢复及量化源码probe，编译和运行exit0；这是缺陷边界探索，不是新产品PASS。
- 当前生产包system_manifest无source_sha256字段，本轮未重新建立部署bit与全部本地源映射；源码机制/本地native结论不冒充现场唯一根因。
- 新板测、真实序列、纯硬件计时、HLS/RTL、综合/实现：未执行。
## Errors and Corrections
历史状态已更新：v20已于session012综合并于014修复上板，015重启；不能沿用session011未综合状态作当前事实。
- 首次批量读历史过长，改按最新检查点和近期决策读取；两次猜测文件名/PowerShell rg glob不存在，随后使用实际pipeline_stages.py及目录/glob检查，不影响结果。
- 原监测cycles结束于PS读ap_done，不能称纯硬件周期；方案已明确纠正此口径。
- 暗蓝缺陷明确复现，但不能泛称所有新字都无法显示；红条纹/偏蓝中性样例有语义歧义，不能当现场视频复现。
## Files Changed
- 正式docs/v20_occlusion_content_redesign_plan_20261019.md。
- 本记录、DECISIONS D-124、PROJECT_STATE最新评估、ai/INDEX。
- 独立test_workspace/v20_redesign_assessment_20261019探针与统计。
- 生产代码、部署包、固件和板端均未修改。
## Remaining Work
本次分析任务已完成。方案实施、同源现场采集/回放、v15遮挡基线对比、准确PL性能归因及新构建等待用户后续任务；不能宣布已解决画质/吞吐。
## Handoff Notes
保持运行板卡与生产源码不动。
下一步实施顺序：取得现场同源证据→v15遮挡基线→唯一可见性/内容提交与中性颜色保护→吞吐归因与减重→去噪选择。任何人物长时污染Canvas先阻止进入下一阶段。
