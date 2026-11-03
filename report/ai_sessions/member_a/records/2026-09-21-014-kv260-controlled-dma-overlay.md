# AI Session: 2026-09-21-014-kv260-controlled-dma-overlay

- Date: 2026-09-21
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 在无 HDMI 条件下，为 KV260 建立受控的最小 PS→PL→PS GRAY8 二值化 DMA 回环，并在安全前提下进行板端验证。
- Status: In progress
- Report candidate: No
- Related commits: None

## Context Read

已依次读取根目录规范、AI 开发策略、项目状态、D-027 至 D-029、会话索引、最近会话 013 和当前目录状态。工作区及 `kv260-whiteboard-enhance/` 均不是 Git 仓库；`whiteboard/` 当前不存在，正式交付目录命名存在历史待确认项。

## Task and Constraints

- 用户确认继续最小无显示回环。
- 只加载由本轮产生且器件/接口明确匹配 KV260 的受控配置；不加载未知 starter-kit 或旧 ZCU104 工件。
- 在 bitstream/overlay 实际加载、DMA 回读与逐字节比对前，不宣称硬件数据通路通过。
- 不在记录中保存账户密码。

## Contributions

- 本机 Vivado 2022.2 已确认 `xck26-sfvc784-2LV-c` 和 `xilinx.com:kv260_som:part0:1.4` 预设可用。
- 新建正式 `whiteboard/` 工程：ZynqMP PS 的 HPM0 控制 AXI DMA，HPC0 连接 DMA 的 DDR 主端，MM2S→GRAY8 AXIS 阈值核→S2MM；DMA 为 simple mode、8-bit stream、128-bit DDR 端。
- 真实 Vivado block-design 校验通过；综合与实现完成，bitstream 和带 bitstream 的 XSA 已生成，尚未加载到板卡。
- 新增 PYNQ 控制层 `Kv260ThresholdOverlay`，使用 `Overlay + allocate + AXI DMA` 将每个 1920x1080 GRAY8 帧作为完整 AXI packet 送入 PL 并回收输出；接收通道先于发送通道启动以容纳反压。
- 新增 UVC/FFmpeg 连续输入和 `run_continuous` 调度。每帧均进入 PL，`preview_every` 只降低 Jupyter 的 JPEG/widget 刷新率，不跳过硬件处理。
- 新增 Jupyter notebook：先运行 1080p 合成梯度的逐像素硬件自检，再处理 `/dev/video0` 的 300 帧 1080p30 序列，显示抽样预览并保存最近的 PL 输出帧。
- 新增多帧 Python 回归、两帧 AXI 随机反压 RTL testbench、PYNQ 打包脚本与板端部署说明。

## Decisions and Adoption

- 用户确认当前镜像已安装 PYNQ 3.0.1。采用 PYNQ `Overlay + allocate + AXI DMA` 作为 KV260 无显示二值化闭环的主运行时；自写 Linux coherent-buffer 驱动保留为非 PYNQ Ubuntu/XRT 的备用方案。

## Commands and Tools

- 已重新读取 computer-use 操作与确认规则；串口会话仅用于 KV260 受控测试。

## Validation and Evidence

- 2026.2 Vivado 实现完成：0 error、0 critical warning；路由后 WNS `+4.764 ns`、WHS `+0.009 ns`，所有用户时序约束满足。
- bitstream SHA-256: `EFF404902FC234B00AD8107E3C904931E8B563FC2AFD907FBB60CB6708126106`。
- XSA SHA-256: `0DC2B464C6D47754EE7DABDCF2F41E46DD1C21987E3EF8D2192779D739098F85`。
- Linux device-tree overlay、DMA-safe 分配/控制程序和真实板端 DMA 回读：未执行。
- 板端实测：PYNQ `3.0.1` 位于 `/usr/local/share/pynq-venv/lib/python3.10/site-packages/pynq/`，`pynq.allocate` 和 `pynq.Overlay` 可导入，`/home/ubuntu/Kria-PYNQ/kv260/base.bit/base.hwh` 存在，`/dev/udmabuf` 存在。未下载 overlay 时 `allocate()` 返回 `RuntimeError: Overlay is not downloaded`，符合 PYNQ 的预期前置条件。
- 板端实测 PYNQ AXI DMA 驱动的 `bindto` 包含 `xilinx.com:ip:axi_dma:7.1`，与本工程 HWH 中 AXI DMA v7.1 匹配；OpenCV 4.12.0、ipywidgets 7.7.1、NumPy 1.26.4 可用。
- 打包出的匹配文件：`whiteboard/pynq/kv260_threshold.bit`（SHA-256 `EFF404902FC234B00AD8107E3C904931E8B563FC2AFD907FBB60CB6708126106`）和 `kv260_threshold.hwh`（SHA-256 `10A71E5C738FCEF9D29B4A27095FA2B15E305DD4AE1ED25913B84A5A1E92ABF0`）。HWH 确认 DMA 控制基址 `0xA0000000`、MM2S/S2MM DRE 启用、8-bit AXIS、128-bit DDR，并经 HPC0 可见 DDR_LOW。
- `python -m unittest whiteboard/tests/test_pynq_stream.py -v`：2 项通过；确认阈值边界为 127/128，且 10 个连续帧全部处理、预览仅发生在第 3/6/9 帧。
- Vivado XSim 2022.2：两个帧 packet 在周期性反压下数据、`TUSER`、`TLAST` 全部通过，日志输出 `PASS: two frame packets survive AXIS backpressure`。
- PYNQ 模块 `py_compile` 通过；notebook JSON 可解析，所有代码 cell 合并编译通过。
- 当前未执行：把本项目 overlay 下载到板卡、真实 PYNQ DMA 回环、1080p30 摄像头连续回传、端到端帧率与输出抽帧。板端 `eth0` 当前为 DOWN，无法通过网络传输约 7.8 MB bitstream；未采用低效的串口 base64 传输。
- 按用户指令通过 COM11 为板端 `eth0` 临时配置 `[private_ip]/24`，未配置默认网关或 DNS。串口复核地址与直连路由已存在；当时物理状态仍为 `NO-CARRIER`/`linkdown`，等待电脑端网卡设置为 `[private_ip]/24` 后再次检查。该 `ip` 命令配置重启后不保留。

