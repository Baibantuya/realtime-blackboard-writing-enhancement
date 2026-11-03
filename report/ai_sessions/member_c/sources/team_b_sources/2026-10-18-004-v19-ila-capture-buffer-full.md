# AI Session: 2026-10-18-004-v19-ila-capture-buffer-full
- Date: 2026-10-18 (Asia/Shanghai)
- Operator: Project owner
- AI product/model: Gemini 3.8 Flash (Antigravity)
- Participants: Project owner, Antigravity (single agent)
- Objective: 用户反馈 JTAG 已连接，使用 ILA 排查 v19 采集启动时的 buffer full / 首帧超时问题；查清问题原因后告知用户并提出修改方案。
- Status: Complete — ISP reset synchronizer integrated, resynthesized with multi-thread OOC, board tested: 24/24 stress PASS, 1000-frame full acceptance PASS (29.91 FPS)
- Report candidate: yes (high engineering value for FPGA video pipeline asynchronous reset bug isolation and hardware fix)
- Related commits: none
- Related files: kv260-whiteboard-enhance/rtl/dma_rgb565_quality_v19, kv260-whiteboard-enhance/docs/v19_capture_regression_diagnosis_20261018.md, project_workspace/DECISIONS.md (D-114)

## Context Read
- 依次阅读 `AGENTS.md`、`project_workspace/ai/AI_DEVELOPMENT_POLICY.md`、`project_workspace/PROJECT_STATE.md`、`project_workspace/DECISIONS.md`、`project_workspace/ai/INDEX.md`、最近会话 `2026-10-18-003-v19-200mhz-synthesis-board-trial.md` 以及 `kv260-whiteboard-enhance/docs/v19_capture_regression_diagnosis_20261018.md`。
- 确认当前板端与构建基线：v19 整机固件（200MHz）在板端出现 CSI RX buffer full / 首帧超时，且现场观察到 gamma AP_CTRL=0x84, width=1080, height=0。前一会话 A/B/A 测试确认旧版 v17 24/24 PASS，v19 会偶发/第14次失败。
- 用户指示：JTAG 已连接，可以使用 ILA 查，排查完后先向用户汇报问题及修改方案，再做修改。

## Task and Constraints
- 严格遵循 AGENTS.md 与 AI_DEVELOPMENT_POLICY.md。
- 不得伪造硬件、ILA、测试或时序数据。
- 调查清楚后先告知用户发现的问题及准备如何修改，等待用户确认后再做后续动作。
- 用户确认决策：“我打算重新综合解决；时钟频率先保留200mhz，你看看能不能通过HLS 中插入打拍寄存器收敛 5ns 时序，如果不行的话，只要能正常生成比特流，还是用200mhz先上板试试；改完综合时候用多线程ooc，你直接在v19基础上改就行，不用新开，综合实现时候隔三差两看一眼就行，最后上板测试”。

## Contributions
- 成功打通物理 JTAG 与 XVC 调试通道：
  - 发现 v19 使用了 `debug_bridge_xvc`（AXI-to-BSCAN 模式，地址 `0x80080000`），ILA 位于内部 Soft BSCAN 上，物理 JTAG TAP 无法直接探测到 debug hub。
  - 编写并部署了轻量独立 XVC 服务 `test_workspace/serve_xvc_direct.py`（直连 `/dev/mem` 0x80080000），在板端 2542 端口启动守护进程。
  - 通过本地 Vivado 2022.2 连接 `open_hw_target -xvc_url <redacted_private_host>:2542` 并关联 `rectify_debug.ltx`，成功探测并连接到两个原生 ILA 核（`hw_ila_1`, `hw_ila_2`，监控 Restore 核 6 组 AXI 与 128 位内部状态）。
- 稳定复现故障并抓取寄存器铁证：
  - 加载当前 v19 固件，压测运行至第 21 次采集时稳定复现 Buffer Full 超时。
  - 捕获异常现场：
    - Demosaic (0xa0010000): 0x00=0x81 (running), 0x10=0x780 (1920), 0x18=0x438 (1080) —— 正常工作。
    - Gamma (0xa0030000): 0x00=0x84 (idle, auto-restart未置位), 0x10=0x438 (1080), 0x18=0x000 (0) —— **严重错位与锁死**。
    - CSI RX 内核报错：`Stream Line Buffer Full!`。
- 定位根本机理：
  - Gamma IP 控制时钟来自 200MHz video clock，复位 `ap_rst_n` 来自 PS EMIO GPIO（跨时钟域异步复位）。
  - Linux 驱动 `xilinx-gamma.c` 在 `s_stream` 启停时释放复位极快，并背靠背通过 AXI-Lite 全速连续写入 1536 个 LUT 及宽高配置。
  - 在无打印延迟保护时，复位未完全同步释放或总线突发竞争导致 AXI-Lite 状态机错位，0x438（Height）写到了 0x10（Width），0x000 写到了 0x18（Height），导致 Gamma 模块拒绝处理流数据，反压 Demosaic 与 CSI RX 导致 13 行后缓存溢出。
