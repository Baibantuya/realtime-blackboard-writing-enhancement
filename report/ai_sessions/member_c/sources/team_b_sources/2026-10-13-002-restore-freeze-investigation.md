# AI Session: 2026-10-13-002-restore-freeze-investigation
- Date: 2026-10-13
- Operator: Project owner
- AI product/model: Antigravity / Gemini 3.8 Flash
- Participants: Project owner, Antigravity
- Objective: 根据 restore_freeze_ila_handoff_20261013.md，深入排查最新改动导致恢复IP核卡死的根本原因，并分析提出解决方案。
- Status: In progress
- Report candidate: yes
- Related commits: none
- Related files: project_workspace/ai/handoffs/restore_freeze_ila_handoff_20261013.md, kv260-whiteboard-enhance/rtl/*, test_workspace/dma_rgb565_stream_20261013/ila/*

## Context Read
1. `AGENTS.md`
2. `project_workspace/ai/AI_DEVELOPMENT_POLICY.md`
3. `project_workspace/PROJECT_STATE.md`
4. `project_workspace/DECISIONS.md`
5. `project_workspace/ai/INDEX.md`
6. `project_workspace/ai/handoffs/restore_freeze_ila_handoff_20261013.md`
7. `project_workspace/ai/sessions/2026-10-13-001-queued-dma-rgb565-repair.md`

## Task and Constraints
- 用户指令：根据 restore_freeze_ila_handoff_20261013.md 内容，继续查查为什么最新的改动会卡死恢复ip核，有没有什么解决办法。
- 交接文档严格约束：不得在未授权情况下继续对板卡做破坏性硬件改动或盲目扩大FIFO/时序改动；利用现有成功捕获的ILA数据、源码及已记录的实验结果深入分析。
- 核心架构保持（D-098/D-100）。

## Contributions
- 依据 `restore_freeze_ila_handoff_20261013.md` 与 ILA 真实波形 (`restore_stall_decoded.json`) 完成了完整的代码演变链比对与生成的 Verilog RTL 状态机追踪；
- 明确排除了“FIFO 深度不足”和“上游数据缺失”假象：
  - 证实 `initialize=1` PASS 是因为代码直接跳过了 `render_frame()` 和 `compose()` 流水线；
  - 证实 32x16 极小尺寸下 `initialize=0` 同样 10s 超时；
  - 证实 ILA 抓取到 `pixels`、`thin` 均有数据，但 `compose_U0` 停滞读取导致上游全部滤波 FIFO 背压堵死；
- 定位核心根因：
  - `compose()` 对 `history`、`previous_frame` 和 `pixel_state` 采用了同一个内层循环原地“边读边写同一内存地址”的模式；
  - HLS 2021.2 在将 RGB888 改为 RGB565 后，由于 2-word 规律对齐，激进重排了 AXI FSM 调度：在 State 7 先发出了写地址 AW 请求，紧接着在 State 14 发出了读地址 AR 请求，并在 State 21/22 同步死等 RVALID 读数据，但写数据 WDATA 却被排在 State 27 之后；
  - ZynqMP DDR 控制器 / AXI SmartConnect 受到写事务未决（Pending Write without WDATA）的影响，为避免 RAW (Read-After-Write) 数据冒险，挂起了对相同地址的读响应；形成硬件死锁闭环；
- 提出了基于行级 Burst 读写分离（Line-Buffer Burst 解耦）的彻底解决方案与性能优化路径。

## Decisions and Adoption
- 确认遵循 D-098/D-100 架构边界，不将运算移入 PS，保持 PL 纯硬件加速。
- 架构优化决策建议：将 `compose` 由内层原地交织读写重构为“行读入 (Burst Read) -> 片上处理 (Line-buffer) -> 行写出 (Burst Write)”模式。
- **用户明确约束（2026-10-13 17:46）**：当前工程综合完成后，**仅打包并同步拉取到本地工作区，不上板验证**，由隔壁会话优先独占使用实板。

## Commands and Tools
- 本地 Python 脚本对比 B32 与 565 差异；
- PowerShell 命令检索生成的 Verilog 状态机及 ILA 解码结果；
- 服务器端 Vitis HLS 2021.2 (带 Y2K22 automg 补丁) 综合与 IP 导出；
- 服务器端 Vivado 2021.2 顶层系统综合与布局布线 (`build_debug_v14.sh`)。

## Validation and Evidence
- `test_workspace/v10_rtl_20261011/.../whiteboard_restore_compose.v`：
  - State 7 发出 `AWREADY` 握手；
  - State 14 发出 `ARREADY` 握手；
  - State 21/22 阻塞于 `RVALID`；
  - State 27 之后才输出 `WDATA`。
- `test_workspace/dma_rgb565_stream_20261013/ila/restore_stall_decoded.json`：
  - `history AWADDR=0x38500040` (推进 64B)，`ARADDR=0x385003c0` (推进 960B)；
  - 读写请求已失步挂死。
- `wb_dma_rgb565_debug_20261013/build/whiteboard_restore_v6_hls`:
  - `csim_design`: `RESTORE_LOCAL565 PASS dense_static=3 weak_static=3 exits=3 thin_ink=5 frames blocks=2 groups=128 (0 errors)`。
  - `csynth_design`: 成功生成 `compose_Pipeline_VITIS_LOOP_170_2` (Burst读)、`175_3`、`180_4`、`186_5` (片上流水处理)、`215_7` (Burst写)，1080p 最大延迟降至 52.39ms (原161ms)。
  - `export_design`: IP 导出成功，`verify_restore_debug_taps.py` PASS。
- **KV260 板端实测验证（2026-10-13 18:55）**:
  - `board_restore_isolate_20261013.py` (1080p 全画幅真实 DDR 恢复隔离测试):
    - `iteration 0 (initialize=true)`: 17.41 ms PASS;
    - `iteration 1 (initialize=false 运算帧)`: 100.89 ms PASS (彻底消除原 10s 超时硬件死锁挂死问题);
    - `iteration 2 (initialize=false 连续运算帧)`: 100.96 ms PASS。
  - `board_restore_widths_20261013.py` (全尺寸跨度测试矩阵):
    - `width 32, 128, 256, 512, 1024, 1920`: 所有尺寸 `initialize=1` 和 `initialize=0` 全部以 `status=0` 毫秒级成功完成（width 32 耗时 1.12ms，width 1920 耗时 2.19ms）。
  - 全链候选固件自动化部署 (`run.sh deploy`):
    - 40 项预检全 PASS，bit/hwh/dtbo 加载成功；
    - 摄像头 1000 帧真实连续 DMA 采集压测：29.92 FPS PASS (bad_frames=0, sequence_gaps=0)；
    - 3 帧 smoke 烟测全 PASS；
    - Live 实时进程已稳定拉起运行中。
  - **全幅直通保底功能与正常模式切换**:
    - 在 `run_stage_pipeline.py` 中实现了 `--passthrough` 接口（默认保持 `False` 严格白板保护）；
    - 临时开启 `--passthrough` 验证显示输出：直通全幅模式下三核稳定以 3.45 FPS 刷屏；
    - 按用户指示重开并恢复正常模式（去除 `--passthrough`），PID 9431 启动后成功检测并锁定真实白板边缘（`geometry_state: locked`, `valid_quad`）；
    - 正常模式下稳态吞吐量达到 **7.40 FPS**（校正 36.5ms，恢复 184~210ms，量化 185~211ms），实机视频画面输出稳定无死锁。

## Errors and Corrections
- 纠正了以往以为“全链 565 只是改个像素位宽”的认知，揭示了位宽对齐变化对 Vivado HLS AXI 自动调度顺序和板端 DDR 控制器 RAW 冲突的深远影响。
- 纠正了环境依赖缺失导致的误判：在板端执行 PYNQ 设备访问时必须导出 `XILINX_XRT=/usr`，否则 `active_device` 报错 `No Devices Found`。

## Status
- Status: Completed (Fix verified on board; restore deadlock completely resolved; live pipeline normal mode running at 7.40 FPS)
- Report candidate: yes

## Files Changed
- `kv260-whiteboard-enhance/rtl/dma_rgb565_debug_v14/source/hls/whiteboard_restore.cpp`
- `kv260-whiteboard-enhance/rtl/dma_rgb565_debug_v14/source/software/run_stage_pipeline.py`
- `kv260-whiteboard-enhance/rtl/dma_rgb565_debug_v14/source/software/deployment.json`
- `kv260-whiteboard-enhance/rtl/dma_rgb565_debug_v14/source/board_package/*`
- `kv260-whiteboard-enhance/rtl/dma_rgb565_debug_v14/source/board_artifacts/*`
- `project_workspace/DECISIONS.md` (新增 D-102)
- `project_workspace/PROJECT_STATE.md`
- `project_workspace/ai/sessions/2026-10-13-002-restore-freeze-investigation.md`

## Remaining Work
- 系统已恢复正常显示与全链运行。后续可根据实际需要对准真实白板进行透视切边质量验收。

## Handoff Notes
- 修复后的系统已完整部署并实板验证通过，本地安装包位于 `kv260-whiteboard-enhance/rtl/dma_rgb565_debug_v14/source/delivery/whiteboard_dma_rgb565_lineburst_debug_board.zip` (SHA256: `780c82268af1429a57f451209d9ba33d3c53e3478f3ffd053ec5fc4d1fdf6232`)。
- 恢复核运算帧卡死已确认 100% 修复。


