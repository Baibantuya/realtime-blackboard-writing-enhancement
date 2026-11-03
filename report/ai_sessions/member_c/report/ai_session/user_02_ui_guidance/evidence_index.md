# U02：相机引导页的字体、精确居中和图标比例：证据索引

本页是整理索引。结论、消息与表中版本对应见[summary.md](summary.md)。同一消息中的“已完成”是历史陈述，需用对应结果文件限定范围。所有本轮动作均为文件读取、哈希/统计核对；没有执行工程脚本。

| 证据 | 相对路径 | 支持范围及限制 |
| --- | --- | --- |
| 可见消息 | [原文摘录](conversation.md) / [平台字段](messages.json) | 范围有限；不是完整导出；不含隐藏推理 |
| v1–v5演变 | [五版预览及检查口径](version_history.md) | 包含v1–v4 validation；早期排版边界和后期可见边界不能直接比较 |
| 五版身份 | [补充清单](../../../ui_history_inventory.json) | 295文件哈希；只有代表图和必要JSON复制入包，未重新渲染 |
| 源说明 | [查看](../../../sources/user_ui/guidance_readme.md) | 生成入口、资源和用途边界 |
| 资源manifest | [查看](../../../evidence/ui_guidance/assets_20261018_v5/manifest.json) | 31资源、字体/版式参数及SHA |
| 预览manifest | [查看](../../../evidence/ui_guidance/preview_20261018_v5/manifest.json) | 28页、指定状态、原图像素范围及SHA |
| 代表预览 | [查看](../../../evidence/ui_guidance/preview_20261018_v5/guidance_up_then_clockwise.png) | 可见排版结果，不是识别精度证据 |
| 资源本轮哈希 | [查看](../../../additional_checks.json) | assets项31/31；其中preview旧条目0/0表示当次未覆盖，不能当通过 |
| 预览补充哈希 | [查看](../../../preview_hash_check.json) | 后续按pages数组核对，28/28 |

原件位置、原件/副本SHA及脱敏信息见[总来源清单](../../../source_inventory.md)及其JSON。记录中提及但未复制的工程/远端文件不视为已离线归档。复制脚本或回执不表示本轮复测；数值结论限于对应平台、样本和版本。

缺项：所选消息的五条预览图片链接已取得；历史生成脚本快照、逐次源码差异和字体本体未完整复制。v5未取得独立validation.json；不据此补造历史记录，不能声称工作区可从零离线重建。
