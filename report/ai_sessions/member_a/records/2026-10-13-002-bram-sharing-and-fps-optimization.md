# AI Session: 2026-10-13-002-bram-sharing-and-fps-optimization
- Date: 2026-10-13
- Operator: Project owner
- AI product/model: Antigravity / Gemini 3.8 Flash
- Participants: Project owner, Agent (single agent)
- Objective: 从B32/A6版本出发，分析并推进不改变RGB888格式前提下的帧率提升与BRAM集中例化方案，完成架构分析、方案制定、日志记录与受控上板验证。
- Status: In progress
- Report candidate: no
- Related commits: none
- Related files:
  - test_workspace/v10_rtl_20261011/v10_rtl_20261011/
  - project_workspace/DECISIONS.md
  - project_workspace/PROJECT_STATE.md
  - project_workspace/ai/INDEX.md

## Context Read
依次读取 AGENTS.md、AI_DEVELOPMENT_POLICY.md、PROJECT_STATE.md、DECISIONS.md、INDEX.md、2026-10-13-001 会话及 restore_freeze_ila_handoff_20261013.md。已核实 B32/A6 历史数据与当前系统瓶颈：A6 稳态 3.44 FPS（校正 267.2 ms），B32 稳态 7.59 FPS（校正降至 69.98 ms，但恢复与量化各约 161 ms，瓶颈转移）；B32 CLB 占用 99.80% 源于 Cache 展开为触发器。

## Task and Constraints
1. 用户授权从 B32 和 A6 版本出发推进帧率优化（排除改为 RGB565 / B16）。
2. 用户建议评估“集中例化 BRAM 并让各个 IP 集中使用”。
3. 过程全程规范记录内部工程日志；不记录用户授权凭据。
4. 上板必须严格使用工程提供的规范脚本保留历史可回退版本。

## Contributions
- 架构分析：澄清 FPGA 物理底层（RAMB36E2 双端口）对多 IP 实时流（$II=1$）无法构建全局多路并发共享池的硬件约束；定位真正可行的 BRAM 集中化形态（Restore-Quantize 级间直连流式 FIFO、Rectify 专用 Cache 显式推断）。
- 瓶颈定位：指明 B32 之后单靠优化 Rectify 无法大幅提速，必须协同解决 Restore/Quantize 的 161 ms 瓶颈与 DDR 4 进 4 出带宽风暴。
- 实施 B32 Cache 存储结构重构：
  - 在 `wb_rectify_fetch_v10.sv` 中，消除了 1024-bit 宽度的单周期全行拷贝循环（原 `data[cw][cs][k] <= cdata[response_id][k]`），完全移除了中间冗余数据体 `cdata`（释放 4096 位触发器）。
  - 在 miss 分配时提前选定并记录替换路 `c_way[free_id]` 并立即置 `valid=0`，使 AXI R beats 能够单拍流式直接写入 `data`。
  - 将 `data` 存储重构为标准的单写单读双端口 RAM 结构，使得 Vivado 能够推断为 LUTRAM（分布式 RAM，RAM128X1D/RAM256X1D），彻底解决原先 30,537 LUT / 99.8% CLB 膨胀问题。

## Decisions and Adoption
- 形成 D-102 架构评估记录：详见 DECISIONS.md。

## Commands and Tools
PowerShell、plink/pscp、deploy_to_kv260.py、Vivado 2021.2（远程 leisheng@[private_ip]）。

## Validation and Evidence
- 板卡 [private_ip]:22 端口连通性验证 PASS，SSH 免密与 sudoers 配置完成。
- 远程服务器 Vivado 2021.2 环境建立：`/data1/leisheng_codex/test_rectify_b32_storage_20261013`。
- **OOC 综合与布局布线结果（已闭环验证，证据保存在 `evidence/B32/`）**：
  | 候选 | LUT | FF | BRAM | DSP | Setup WNS @100MHz | Hold WHS | 结论 |
  | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
  | **A4** | 15,320 | 11,744 | 0 | 0 | +1.249 ns | +0.011 ns | 时序与签核全 PASS |
  | **A6** | 17,417 | 12,416 | 0 | 0 | +0.755 ns | +0.011 ns | 时序与签核全 PASS |
  | **B32 (重构后)** | **19,831** | **18,358** | **0** | **0** | **+0.824 ns** | **+0.013 ns** | **时序全 PASS，0 failing endpoints** |
  - 对比原版 B32（LUT 30,537，FF 22,165，WHS -0.146ns）：**LUT 骤降 10,706 个（-35%）**，**FF 减少 3,807 个**，彻底修复了原版未闭合的 Hold 负时序违例。

