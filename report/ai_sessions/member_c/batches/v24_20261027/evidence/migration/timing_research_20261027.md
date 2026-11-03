# Vivado 2025.2 迁移：官方与社区方案核查

检索日期：2026-10-27。适用工程：本目录内的隔离迁移候选；原始 v24 不改动。检索覆盖 AMD 技术支持社区、Reddit r/FPGA、Stack Overflow 和公开 GitHub 实验源码。没有向论坛发帖，也没有上传本项目代码或日志。

## 可采用的方向与证据边界

### 1. 条件累加链：先改变表达结构，再检查实际映射

本工程第二轮布线的最差路径是量化核 `count_29` → `count_117`，有 4 级 DSP ALU，数据延迟 6.547 ns，其中逻辑占 71.249%。源文件的六邻点条件递增与全局 `config_op add -impl dsp` 是本次隔离试验的直接依据。

[Stack Overflow 的累加讨论](https://stackoverflow.com/questions/78576396/how-to-implement-pipelined-floating-point-accumulation-in-ii-1-in-vitis-vivado-h)提出并行分支或加法树。该问题是浮点累加，不能把其关于 II 的判断直接套到本工程的整数计数上。

[Fertrin 等作者公开的实验仓库](https://github.com/Viratrin/hls-vs-rtl-fpga-kernels)声明使用 Vivado / Vitis HLS 2025.2，提供 population count 的平衡流水加法树 RTL 与不同展开因子的 HLS 循环。已阅读其 README、RTL、HLS 展开版本与配置，固定检查版本为 `e54befb76f668162937922e28293804628d3d09f`。目标是 Artix-7，所列报告是综合结果与 HLS 估计，不是本工程 K26 的布线验证。只借鉴结构分析方法，没有复制仓库实现到产品。

[AMD expression_balance 文档](https://docs.amd.com/r/en-US/ug1399-vitis-hls/set_directive_expression_balance)说明整数表达式平衡默认启用。因此“再加一个平衡 pragma”不是本问题的充分解决方案；带条件选择、数组更新和前缀有效性的循环需要单独分析。[AMD BIND_OP 文档](https://docs.amd.com/r/en-US/ug1399-vitis-hls/set_directive_bind_op)提供 fabric/DSP 绑定能力，但资源绑定也可能影响组合运算匹配，不能将所有运算统一改成 fabric。

**本地行动：** `scene_count_tree/` 只把每条射线的连续有效性、标签计数拆开，以显式平衡的小位宽 fabric 加法树替换计数链。空标签中断、无效非零标签的连接语义、两侧跨度、冲突判定及阈值保留。没有改 200 MHz 目标、外层 II 或接口。

**截至首次记录：** 531,441 组标签等价类别的穷举及 100,000 组固定种子字节标签测试通过；原 Scene C 测试通过；HLS 综合与导出通过。HLS 估算 DSP 785→649，LUT 72,199→73,472，FF 48,897→49,154。估计周期仍为 4.510 ns，仍超过 5 ns 周期减 1.35 ns uncertainty 的预算。RTL 联仿及新整机结果见后续验证记录。

<span style="color:#C00000">【尚不能判定时序修复】HLS 资源下降和 C 仿真通过不足以证明布线时序、整机帧率或板端功能通过。</span>

### 2. LUT 有余量、CLB 接近满载：控制集优化需要实际对照

[Reddit 原作者的控制集试验](https://www.reddit.com/r/FPGA/comments/1n1vg6x)与本工程现象接近：LUT 约 60%，CLB 接近满载。作者在后续回复中报告，把控制集优化阈值提高到 8／16 后，控制集比例从约 12% 降到 8%／6%，CLB 却从 98.5% 上升至 99.5%。这是一份社区项目自述，器件、设计与约束不同，不是普遍规律；它说明不能只依据控制集数量判断收益。

[AMD 控制集指南](https://docs.amd.com/r/2025.2-English/ug949-vivado-design-methodology/Reduce-the-Number-of-Control-Sets)建议分析低扇出控制集、优化或合并等价控制信号。[控制集使用指南](https://docs.amd.com/r/2025.2-English/ug949-vivado-design-methodology/Follow-Control-Set-Guidelines)提供检查标准。具体阈值和实现阶段需要结合报告使用。

**本地判断：** 第二轮布线 LUT 62.77%，CLB 96.94%，控制集 4,040 个（13.80%）。顶层综合已设置阈值 16，不能把该设置重复描述为新修复。OOC IP 的综合设置与顶层并不自动相同；后续可按 `control_sets.rpt` 的来源定位最严重的核，再进行单独对照。当前最差路径主要是逻辑延迟，优先处理计数链；不盲目全局提高阈值、不删除功能复位。

补充本地定位：`control_set_driver_summary.json` 按使能驱动层级归类、没有使能时按复位驱动归类，共归类 4,040 项。恢复核 981 项、恢复内存互连 548 项、量化核 416 项、校正核 391 项、校正内存互连 362 项。它统计驱动来源，并非严格的消费寄存器归属证明；跨模块控制集可能共用。低扇出及复位语义需要在具体修改前再查。

还需区分名称相近的工具选项：第二／第三轮 2025.2 日志都明确记录 `Opt 31-1555`，`control_set_opt` 仅支持 Versal，当前 xck26 不支持。可读取的 [AMD 2025.1 opt_design 命令说明](https://docs.amd.com/r/2025.1-English/ug835-vivado-tcl-commands/opt_design?contentId=o3Wa3etx9L~ft~cmC674jg)也区分该选项与 `control_set_merge`，与本机 2025.2 的实际提示一致。因此不能把 ExploreArea 的相关提示当成已在 K26 上执行此项优化；后续应分别验证合并等价驱动、同步控制重映射与 OOC 综合阈值。

### 3. DSP 路径需要检查流水寄存器，但延迟与吞吐应分开

[AMD 专用模块路径优化指南](https://docs.amd.com/r/2025.2-English/ug949-vivado-design-methodology/Optimizing-Paths-with-Dedicated-Blocks-and-Macro-Primitives)建议减少 DSP 周围组合逻辑并利用流水寄存器。工具提供 DSP 寄存器优化选项，但启用选项不等于已取得效果。

第三轮 `AggressiveExplore` 物理优化日志已实际执行 DSP register optimization，并记录部分 DSP 输出寄存器被移到 fabric、部分候选无变化。因此“打开 DSP 寄存器优化”不能再当作完全未尝试的方案。

**备选源码行动，尚未执行：** 如果计数树试验后仍由 DSP 链主导，可针对剩余路径检查 HLS 运算 latency 和寄存器位置，必要时显式增加同步流水级，并验证数据／控制延迟对齐与 II。不能简单增加多周期约束，也不能把真实相关性用 `DEPENDENCE false` 隐去。

### 4. HLS 200-1715 是外层错误，未发现本问题的同版本现成补丁

[AMD 社区 2023.1 案例](https://adaptivesupport.amd.com/s/question/0D54U00007Pf3FbSAJ/the-c-synthesis-fails-with-an-uninformative-error-message?language=en_US)与[含 .clang-tidy 的顶层函数识别案例](https://adaptivesupport.amd.com/s/question/0D54U00005ec6FZSAY/vitis-hls-causes-top-function-not-found-there-is-no-function-named-error-with-a-project-containing-clangtidy?language=en_US)都出现同一外层错误，但失败阶段和触发条件不同。检索未找到与本工程 2025.2 Performance 阶段调用栈、资源绑定最小复现完全匹配的公开修复。

**本地已验证：** 保留原整数计算，仅移除恢复核三条乘法 DSP 强制绑定后，最小复现与完整恢复核均能综合；原 C 测试、123 次 Verilog 联仿和 IP 导出通过。该结论属于本工程验证结果，不是 AMD 已确认根因或正式补丁。失败试验保留。

### 5. CDC 不能通过扩大异步时钟组来“消红”

[AMD 时钟组与 CDC 约束说明](https://docs.amd.com/r/2025.2-English/ug949-vivado-design-methodology/Defining-Clock-Groups-and-CDC-Constraints)指出时钟组／false path 的优先级会覆盖 `set_max_delay -datapath_only`。本工程已对一个 MIPI 宽范围异步时钟组做隔离诊断，在保留实际 XPM 延迟与总线偏斜约束后，第二轮采用了更严格的版本。

**本地结果：** `impl2` 布线后全部检查项 CDC Critical 为 0，仍有 70 项 Warning；TIMING-24／TIMING-28 不再出现。未加入 CDC waiver。警告、复位结构和接口时序的剩余审查见 `cdc_review_packet_20261027.md`。

### 6. Windows 路径与临时 W:：可以换构建目录，不必保留盘符

[AMD 2025.2 命名规范](https://docs.amd.com/r/2025.2-English/ug973-vivado-release-notes-install-license/Vivado-Naming-Conventions)限定工程目录字符，并明确提示 Windows 长路径可能影响工具。[新建工程说明](https://docs.amd.com/r/2025.2-English/ug895-vivado-system-level-design-entry/Creating-a-Project)也要求尽量使用短名称与短路径。因此，可将未来独立构建输出放在纯英文短路径（例如 `D:/fpga_work`）；不需要改中文资料目录，也不需要创建新磁盘分区。

本次 W: 是现有隔离工作区的临时 SUBST 别名，源码与输出仍在 D:。它解决了已复现的 HLS 路径问题，但不是所有 Windows 子进程问题的保证修复。另有本机进程级 UTF-8 manifest 试验和一次串行重试；它们有本地成功日志，不是已核实的 AMD 官方补丁。正在执行的工程仍引用 W:，必须等工具全部退出后再取消映射，不能中途删除别名。移除脚本会核对映射目标并保留实际文件。

### 7. `Could not open 'C' for writing`：多实例本地用户数据的候选解决办法

[Electronix 社区的原始复现与后续反馈](https://electronix.ru/forum/topic/219226-vivado-abnormal-program-termination-exception_access_violation/page/2/)列出了与本机相同的 Common 17-1257／17-354 报错：多个 OOC 综合同时启动容易出错，串行启动可绕过；后续用户反馈 `XILINX_LOCAL_USER_DATA=no` 后恢复。该页面同时讨论其他崩溃，不能将全部回复都视为同一个故障。

交叉检查发现，[Xilinx 官方 GitHub 仓库的启动脚本](https://github.com/Xilinx/finn/blob/main/run-docker.sh)也传递 `XILINX_LOCAL_USER_DATA=no`，注释说明用于多个 Vivado 实例并行运行，并引用 [AR 63253](https://adaptivesupport.amd.com/s/article/63253?language=en_US)。本次 AR 页面只返回加载／CSS 错误，未读取其正文，不声称已确认其完整适用版本。GitHub 证据来自原仓库，不采用第三方镜像转载。

**待本机验证的用法：** 仅在启动 Vivado 的那个 PowerShell 进程中设置 `$env:XILINX_LOCAL_USER_DATA='no'`，让子工具继承；不要通过 `setx` 修改全局环境。本轮第三候选启动后才找到这条线索，因此没有改动正在执行的环境，第三轮结果也不能归功于该变量。本机之前已验证串行重试能完成，但尚未证明此变量能消除本机的偶发并行启动故障。

中文路径、HLS 编译器崩溃、子进程启动竞争和负 WNS 分别记录、分别验证。

## 本机最终验证补充

所有工具退出后，临时 W: 别名已取消，实际 D 盘文件保留，证据见 `drive_cleanup.json`。此前“正在执行”的描述是当时状态；再次使用保存的 W: 构建工程需先恢复映射或重新生成。

第三轮原 Scene 9 次 RTL 联仿通过，完整布局布线完成：WNS −0.219 ns、TNS −84.981 ns、624 个建立时间违例端点；第二轮为 −1.411 ns。DSP 1098→964、CLB 96.94%→94.49%，控制集 4040→4113。平衡计数树在本工程得到实测改善，仍未完成 200 MHz 时序闭合。最终最差路径转移至恢复核 local_ink 的 DSP 运算链，不能继续按布线前路径排序决定唯一优化对象。

原生 Vivado 加进程级 `XILINX_LOCAL_USER_DATA=no` 的单 AE 综合探针异常退出（−1073740940），没有产出 DCP。此试验未复现并行启动竞争，只表明该变量单独不足以使本机原生综合探针完成。已保留日志；没有全局设置环境变量、删除用户配置或安装论坛建议的其他补丁。

建立时间达标按 [AMD UG906 时序指标定义](https://docs.amd.com/r/2025.2-English/ug906-vivado-design-analysis/Table-Columns?contentId=mgMCEv4QzOpcGzY9491CYQ)：最终 WNS≥0、TNS=0、失败端点0，并确保约束覆盖正确。200 MHz 的周期是5 ns，但实际可用预算还涉及建立时间、时钟偏斜和不确定度，不能直接以组合延迟小于5 ns代替签核。

<span style="color:#C00000">【仍未通过】负 WNS、CDC／复位事项与未板测事实保留。资料检索和工具成功退出都不能替代验证。</span>

## 后续证据入口

- [完整阶段记录](phase2_notes_20261027.md)：实际 CSim、CoSim、综合和实现结果。
- [机器可读审计](phase2_validation.json)：报告数值、状态、文件哈希；以审计时间为准。
- `scene_count_tree/tally_test.log`：计数逻辑对照测试。
- `scene_count_tree_contract_diff.json`：前后 IP 静态接口对照。
- `scene_count_tree_cosim_20261027.log`：原测试 RTL 联仿日志。

所有未闭合、未上板、未覆盖的事项都继续保留。论坛建议只是试验依据，最终结论必须来自本工程相同目标与约束下的实际报告。
