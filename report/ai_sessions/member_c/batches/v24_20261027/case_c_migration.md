# V24-C：2025.2迁移、最小复现与仍未通过的时序

整理日期2026-10-27，过程状态截到已完成的第二阶段轮次N058–N142。N028–N057为第一阶段，旧报告和原话保持原状。所有工程执行发生于“项目综合”的历史轮次；本整理只复制、读取和核对。

## 从旧RTL可综合到源码可重建

[N028](conversation.md#n028)提出整体架构需在2025.2验证。第一阶段完成旧BD/XCI升级、连接核对和部分C测试；恢复核C++在综合阶段崩溃，尚未进入那次RTL联仿。N049区分“旧RTL被新版Vivado接受”和“源码能重新生成RTL”。这一阶段的候选综合成功，没有掩盖恢复源码重建失败。

[N058](conversation.md#n058)继续要求处理时序、CDC、HLS并完成布局布线，保留原V24。诊断先缩小到局部笔迹函数，再到亮度入口。强制内联等尝试失败；N063记录只移除三条强制DSP乘法资源绑定、保留整数表达式后最小入口通过。它是本机可复现触发条件和兼容规避方案，不能当作已经证明厂商内部根因或官方修复。

| 原文与证据 | 结论 |
| --- | --- |
| [N063](conversation.md#n063)、[失败探针](evidence/migration/hls_probe_luma.log)、[成功探针](evidence/migration/hls_probe_inferred_luma.log) | 最小对照用于定位绑定触发条件 |
| [失败内联尝试](evidence/migration/hls_restore_inline_ascii_cwd.log)、[修改manifest](evidence/migration/restore_inferred/manifest.json) | 失败保留，调整限于独立副本；manifest记录输入身份 |
| [N065/N076](conversation.md#n065)、[完整日志](evidence/migration/restore_inferred_20261027.log)、[Verilog报告](evidence/migration/rh1/s/sim/report/whiteboard_restore_cosim.rpt) | 恢复核C测试、综合、123次联仿和IP导出通过；64×32原测试，不外推1080p帧率 |
| [N110](conversation.md#n110)、[计数测试](evidence/migration/scene_count_tree/tally_test.log)、[修改清单](evidence/migration/scene_count_tree/manifest.json)、[联仿](evidence/migration/sc1/s/sim/report/board_scene_quantize_cosim.rpt) | 531441组类别穷举＋100000组固定种子测试，原160×33的9次RTL联仿通过；不是全部实景覆盖 |

## 布线结束后继续保留负结果

| 完整实现 | WNS/ns | TNS/ns | setup失败端点 | 对应原始报告 |
| --- | ---: | ---: | ---: | --- |
| impl1 | −1.014 | −1014.192 | 4143 | [timing](evidence/migration/impl1/timing.rpt)、[阶段记录](evidence/migration/impl1/stages.tsv) |
| impl2 | −1.411 | −1201.115 | 2961 | [timing](evidence/migration/impl2/timing.rpt)、[阶段记录](evidence/migration/impl2/stages.tsv) |
| impl3 | −0.219 | −84.981 | 624 | [timing](evidence/migration/impl3/timing.rpt)、[阶段记录](evidence/migration/impl3/stages.tsv) |

第二轮资源减少但WNS更差，不能称每次优化均有效；第一、二轮核实现不同，也不是单变量比较。第三轮WNS比第二轮改善1.192ns，仍小于0。[N139–N142](conversation.md#n139)明确使用最终报告值，而非路由器中途估计−0.407ns；最差路径转到恢复核局部笔迹计算，不继续把量化核称为最终唯一瓶颈。

<span style="color:#C00000">【待核验／时序未通过】第三轮仍有624个setup失败端点，保持时间无违例不能抵消建立时间失败。没有新发布bit/XSA、没有新版KV260板测，不得配用候选HWH与旧bit。</span>

[CDC报告](evidence/migration/impl3/cdc.rpt)和[阶段审计](evidence/migration/phase2_validation.json)保留Critical 0、CDC-6 Warning 2及CDC-15 Warning 68；原CDC-11在优化后消失且未新增waiver，但警告、外设约束与复位仍需审查。“无Critical”不等于完整CDC签核。

第三候选[BD结构](evidence/migration/candidate3_bd_diff.json)、[HWH](evidence/migration/candidate3_hwh_diff.json)及[Windows](evidence/migration/ps_candidate/validation_c3_win32.json)/[WSL](evidence/migration/ps_candidate/validation_c3_linux.json)别名检查属于静态接口证据。26地址范围相同不意味着所有描述相同；Scene control→control_r偏移仍为0x68。MIPI/帧缓存无寄存器元数据仍为NOT_CHECKED。

## 用户询问、社区方案和本机试验分别记录

[N099/N100](conversation.md#n099)保留W:问题与临时SUBST说明；[清理回执](evidence/migration/drive_cleanup.json)记录活跃工具为0后取消别名、D盘目录保留。本轮没有创建或取消盘符。

[N106/N112](conversation.md#n106)要求检索网络及社区。历史[方案核查文档](evidence/migration/timing_research_20261027.md)是当时研究记录，本轮没有重新搜索或把外部经验当成新验证。进程级环境变量建议的[本机试验](evidence/migration/startup_no_local_data_result.json)仍异常退出；N141保留负结果。此探针未复现论坛原有并行启动条件，不能据此否定原帖，也不能宣布本机已修复。

可提炼的两个流程是“最小复现→单变量调整→原测试→整机仍有负结果”和“外部建议→适用条件→本机试验→保留失败”。它们目前为案例经验，未另建已验证通用Skill。未来优化/签核不属于本次归档操作。
