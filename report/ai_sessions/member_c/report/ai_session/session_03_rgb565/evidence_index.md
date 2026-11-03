# C03：RGB565手形适配、三种子重复与JS负结果：证据索引

本页是整理索引。结论、消息与表中版本对应见[summary.md](summary.md)。同一消息中的“已完成”是历史陈述，需用对应结果文件限定范围。所有本轮动作均为文件读取、哈希/统计核对；没有执行工程脚本。

| 证据 | 相对路径 | 支持范围及限制 |
| --- | --- | --- |
| 可见消息 | [原文摘录](conversation.md) / [平台字段](messages.json) | 范围有限；不是完整导出；不含隐藏推理 |
| 三种子说明 | [查看](../../../sources/user_models/rgb565_replicates.md) | 环境、冻结起点/数据、选择规则与结论 |
| 重复配置 | [查看](../../../evidence/model_rgb565/server_results/replication_config.json) | 种子、方法、预算、初始化身份 |
| 全种子汇总 | [查看](../../../evidence/model_rgb565/server_results/three_seed_summary.json) | 每种子、所选epoch、均值/样本SD、门槛 |
| 手机框原生CPU | [查看](../../../evidence/model_rgb565/server_results/phone66_multiseed_native_cpu.json) | 颜色状态和拒识，非准确率 |
| 既有本地核验 | [查看](../../../evidence/model_rgb565/local_verification.json) | 历史校验范围 |
| 本轮统计复算 | [查看](../../../additional_checks.json) | 14项均值与样本标准差相符 |
| 连续回放边界 | [查看](../../../sources/user_models/sequence_boundary.md) | 候选事件/关键点诊断的真值限制 |

原件位置、原件/副本SHA及脱敏信息见[总来源清单](../../../source_inventory.md)及其JSON。记录中提及但未复制的工程/远端文件不视为已离线归档。复制脚本或回执不表示本轮复测；数值结论限于对应平台、样本和版本。

缺项：前序首轮与TF32/ONNX的完整底层输出未全部纳入本包；本案主结果以三种子结构化归档为准。新增种子未有各自导出/板端证据，缺乏陌生实拍事件真值验收；完整训练日志、数据/权重没有复制。
