# V24-A：发布材料核验与结论纠正

<span style="color:#C00000">【本次整理新发现／待核验】signoff_timing.json的setup_failing_endpoints为100，而完整combined_timing.rpt为8069。两者都未通过，但计数不一致；正文采用完整报告，摘要字段需交付维护方核对。本发现来自10/27整理读取，不补写成此前AI已发现。</span>

整理日期2026-10-27。本页为导读；原话在[消息摘录](conversation.md)，不是用交接摘要重建的问答。对应10/25、10/26两个所选轮次，其中后一个与Word案例共享。

## 需求、发现与更正

| 原文入口 | 当时的问题与处理 | 证据及可用结论 |
| --- | --- | --- |
| [N001–N011](conversation.md#n001) | 用户称新版PL/PS效果已较好，询问上传材料。核验发现原V24负时序、旧冻结runtime七项冲突及测试/重建资料缺口；用户N006回答暂时没有另一套报告 | [旧包审阅](evidence/handoff/v24_old_freeze_review.md)保留旧结论；文件名final不能替代签核 |
| [N012–N015](conversation.md#n012) | 用户提供S、旧冻结包、slim三目录；AI明确据新材料撤下不适用于slim的旧清单问题 | [10/26审计](evidence/word/material_audit.json)：新runtime两处各80项，35个Python副本一致。属当时只读文件比较，不是启动测试 |
| [N015–N023](conversation.md#n015) | 补入历史仿真、构建入口、发布与板端摘要，同时保留负时序 | [构建入口](evidence/release/build/rebuild_vivado.tcl)、[HLS入口](evidence/release/build/rebuild_hls.tcl)确实已提供；不再笼统说“入口缺失”，但干净环境重建仍需证据 |
| 同一发布审阅 | 总清单14项仍写v24，实物位于impl | 当时审计missing表示旧路径未命中；[交接核验](evidence/handoff/v24_word_handoff.md)解释移位与哈希匹配，不能把14份报告说成丢失 |

S/R/旧冻结包的原始绝对路径及副本身份在[来源清单](source_index.md)。本轮没有执行原包verify_submission.py、run.sh或加载器；清单规则与新增Skill未同步的问题仍独立存在，不能用runtime一致性掩盖。

## 结果必须按层陈述

- 原2021.2 V24的[完整时序报告](evidence/release/build/reports/impl/combined_timing.rpt)：WNS −1.588 ns、TNS −2182.223 ns、8069个setup失败端点；[时序摘录](evidence/release/build/reports/impl/timing_result.txt)仅列WNS/WHS。不得借用V23或2025.2候选结果。
- S/sim/results/v24是交付方历史CSim/Verilog CoSim，已选日志见来源索引；10/26及本次整理均没有重新仿真。保存的C/RTL gmem1输出哈希相等属于文件比较，不能改写为本地执行CoSim。
- [板端交付摘要](evidence/release/board/results/validation.json)只展示短窗口末两条display_presented为12.5 FPS；不是长期帧率、23.9ms端到端延迟或本轮板测。
- 用户“效果很好”的反馈、文件一致、仿真通过和时序失败可以同时成立；各自回答不同问题。

<span style="color:#C00000">【待核验】完整发布清单/规则、同版本干净重建、当前连续板测及时间校准仍需处理；队友B02/B04原文没有因新包到达而补齐。</span>

本案可提炼为“新证据到达后按版本撤回旧判断”的审阅流程；尚未新建或验证独立Skill。相关既有PYNQ检查器和新候选工具分列在[Skill索引](skill_evidence_index.md)。
