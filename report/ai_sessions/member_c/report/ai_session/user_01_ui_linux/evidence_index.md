# U01：Linux UI适配、自动收起与1080p清晰度：证据索引

本页是整理索引。结论、消息与表中版本对应见[summary.md](summary.md)。同一消息中的“已完成”是历史陈述，需用对应结果文件限定范围。所有本轮动作均为文件读取、哈希/统计核对；没有执行工程脚本。

| 证据 | 相对路径 | 支持范围及限制 |
| --- | --- | --- |
| 可见消息 | [原文摘录](conversation.md) / [平台字段](messages.json) | 范围有限；不是完整导出；不含隐藏推理 |
| 原消息附件 | [两张截图与消息ID](attachment_index.md) | 从localImage精确路径补取；当前哈希不等于消息自带历史哈希 |
| 中间版本证据链 | [需求、修正、截图与回执](evidence_chain.md) | x11_04/11/12/13/14分版本；早期回执缺二进制SHA |
| 历史执行记录 | [14条命令索引](tool_evidence.md) | 包含7次非零退出；完整可见字段另存JSON，没有本轮执行历史命令 |
| UI源说明 | [查看](../../../sources/user_ui/linux_readme.md) | 构建、依赖、验证用法与版本上下文；不是聊天原文 |
| 最终回执 | [查看](../../../evidence/ui_linux/validation_receipt.json) | 平台、源码和二进制身份；源码17项本轮可对应 |
| 早期Linux失败 | [查看](../../../evidence/ui_linux/history/ctest-1792256470684824932.log) | 显示自检失败/超时历史；不能删去 |
| Linux最终验证 | [查看](../../../evidence/ui_linux/ctest.log) | 4项既有CTest结果，非本轮新执行 |
| 像素与显示检查 | [查看](../../../evidence/ui_linux/linux_display_selftest.log) | 输出与字体/坐标等自检，不等于板卡显示 |
| Windows断言失败 | [查看](../../../evidence/ui_linux/windows_regression/idle-assert-before-fix.log) | 失败前状态，和最终CTest分开 |
| Windows最终回归 | [查看](../../../evidence/ui_linux/windows_regression/ctest.log) | 3项既有测试 |
| 中间Medium资源 | [查看](../../../evidence/ui_linux/font_medium_resources.json) | 低资源尝试的量化代价 |
| 最终Regular资源 | [查看](../../../evidence/ui_linux/font_regular_1080p_resources.json) | 最终字体、画布与资源代价 |
| 最终X11交互 | [查看](../../../evidence/ui_linux/x11_14/interaction_receipt.json) | 65项检查、时间/窗口信息 |
| 展开截图 | [查看](../../../evidence/ui_linux/x11_14/main.png) | 辅助视觉证据，非摄像头板测 |
| Linux验证脚本 | [查看](../../../evidence/ui_linux/verify_linux.py) | 历史执行用法/检查定义；本轮未执行 |
| X11验证脚本 | [查看](../../../evidence/ui_linux/verify_x11_interaction.py) | 交互回执的测试流程；本轮未执行 |

原件位置、原件/副本SHA及脱敏信息见[总来源清单](../../../source_inventory.md)及其JSON。记录中提及但未复制的工程/远端文件不视为已离线归档。复制脚本或回执不表示本轮复测；数值结论限于对应平台、样本和版本。

缺项：没有导出完整工具历史与全部上下文；历史模型未记录。两张所选用户消息附件已取得，不再列为缺项。从零构建所需完整依赖和中间源码快照没有全部复制进工作区。
