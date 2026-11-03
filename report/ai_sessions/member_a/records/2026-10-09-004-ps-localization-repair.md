# AI Session: 2026-10-09-004-ps-localization-repair
- Date: 2026-10-09
- Operator: Project owner
- AI product/model: Codex / GPT-6
- Participants: Project owner, Codex (single agent)
- Objective: 仅修正v5 PS黑板定位和状态机，验证并更新已部署版本。
- Status: Completed; actual live lock/output verified
- Report candidate: yes
## Context Read
按序重读AGENTS/policy、state/decisions/index当前条目、session003近期记录及Git状态、v5 detector/pipeline源码。长期历史前会话已读，本次定位相关上下文无缺失。
## Task and Constraints
用户明确暂不改笔迹量化，只修PS定位。现有PL固件、量化、WB和通道配置保持；无需重复红蓝验收。保留板端备份，安全等待DMA退出，不强杀或重新加载硬件。
## Contributions
安全stop后实际抓8张fixedWB帧，旧检测8/8失败。图像左侧黑板边在视野外且斜拍，弱色门限排除部分暗板，旧共用窄高度段使左右线外推失稳。实现单边裁切可见ROI、持续暗支持/最近可信边界、每条边独立采样范围、局部64px搜索，避免疑似移动永久unsafe；新增日志accepted角点/restore_safe。同步正式v5软件及回归测试；PL/量化/WB未动。
## Decisions and Adoption
采用PS定位修正；具体参数以真实帧和状态机测试为依据。算法变化记入决策。
## Commands and Tools
PowerShell、PuTTY、Python，原板端stop/activation流程。
## Validation and Evidence
本地专项7checks PASS（8真实帧跟踪/全板斜板/均匀画面拒绝/孤立异常/连续移动确认/失败恢复与主动校准/pending搜索）；现场8帧可见框与人工粗略地标误差<12px（非标定精度）。新矩阵一代锁定。图像/NPY/检测红框/replay.json位于test_workspace/ps_localization_20261009。板端新包13runtime回归PASS、31文件preflightPASS；安装器原流程保留previous/current历史。新的33文件ZIP两校验清单/CRC和原bit/HWH哈希PASS，SHA74232a25b6f3152cc78519d6ba7b85e3374c14bd21d82d4874a66bae9ede95ca；正式handoff同步。实际长期输出检查待补齐。
## Errors and Corrections
本地Python无cv2/paramiko：使用内置numpy/PIL完成实际帧回放，Linux板端执行原cv2回归。扩大coarsegap8试验错误合并桌面/背景，退回原gap2；仅统一扩窗未解决旧共用窄采样区，改每边独立全跨度。边界0有一小误检使拟合产生负角点，>=6零边点固定裁切线；专项断言误把跟踪要求设为8px而正式hold门限16px，实际8.05px变化不应切代，改验证16px并保持连续确认8px不变。最终7checks/13runtimePASS。没有以失败试验作为最终结果。新HLS/综合/时序测试未执行（固件不变）。
## Files Changed
正式v5software/board_detector.py、run_stage_pipeline.py，tests/test_runtime.py；同名candidate board_package/source同步，system_manifest.json与33文件ZIP及正式handoff刷新；test_workspace/ps_localization_20261009诊断/7checks/包刷新脚本及实际图像；内部限定update_ps_localization_20261009.py、会话/状态/决策/索引。硬件、量化和WB字节未变，更新器安装前逐项确认。
## Remaining Work
定位任务完成。笔迹量化质量/实际移动后的旧H保持策略/长期稳定性另行验收；用户新要求优先诊断低帧率，见下一会话。
## Handoff Notes
现有v5板端whiteboard_candidate，历史PID7909。依旧保留相机共享环和FIFO/代次排空规则。

## Actual Final Board Result
- 更新无FPGA重载，三帧实际1080p全像素smoke PASS，PID15508 alive=true，FPGA operating。连续8日志geometry_generation1/locked/small_change_hold、restore_safeTrue、edges8/8/8/8、clipped1，accepted可见区域corners约[[0,192.79],[1458.76,572.48],[1382.03,1000.74],[0,696.41]]固定。
- rectified70→92、restored69→91、quantized68→91，bad0。由quantized/output_fps反算最近14秒窗，输出约1.64FPS，采集约19.4FPS；累计output_fps1.464含启动时间，不当稳态IP吞吐。定位解决当前重复确认停顿，低处理吞吐另测。
- 用户后续报告字迹淡/两边缺失并要求优先找IP瓶颈；本次未宣称量化质量通过，也未改量化/红蓝/白平衡。原因和性能实测另记session005。更新器保留旧包的previous/history，可回退；此回退previous是修复前v5，原v4已进入不可变history。
