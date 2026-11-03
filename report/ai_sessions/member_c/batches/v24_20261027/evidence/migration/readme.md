# V24 → Vivado / Vitis 2025.2 验证记录

日期：2026-10-27（Asia/Taipei）。本目录是隔离的迁移验证工作区，**不是新的上板发布包**。原 `最终素材` 三个目录未改动。本阶段不接入神经网络和手势控制。

## 最新进展：第二阶段

第三轮完整布局布线与报告于 2026-10-27 17:13:34 完成，Vivado 退出 0。158,128 条可布线网络全部布通，布线错误 0。**最终 WNS −0.219 ns、TNS −84.981 ns、624 个建立时间违例端点，200 MHz 尚未达标。** WHS +0.010 ns、WPWS +0.164 ns，保持／脉宽违例为 0。详见 [完整验证记录](phase2_notes_20261027.md) 和 [机器可读审计](phase2_validation.json)。

量化计数树候选通过原 C 测试、9 次 Verilog 联仿及静态接口对照，整机 WNS 较第二轮 −1.411 ns 改善；DSP 1,098→964，CLB 96.94%→94.49%。最新最差路径在恢复核 local_ink 的连续 DSP 运算，不再是第二轮的量化计数链。恢复核的编译崩溃已通过最小资源绑定调整绕过，123 次原 Verilog 联仿通过，但这不等于其整机时序通过。

第三轮全部检查项 CDC Critical 为 0，仍有 70 条 Warning；复位／约束审查未全部结束。26 个 HWH 地址范围保持，Scene control_r 别名适配通过 Windows／WSL 静态回归；没有板端 MMIO／DMA 验证。

<span style="color:#C00000">【整机签核未通过】三轮实现与失败证据均保留。没有生成发布位流／XSA，没有替换原 PS 或进行 KV260 板测。</span>

[官方与论坛方案核查](timing_research_20261027.md)已更新本地试验。仅设置 XILINX_LOCAL_USER_DATA=no 的原生 AE 综合探针仍异常退出，不能将该论坛方案称为本机已修复。完整构建成功所用的私有进程级 UTF-8 试验不是 AMD 官方补丁，不随项目发布。

以下内容保留为第一阶段历史记录；其中“未运行／恢复核崩溃”是当时的状态，最新进展以上述第二阶段记录为准。

本次工具进程全部退出后，已核对目标并取消临时 W: 映射，D 盘源码与全部结果保留，见 `drive_cleanup.json`。部分保存的构建工程／日志仍引用 W:；再次重建前需恢复相同映射，或在新的纯英文短路径副本中重新生成，不能把取消别名误认为工程删除。

## 第一阶段结论（保留历史）

已完成 2021.2 原生 BD 重建、2025.2 正式 IP 升级、BD 验证与输出生成。量化核和恢复核的现有 C 仿真已在 Vitis 2025.2 实际通过；量化核完成综合和 9 次 Verilog C/RTL 联仿，结果 PASS。校正核通过 20 组 1920×1080 C 测试，完成 HLS 综合和候选 IP 导出。**采用新版校正 IP 的独立候选整机已通过 Vivado 2025.2 综合**，`synth_1` 为 Complete、100%；顶层综合 0 errors、0 critical warnings。

<span style="color:#C00000">【尚未完成】候选整机综合通过，但实现、时序闭合和新位流板测尚未完成。恢复核从 C++ 重新综合仍发生工具崩溃；本次整机使用原恢复／量化 RTL。不能写“整体架构已完成 2025.2 全部验证”或“新版可直接上板”。</span>

主要构建已结束：第二条候选综合、报告导出和 DCP 保存均完成，进程退出码 0。详细终态及日志哈希见 `validation_summary.json`；未生成发布位流。

