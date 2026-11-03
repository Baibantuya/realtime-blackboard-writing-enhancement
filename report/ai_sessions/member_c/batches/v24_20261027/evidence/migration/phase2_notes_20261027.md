# V24 → 2025.2：时钟、CDC、恢复核与实现验证

日期：2026-10-27（Asia/Taipei）。本轮在 `v24_2025_2` 的新目录继续验证，原始 `最终素材`、`baseline`、上一轮的成功／失败结果均保留。处理和视频／PHY 时钟仍为 200 MHz。

## 时钟约束

Clock Wizard 设置仍为外部单端输入，但其输入实际接 PS `pl_clk0`。`cr2/physical_clock_connection.txt` 证明两者在同一网线上，`upstream_clock_cells.txt` 显示上游只有 `BUFG_PS` 和 `PS8`。首次 `cr1` 使用了缓冲前 PS8 管脚作为相等性比较锚点，断言安全停止，未改变约束；改用缓冲后的接口网线后通过。

`clock_review_buffered_20261027.tcl` 只从导出的完整时序约束中移除 Clock Wizard 重复的 `create_clock` 及对应输入 jitter，将同样的 0.100 ns jitter 赋给真实的 `clk_pl_0`。随后确认三个 5 ns 输出都以 `clk_pl_0` 为主时钟，重新生成全部派生时钟并保存新 DCP。其余时序例外保留。新 DCP：`cr2/corrected_synth.dcp`。

这是候选检查点的约束修正。后续重新生成 BD 时，还应将 Clock Wizard 的输入类型按真实 PS 缓冲输出配置，重新生成并验证；不能只在最终报告阶段删除时钟来美化结果。修正后综合估算 WNS 仍为 −1.736 ns，不能把重复时钟当成所有负 slack 的原因。

## 恢复核 HLS 排查

依次将原函数拆成独立综合入口：颜色通道和形态滤波可通过；局部笔迹函数失败；进一步缩小到只有 41 条中间指令的亮度函数，同样在 Performance 阶段崩溃，调用栈偏移 `clang.exe+0x5535a6` 相同。

原 `resource_math.h` 的三条 `BIND_OP ... op=mul impl=dsp latency=2` 是本机这条编译路径的可复现触发条件。独立副本只移除这三条资源绑定，整数表达式、舍入和 `INLINE` 保留，同一亮度入口综合通过。候选文件在 `restore_inferred/`，修改及原文件哈希见其 `manifest.json`。这是通过对照试验确认的兼容规避方法，尚不等于已经知道厂商编译器内部缺陷的全部成因。

失败的诊断也保留：强制内联、禁止局部循环 flatten、关闭 auto-rewind、仅把同一行的两个循环分行均未解决；Clang 7 选项被工具接受，但前端拒绝工具自己传入的 `-hls-directive-location`，不能作为可用后备。auto-rewind 首次使用空格布尔语法时报选项错误，随后用 `=false` 正确重跑，仍复现原崩溃。

完整候选使用原 `test_scene_rebase565.cpp`，64×32、123 次调用，包含静止人员、白衬衫、不可信观察、参考重建、状态尾部保护和非法参数。**C 仿真、HLS 综合、123 次 Verilog 联仿和 IP 导出全部通过**，2026-10-27 14:32:07 结束，进程退出码 0。HLS 估算 LUT 34,952、FF 24,305、DSP 211、BRAM18K 99、URAM 35；估计周期 3.650 ns，目标 5 ns、uncertainty 1.35 ns。块状态读取循环目标 II=1、实际 II=2，并非所有像素循环均为 II=2。不能据此给出 1080p 帧率或布线后时序结论。

联仿报告 `rh1/s/sim/report/whiteboard_restore_cosim.rpt`：Verilog Pass，最小／平均／最大调用延迟 4／10,857／11,278 周期；最小值包含非法参数快速返回，不能把它作为帧处理时间。该小尺寸、混合场景回归不是全部实景和分辨率的覆盖证明。导出核位于 `rh1/s/impl/ip/`。

