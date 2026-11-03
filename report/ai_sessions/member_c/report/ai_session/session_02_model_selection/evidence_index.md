# C02：三条检测优化路线、评价口径修正与候选选择：证据索引

本页是整理索引。结论、消息与表中版本对应见[summary.md](summary.md)。同一消息中的“已完成”是历史陈述，需用对应结果文件限定范围。所有本轮动作均为文件读取、哈希/统计核对；没有执行工程脚本。

| 证据 | 相对路径 | 支持范围及限制 |
| --- | --- | --- |
| 可见消息 | [原文摘录](conversation.md) / [平台字段](messages.json) | 范围有限；不是完整导出；不含隐藏推理 |
| 完整路线记录 | [查看](../../../sources/user_models/three_routes.md) | 各路线、身份、环境/命令、采纳/否决与负结果 |
| 开发集校准 | [查看](../../../evidence/model_selection/object_operating_point_calibration_01.json) | 阈值选择规则，不能把test用于选阈值 |
| 向量尺度检查 | [查看](../../../evidence/model_selection/resolution_magnitude_units_cpu_01.json) | 已知50px的单位错误及修正 |
| 首轮1000视频测试 | [查看](../../../evidence/model_selection/frozen_test_comparison_verified_01.json) | 该候选召回差值区间含零 |
| 后续候选登记 | [查看](../../../evidence/model_selection/followup_test_candidate_registry_01.json) | 检查点/阈值/测试身份，完整SHA |
| 后续2000视频结果 | [查看](../../../evidence/model_selection/followup_test_comparison_verified_01.json) | 计数、区间及提升范围 |
| 研究收尾 | [查看](../../../evidence/model_selection/research_goal_closeout_audit_01.json) | 训练分支/证据完成情况，是已有审计 |
| 640手机回归 | [查看](../../../evidence/model_selection/step_10000_native640_qualification.json) | 60/66及覆盖，不是手势准确率 |
| 640最终汇总 | [查看](../../../evidence/model_selection/highres640_final_summary.json) | 不同输入/训练分支身份 |

原件位置、原件/副本SHA及脱敏信息见[总来源清单](../../../source_inventory.md)及其JSON。记录中提及但未复制的工程/远端文件不视为已离线归档。复制脚本或回执不表示本轮复测；数值结论限于对应平台、样本和版本。

缺项：没有取得目标调整的全部用户原话、所有训练控制台/逐帧预测/重采样输入；仅选取必要JSON与文档。公开数据许可/打包与全链路离线复现未完成；不在本轮重新下载数据或训练。
