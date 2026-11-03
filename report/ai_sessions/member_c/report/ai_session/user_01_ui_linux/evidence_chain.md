# U01：需求、修改与验证的对应链

以下是本次整理索引，不是新编对话。消息号均相对于本案[原文摘录](conversation.md)。按结果目录排序只能辅助定位，关键对应来自消息链接、工具执行ID与文件身份。

| 需求/反馈 | 历史AI建议和修正 | 当时产物/验证 | 本轮读取结论 |
| --- | --- | --- | --- |
| U01：Linux显示、中文和交互 | U03–U08：SDL2；显示自检超时后扩大池并报告断言 | [初次失败CTest](../../../evidence/ui_linux/history/ctest-1792256470684824932.log)、[x11_04](../../../evidence/ui_history/linux/x11_04/interaction_receipt.json) | 保留早期失败和37项通过；不是仅依据“编译成功” |
| U13：旧提示让人不理解 | U15：改为“记录完成后，可手动开启历史恢复” | [用户原图](../../../evidence/ui_history/attachments/wording_question.png)、[x11_11确认页](../../../evidence/ui_history/linux/x11_11/initialize.png) | 现在有明确修正前后文案，未改变两操作独立语义 |
| U14：恢复开启色改暖棕 | U15：改色 | [用户原图](../../../evidence/ui_history/attachments/recovery_color_feedback.png)、[x11_11恢复页](../../../evidence/ui_history/linux/x11_11/recovery.png) | 原绿色与后续暖棕色在图中可见 |
| U16：界面占比大，要箭头展开/收起 | U17–U23：默认仅留箭头，保留F9；排查WSLg输入时序 | [默认收起图](../../../evidence/ui_history/linux/x11_11/startup-collapsed.png)、[47项回执](../../../evidence/ui_history/linux/x11_11/interaction_receipt.json) | 真实输入执行经历x11_05–10失败后有通过记录，见工具索引 |
| U24：无操作自动隐藏 | U25–U30：10秒、输入重置、弹窗保护；修正Windows池断言 | [x11_12回执](../../../evidence/ui_history/linux/x11_12/interaction_receipt.json)、[Windows失败](../../../evidence/ui_linux/windows_regression/idle-assert-before-fix.log) | 64项历史检查；静态隐藏图不能替代计时回执 |
| U31：低资源改善清晰度 | U33–U35：Medium字重，保留75%窗口比例 | [x11_13图](../../../evidence/ui_history/linux/x11_13/main.png)、[资源JSON](../../../evidence/ui_linux/font_medium_resources.json) | Medium是实际实施的中间方案，后来被要求恢复Regular |
| U36：恢复Regular，放宽资源适配1080p | U37–U41：A8、原生输出、平滑缩放 | [最终图](../../../evidence/ui_linux/x11_14/main.png)、[65项回执](../../../evidence/ui_linux/x11_14/interaction_receipt.json)、[最终资源](../../../evidence/ui_linux/font_regular_1080p_resources.json) | 与最终回执和17源码身份对应；没有将该二进制SHA套给旧版 |

## 核对强度和局限

- x11_04/11/12/13的所选图与回执及x11_14两张补图，在既有export_sha256.json中有相应条目，本轮17个所选条目全部匹配；清单本身是本地证据，不是第三方签名。
- x11_11和x11_12的main.png字节完全相同。自动隐藏改变的是时间行为，因此用“新版截图更好”证明自动隐藏会失真，必须看x11_12新增的回执项。
- x11_04/11/12/13回执没有二进制SHA；保留这一缺口，不使用x11_14的SHA补填。
- 初次主屏、Medium与原生1080p的输出尺寸不完全相同；图片显示大小/截图缩放不能作为清晰度的定量指标。最终原生像素回读与资源记录提供更直接依据。
- 14条执行记录中7次失败、7次通过，不是同一条件的重复抽样，不能计算可靠性百分比。失败保留用于说明测试脚本/焦点与实际UI行为需要分开排查。
- 未新增工程执行。当前结果只支持该历史环境与版本，后续U03按键/记录含义变化见[版本边界](../version_and_contribution.md)。