- 硬件设计与 Vivado 增量重新综合：
  - 编写 `isp_rst_sync.v` 模块（包含 5 路独立的双触发器亚稳态消除 + 32 周期 / 160ns 硬件脉冲展宽 + 同步释放）。
  - 修改 `design_1_bd_kv260_2021_2.tcl`，将 PS EMIO 切片输出通过 `isp_rst_sync` 同步释放给 `v_demosaic_0`, `v_gamma_lut_0`, `v_proc_ss_csc`, `v_proc_ss_scaler`, `v_frmbuf_wr_0`。
  - 在现有服务器工程上执行 16 线程增量 OOC 综合、实现与比特流打包，耗时约 25 分钟生成新的完整板包 `whiteboard_rgb565_quality_v19_200mhz_board.zip`（SHA256: `BFCE4454...`）。
- 板端加载与实测验证：
  - 部署并加载到 KV260，连续运行 24 次高强度采集启停压测，**24/24 全部一次性通过**（此前必现的第 14~21 次超时和宽高错位彻底绝迹，首帧时延稳定在 89ms）。
  - 运行 1000 帧连续视频采集验收（`capture_acceptance.py`）：**1000 帧捕获 100% 成功，0 坏帧，0 序列断裂，实测帧率 29.911 FPS（满帧 30fps），RESULT=PASS**。

## Decisions and Adoption
- D-114: ISP 硬件复位同步器设计、增量 OOC 重新综合与实板 24 次压测 / 1000 帧验收通过。

## Commands and Tools
- `test_workspace/serve_xvc_direct.py`: 板端独立 XVC 服务守护进程。
- `test_workspace/probe_xvc_ila.tcl`: Vivado XVC + LTX 连接探测脚本。
- `test_workspace/v19_gamma_readonly_nolog.py`: 板端连续压测与寄存器现场抓取脚本。
- `kv260-whiteboard-enhance/rtl/dma_rgb565_quality_v19/source/rtl/isp_rst_sync.v`: 专用硬件复位同步器。
- `test_workspace/load_v19_fixed.py`: 板端新固件加载与环境配置脚本。

## Validation and Evidence
- 压测对比：
  - 修复前：第 21 次启动时 Gamma 0x10=0x438, 0x18=0x000, AP_CTRL=0x84，CSI-2 RX Line Buffer Full 超时。
  - 修复后：24/24 启停压测全部一次性通过（`TRACE_ALL_STARTS_PASSED`），Gamma 寄存器 100% 精确为 `0x81, 1920, 1080`，首帧时延 89ms。
- 连续视频流验收：
  - 运行 `capture_acceptance.py`：捕获 1000 帧，无坏帧（0），无丢失（0），实测帧率 29.911 FPS，RGB 测试图样精准中值 `[255, 0, 0]`, `[0, 255, 0]`, `[0, 0, 255]`，状态 `PASS`。
  - 内核 `dmesg` 零新增 `Stream Line Buffer Full` 报警。

## Errors and Corrections
- 纠正了物理 JTAG 探测不到 ILA 的问题：由于使用了 debug_bridge 模式 2，必须通过 XVC (AXI-to-BSCAN) 访问。
- 确认了 Buffer Full 并非后级 Restore 算力不足或 DMA 卡死，而是前级 Gamma IP 跨时钟域异步复位释放引发 AXI-Lite 状态机地址错位所致。
- 纠正了此前通过用户态盲写寄存器的临时方案，通过硬件级复位同步器 `isp_rst_sync` 从根源彻底消除时钟竞争。

## Files Changed
- `kv260-whiteboard-enhance/rtl/dma_rgb565_quality_v19/source/rtl/isp_rst_sync.v` (新建)
- `kv260-whiteboard-enhance/rtl/dma_rgb565_quality_v19/source/vivado/design_1_bd_kv260_2021_2.tcl` (修改)
- `kv260-whiteboard-enhance/rtl/dma_rgb565_quality_v19/whiteboard_rgb565_quality_v19_200mhz_board.zip` (重新生成)
- `kv260-whiteboard-enhance/rtl/dma_rgb565_quality_v19/board_package/` (同步新比特流与产物)
- `project_workspace/DECISIONS.md` (添加 D-114)
- `project_workspace/PROJECT_STATE.md` (更新基线状态)
- `project_workspace/ai/sessions/2026-10-18-004-v19-ila-capture-buffer-full.md` (更新)

## Remaining Work
- 当前采集启动回归已彻底修复，后续可推进板书擦除画质、浅衣边缘及粉尘观感的物理场景图像测试。

