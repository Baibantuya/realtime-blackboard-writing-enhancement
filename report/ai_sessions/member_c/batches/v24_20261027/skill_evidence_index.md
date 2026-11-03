# Skill双向证据索引

2026-10-27快照。这里将两项既有草稿、PYNQ离线检查器、S/skill六组候选分开登记。文件来源不等于实际历史使用；不合并成“全部通过”。[机器可读映射](case_skill_map.json)保存选定平台消息ID、源回执、完整文件SHA、环境与限制；下表使用简短编号便于阅读，空消息字段表示尚未取得对应原文，不能补造。

## 案例→规则→工具

| case_id | source_message_ids / source_tool_log | 提炼规则与skill_id | artifact_hash入口 | test_environment / actual_result / limitations |
| --- | --- | --- | --- | --- |
| U01–U03 | 各案messages.json；Linux/Windows失败与回执、居中修正、流水纠正 | ui-evidence-validation：分开检查资源、可见像素、真实输入和硬件层 | [旧核查](../../validation_results.json) | 10/23结构检查通过；案例内工程测试为历史。新流程未做跨任务试用 |
| C01–C03（历史研究） | 原三案messages.json、严格导出失败、尺度修正与种子负结果 | controlled-model-comparison：固定比较条件，保留全部种子和负结果 | [旧检查](../../validation_results.json) | 结构/统计回溯；不是当前整机部署或新训练 |
| A02/V24-A（审阅关联） | [既有PYNQ关联说明](evidence/pynq/ai_session_links.md)、[V22检查](evidence/pynq/evidence/20261022/v22_preflight.json) | pynq-overlay-preflight：先核对版本、文件和寄存器，再进入有副作用的步骤 | [构造测试](evidence/pynq/evidence/20261022/constructed_tests.json)含脚本/测试SHA | V22本地离线429通过、7未检查；23构造测试通过。没有自动变成V24或多板验证；其原开发对话未在本批次归档 |
| V24-C／候选工具反例 | N042/N057主对话反馈；[实际解析失败](evidence/pynq/pynq_codegen_audit.json) | 03_contract_codegen：读取HWH真实PROPERTY、缺字段失败；生成前先与已知寄存器对照 | audit含脚本和HWH输入SHA | 其他审阅轮次实际无硬件执行：70寄存器全部读0、67错误。本轮只核对记录，未重跑或修复 |
| V24-C | N063/N076/N110/N139；探针、HLS与实现原报告 | 尚未独立建Skill：分层验收与最小变量诊断 | [迁移证据](case_c_migration.md) | 有本工程C/RTL与实现结果，仍有负WNS；不是跨题/跨板复用证据 |

## 工具→来源→验证状态

| skill_id / 来源 | 输入、输出及用途 | 结构/文件核验 | 模拟或构造测试 | 硬件/跨任务状态与失败条件 |
| --- | --- | --- | --- | --- |
| [ui-evidence-validation](../../skill/ui-evidence-validation/readme.md)，本整理草稿 | UI版本、需求和证据→分层验证流程 | 10/23结构通过；本次保留 | 没有独立新任务执行 | 跨任务未验证；不能用WSL证明板端 |
| [controlled-model-comparison](../../skill/controlled-model-comparison/readme.md)，历史研究草稿 | 数据/配置/模型输出→受控比较 | 10/23结构通过；原实验保留 | 没有按新Skill重跑 | 当前部署范围外；迁移未验证 |
| [pynq-overlay-preflight](evidence/pynq/skill/pynq-overlay-preflight/skill.md)，PYNQ工作区草稿 | 文件/manifest/HWH/契约→离线报告 | 已有结构记录；V22输入身份 | 23项构造测试历史通过 | 板卡/跨板未验证；7项明确未检查 |
| [01_overlay_manager](evidence/received_skills/01_overlay_manager/readme.md)，S提供 | bit/DTBO/HWH→加载与映射；有系统副作用 | 文档副本与SHA已登记，未验证全包规范 | 本批次未取得与当前实现绑定的执行回执 | 跨板声明未证实；download=False也不能笼统称只读 |
| [02_dma_buffer_guard](evidence/received_skills/02_dma_buffer_guard/readme.md)，S提供 | 缓冲、超时/缓存策略→资源管理 | 同上 | 本批次未重跑；超时隔离仍需具体反例 | 超时异常不等于PL停稳，不得在途复用/释放 |
| [03_contract_codegen](evidence/received_skills/03_contract_codegen/readme.md)，S提供 | HWH/头文件→驱动/测试骨架 | CLI/路径与README不一致 | 已有真实HWH失败回执，67处偏移错误 | 修复和回归前不能作为板端驱动；不等于现用PS驱动有此故障 |
| [04_golden_benchmark](evidence/received_skills/04_golden_benchmark/readme.md)，S提供 | 参考/实际帧和时间→比较/性能报告 | 已登记，未验证全部说明 | 本批次未取得匹配的完整执行回执 | 首次传入时延≠冷启动；单帧时延标准差≠帧间隔抖动；FPS>0不等于达标 |
| [05_troubleshooting](evidence/received_skills/05_troubleshooting/troubleshooting.md)，S提供 | 故障现象→排查顺序 | 已收到文档，不是可执行测试结果 | 无逐条故障注入回执 | 真实源消息未逐条绑定；不能把手册内容当全部已复现 |
| [06_prompt_workflows](evidence/received_skills/06_prompt_workflows/readme.md)，S提供 | 三组模板→拟用提示词 | 已收到模板 | 未取得与模板逐字匹配的执行链 | 模板不是原始提示词；不得倒填历史 |

通用性、作者归属及许可均应以明确来源字段或文件为准。本批次只确认提供入口：本整理工作区、PYNQ工作区、S交付目录；未推断具体个人作者，亦未完成候选代码的许可审计。收到测试源码不等于测试已执行，缓存文件不是独立Skill。

<span style="color:#C00000">【待核验】候选六组的跨KV260/KR260/PYNQ-Z2/ZCU/Versal及多PYNQ/Python/内核声明没有对应验证矩阵；仍按目标范围处理。代码修复和新测试由PYNQ维护任务继续，本整理不覆盖其工作区。</span>

10/27材料审阅的授权在N037，职责在N038，[活动元数据](tools.json)保留三个started及后续事件。原子代理完整对话和逐次修改链未全部归档，因此只记录有证据的有限分工，不作为“硬件多代理工作流已验证”。
