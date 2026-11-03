# MIPI RX CDC 待审查记录

此记录只汇集本地核查证据，不代表已向 AMD 或队友发送。目标器件 xck26-sfvc784-2LV-c，Vivado 2025.2 Build 6299465；源工程 v24 保留。

## 当前结论

综合阶段曾有 2 条 CDC-11（Fan-out from launch flop to destination clock）。14:31 完成的额外核查确认：优化后与布线后使用 `-all_checks_per_endpoint` 均为 Critical 0，这两条不再出现；没有新增 waiver。以下复现记录保留用于解释阶段差异。

<span style="color:#C00000">【尚未完成全部 CDC／约束审查】布线后仍有 CDC-6 Warning 2、CDC-15 Warning 68，方法学报告还有 TIMING-9 和 4 条 LUTAR-1。5 条 TIMING-24 已在下述严格约束诊断中解决，但最终候选仍须重新检查。不得将 Critical 0 改写为所有跨时钟与复位协议均已验证。</span>

## 15:14 严格约束诊断更新

`mipi_exception_diagnostic3.tcl` 在第一轮 `impl1/routed.dcp` 上完整导出约束，只移除一条覆盖 MIPI FIFO／video 域的宽泛异步时钟组。保留其余原有例外及 XPM 的 `set_max_delay -datapath_only`、总线偏斜约束，不增加 false path 或 waiver。

- 时钟物理源引脚、主时钟源、周期、波形、相位和抖动签名逐项相同。前两次诊断因自动派生时钟重命名触发名称保护而停止；证据保留。第三次同时证明被重命名的标签未被 XDC 引用，才继续。
- MIPI FIFO→video 最差裕量 +7.729 ns；video→FIFO +4.487 ns。所有已报告总线偏斜约束满足，最小裕量 +4.084 ns。
- 建立时间受检端点由 332,886 增至 332,908，增加 22 个；整机 WNS 仍为 −1.014 ns。没有靠减少检查获得改善。
- 5 条 TIMING-24 和对应 TIMING-28 不再报告。全检查项 CDC 仍为 Critical 0、CDC-6 Warning 2、CDC-15 Warning 68。
- `no_clock`、内部未约束端点、重复时钟、错误派生时钟、组合环均为 0。外部 I²C 两个双向端口缺输入／输出延迟，MIPI 两路数据输入缺常规输入延迟，仍需按实际接口和 IP 时序方法审查，未虚构数值或添加豁免。

证据目录 `mipi_exception_review3/`；诊断进程退出码 0。这仅证明已布线的第一候选在收紧约束后上述检查成立。`tighten_mipi_exception.tcl` 将同样的删除范围和时钟签名保护用于隔离的第二候选实现；厂商 IP 和原 v24 工程未修改，第二候选结果单独报告。

## 已排除与已核实

- 已修正 Clock Wizard 对 PS 内部时钟重复建立主时钟的问题。三个输出仍为 200 MHz，并共同派生自真实的 PS `clk_pl_0`。两条 CDC-11 未因此消失。
- 顶层来源是 `clk_out2_video_design_1_clk_wiz_0_0`，目的为 `clk_out1_design_1_clk_wiz_0_0`，报告同步深度为 3，现有例外为 False Path。没有为消除告警新增例外。
- `lite_aclk` / `video_aclk` 分别连接对应 Clock Wizard 输出；复位分别来自 `rst_clk_wiz_0_100M` / `rst_clk_wiz_0_200M` 的 `peripheral_aresetn`。模块名称中的 100M 不是当前实际运行频率证据。
- 含未展开子核、没有时钟的外层 DCP 的“安全”报告无效，不能作为签核依据。
- 无黑盒的 `bd_d10d_rx_0.dcp` 叶核，在明确定义的边界时钟下也能复现 2 条 CDC-11。此独立模型用于定位内部结构，不能代替顶层真实时钟关系。
- 加密节点名称在报告中为 `<hidden>`；本轮未尝试修改或解密厂商逻辑。

