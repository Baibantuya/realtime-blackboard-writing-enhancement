# PYNQ 提交准备工作区

更新：2026-10-27，Asia/Taipei。当前基线：**V24 硬件＋V24-PS-SLIM-20261026 结构化运行包**。本轮本地整理与离线修订可审阅；正式发布、干净环境重建及板测验收仍未就绪。

| 阅读入口 | 内容 |
| --- | --- |
| [V24 本轮结果](../../../skill/evidence/v24_review_20261027.md) | 输入核验、候选工具修复、迁移差异与证据边界 |
| [来源索引](../../../skill/evidence/source_inventory.md) | 新旧版本、来源类别、指纹与阅读范围 |
| 当前状态（历史工作区路径：`status.md`） | 本轮离线、已核验源码、历史验证、反馈、计划 |
| [复现说明](../../../skill/evidence/board_reproduction/readme.md) | schema 2 入口、加载副作用、数据与调度 |
| Skill（历史工作区路径：`skill/readme.md`） | 保留原预检器，增加隔离修订的候选工具 |
| [缺项](../../../skill/evidence/missing_items.md) | 当前验收、发布与许可的解除条件 |
| [AI session 关联](../../ai_sessions/member_c/batches/v24_20261027/evidence/pynq/ai_session_links.md) | 独立对话负责AI_Sessions，本工作区只关联工程证据 |
| 更新记录（历史工作区路径：`update_log.md`） | 本次及后续增量维护方式 |

本轮结果：两份运行包各80项负载通过，35个Python源码/运行副本一致；V24专属预检439 pass / 0 fail / 8 not_checked；70个寄存器字与真实HLS头文件交叉一致；31项候选工具回归、5项V24负例通过；原预检器23项测试另行复跑通过。数量是具体检查/用例数，不代表系统覆盖率。

原V22的429/7、23项记录以及9文件/3IP/70寄存器配置完整保留在 20261022证据（历史工作区路径：`evidence/20261022`）。[旧入口冲突](../../../skill/evidence/board_reproduction/entrypoint_conflict.md)限定V22，不套用新包。更新前文档保存在 历史快照（历史工作区路径：`evidence/20261027/previous_workspace`）。

<span style="color:#C00000">【待核验】总提交清单有14条路径过期及Skill漏列；原V24和2025.2候选均未达到时序签核。静态一致、历史能运行与正式发布通过分别记录。</span>

本轮始终单代理。源包保持不变；未连接板卡/服务器、加载FPGA、运行run.sh、升级依赖、训练/综合、改Word/LaTeX报告、提交Git或发送消息。神经网络及手势控制移至后续扩展，不列当前部署依赖或验收缺项。

后续收到新vision版本、队友反馈或验证记录时新增来源和日期，绑定PS/PL/环境/哈希，更新当前状态并保留历史结论。不会自动监控其他对话或建立后台任务；新材料不自动授权部署。