| 验证层级 | 当前状态 | 证据 |
|---|---|---|
| 2025.2 环境、K26 器件与 KV260 板卡文件 | PASS | `preflight/environment.txt`、`preflight/ip_catalog.tsv` |
| 原 PL 输入快照 | 582 文件，65,067,762 byte，逐文件哈希保存 | `baseline_manifest.json` |
| 2021.2 原生 BD 重建与 validate | PASS，带警告 | `export_2021.log`、`legacy_bd/`、`ip_status_2021_2.rpt` |
| 2025.2 IP 升级、validate、生成输出及 wrapper | PASS，仍有待审阅警告 | `upgrade_with_xci.log`、`upgrade_with_xci/reports/` |
| BD 外部端口／信号连线／地址分配对比 | 信号端口、信号网和接口网、地址分配无差异；新增接口 port_maps 描述 | `bd_structural_diff.json` |
| 原包 HWH 与候选 HWH | 三颗自定义核 70 寄存器描述、26 内存范围相同 | `hwh_contract_diff.json` |
| MIPI／帧缓存寄存器兼容 | NOT_CHECKED：HWH 未提供寄存器列表 | 同上；0 对 0 不是通过证据 |
| 2025.2 scene CSim | PASS，errors=0 | `hls_scene_csim_ascii.log` |
| 2025.2 restore CSim | PASS，SCENE_REBASE565、errors=0 | `hls_restore_csim_ascii.log` |
| 2025.2 scene 综合／Verilog CoSim | PASS，退出码 0；160×33 测试、9 次事务 | `hls_scene_cosim_ascii.log`、`hls_runs/scene_cosim_ascii/solution1/sim/report/board_scene_quantize_cosim.rpt` |
| 2025.2 restore 综合／CoSim | FAIL：综合中编译器崩溃；CoSim 未进入 | `hls_restore_cosim_ascii.log` 和 `.autopilot/db/a.g.ld.0.bc.clang.reflow.err.log` |
| 整机使用原 HLS RTL 的 2025.2 综合 | FAIL，退出码 1 | `synth_2025_2.log`、`upgrade_with_xci/project/*.runs/` |
| AE 模块 Windows 路径诊断 | PASS，退出码 0；只证明该 OOC 综合 | `rtl_probe_utf8.log`、`rtl_probe_utf8/probe.dcp` |
| rectify 源码重新综合候选 | CSim 20 组 1080p PASS＋HLS 综合／导出成功，退出码 0 | `hls_rectify_export.log`、`rectify_test/manifest.json` |
| rectify 新旧 IP 描述对照 | 15 寄存器的地址、大小、访问属性一致；诊断／中断字段有差异，不能视为完整等价 | `rectify_ip_contract_diff.json` |
| restore 单变量诊断 | FAIL，短路径 CSim 通过后仍发生同阶段编译器崩溃 | `hls_restore_inline_ascii_cwd.log`、`ri/solution1/.autopilot/db/` |
| 短路径＋新版 rectify 的整机候选 | PASS，退出码 0；综合 Complete、100%，44 个执行任务结束且无失败标记 | `candidate_system.log`、`c/reports/run_status.tsv`、`c/reports/synthesized.dcp` |
| 综合后资源、时序估算、DRC/CDC 报告 | 已生成；时序与 CDC 仍有待处理项，见下节 | `c/reports/` |
| 布局布线、DRC/CDC 签核、时序闭合 | NOT_RUN；未取得新的布线后 WNS | 综合后报告不能替代实现签核 |
| 新 bit/HWH/DTBO 配对和 KV260 实测 | NOT_RUN | 未部署或访问 KV260 |

## 输入、平台和迁移策略

- 原件：`D:/2026嵌赛/最终素材/submission_v24/submission_v24`；只复制 `src/pl`、测试平台及必要构建/XDC 文件到 `baseline/`。
- Vivado：本机 `D:/Xillinx/2025.2/Vivado/bin/vivado.bat`，Build 6299465；Vitis/HLS：`D:/Xillinx/2025.2/Vitis/bin/vitis-run.bat`，Build 6295257。
- 目标器件：`xck26-sfvc784-2LV-c`。保持原 200 MHz 处理目标和其他时钟域，不通过降低频率、删除约束或放宽误差伪造通过。
- 原 2021.2 工程的 BD Tcl 会拒绝 2025.2。采用“原版生成原生 BD＋XCI → 新版升级副本”的路径，未直接改掉版本检查冒充迁移。
- 既有 FPGA 服务器只读检查发现 Vivado 2021.2/2024.2，未发现 2025.2；在独立 `v24_migration_20261027_01` 目录运行了 2021.2 BD 导出，没有修改服务器原工程。
- 主线整机验证保留原生成 HLS RTL/IP，独立 HLS 测试检查 C++ 在 2025.2 的再生成能力。二者不能互相代替。新 HLS 候选未经行为、接口和整机验证，不自动替换主线 IP。

