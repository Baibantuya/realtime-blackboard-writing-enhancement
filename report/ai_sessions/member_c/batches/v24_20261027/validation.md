# 2026-10-27增量归档核查

本次只读核对文件身份、消息ID、相对链接、报告字段和既有回执；没有执行工程、仿真、训练或板测。10/23核查报告未覆盖。

| 检查 | 结果 |
| --- | --- |
| copied_file_identity | 通过 |
| selected_sources_still_match_read_snapshot | 通过 |
| old_messages_receipts_word_latex_preserved | 通过 |
| platform_id_deduplication | 通过 |
| visible_text_mapping | 通过 |
| selected_command_metadata | 通过 |
| historical_limited_delegation_provenance | 通过 |
| migration_raw_timing_reports | 通过 |
| v24_summary_disagreement_recorded | 通过 |
| migration_prior_manifest_selected_hashes | 通过 |
| word_scope_revision_identity | 通过 |
| skill_receipt_scope | 通过 |
| generated_navigation_links | 通过 |
| batch_english_child_paths | 通过 |
| obvious_secret_private_host_scan | 通过 |
| batch_json_parse | 通过 |

新增74份副本；142条／5轮消息与旧182条／24轮按ID去重为324条／29轮。93条命令只有可见元数据，7条子代理活动只支持当时有限材料审阅。保护快照覆盖旧原文/回执及当前Word、LaTeX。

原V24完整时序报告8069个setup失败端点与signoff摘要100不一致，已作为待核验项保留。三轮2025.2原始时序与阶段审计哈希/字段匹配，但第三轮仍WNS−0.219、TNS−84.981、624个失败端点。此处“通过”指归档检查通过，绝不代表工程签核通过。

当前Word哈希与历史范围修订after_sha256一致；未重渲染。V22检查器429/7及23构造测试、候选生成器67处错误来自既有回执，本轮未重跑。没有调用可能写文件或加载硬件的run.sh/check。

新增英文子路径检查不覆盖中文父目录。原始路径、外链和用户可见消息仍保留；未完成公开匿名/许可审查，也未发布。未读取work/logs/work.steps.log。

[机器记录](validation.json) · [来源索引](source_index.md) · [Skill机器映射](case_skill_map.json) · [10/23历史核查](../../validation_report.md)
