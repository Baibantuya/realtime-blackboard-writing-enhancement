# UI历史材料补充核对

检索/复制日期：2026-10-22；本次文件核对：2026-10-23。仅读取原件、比较哈希、核对消息和历史回执、复算manifest字段；没有执行工程、重新渲染、训练或板端测试。

| 核对项 | 本轮结果 |
| --- | --- |
| ui_history_42_copies_and_originals | 通过，42项 |
| ui_historical_export_manifest | 通过，17项 |
| guidance_five_versions_hash_and_manifest_arithmetic | 通过，295项 |
| recovered_attachments_message_mapping | 通过，2项 |
| visible_x11_records_mapping | 通过，14项 |
| historical_receipt_consistency | 通过，7项 |
| original_message_file_links | 通过，18项 |
| main_case_quoted_original_text | 通过，5项 |

新增42份文件为原字节副本，其中两张为原用户消息附件。17份Linux导出文件同时匹配既有export manifest；这是一致性核对，不是独立签名认证。五版295个文件做哈希核对，只有代表页和必要记录入包，不能称295份全部离线归档。

14条历史X11可见输出均未标截断，保留7条非零退出。37/47/64/64/65取自各版汇总和对应回执；中间单帧93/98项是另外的软件测试集合。没有把历史通过改写为本轮复测。

v3选定排版边界109行偏差0，v4/v5选定可见边界各84行最大0.25px；这是记录字段的算术核对。v4历史validation对100行给出最大0.5px，范围不同，保留原结果；约7px仍仅作为历史消息中的分析。

原附件没有平台嵌入的独立历史哈希，早期回执没有二进制SHA，中间源码快照/逐次差异及完整会话仍未齐；当前也没有对应版本的KV260验证。详见[缺项清单](missing_items.md)。

[机器可读结果](ui_followup_verification.json) · [新增副本与原件路径](ui_history_inventory.json) · [UI主案例](report/ai_session/ui_main_case.md) · [工作区综合核对](validation_report.md)