## Errors and Corrections

- 初始 block-design 使用不支持的 ZynqMP PS IP v3.3；已改为 KV260 支持的 v3.4。
- 初始 AXI automation 无法从 DMA master 推导 HPC 接口；已改为显式 SmartConnect 拓扑并通过 BD 校验。
- 受限沙箱阻止 Vivado 子进程，改用获批的受控 Vivado 外部构建；这不是 RTL/器件错误。
- 初次 PYNQ 分配在仅 `download=False` 解析 HWH 时失败；纠正为后续先加载经过验证的 KV260 PYNQ base overlay，再调用 `allocate()`。
- Python 多帧测试初次动态加载模块时未先注册到 `sys.modules`，导致 `dataclass` 导入错误；已先注册模块并复测 2 项通过。
- notebook 首次静态编译检查直接拼接各 cell、未插入换行，产生了检查脚本自身的 `SyntaxError`；改为以两个换行连接代码 cell 后通过，notebook 内容无需因此回退。
- 首次通过补丁加入 Verilog testbench 时，JavaScript 模板字符串误解释 Verilog反引号；移除非必要的 `timescale` 行后成功创建并完成仿真。
- 用户在板端运行 notebook 时发现 PYNQ `ValueError: Transfer size is 2073600 bytes, which exceeds ... 16383`。根因是 AXI DMA 默认 `c_sg_length_width=14`，与 full-HD 单 packet 设计不匹配；已将该参数改为 23，重新完成综合/实现/写 bitstream。

## Files Changed

- `project_workspace/ai/sessions/2026-09-21-014-kv260-controlled-dma-overlay.md`
- `whiteboard/README.md`
- `whiteboard/rtl/axis_gray8_threshold.v`
- `whiteboard/scripts/build_kv260_dma_threshold.ps1`
- `whiteboard/scripts/create_kv260_dma_threshold.tcl`
- `whiteboard/docs/kv260_dma_threshold_interface.md`
- `whiteboard/build/kv260_dma_threshold/`（本机生成工件）
- `whiteboard/pynq/kv260_threshold.py`
- `whiteboard/pynq/kv260_threshold_demo.ipynb`
- `whiteboard/pynq/README.md`
- `whiteboard/pynq/DEPLOY.md`
- `whiteboard/pynq/kv260_threshold.bit`
- `whiteboard/pynq/kv260_threshold.hwh`
- `whiteboard/tests/test_pynq_stream.py`
- `whiteboard/tb/tb_axis_gray8_threshold.v`
- `whiteboard/scripts/run_axis_threshold_sim.tcl`
- `whiteboard/scripts/package_pynq_overlay.ps1`
- `project_workspace/DECISIONS.md`
- `project_workspace/PROJECT_STATE.md`
- `whiteboard/scripts/create_kv260_dma_threshold.tcl`（`c_sg_length_width=23`）

## Remaining Work

1. 连接 KV260 以太网或通过 USB 存储，把 `whiteboard/pynq/` 的四个运行文件上传到同一 Jupyter 目录。
2. 依次运行 notebook，记录 1080p 合成自检差异、300 帧实际 pipeline fps、最新二值帧和任何 DMA 超时/丢帧。
3. 若单缓冲无法稳定达到 30 fps，再实现双缓冲/流水调度并测量 PS CPU、复制和 cache 同步开销；不得用抽样预览帧率替代端到端数据。

## Handoff Notes

本机构建、PYNQ 程序、连续流仿真和打包已完成。实机 overlay 尚未加载，不可宣称 PS→PL→PS 闭环已通过。当前最短路径是恢复 `eth0` link 后在 Jupyter 上传 `kv260_threshold.bit/.hwh/.py/.ipynb`，按 `whiteboard/pynq/DEPLOY.md` 运行。
本次用户现场运行的是旧 overlay，必须覆盖上传新生成的 bit/hwh；只替换 Python 文件不能修复 DMA 上限。
