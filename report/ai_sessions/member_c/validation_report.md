# 本轮文件与证据核对

日期：2026-10-23。以下为本轮实际执行的只读核对。未运行UI、训练、推理、综合或板端测试。工程历史回执中的PASS保持其原有时间和平台。

| 核对项 | 本轮结果 |
| --- | --- |
| selected_evidence_copies | 通过，103项 |
| selected_originals_unchanged_since_copy | 通过，103项 |
| supplied_archive_identity | 通过，3项 |
| teammate_source_copies | 通过，10项 |
| ui_linux_sources | 通过，17项 |
| ui_pipeline_sources | 通过，98项 |
| guidance_assets_hashes | 通过，31项 |
| guidance_preview_hashes | 通过，28项 |
| visible_message_mapping | 通过 |
| rgb565_summary_arithmetic | 通过，14项 |
| phone_per_hand_counts | 通过 |
| latex_source_unchanged | 通过 |
| skill_structure_ui-evidence-validation | 通过 |
| skill_structure_controlled-model-comparison | 通过 |
| generated_prose_relative_links | 通过，266项 |
| skill_and_prose_placeholders | 通过 |
| json_parse | 通过，73项 |
| workspace_child_ascii_names | 通过 |
| obvious_secret_and_private_host_scan | 通过 |
| ui_followup_audit | 通过，8项 |

六案共182条可见消息、24个所选轮次。核对摘录与messages.json映射，不能证明平台之外或未选轮次没有缺失。

Skill结构检查首次在捆绑Python中因缺少PyYAML无法运行，随后使用已安装的Python 3.14/PyYAML 6.0.3执行原校验器，两项结果见JSON；没有安装依赖或修改系统配置。启动器提示路径定位警告，但校验器实际运行、返回码为0。

链接检查覆盖新写导读与Skill正文；sources/evidence内的原件副本和原文中的旧本机/远程引用不计作离线可用链接。明显秘密/私网地址模式未命中也不等于完成匿名审查。

31资源/28预览哈希核对未重新渲染；17/98源码哈希核对未执行源码；三种子14项统计复算未重训；手机逐手计数重算未推理；LaTeX原件哈希与开始快照一致。V22整包历史审计未在本轮重新执行。

UI补充核对另覆盖新增42份副本、两张消息附件、14条历史X11记录、五版295文件哈希及单帧中间候选；详见[补充报告](ui_followup_verification.md)。综合副本数为103，不等于全量原始实验归档。

初次消息校验把平台的final_answer误写为final白名单，已按实际API字段修正校验器；没有改动原文/消息角色。[初次检查记录](validation_initial_run.json)保留该问题。

详见[机器可读记录](validation_results.json)、[来源清单](source_inventory.md)、[缺项清单](missing_items.md)。**这些检查通过不等于正式提交就绪。**
