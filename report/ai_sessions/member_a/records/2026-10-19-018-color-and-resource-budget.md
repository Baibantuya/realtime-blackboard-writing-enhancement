# AI Session: 2026-10-19-018-color-and-resource-budget
- Date: 2026-10-19 (Asia/Shanghai)
- Operator: User
- AI product/model: Codex / GPT-6
- Participants: User, Codex (single agent)
- Objective: 补全白/蓝/红字迹颜色判定，并评估v15恢复核冻结、外置前景/Canvas方案的KV260资源与吞吐影响。
- Status: Complete; plan and resource assessment only
- Report candidate: no
- Related commits: none

## Context Read
承接session017完整规定阅读顺序；本轮重读最新PROJECT_STATE/DECISIONS/INDEX/session017/Git，核对v15真实route资源和v20匹配board_package资源及时序证据。
## Task and Constraints
当前只要求方案补正和硬件开销评估；用户补充必须考虑帧率，并在恢复/量化两个核分担工作。不修改生产算法、不综合、不上板。
## Contributions
补全红色与白/蓝的统一判定和颜色重写回归；核对v15真实route及v20匹配manifest，计算Canvas/网格/掩膜容量和融合量化核逻辑DDR流量。将外置Scene明确落在替换原Quantize的位置：Restore仅保留原v15逻辑，Quantize负责可见性门控、唯一ADD/ERASE提交和颜色输出，PS小图对象跟踪与Restore并行；不新增第三个全帧PL核。明确mask截止、Ring A/B释放、Canvas读写和真实FPS门槛。
## Decisions and Adoption
D-126：两核分工作为当前明确候选；保留D-125的v15冻结约束。新量化核不慢于v15恢复核、完整流水不低于同源v15作为设计门槛，待实测。颜色与资源/吞吐方案已写入正式文档，算法尚未实施或验收。
## Commands and Tools
只读资源核对、算术评估、正式方案与内部记录编辑。
## Validation and Evidence
核对既存v15 route：CLB14045/14640、BRAM134/144、DSP242/1248；v20 route：CLB14615/14640、BRAM137/144、DSP771/1248，WNS=-2.019ns。静态计算1080p RGB565单帧4,147,200B、8160块；新量化核最坏五条像素流20,736,000B/帧，相对原量化新增12,441,600B/帧。算术保存在test_workspace/v15_scene_resource_assessment_20261019/resource_arithmetic.json；不是DDR实测。Python独立重算帧尺寸、网格、流量和资源余量全部PASS；文档新增第8节、记录无占位及D-126/索引/状态一致性核对完成。新native/HLS/RTL/综合/时序/上板/FPS：未执行。
## Errors and Corrections
首次合并patch因文段不匹配被工具拒绝，未落盘，按实际内容拆分修正。初版架构图像是第三个PL阶段，已改成替代原量化核的融合实现；明确冻结v15意味着无法承诺降低其本身周期。25空余CLB不能直接证明任何新核必然不可实现，结论修正为极高放置/时序风险。区分PS小图载荷与真实DDR抽样读取，Canvas乒乓流量不重复计数。
## Files Changed
- kv260-whiteboard-enhance/docs/v15_frozen_restore_scene_algorithm_20261019.md
- project_workspace/ai/sessions/2026-10-19-018-color-and-resource-budget.md
- project_workspace/DECISIONS.md
- project_workspace/PROJECT_STATE.md
- project_workspace/ai/INDEX.md
- test_workspace/v15_scene_resource_assessment_20261019/resource_arithmetic.json
## Remaining Work
后续先同源真实序列验证人物静止/露出、新字/擦除和白蓝红颜色；离线实现与接口冻结后，才进行新量化核HLS/OOC及两核并发、整机资源时序和现场FPS验收。PS掩膜迟到率、CLB/BRAM、Ring A延长占用与DDR争用仍是主要风险。
## Handoff Notes
无新增板端状态。
