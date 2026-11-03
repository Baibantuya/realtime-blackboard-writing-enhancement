# AI session 与工程证据关联

2026-10-27新增关联：AI_Sessions仍由独立对话负责，不重复索要原文，不向另一对话发送消息。

| 主题 | 工程证据 | 边界 |
| --- | --- | --- |
| 真实HWH生成器修复 | [失败复现](evidence/20261027/candidate_failures.json)、[70字交叉](evidence/20261027/v24_contract_regression.json)、[副本](skill/v24-reviewed-tools/readme.md) | 本对话离线修复；不是现役V24驱动错误 |
| DMA超时所有权 | 同上失败记录、[31项日志](evidence/20261027/reviewed_tools_tests.log) | mock证据；实机停稳/复位待核验 |
| Overlay和性能口径 | [本轮结果](v24_review_20261027.md) | 源码与受控调用，不伪造历史故障 |
| 2025.2接口 | [迁移审阅](board_reproduction/migration_v24_2025_2.md) | 本轮静态核查；构建是原工作记录 |

本轮贡献为输入核对、候选缺陷复现、隔离修订和测试/文档；团队原系统设计、硬件与板测保持原归属。S/skill中的Session编号未自动认证为本工作区案例编号。

---

2026-10-22用户明确：**AI_Sessions已在独立对话窗口推进。** 本文件只维护PYNQ工程证据与对应案例的关联入口；原文整理、脱敏和案例编写由该独立对话负责。本工作区尚未接收其案例索引，不据此判断另一对话是否已导出或完成材料，也不将关联待补作为PYNQ工作的阻塞项。

| 可关联主题 | 当前可定位的真实工程材料 | 关联状态 |
| --- | --- | --- |
| PYNQ平台加载适配 | S10 `kv260_overlay.py`，fpgautil与metadata分离、check-only副作用 | 最终关联AI_Sessions中的相应案例；当前仅按源码/注释说明，不补写历史报错 |
| V22发布与当前入口核对 | S04/S05/S08、release_identity、v2入口及清单 | 工程材料可供引用；对应案例编号/路径待关联，不归功本轮设计了整机 |
| 本轮Overlay预检Skill提炼 | 用户本轮任务、[源码核验](evidence/20261022/source_review.json)、[检查输出](evidence/20261022/v22_preflight.json)、[构造测试](evidence/20261022/constructed_tests.json)、[Skill](skill/pynq-overlay-preflight/skill.md) | 本对话保留工程产物与可见过程；由AI_Sessions统一整理案例后关联 |

本轮实际贡献：阅读条款与源码；发现旧入口检查冲突；实现独立检查器与配置；运行真实副本离线对照和构造负例；写复现和缺项。用户贡献为任务目标、禁止自动部署的边界、提供来源与版本背景。团队贡献为已有PL/PS架构、原始工程与历史板测。官方文档只提供通用接口语义。

本对话不再重复索取相关聊天原文。后续总归档只需对齐案例编号、材料路径、适用版本和工程证据；已知源码、现场反馈与历史对话仍分别标注，缺乏直接证据时不把源码注释提升为实际故障记录。

关联参考为 [AI session准备指南](../../report/attachments/history/ai_session_preparation_20261022_4763338b.md)、[案例模板](../../report/attachments/history/ai_session_case_template_18cd4bbc.md) 和 [现有材料索引](../../report/attachments/history/ai_session_material_index_20261022_53c6b163.md)。实际AI_Sessions产物路径由独立整理工作确定，本文件不创建重复提交包。

未读取或复制 `work/logs/work.steps.log`，未访问其他聊天、向队友发送消息、创建分享链接或公开发布任何内容。