## 复核入口

| 内容 | 文件 |
|---|---|
| 顶层修正后的 CDC | `cr2/cdc.rpt` |
| 主时钟与派生关系 | `cr2/clocks_after.rpt`、`cr2/interactions.rpt` |
| 原有全部时序约束 | `cr2/before.xdc` |
| 修正后的约束 | `cr2/corrected.xdc` |
| 物理时钟连线证明 | `cr2/physical_clock_connection.txt`、`cr2/upstream_clock_cells.txt` |
| 叶核可复现诊断 | `mipi_rx_cdc_leaf_primary_20261027.tcl`、同名 `.log` |
| 叶核详细 CDC | `mipi_leaf2/cdc_all_checks.rpt` |
| 实际布线后的最终复核 | `impl1/cdc.rpt`；须在实现完整结束后读取 |
| 包含全部检查项的复核 | `cdc_impl_review/optimized_all_checks.rpt`、`routed_all_checks.rpt`；两者均 Critical 0 |

## 仍须确认

1. 这两条扇出分别传递什么状态或复位语义，目的寄存器是否会重新汇合。
2. 是否属于合法的异步 FIFO 复位结构；若是，复位同时置位、各域同步释放、等待 busy 完成后才读写的条件如何由本设计保证。
3. 当前 MIPI RX 6.0 的该 revision 是否有适用的官方说明或补丁。厂商 IP 身份、同步深度 3、相同标称频率本身都不足以证明可以忽略。
4. 实现后例外、同步寄存器属性及结构是否仍然一致。

现有两条 CDC-11 不需要为了消除报告而添加 waiver；它们已经在实现优化后不再出现。剩余多位／使能跨域结构、TIMING-9 和异步复位组合逻辑仍需审查。若后续确需豁免其他事项，必须记录精确端点、规则 ID、依据和适用 IP 版本，并重新运行顶层检查。

## 第二轮布线实际复核（16:01 完成）

`impl2/cdc.rpt` 使用 `-details -all_checks_per_endpoint`，Critical 为 0；CDC-3 Info 85、CDC-6 Warning 2、CDC-9 Info 3、CDC-15 Warning 68。严格约束操作已在 `impl2/mipi_constraints/` 留档；`impl2/methodology.rpt` 无 TIMING-24／TIMING-28，仍有 LUTAR-1 4 条、TIMING-9 1 条以及其他时序／资源检查项。没有为消除警告增加 waiver。

<span style="color:#C00000">【CDC 尚非全部签核】Critical 0 不能替代对 70 条 Warning、复位结构和板端行为的审查。第二轮 WNS −1.411 ns，整机建立时间仍未通过。</span>

参考：[AMD UG906 CDC 规则](https://docs.amd.com/r/2023.1-English/ug906-vivado-design-analysis/CDC-Rules-Precedence)、[异步复位同步器说明](https://docs.amd.com/r/2023.2-English/ug906-vivado-design-analysis/Asynchronous-Reset-Synchronizer)。这些是方法依据，不是对本工程的个案批准。


## 第三轮实现终态补充

2026-10-27 17:13:34 的 `impl3/cdc.rpt` 已使用 `-all_checks_per_endpoint`：Critical 0；CDC-6 Warning 2、CDC-15 Warning 68；CDC-3 Info 85、CDC-9 Info 3。未增加 waiver。`impl3/methodology.rpt` 保留 LUTAR-1 4、TIMING-9 1、ULMTCS-1 1、CLKC-56／58 各1；TIMING-16 本轮未出现。

`impl3/timing.rpt` 最终 WNS −0.219 ns、TNS −84.981 ns，624 个建立时间违例；保持／脉宽违例0。no_clock／unconstrained_internal_endpoints 为0，接口 missing input/output delay 分别4／2，仍需按实际外设路径审查。

<span style="color:#C00000">【未完成签核】Critical 为0不代表 CDC、复位及外设时序审查全部通过。原 v24 保留，无新位流、无板端验证。</span>
