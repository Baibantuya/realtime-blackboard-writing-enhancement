# Technical report evidence index

本索引对应仓库版 [technical_report.docx](technical_report.docx)。报告正文保持原样，本页提供章节到源文件、原始结果及待补资料的对应关系。单独提交的 Word 报告不作修改。

| 仓库报告位置 | 依据或附件 | 核对与使用方式 |
|---|---|---|
| 2.1–2.4 系统与流水 | [HLS 源码](../src/pl/hls/)、[PS 源码](../src/ps/)、[部署配置](../board/runtime/config/deployment.json) | 对照 Rectify、Restore、PS 内容服务和 Scene Q 的实际连接与职责 |
| 4.1–4.3 时序、资源 | [C5 timing](../build/reports/c5/timing.rpt)、[C5 utilization](../build/reports/c5/utilization.rpt)、[R5 timing](../build/reports/r5/timing.rpt)、[R5 原始日志](../build/reports/r5/logs/) | C5/R5：WNS +0.011 ns、DSP 839；原 V23 资源对比另需匹配来源 |
| 4.3 CDC / 复位 | [C5 实现报告](../build/reports/c5/)、[补充 CDC 仿真](../sim/supplemental/cdc/) | 总线偏斜裕量与 CDC 分类分别引用；保留 70 Warning、4 LUTAR-1 的审查项 |
| 5.1 HLS 与 RTL 测试 | [三核原始报告](../build/reports/hls/)、[Rectify 补充记录](../sim/supplemental/rectify/) | Rectify 20 组1080p C测试、Scene 9 次RTL事务、Restore 123 次RTL事务；63次小图与12次边界调用另列 |
| 5.2 整机帧率 | [旧版板测 validation.json](../board/results/legacy_v24/validation.json)、[board_health.json](../board/results/legacy_v24/board_health.json) | 旧 V24 两个末次窗口 display_presented 为12.5 FPS；按 capture / rectify / restore / quantize / display 字段区分 |
| 5.2–5.3 29.92 FPS、52.39 ms、89 ms、24 次启动等 | [评审清单](../report_review.md) | 部分数字目前来自会话总结；对应运行原始记录、版本和统计口径待逐项补齐。现有旧版板测窗口不能替代这些数字的来源 |
| 5.1 QEMU | [评审清单](../report_review.md) | 成功执行记录尚未找到；已有主机、C/RTL 与实现报告分别使用 |
| 6.1–6.2 AI Sessions | [团队索引](ai_sessions/readme.md)、[文件来源与哈希](ai_sessions/source_manifest.json) | 总结、原始可见消息与结果附件分别标识；按所选案例引用 |
| 6.3 Skill 测试 | [离线验证汇总](../build/reports/packaging/validation_summary.json)、[工具目录](../skill/) | 对应实际离线测试；跨板卡验证和长期板端效果另附现场记录 |
| 7.1–7.2 板端环境 | [环境说明](../board/environment.md)、[二进制核验](../board/environment_binary_inspection.json) | Ubuntu22.04/PYNQ3.0.1为历史确认；内核和ARM64来自随包文件；待现场采集项见说明 |
| 7.3–7.4 构建与封装 | [当前入口说明](../readme.md)、[构建目录](../build/)、[C5导出记录](../build/provenance/export_history/) | 使用2025.2入口；整机P&R与硬件导出步骤分别列明 |
| 历史60+4测试 | [原始汇总](attachments/legacy_test_summary.json)、[旧入口](attachments/legacy_run_tests.py.txt) | 属于历史交付汇总；当前测试单独列举 |
| 整机实拍 | [照片与图题](photos/readme.md)、[原文件哈希](photos/source_manifest.json) | 已提供1张整机全貌、2张板卡实物图；整机正面照可与现有全貌图配对 |

## 历史附件整理

上一轮的93项统计是旧 Markdown 中的相对路径引用，包含搬迁后的链接、同一文件被多次引用和旧阶段资料。它们不等于93项赛事必交附件。本轮优先恢复可定位的工程/报告/Skill引用；原始路径、恢复位置、哈希与仍保留的历史引用见 [附件整理记录](attachments/reference_resolution.json)。暂缓的模型/手势探索和旧整包可保留出处，不扩展本次整机交付范围。
