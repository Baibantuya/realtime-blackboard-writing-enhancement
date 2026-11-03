# U03：UI接入时保持显示刷新与多阶段流水：证据索引

本页是整理索引。结论、消息与表中版本对应见[summary.md](summary.md)。同一消息中的“已完成”是历史陈述，需用对应结果文件限定范围。所有本轮动作均为文件读取、哈希/统计核对；没有执行工程脚本。

| 证据 | 相对路径 | 支持范围及限制 |
| --- | --- | --- |
| 可见消息 | [原文摘录](conversation.md) / [平台字段](messages.json) | 范围有限；不是完整导出；不含隐藏推理 |
| 2Hz源说明 | [查看](../../../sources/user_ui/refresh_2hz_readme.md) | 早期线程/显示契约与运行说明 |
| 2Hz回归 | [查看](../../../evidence/ui_2hz/wsl_regression_01/validation.json) | 早期软件检查身份与结果 |
| 2Hz回放 | [查看](../../../evidence/ui_2hz/wsl_window_01/replay.json) | 识别与提交时间序列；不等于板端显示 |
| 单帧中间说明 | [原README](../../../evidence/ui_history/full_ui/full_ui_readme.md) | 明确承认单帧调度；旧F4/F5、记录初始化恢复，非最终语义 |
| 单帧两轮回归 | [93项](../../../evidence/ui_history/full_ui/evidence/full_regression_01/validation.json) / [98项](../../../evidence/ui_history/full_ui/evidence/full_regression_02/validation.json) / [98项日志](../../../evidence/ui_history/full_ui/evidence/full_regression_02/unittest.log) | 历史软件检查；通过不意味着满足多阶段流水需求 |
| 单帧窗口记录 | [图](../../../evidence/ui_history/full_ui/evidence/full_window_01/expanded.png) / [回执](../../../evidence/ui_history/full_ui/evidence/full_window_01/interaction.json) | WSLg真实LVGL窗口＋录制视频/硬件替身；window_keys为空，不证明真实键盘覆盖 |
| 最终流水说明 | [查看](../../../sources/user_ui/pipeline_readme.md) | 模式、记录、流水、运行边界及构建命令 |
| 最终回执 | [查看](../../../evidence/ui_pipeline/regression_03/validation.json) | 98个源码哈希、软件验证环境 |
| 最终测试日志 | [查看](../../../evidence/ui_pipeline/regression_03/unittest.log) | 96项既有回归，未在本轮重跑 |
| 窗口回放 | [查看](../../../evidence/ui_pipeline/window_grouped_01/interaction.json) | 477帧、13截图、三模式保存；window_keys为空 |
| 分组截图 | [查看](../../../evidence/ui_pipeline/window_grouped_01/expanded.png) | 下栏分组与离线标签，不能证明PL增强 |
| 集成回执 | [查看](../../../evidence/ui_pipeline/integration_receipt.json) | 上游/候选包身份线索 |

原件位置、原件/副本SHA及脱敏信息见[总来源清单](../../../source_inventory.md)及其JSON。记录中提及但未复制的工程/远端文件不视为已离线归档。复制脚本或回执不表示本轮复测；数值结论限于对应平台、样本和版本。

缺项：中间单帧候选的说明、两轮验证与代表图已经补取，完整工具历史和逐次源码差异仍未齐。板端ARM/DRM/真实键鼠和性能属于待验证范围，不在本轮补做。原README为字节保留副本，其内部旧路径不作为整理包的离线入口。