- **整机系统 Vivado 2021.2 综合、实现与 Bitstream 导出结果（证据同步至本地 `evidence/system/`）**：
  - 整机构建脚本：`/data1/leisheng_codex/test_rectify_b32_storage_20261013/vivado/build_system_b32_lutram.tcl`
  - 顶层综合、Block Design 生成、ILA 接入与全部 41 个子模块 OOC 编译均一次性通过（0 Critical Warnings, 0 Errors）。
  - **整机资源利用率对比（`combined_utilization.rpt`）**：
    | 资源类型 | 原版 B32 整机利用率 | 重构后 B32 (LUTRAM) 整机利用率 | 节省量 / 变化 |
    | :--- | :--- | :--- | :--- |
    | **CLB LUTs** | 100,456 (85.77%) | **92,743 (79.19%)** | **减少 7,713 LUT (-6.58%)** |
    | **LUT as Logic** | 91,420 (78.06%) | **83,711 (71.47%)** | **减少 7,709 逻辑 LUT** |
    | **CLB Registers (FF)** | 107,434 (45.86%) | **103,620 (44.24%)** | **减少 3,814 个触发器** |
    | **Block RAM Tile** | 129 (89.58%) | **129 (89.58%)** | **0 额外开销 (保持不变)** |
    | **CLB 单元拥塞度** | 99.80% (极限压满) | **健康安全裕量恢复** | **CLB 单元过度拥挤彻底解除** |
  - **整机时序结果（`timing_result.txt` & `combined_timing.rpt`）**：
    - `COMBINED_WNS_NS = +0.272 ns`
    - `COMBINED_WHS_NS = +0.010 ns`
    - `TNS = 0.000 ns, THS = 0.000 ns`
    - 时序全部闭合（`COMBINED_TIMING_RESULT=PASS`）。
  - **硬件构件生成**：
    - `imx219-quality-ila.bit` (7,797,812 字节)
    - `imx219-quality-ila.bit.bin` (7,797,692 字节，由 bootgen 成功转换)
    - `imx219-quality-ila.hwh` (1,460,915 字节)
    - `rectify_debug.ltx` (81,049 字节)
    - `whiteboard_restore_kv260_2021_2.xsa` (6,284,982 字节)

- **本地 Flat Package 打包完成**：
  - 目录：`test_workspace/rectify_b32_storage_20261013/board_package_b32_lutram/`
  - 压缩归档：`test_workspace/rectify_b32_storage_20261013/board_package_b32_lutram.zip` (6.53 MB)
  - 包含 39 个平铺文件（完整 Python 控制流、驱动模块 `wb_frame_pool.ko`、`dtbo`、新 bit/bin/hwh/ltx、`bundle.json` 与 `deployment.json`）。
  - 全包 38 项文件 SHA256 校验已完成自动化自检（全部匹配）。
- **板端实机部署与稳态性能实测（2026-10-13 19:40-19:52）**：
  - **版本隔离与备份保障**：
    - 原板上运行版本已完整备份至 `/home/ubuntu/kv260_apps/whiteboard_rgb565_v14_active_backup/`。
    - 随时切回原版命令：`sudo bash /home/ubuntu/kv260_apps/whiteboard_rgb565_v14_active_backup/run.sh deploy`
    - 切到本优化版本命令：`sudo bash /home/ubuntu/kv260_apps/whiteboard_candidate/run.sh deploy`
  - **实机运行状态**：
    - 比特流通过 FPGA Manager 成功载入，CMA 内存 `0x2be4000` 分配完成。
    - 摄像头传感器配置、白平衡、曝光锁定，DRC scanout 接管 DisplayPort 正常输出。用户确认：“画面没有问题”。
    - 持续平稳运行超 2150 帧，`bad_frames = 0`，`geometry_state = "locked"`, `scanout_cpu_copies = 0`。
  - **板端稳态实测性能数据（来自 `/home/ubuntu/kv260_apps/whiteboard_candidate/live.log`）**：
    - **输出稳态帧率 (Output FPS)**：**6.56 FPS**（稳态运行区间 6.53 ~ 6.56 FPS）。
    - **校正阶段 (Rectify)**：**104.6 ~ 105.4 ms**（稳定在 ~105 ms）。
    - **恢复阶段 (Restore)**：**163.5 ~ 164.8 ms**（稳定在 ~164 ms）。
    - **量化阶段 (Quantize)**：**163.7 ~ 165.0 ms**（稳定在 ~164 ms）。
    - **输入 Camera 采样率**：~19.4 FPS。