完整接口深度会让 64×32 测试仍生成较大的内存向量，RTL 联仿启动阶段耗时较长。已观察到输入加载完成后事务计数持续推进，因此没有将初始化等待误判为死锁，也没有减少测试序列或缩小生产接口深度。

## 量化核的时序候选

综合关键路径中出现 2～5 位投票计数的多级 DSP 加法链。`scene_vote_fabric/` 仅将 `balanced_sum<uint8_t>` 的加法绑定为 fabric，16 位空间求和仍沿用原配置，整数运算规则不变。候选源、原文件哈希及差异说明已保存。

同一 2025.2 配置下，HLS 估算 DSP 从 834 降至 785，LUT 从 71,037 增至 72,199，FF 从 48,761 增至 48,897；这是资源取舍，不是整机实测节省。C 仿真通过，**9 次 Verilog 联仿及 IP 导出已于 14:40:32 通过，重跑进程退出码 0**。另一条观察／标签选择路径仍估计 4.510 ns，超过扣除 1.35 ns uncertainty 后的 3.650 ns 有效预算。

首次量化联仿的 xelab 与恢复核 XSim、整机布线同时运行时，系统剩余提交容量降至 0.63 GB；核实进程身份后主动停止量化 xelab，外层退出 1。原日志与报告在 `sf1_interrupted/`，这是资源压力下未完成的运行，不是功能不一致。等待恢复核退出后，使用相同 RTL 和原测试串行重跑通过，没有减少测试或改变接口深度。

<span style="color:#C00000">【尚未通过时序验证】投票加法候选不能仅凭 DSP 减少视为成功；RTL 联仿和接口已核查，整机综合及布线后的真实关键路径另行验证。</span>

## CDC 核查

顶层两条 CDC-11 在修正时钟后仍然存在，均位于 MIPI RX 厂商加密核内部，不能直接归因于自定义 RTL。先检查独立 MIPI 外层 DCP，但它含未展开子核且没有时钟，`All paths are Safely Timed` **不构成通过证据**。

接着检查无黑盒的 `bd_d10d_rx_0.dcp` 叶核。第一版独立诊断试图模拟共同主时钟，因独立 IP 没有 Clock Wizard 的物理路径产生 generated-clock 警告；保留但不用于签核。第二版在 IP 边界定义实际频率的主时钟，主系统内的派生关系由 `cr2`／实现报告单独检查。此试验只用于判断厂商内部拓扑，不能替代顶层 CDC 或自行豁免。