按照 AMD 的 [UG994 升级说明](https://docs.amd.com/r/2025.2-English/ug994-vivado-ip-subsystems/Upgrading-a-Block-Design-in-Project-Mode)在独立副本审阅 IP 状态、升级和检查警告。HLS 使用 [UG1399 的 vitis-run Tcl 入口](https://docs.amd.com/r/2025.2-English/ug1399-vitis-hls/vitis-v-and-vitis-run-Commands)。本轮沿用可执行的传统 `open_project/open_solution` 批处理结构；工具提示其不是新 IDE Component 工作区，这不影响已执行的批处理结果。

## 已发现的问题与处理轨迹

1. **首次默认沙箱初始化失败。** `preflight.log` 在创建项目时报 Tcl appinit 缺失；同脚本在获准访问工具目录后通过（`preflight_escalated.log`）。未重装工具或改全局 Tcl 配置。
2. **HLS 中文路径失败。** 原路径在 `open_solution` 创建日志时报错；临时映射为 `W:` 后同配置 CSim 通过。W: 指向本目录，不是另一份源码。
3. **只有 BD 文件不足以升级。** 首次缺配套 XCI，旧版本 IP 无法恢复；补齐原版完整 BD 树后升级成功。保留 `upgrade.log` 失败记录和 `upgrade_with_xci.log` 成功记录。
4. **实际 IP 升级。** MIPI CSI-2 Rx 5.1→6.0、Video Frame Buffer Write 2.3→3.0、Zynq UltraScale+ PS 3.3→3.5；其他 IP 也有 revision 更新。保留前后状态报告，不能只核对顶层文件名。
5. **HWH 范围。** 自定义 Rectify/Scene/Restore 分别 15/20/35 个寄存器描述一致；不是所有外设行为和 Linux 驱动已验证。MIPI 和帧缓存寄存器需按 IP 文档／驱动单独核对。
6. **旧浮点 IP 不兼容。** 原 Rectify 包内部例化 `floating_point_v7_1_13`，2025.2 综合找不到该模块。已从与当前源码哈希相同的完整冻结包取配套测试，原样通过 20 组 1080p C 测试并生成候选 IP；不直接把旧模块名替换成新版本号。
7. **恢复核编译器崩溃。** `.autopilot` 日志定位到 `clang-3.9-csynth` 前端异常，外层为 HLS 200-1715。最后提示涉及 `channel` 的 recurrent-II 估算，但这还不是根因证明。独立试验仅添加 `set_directive_inline channel`；首次因路径导致 CSim 生成列表缺源码，改用统一 ASCII 工作目录后 CSim 通过，综合仍在 Performance 阶段以相同调用栈崩溃。假设未解决问题，不采用该指令，不修改原算法或削弱测试。两次失败记录保留，不上传内存转储。
8. **Windows 子任务问题。** 部分原生综合子任务报目录创建失败或停在 RTL 展开后。复用本机 FPGA-Automatic 的私有 UTF-8 进程 manifest 排查方法，只修改任务副本的 manifest，原安装二进制与代码段哈希保持不变。AE OOC 综合已通过；`private_utf8/manifest-change.json` 保存变更和哈希。本方法不是 AMD 官方补丁。采用此环境的候选整机综合已通过，跨机器可复现性仍需另行验证。

## 两条迁移分支不要混用

`upgrade_with_xci/` 是保留原三颗 HLS RTL 的正式升级副本；前述“70 个寄存器描述、26 个内存范围一致”仅指这条分支的 HWH。其整机综合已失败。

`c/` 是第二个独立候选：由已升级导出的 2025.2 BD Tcl 重新生成短路径工程，Rectify 改用 2025.2 重建 IP，Scene/Restore 仍用原 RTL。生成和综合使用进程级 UTF-8 副本；未修改原 PL C++／RTL、时钟或约束。它不是原包重新命名，也不能直接使用第一条分支的 HWH 检查结论。

第二条分支已单独导出 `candidate_bd_diff.json` 与 `candidate_hwh_diff.json`：信号端口、信号／接口连线、地址分配仍无差异；26 个内存范围一致，Scene/Restore 的 55 个寄存器描述一致，Rectify 的字段差异如下一段。两个厂商视频 IP 仍没有可比较寄存器列表。

新 Rectify IP 的 155 个保留端口方向／宽度一致；旧 `ap_local_block` 诊断输出不再导出，原 BD 未连接该端口。总线描述的 gmem0/gmem1 从 READ_WRITE 分别细化为 READ_ONLY/WRITE_ONLY，物理映射保持一致。CTRL 新增 INTERRUPT bit 9 描述，IP_IER／IP_ISR 不再含旧 bit 5 诊断通道；15 个寄存器地址、大小、访问属性一致。现有 `drivers/rectify_rgb.py` 轮询 CTRL 的 done/idle 并写原参数地址，但**这不是整机软件兼容或数值 RTL 等价性证明**。尚未进行 Rectify C/RTL 联仿和新位流板测。

HLS 的时序／资源均为综合估算：Scene 估计周期 4.510 ns，目标 5 ns、uncertainty 1.35 ns；不能将 4.510＜5 直接当作时序达标。Rectify 估计周期 3.650 ns，同样不能替代布线后时序。Scene 联仿只有上述测试大小，不外推到 1080p 实景覆盖或板端帧率。

## 候选综合报告必须保留的结论

完成时间：2026-10-27 12:09:42（本机时间）。`c/reports/run_status.tsv` 中 synth_1 Complete/100%，impl_1 Not started/0%。顶层综合自身为 0 errors、0 critical warnings、215 warnings；整个候选构建与报告导出进程返回 0。子任务有 3 份日志出现启动阶段 `Could not open 'C' for writing` 等 ERROR 行，但随后完成并保存 DCP；保留在 `validation_summary.json`，不称整个日志零错误，也不删除证据。

| 项目 | 综合后结果 | 解释 |
|---|---|---|
| LUT / FF | 84,913 / 99,503 | 72.50% / 42.48%；不是布线后资源 |
| BRAM tile / URAM / DSP | 84 / 50 / 1,145 | 58.33% / 78.13% / 91.75%；不由 LUT 余量推断布局容易 |
| Setup 估算 | WNS −1.736 ns，TNS −93.588 ns，150 失败端点 | <span style="color:#C00000">【未达标】原始综合后约束报告，不可与旧版布线后 WNS −1.588 ns直接计算改进或退化</span> |
| Hold / 脉宽估算 | WHS −0.410 ns，WPWS −0.712 ns | 尚未布局布线，不据此断言实机必然失效；也不能宣布时序通过 |
| 默认 DRC | 1,707 Warning＋122 Advisory，无 Error/Critical 条目 | 多为 DSP 输入／输出流水建议；仍需实现后检查 |
| CDC | video→处理时钟一组标 Critical，115 端点中 2 Unsafe | <span style="color:#C00000">【待处理】必须定位并审阅同步方式、例外约束和采样意图，不能批量加 false path 消除提示</span> |
| 约束完整性 | no_clock 8、no_input_delay 4、no_output_delay 2；内部最大延迟未约束端点 0 | <span style="color:#C00000">【待审阅】涉及 PS EMIO、I²C 与 MIPI 输入；需按实际接口解释，不能只引用内部端点 0 称约束完整</span> |

本轮未执行 `place_design`、`route_design`，未导出 bit/XSA 或发布包。下一步应先完成时钟／CDC 审阅，再跑实现并复核总线偏斜和资源；现有硬件留作原版本使用。

已只读重开综合 DCP 做补充检查（`inspect_synthesis.log`，退出码 0）：

- `c/detail/cdc_details.rpt` 将两条 Critical 定位为 **CDC-11（源触发器向目的时钟域扇出）**，位于 MIPI RX 厂商加密 IP 内部，内部名称显示 `<hidden>`，已有 False Path 例外。不能直接断言自定义 RTL 同步错误，也不能自行豁免；需核对该 IP 版本说明／厂商意见和实际采集测试。
- `c/detail/setup10.rpt` 的最差 setup 路径位于旧 Scene RTL 的 `scan_Pipeline_VITIS_LOOP_545_5`，经过 DSP 加法逻辑；估计 13 级逻辑、数据路径 6.153 ns。后续应按真实布线结果决定是否优化统计加法流水，不借改 UI 或提高 PS 线程数处理 PL 时序。
- `c/detail/clocks.rpt` 同时保留 PS `clk_pl_0` 与 Clock Wizard 输入的 10 ns 主时钟，处理／video／phy 三路配置均为 5 ns；旧脚本的重复主时钟问题仍需审查，不能擅自降频。
- `c/detail/bus_skew.rpt` 已保存综合阶段偏斜估算，必须在实现后复查；这不构成布线后偏斜通过证明。

<span style="color:#C00000">【仍需审阅】AE 旁路观察模块把输入 TREADY 与其他流信号一起命名，Vivado 自动推断为标准 AXIS 时报告端口方向警告；恢复核部分 AXI LOCK 宽度以及时钟／复位关联也有警告。保留原连接，不静默修改为驱动总线的端口；后续分别确认意图和综合结果。</span>

PS 与视频子系统的参数差异也保留在结构 JSON：2025.2 增加 SD1 若干 ITAP/OTAP 时序参数、MIO 输入类型和保护段描述，MIPI 新增 TDEST 宽度描述，帧缓存新增 64-bit AXI 宽度参数。部分差异来自新版显式记录旧默认值，部分需按 IP 迁移文档确认；没有把“地址相同”当作启动、设备树或驱动兼容证明。当前不改板端 FSBL、Linux 或 PYNQ。

## 可复现入口与保留规则

核心脚本：`prepare_workspace.py`、`export_2021_bd.tcl`、`preflight.tcl`、`upgrade_2025_2.tcl`、`synth_2025_2.tcl`、`hls_2025_2.tcl`、`rectify_2025_2.tcl`、`candidate_system.tcl` 及三个 `compare_*.py`。构建脚本遇到既有结果会停止，避免覆盖失败证据；只读比较脚本可重写自身 JSON 报告。重跑构建应使用新目录副本，不能直接删除本目录的旧结果。

已取得 `legacy_bd/`，后续新机器可使用该原生输入，不必每次访问原服务器。归档正式发布前需将路径配置改为参数或包内相对路径，并核对许可证和来源。

本机执行时为规避非 ASCII 路径，临时使用：

```powershell
# 仅在 W: 尚未使用时执行；使用结束且所有任务退出后再解除。
subst W: 'D:\2026嵌赛\v24_2025_2'
```

原工具命令示例（已有输出目录时不会覆盖，应先准备新的工作副本）：

```powershell
& 'D:\Xillinx\2025.2\Vivado\bin\vivado.bat' -mode batch -source W:/upgrade_2025_2.tcl
$env:WB_HLS_CORE='scene'   # 或 restore
$env:WB_HLS_MODE='cosim'   # csim/synth/cosim/export
$env:WB_RUN_TAG='new_run'
& 'D:\Xillinx\2025.2\Vitis\bin\vitis-run.bat' --mode hls --tcl W:/hls_2025_2.tcl
```

HLS 需要同时以 `W:\` 为进程工作目录，脚本中的路径也使用 W:；只把脚本参数写成 W:、却从中文 D: 路径启动，可能生成错误的相对源码列表。失败样本保存在 `hls_restore_inline_diagnostic.log`，不是恢复算法的 C 测试失败。

本轮私有 manifest 副本由已安装的 `D:/Codex_Projects/FPGA - Automatic/scripts/prepare_vivado_utf8.py` 生成，并核对原文件／代码段哈希。候选启动前检查没有既有 `XILINX_PATH` 或 `MYVIVADO` 覆盖，然后仅给该进程设置 `XILINX_PATH=W:\private_utf8`，调用原版 `vivado.bat -mode batch -source W:/candidate_system.tcl`。跨机器先核对版本和具体失败证据，不直接套用此 Windows 诊断方法。

私有 UTF-8 副本仅留本机诊断；不要把 `private_utf8/`、`.exe/.dll`、`.dmp` 或工具安装目录打入比赛提交包。原始日志可能含个人路径，公开 AI Sessions 前另做脱敏副本，不改原始记录。

本轮临时 W: 映射已解除，文件保留在 D 盘任务目录。重新打开 `W:/c/p/v24.xpr` 前，请先在启动 Vivado 的同一终端按上面命令恢复映射；不同权限的进程可能看不到同一映射。所有本轮启动的编译／检查进程均已结束，没有后台验证或自动部署任务。

## 下一步通过标准

1. 候选已解决 Rectify 旧浮点依赖；继续补齐 RTL 协同仿真，并确认新 IP 的数值、时序协议、寄存器和资源变化；不混用候选 HWH 与旧 bit。
2. 定位 restore HLS 编译器异常；必要时用有授权的 Linux 2025.2 环境进行对照。本服务器现有 2024.2 结果不能充当 2025.2 结果。
3. 候选整机综合已通过；接续完成时钟／CDC 审阅、实现、全时钟 setup/hold、未约束路径与 DRC 核查。原 V24 的 WNS −1.588 ns 不会因工具升级自动消失。
4. 绑定同次构建的 bit/HWH/XSA、设备树和驱动；复核采集、三模式、内容保持、保存/回看、AE、输入及长时间运行。
5. 只有相应阶段实际通过后，才更新 Word 报告、视频技术字幕、PYNQ 版本矩阵和 AI Sessions 结果。

原 `rebuild_vivado.tcl` 还包含实现策略（ExploreArea、AltSpreadLogic_high、AggressiveExplore）及布局布线后的重复 Clock Wizard 主时钟修正。2025.2 后续应先检查实际生成时钟与原始时序报告，再判断是否仍存在同一重复约束；不能盲目删除时钟或开启 `WB_ALLOW_NEGATIVE_TIMING` 来宣称迁移通过。原修正逻辑保留为证据，本轮候选没有执行布局布线或该修正。

## 三份资料同步入口

- [视频补充](../../../../../../attachments/history/video_sync_v24_20261027_f98266a9.md)
- [PYNQ 补充](../handoff/pynq_sync.md)
- [AI Sessions 补充](../handoff/ai_sessions_sync.md)