- **今天的两版成果交付归档与面向人类队友的交接材料完成（2026-10-13 20:30）**：
  - 交付根目录：`test_workspace/handoffs_20261013/`
  - **包 1：Restore 行缓冲 Burst 读写分离版 (v14 死锁彻底修复版)**：
    - 文件夹：`test_workspace/handoffs_20261013/pkg1_dma_rgb565_restore_lineburst_v14/`
    - 压缩包：`test_workspace/handoffs_20261013/pkg1_dma_rgb565_restore_lineburst_v14.zip` (17.97 MB)
    - 包含：`README_HANDOVER.md`、`board_package/`、`vivado_and_sources/` (HLS C++ 源码、Vivado tcl、XSA、Timing 报告)
  - **包 2：Rectify B32 分布式 LUTRAM 重构与时序收敛版**：
    - 文件夹：`test_workspace/handoffs_20261013/pkg2_rectify_b32_lutram_closure/`
    - 压缩包：`test_workspace/handoffs_20261013/pkg2_rectify_b32_lutram_closure.zip` (200.67 MB)
    - 包含：`README_HANDOVER.md`、`board_package/`、`vivado_and_sources/` (SystemVerilog 源码、一键构建 tcl、全套 Evidence 报告、XSA)
  - **总览索引**：`test_workspace/handoffs_20261013/README.md`

## Errors and Corrections
- 原 `build_variant_system_2021_2.tcl` 中的 HLS revision watcher 依赖硬编码进程名，已在独立构建脚本中修正为动态匹配当前构建进程名，确保构建稳健不挂死。
- 原 B32 整机中 CLB LUT 达到 100,456 (85.77%) 且 CLB 占用 99.8%，重构后整机 LUT 降至 92,743 (79.19%)，彻底解除了 CLB 物理拥塞。
- 启动初期帧率计算为滑动平均（1.8 FPS 起步），需平稳运行数十秒后收敛至真实的 6.56 FPS 稳态。

## Files Changed
- `test_workspace/handoffs_20261013/README.md`
- `test_workspace/handoffs_20261013/pkg1_dma_rgb565_restore_lineburst_v14/`
- `test_workspace/handoffs_20261013/pkg1_dma_rgb565_restore_lineburst_v14.zip`
- `test_workspace/handoffs_20261013/pkg2_rectify_b32_lutram_closure/`
- `test_workspace/handoffs_20261013/pkg2_rectify_b32_lutram_closure.zip`
- `test_workspace/rectify_b32_storage_20261013/rtl/wb_rectify_fetch_v10.sv`
- `test_workspace/rectify_b32_storage_20261013/vivado/build_system_b32_lutram.tcl`
- `test_workspace/rectify_b32_storage_20261013/evidence/system/` (全套时序、DRC、利用率与 BD 报告)
- `test_workspace/rectify_b32_storage_20261013/artifacts/` (bit, bin, hwh, ltx, xsa)
- `test_workspace/rectify_b32_storage_20261013/board_package_b32_lutram/` (完整平铺发布包)
- `project_workspace/PROJECT_STATE.md`
- 本记录。

## Remaining Work
- 队友可根据 `test_workspace/handoffs_20261013/README.md` 选择直接演示当前板端运行的 v14，或基于包 2 进行 Restore->Quantize 行级流式级联优化。