已查阅 AMD [UG906 CDC 规则](https://docs.amd.com/r/2023.1-English/ug906-vivado-design-analysis/CDC-Rules-Precedence)和[异步复位同步器说明](https://docs.amd.com/r/2023.2-English/ug906-vivado-design-analysis/Asynchronous-Reset-Synchronizer)：CDC-11 不能仅因属于厂商 IP 就视为安全，须证明扇出接收逻辑的复位／使能协议满足条件。当前未新增 CDC waiver、false path 或异步时钟组。

**实现后的更新：**`cdc_post_impl_20261027.tcl` 分别打开优化后和布线后检查点，使用 `-all_checks_per_endpoint` 再次检查，均为 Critical 0、CDC-6 Warning 2、CDC-15 Warning 68。两条 CDC-11 在 `opt_design` 后不再报告，排除了仅被默认报告优先级隐藏的可能；本轮没有新增豁免。但这不证明所有剩余结构均安全。方法学报告仍有 TIMING-9、5 条 TIMING-24（MIPI 时钟组覆盖 datapath-only 最大延迟）、4 条 LUTAR-1 等，须逐项审阅。复核进程退出码 0，证据在 `cdc_impl_review/`。

**进一步处理例外覆盖：**15:14 完成 `mipi_exception_review3/`，对第一候选只移除一条宽泛 MIPI 异步时钟组，保留其余约束、XPM datapath-only 最大延迟和 bus-skew。以物理源、主时钟源、周期、波形及抖动签名验证时钟不变；新增 22 个受检建立时间端点，两个方向最差裕量为 +7.729 ns／+4.487 ns，总线偏斜最小裕量 +4.084 ns。5 条 TIMING-24 和对应 TIMING-28 消失，整机负 WNS 和 70 条 CDC Warning 不变。这一更严格的操作通过 `tighten_mipi_exception.tcl` 接入第二候选实现，不修改厂商或原 v24 源码。完整限制和剩余问题见 [CDC 审查记录](../../../../../../attachments/history/cdc_review_packet_20261027_11a2fcaf.md)。

## 布局布线

`implement_candidate_20261027.tcl` 从 `cr2/corrected_synth.dcp` 开始，在 `impl1` 保存优化、布局、物理优化和布线检查点及报告。使用原工程的 ExploreArea／AltSpreadLogic_high／AggressiveExplore 指令组合，保持原 200 MHz。此分支仍使用原 Scene/Restore RTL，新版 Rectify 已接入；新的恢复候选不会在测试结束前替换该分支。

第一轮已于 14:25:59 完成全部实现和报告导出，进程退出码 0，保存 `impl1/routed.dcp`。

| 布线后项目 | 结果 |
|---|---|
| 可布线／已完整布线网络 | 165,158／165,158 |
| 布线错误 | 0 |
| WNS／TNS | −1.014 ns／−1014.192 ns |
| 建立时间违例端点 | 4,143 |
| WHS／保持时间违例端点 | +0.010 ns／0 |
| WPWS／脉宽违例端点 | +0.164 ns／0 |
| LUT／FF | 77,895／93,744 |
| CLB／DSP | 14,376（98.20%）／1,145（91.75%） |
| BRAM Tile／URAM | 84／50 |
| 默认 DRC | 无 Error／Critical；仍有 1,718 条 Warning 与 Advisory 检查项 |

最差路径仍在量化核：9 位 DSP 加法输出到 `center_pigment` 判定寄存器，共 13 级逻辑，数据路径 5.869 ns，其中逻辑 2.972 ns、布线 2.897 ns。高 CLB 占用和控制集分散限制布局；窄投票加法优化仍需在整机中验证，不能保证它解决这条新暴露的最差路径。

<span style="color:#C00000">【实现流程完成，时序未通过】布线完成不等于 200 MHz 时序闭合。第一轮结果可以用于定位问题，不能用于宣称整机签核通过。未生成位流、未部署 KV260。</span>

## 全部重建 HLS 的第二个整机候选

`c2` 接入 2025.2 生成的 Rectify、上述恢复核候选和量化投票加法候选。Clock Wizard 配置在源 BD 中改为 `PRIM_SOURCE=No_buffer`，其生成的顶层 XDC 已将重复 `create_clock` 注释，独立 OOC 的输入时钟仍正常保留。`clock_source_jitter.xdc` 把原 0.100 ns 输入抖动预算放在真实 `clk_pl_0` 上，实施前同样显式读取；不是降低时钟或抖动要求。

第二候选的接口网、信号网、外部信号端口和地址分配与原 BD 无差异；26 项 HWH 内存范围一致。三颗核仍共 70 个寄存器，但描述并非完全一致：共同有中断／诊断字段变化，量化核 `control` 更名为 `control_r`，其地址、大小和访问属性未变。证据为 `candidate2_bd_diff.json`、`candidate2_hwh_diff.json`、`candidate2_hls_contract_diff.json`。

已在隔离的 `ps_candidate/scene_registers.py` 增加名称映射。真实旧／新 IP 包、第二候选 HWH 和重复别名拒绝用例均通过 Windows 与 WSL2 验证；原 PS 包不替换，板端 MMIO／DMA 仍未测试。

从第一候选复制了 33 项未修改厂商 IP 的 2025.2 缓存，排除全部自定义 HLS 和 Clock Wizard 缓存，由 Vivado 自行按配置匹配，未强行复用不匹配 DCP。缓存副本为 `vendor_cache2`，原缓存保留，来源与哈希见 `vendor_cache2_manifest.json`。[AMD 的缓存命令说明](https://docs.amd.com/r/2024.2-English/ug835-vivado-tcl-commands/config_ip_cache)说明版本匹配和配置匹配要求，本地实际使用 2025.2 执行。

首次整机综合进程退出 1：只有 `rectify_mem` 在加载 Tcl 应用、创建子工程时失败，未进入 RTL 综合；失败原文为 `Could not open 'C' for writing` / `tclapp::load_apps`。其余子综合均完成。`c2/startup_failure_archive/` 保留原失败目录。

准备串行重试时，补入真实 PS 主时钟的 0.100 ns jitter XDC 后，Vivado 要求先重置尚未执行的顶层综合；首次恢复脚本因此在启动前退出 1，日志保留。`candidate2_resume_top_reset.tcl` 只重置隔离工程的未完成顶层运行，再串行启动。`rectify_mem` 已于 15:25:26 成功结束，整机顶层综合继续。初次 `candidate2_system.tcl` 启动时尚未包含这个独立 jitter XDC；应以恢复后的工程与实现输入为准，不能把后来保存的脚本文字当成初次执行内容。

第二候选整机综合和报告导出已于 15:29:58 完成，恢复进程退出 0，保存 `c2/reports/synthesized.dcp`。顶层综合 0 Error、0 Critical Warning、224 Warning。实际综合资源 LUT 80,437、FF 93,897、DSP 1,098、BRAM Tile 81.5、URAM 50；这些是 Vivado 综合结果，不能与 HLS 估算混写。

<span style="color:#C00000">【综合通过，时序未通过】第二候选综合估算 WNS −2.321 ns。该值尚未布线，不与第一候选布线后 −1.014 ns 直接比较优劣。最差综合路径为量化核 `label_14` → `count_355`，16 级逻辑，仍含 4 级 DSP 运算；投票树的小范围修改没有覆盖所有计数路径。</span>

第二候选完整实现已于 15:30 启动，输出 `impl2/`。严格 MIPI 约束操作及物理时钟签名检查于 15:32:08 通过后，开始逻辑优化。此轮未修改 200 MHz 时钟、抖动预算、原整数算法或板端文件；未生成位流。

综合关键路径已对应到 `scene_vote_fabric/board_scene_quantize.cpp` 第 331～359 行的颜色一致性计数。生成 RTL 的 `count_355_reg` 被用于第 355／356 行判断，路径中可见 3／4 位 DSP 加法与条件选择串联。后续若布线仍以此为瓶颈，应优先把每条射线的连续有效性与六个邻点计数分开，再评估小位宽加法树／fabric 绑定；必须保留遇到空标签中断、两侧跨度、颜色冲突和阈值语义，并重新联仿与整机实现。此建议尚未改入第二候选，不能记为已完成优化。

## 第二轮布线终态与第三轮候选

第二轮 `impl2` 已于 16:01:53 完成完整实现和报告导出，进程退出 0。158,438 条可布线网络全部布通，布线错误 0。WNS −1.411 ns、TNS −1201.115 ns、2,961 个建立时间违例端点；WHS +0.008 ns、WPWS +0.164 ns，保持／脉宽违例端点均为 0。

实际布线资源为 LUT 73,514（62.77%）、FF 89,926、CLB 14,192（96.94%）、DSP 1,098（87.98%）、BRAM Tile 81.5、URAM 50；控制集 4,040（13.80%）。资源比第一轮减少，但 WNS 从 −1.014 ns 变为 −1.411 ns，**不能称时序改善**。两轮使用不同 HLS 核实现，亦不能视为单变量对照。

最差路径 `count_29_reg_68130[0]` → `count_117_reg_68526[1]` 含 16 级逻辑与 4 级 DSP ALU，数据延迟 6.547 ns（逻辑 4.665 ns／71.249%，布线 1.882 ns）。完整关键路径见 `impl2/setup30.rpt`。

严格 MIPI 约束已实际用于本轮实现。全部检查项 CDC Critical 为 0，保留 CDC-6 Warning 2 条与 CDC-15 Warning 68 条；TIMING-24／TIMING-28 不再出现。方法学仍有 LUTAR-1 4 条、TIMING-9 1 条、TIMING-16 216 条、ULMTCS-1 1 条及 2 条时钟位置 Advisory。

<span style="color:#C00000">【第二轮仍未签核】完整布局布线已完成，但 200 MHz 建立时间未闭合，CDC／复位相关 Warning 尚需审查。没有生成新位流或进行 KV260 板测。</span>

针对实际计数链新增隔离候选 `scene_count_tree/`，仅重写六邻点条件累加表达结构，保留原判定语义。531,441 组标签类别穷举及 100,000 组固定种子字节标签测试通过；原 Scene C 测试、HLS 综合及 IP 导出通过。HLS DSP 785→649，LUT 72,199→73,472，FF 48,897→49,154；估计周期仍为 4.510 ns，不能据此认定时序通过。相对 `sf1` 的端口、总线、地址块、寄存器静态对照零差异。

原测试的 9 次 Verilog 联仿于 16:23:58 报告 Pass，`errors=0`；IP 重新导出与进程退出 0 已确认。保持原 160×33 测试，未以低分辨率测试冒充 1080p 验证。随后启动独立 `c3/impl3`，使用原生 2025.2 BD 导出、相同器件／时钟／综合和实现策略，复用由工具匹配的未改 IP 缓存；排除旧 Scene 缓存，69 项缓存副本的来源与文件哈希见 `vendor_cache3_manifest.json`。

16:38:53 新量化核 Vivado OOC 综合完成，0 Error、0 Critical Warning、26 Warning。相对上一量化候选，实际 OOC 资源 DSP 775→641，LUT 17,666→17,599，FF 13,737→13,822，BRAM Tile 1／URAM 6 不变。这些是单核 Vivado 综合数值，与前述 HLS 估算口径不同，不能混写。当时整机尚在运行；最终结果见下节。

官方与社区资料、适用范围、未采用的推论整理在 [时序方案检索记录](timing_research_20261027.md)。保留原 `impl1`、`impl2` 和所有失败试验。

## 第三轮最终报告（17:13:34）

`run_candidate3.ps1` 已结束，进程退出 0；`impl3/stages.tsv` 中 route、reports 均 COMPLETE。158,128 条可布线网络全部布通，布线错误 0。仍保留原 200 MHz／5 ns 目标、真实 PS 派生时钟与 0.100 ns 输入抖动；未放宽时序例外。

| 指标 | 第二轮 impl2 | 第三轮 impl3 |
|---|---:|---:|
| 最终 WNS / ns | −1.411 | −0.219 |
| 最终 TNS / ns | −1201.115 | −84.981 |
| 建立时间违例端点 | 2961 | 624 |
| WHS / ns | +0.008 | +0.010 |
| 保持时间违例端点 | 0 | 0 |
| WPWS / ns | +0.164 | +0.164 |
| LUT / FF | 73514 / 89926 | 73513 / 90422 |
| CLB | 14192（96.94%） | 13833（94.49%） |
| DSP | 1098（87.98%） | 964（77.24%） |
| BRAM Tile / URAM | 81.5 / 50 | 81.5 / 50 |
| 控制集 | 4040（13.80%） | 4113（14.05%） |

WNS 改善 1.192 ns，仍小于零。路由器过程估计 −0.407 ns 不能替代最终 `report_timing_summary` 的 −0.219 ns。控制集数略增但 CLB 减少，说明必须综合评估实际布局，不能只按控制集数量作结论。

**最终最差路径发生转移。** `impl3/setup30.rpt` 首条从恢复核 `local_ink_U0/win_fu_64_reg[3]` 到 `sub_ln95_21_reg_2212_reg`，11 级逻辑，包含 5 级 DSP ALU；数据路径 5.288 ns，逻辑 4.775 ns（90.299%），布线 0.513 ns。源码定位在 `restore_inferred/whiteboard_restore.cpp` 的 7×7 窗口求和及第 98 行附近的局部对比判定。需要检查窗口求和／比较的运算映射与流水切分，并维持整数位宽、边界语义、流对齐和 II；尚未实施该后续优化。

布线前量化核 `balanced_sum<uint16_t,64>` 的 DSP 链曾是最差路径，应作为次级候选继续检查，不能在最终报告出炉后仍将其称为全设计最差路径。仅对最差路径做改动也不保证所有 624 个端点都达标。

第三轮全部检查项 CDC 报告：Critical 0，CDC-6 Warning 2、CDC-15 Warning 68，Info CDC-3 85、CDC-9 3。方法学保留 LUTAR-1 4、TIMING-9 1、ULMTCS-1 1，CLKC-56／58 各 1 条 Advisory；本轮不再出现 TIMING-16。`check_timing` 为 no_clock 0、unconstrained_internal_endpoints 0；4 个输入与 2 个输出缺 delay 的接口项仍需按 MIPI／I2C 的实际约束方式审查。无新增 waiver，不能把 Critical 0 等同完整 CDC 签核。

第三候选 BD/HWH 静态对照、Windows 3.9／WSL 3.10 的 PS 别名适配回归均通过。26 项地址范围一致；Scene control 更名 control_r，偏移保持 0x68。原 PS 不替换；MIPI／帧缓存缺寄存器元数据，仍为 NOT_CHECKED。

<span style="color:#C00000">【尚未达标】建立时间签核需要正确完整约束下的最终 WNS≥0、TNS=0、Setup Failing Endpoints=0。本轮三个条件均未达到；保持与脉宽的数值通过不能抵消建立时间失败。未生成发布 bit／XSA、未上板。</span>

### 论坛启动方案的本机探针

第三轮全部退出后，对原生安装的 Vivado 运行小型 AE OOC 综合，仅在该进程设置 `XILINX_LOCAL_USER_DATA=no`，不设置私有 UTF-8 overlay、不修改全局环境。已完成模块展开，随后异常退出，退出码 −1073740940；没有完成标记、报告或 DCP。日志和状态为 `startup_no_local_data_probe.log`、`startup_no_local_data_result.json`。

<span style="color:#C00000">【本机探针未通过】该变量单独使用未解决此原生 Windows 综合试验；探针并未复现并行 Tcl 启动竞争，因此也不能据此否认其对论坛原问题的作用。两种故障不能混为一个根因。</span>

## 原始证据入口

本次所有编译／验证进程退出后，`remove_task_drive.ps1` 核对 W: 指向本任务目录且活跃工具为0，再仅取消 SUBST 别名。`drive_cleanup.json` 确认 D 盘目录保留。构建记录中的 W: 路径仍作为当时的原始证据保留；再次执行需要先恢复映射或重建到合适短路径。

- `clock_review_20261027.log`：第一次锚点断言停止；`clock_review_buffered_20261027.log`：修正与频率检查通过。
- `hls_probe_local.log`、`hls_probe_luma.log`：崩溃复现；`hls_probe_inferred_luma.log`：移除三条绑定后通过。
- `restore_inferred_20261027.log`、`rh1/s/syn/report/`：完整恢复候选验证。
- `mipi_review/`、`mipi_leaf/`、`mipi_leaf2/`：CDC 诊断范围与模型差异。
- `implement_candidate_20261027.log`、`impl1/stages.tsv`：实现运行进度和终态。

不得打包私有 UTF-8 可执行文件、厂商安装目录或崩溃内存转储到比赛材料中。原始日志保留，公开时另做脱敏副本。
