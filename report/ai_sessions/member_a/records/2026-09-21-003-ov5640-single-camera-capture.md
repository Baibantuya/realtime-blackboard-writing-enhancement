# AI Session: 2026-09-21-003-ov5640-single-camera-capture

- Date: 2026-09-21
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 使用已连接的小眼睛双目 OV5640 与 MES-FMC-LPC-IO，启用单个摄像头、抓取一帧并交付可见图像与可复现测试目录
- Status: Blocked awaiting electrical-safety confirmation
- Report candidate: No
- Related commits: None
- Related files: pending

## Context Read

已按规定读取根目录 `AGENTS.md`、AI 开发政策、项目状态、决策流水、内部索引、最近串口检查记录及正式仓库 Git 状态。外层工作区不是 Git 仓库；正式仓库存在既有未提交改动，本任务不覆盖它们。

## Task and Constraints

- 用户已接入小眼睛双目 OV5640 和小眼睛 MES-FMC-LPC-IO，要求只启用一路并抓取、展示一张图像。
- 用户要求在根目录新建独立测试目录。
- 既有项目决策指出双目 OV5640 的 DVP/SCCB 默认 3.3 V，而 ZCU104 FMC VADJ 只能是 1.2/1.5/1.8 V；在未确认中间电平转换前不得驱动或接收相机 I/O。

## Contributions

- 审查根目录 `OV_SD_PCIe_200h_v2.3`：这是 Pango `PG2L200H-FBB676`、Fabric Compiler 2022.2-SP6.4 工程；其 `ovpcienpu.fdc` 的 camera I/O 全部为 LVCMOS33，不能用于或加载到 ZCU104。
- 复核 v2.3 有可复用的单目 `cmos2_*` 路径：SCCB 8-bit 地址 `0x78`（7-bit `0x3c`）、357 条寄存器写入、720p30 RGB565、8-bit 输入拼成一像素 RGB565；但原工程输出到 Pango DDR/PCIe，不具备 ZCU104/PYNQ 抓图软件路径。
- 阅读小眼睛官方 MES-FMC-LPC-IO 硬件手册和 Double_OV5640 实验说明。手册明确子卡用户 I/O 电平取决于载板 FPGA Bank 供电，并要求与外设一致；该子卡不是电平转换器。Double_OV5640 官方例程为 720p30 RGB565，适用其 Pango 平台。
- 通过已连接板卡的串口做只读预检：PynqLinux 仅有 stock `base.bit/base.hwh`，没有相机 overlay、V4L2 视频节点或现成 camera device-tree 描述；当前不能直接由 Linux 配置或抓取该 DVP 相机。
- 建立根目录独立测试目录 `zcu104_ov5640_capture_test/`，其中包含安全门槛、现场软件状态和只读 JTAG 探测 Tcl。
- 运行只读 Vivado Hardware Manager 探测。Vivado 2022.2 能启动并拉起 `hw_server`，但 `connect_hw_server` 因 `cs_server` 初始化连接失败而终止；未编程 FPGA。

## Decisions and Adoption

采用既有 D-020/D-021/D-022/D-023 的电压约束：在确认 3.3 V↔1.8 V 电平转换板存在并经核对前，不加载或开发会驱动/接收该 FMC 相机 I/O 的 bitstream。此为设备保护门槛，不是接口架构变更。

## Commands and Tools

- 读取项目规定上下文、正式仓库 Git 状态、v2.3 `impl.tcl`/顶层/寄存器配置/I2C/FDC。
- 浏览小眼睛官方 MES-FMC-LPC-IO 和 Double_OV5640 PDF 手册。
- 通过 COM8 对 PYNQ 系统做只读 overlay/I2C/V4L2/设备树检查。
- 执行 `vivado -mode batch .../probe_jtag.tcl` 只读探测；未调用 `program_hw_devices`。

## Validation and Evidence

- v2.3 `reg_config.v` 证明其初始化写地址和 RGB565 设定的来源，但该工程目标器件为 PG2L200H，不是 ZCU104。
- 小眼睛官方子卡手册第 5 节说明 I/O 电平由所属 Bank 供电决定；其 J2/J3 的 Pin39/40 是 3.3 V 电源，不等于用户信号已有电平转换。
- PYNQ 串口实测：仅 `/home/xilinx/pynq/overlays/base/base.bit`、`base.hwh`；不存在 `/dev/video*`，且当前 Python 目录中的 `pynq` 源树缺少 `pydantic` 依赖，不能直接作为可靠的 overlay 控制入口。
- Vivado JTAG 探测未成功：`cs_server` 在 `TCP:localhost:0` 初始化失败。未执行 bitstream 加载、相机 SCCB 配置、图像捕获或图像传输。

## Errors and Corrections

- 用户在本轮将相机和 MES-FMC-LPC-IO 接至 ZCU104，但没有描述中间电平转换板。此前材料和本轮官方手册均不支持假定该子卡自带转换；为避免 3.3 V 相机信号直接进入 1.8 V ZCU104 FMC I/O，暂停相机配置。
- JTAG 探测脚本最初在正式仓库路径下引用了不存在的文件；随后在用户要求的新测试目录创建 `probe_jtag.tcl` 并执行，结果暴露为 cs_server 连接失败，而非 FPGA 编程问题。
- 用户询问相机支持 1.8 V 与转接板 3.3 V 的关系。已澄清：MES-FMC-LPC-IO 的 J2 Pin39/40 是 FMC 载板提供的固定 A3V3 电源，不来自 VADJ；相机芯片的 DOVDD 能为 1.8 V不代表整块模组的40pin DVP/SCCB 已经是 1.8 V，也不代表可把模组主输入直接改为1.8 V。必须以模组原理图或实际无侵入测量确定 DOVDD、输出高电平和 SCCB 上拉域。

## Files Changed

- `project_workspace/ai/sessions/2026-09-21-003-ov5640-single-camera-capture.md`
- `zcu104_ov5640_capture_test/README.md`
- `zcu104_ov5640_capture_test/probe_jtag.tcl`

## Remaining Work

1. 用户确认已断电并已在 J2 与相机之间接入合格的 3.3 V↔1.8 V 电平转换，或提供模组/中间板原理图证明所有 DVP/SCCB I/O 已为 1.8 V。
2. 修复 Vivado Hardware Manager 的 cs_server 连接，再确认 JTAG 可见的 ZU7EV；或明确采用 SD/串口加载流程。
3. 在安全门槛通过后，建立 ZCU104 专用 PL capture overlay，复用 v2.3 的 `cmos2_*` SCCB 初始化序列和 RGB565 字节组合，抓取一帧到 PS 可读取内存并生成 PNG。

## Handoff Notes

本任务尚未完成；当前没有可靠、安全的方式配置相机或产生图像。继续之前必须由用户确认电平转换条件。
