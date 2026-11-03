# C01：公开物体漏检、手机手框与ONNX严格一致性诊断：证据索引

本页是整理索引。结论、消息与表中版本对应见[summary.md](summary.md)。同一消息中的“已完成”是历史陈述，需用对应结果文件限定范围。所有本轮动作均为文件读取、哈希/统计核对；没有执行工程脚本。

| 证据 | 相对路径 | 支持范围及限制 |
| --- | --- | --- |
| 可见消息 | [原文摘录](conversation.md) / [平台字段](messages.json) | 范围有限；不是完整导出；不含隐藏推理 |
| 公开漏检/导出源说明 | [查看](../../../sources/user_models/detection_analysis.md) | 身份、环境/命令、统计与限制 |
| 公共集统计 | [查看](../../../evidence/model_detection/objects/summary.json) | 2000图漏检分组/数量 |
| 阈值后续 | [查看](../../../evidence/model_detection/objects/cached_followup.json) | 缓存输出的不同阈值取舍 |
| 导出细节 | [查看](../../../evidence/model_detection/export/details.json) | 51图、后端与逐元素差异 |
| 关闭优化对照 | [查看](../../../evidence/model_detection/export/optimization_replay.json) | 未修复的负结果 |
| 手机诊断说明 | [查看](../../../sources/user_models/phone_miss_analysis.md) | 55帧66手、裁剪是GT诊断 |
| 手机统计 | [查看](../../../evidence/model_detection/phone/summary.json) | 视频/标注/ONNX完整SHA及分组 |
| 同尺度上下文 | [查看](../../../evidence/model_detection/phone/peripheral_context_control.json) | 20/66，输入手区域像素不变 |
| 逐手表 | [查看](../../../evidence/model_detection/phone/per_hand.csv) | 每手候选与对照结果可追踪 |
| 手机检查输出 | [查看](../../../evidence/model_detection/phone/verification.txt) | 3项既有追踪测试与基线复现 |
| 手机输入/脚本清单 | [查看](../../../evidence/model_detection/phone/analysis_manifest.json) | 版本和输入身份 |
| 既有本地回执 | [查看](../../../evidence/model_detection/local_receipt.json) | 历史本机核验，非本轮推理 |

原件位置、原件/副本SHA及脱敏信息见[总来源清单](../../../source_inventory.md)及其JSON。记录中提及但未复制的工程/远端文件不视为已离线归档。复制脚本或回执不表示本轮复测；数值结论限于对应平台、样本和版本。

缺项：没有完整聊天和工具输出，原始NPY/全部手卡未复制；首个后端差异算子尚未确定。后续候选的一致性结论需独立案例证据，不能回写旧结果。
