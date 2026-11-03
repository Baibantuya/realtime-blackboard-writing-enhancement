# AI Session: 2026-09-21-008-kv260-serial-board-check

- Date: 2026-09-21
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 通过已连接的串口对 AMD Kria KV260 执行只读基础板卡健康检查。
- Status: Completed
- Report candidate: No
- Related commits: None
- Related files: `project_workspace/ai/sessions/2026-09-21-008-kv260-serial-board-check.md`, `project_workspace/PROJECT_STATE.md`, `project_workspace/ai/INDEX.md`

## Context Read

已按入口规范阅读 `AGENTS.md`、AI 开发政策、项目状态、决策流水、索引，以及最近的 KV260 会话 `2026-09-21-006-kv260-project-summary-wording.md` 和 `2026-09-21-007-archive-zcu104-demos.md`；已检查 `kv260-whiteboard-enhance/` Git 状态。根目录和新的 KV260 入口均不是 Git 仓库；本次不修改工程代码。

## Task and Constraints

- 用户说明 KV260 已经通过串口连接，并推测默认账密为 `xilinx`。
- 本次仅做登录与只读信息采集：系统/内核、存储、内存、网络、USB/视频设备、FPGA 管理器及近期严重日志。
- 不写入板端文件系统、不加载 bitstream、不改网络或设备配置；登录凭据不写入后续工程记录。

## Contributions

- Windows 已枚举 `COM3`、`COM4`、`COM5`、`COM6`、`COM7`、`COM11`、`COM12`。其中 COM11/COM12 分别是同一 FTDI 4232H 调试模块的两个 USB Serial 通道（实例后缀 `...PQKLB` / `...PQKLC`）。
- 在 115200-8-N-1 下，COM11 对 CR/LF 和 `xilinx` 文本有字符回显，但没有启动日志、`login:` 或 `Password:`；COM12 无输出。两口的 CTS/DSR/RI/CD 均为低。
- COM3 无法打开，Windows 返回 timeout（错误 121）；其他通用端口无自动输出。无法根据当前证据确认哪一个是 KV260 的有效 PS UART 控制台，或板端是否已启动。
- 用户补充 PuTTY 使用 XON/XOFF 软件流控后，改用 Plink 以 `COM11, 115200, 8N1, XON/XOFF` 保持交互会话，成功进入已有的 `ubuntu@kria` shell，并完成只读板卡健康检查。
- 板卡识别为 `ZynqMP KV260 revB`；Ubuntu 22.04.4 LTS，Linux `5.15.0-1027-xilinx-zynqmp`，4 核 Cortex-A53（333 MHz–1.333 GHz），3.8 GiB RAM，无 swap。
- 59.5 GiB SD 卡根分区为 ext4，约 58 GiB、已用 11 GiB（20%）；根分区以 `rw,relatime,discard,errors=remount-ro` 挂载。systemd 状态为 `running`，未列出失败单元。
- FPGA manager 状态为 `operating`；XRT 2.13.0 / ZOCL 2.13.0，`xbutil examine` 将 KV260 设备报告为 `Device Ready: Yes`。`dfx-mgrd` 为 inactive，普通用户运行 `xmutil listapps` 因 socket 权限失败。
- DRM `card0-DP-1` 为 connected。USB 仅枚举板载 Microchip hub，未发现 UVC 摄像头；无 `/dev/video*`，`v4l2-ctl` 无法打开 `/dev/video0`。
- `eth0` 为 UP 但 `NO-CARRIER`，没有 IP 或默认路由。系统时间显示 2025-10-17，RTC 为 1970，NTP 服务 active 但尚未同步。
- 板上温度初始约 30.3–31.8 °C。四核 OpenSSL SHA-256 冒烟负载完成，16 KiB 块总吞吐约 351.9 MB/s；负载后最高约 32.7 °C，最近两分钟无新增内核 error。
- 本次内核 warning 包括 device-tree overlay 卸载可能内存泄漏，以及 `zocl-drm` 缺少 IRQ index 0；未观察到存储 I/O、EXT4、崩溃或过热错误。

## Decisions and Adoption

- 未形成架构或接口决定。

## Commands and Tools

- 已读取项目规范、状态、决策、索引、近期记录和正式仓库状态。
- 只读检查 Windows 的 COM 口清单、FTDI 注册表识别信息和串口状态；以 115200-8-N-1 对可打开端口读取启动输出。
- 向 COM4/5/6/7/11/12 发送 CR/LF 以请求已有控制台显示提示；仅向 COM11 尝试用户名 `xilinx`，未收到密码提示，因此未发送密码。
- 使用 Plink 以 XON/XOFF 软件流控连接 COM11；读取身份、OS、内核、CPU/内存、块设备/挂载、systemd、时间、网络、USB/V4L2、DRM、FPGA manager、XRT、温度、进程和内核日志。
- 执行 3 秒、4 进程 OpenSSL SHA-256 短负载测试，并复查温度与近两分钟内核 error；随后正常退出板端 shell 并关闭串口客户端。

## Validation and Evidence

- 已实际验证 KV260 的 Linux/内核、CPU/内存、存储挂载、systemd、时间、网络、USB/视频、DRM、FPGA manager、XRT、温度及内核日志。
- 短负载测试正常完成，四核均产生结果，温升低于 1 °C，测试后无新增内核 error。
- 未修改板端配置、文件系统、bitstream 或网络设置。

## Errors and Corrections

- 初次多端口探测命令因 Windows 命令行换行转义而发生 Python `SyntaxError`；该命令未打开串口且未发送数据。后续改为逐口探测。
- 初始上下文中将 `kv260-whiteboard-enhance/` 描述为嵌套正式仓库；复查 `git -C kv260-whiteboard-enhance status --short` 返回“not a git repository”，已更正本记录。
- 直接 pyserial 会话最初仅收到字符回显；原因是未复现用户 PuTTY 的 XON/XOFF 会话方式。改用 PuTTY 套件的 Plink 并显式设置 XON/XOFF 后成功接入。
- 第一次发送 XON 时板端出现一次 `rnx11: command not found`，属于控制字符/终端转义被 shell 拼接后的无害命令错误；没有配置变更，随后提示符正常。
- 临时创建的串口中继脚本因执行环境标准输入立即关闭而不可用；已在本次结束前删除。

## Files Changed

- `project_workspace/ai/sessions/2026-09-21-008-kv260-serial-board-check.md`
- `project_workspace/PROJECT_STATE.md`
- `project_workspace/ai/INDEX.md`

## Remaining Work

1. 接入以太网后验证 DHCP、默认路由和 NTP 同步，纠正系统时间与 RTC 状态。
2. 接入实际 UVC 摄像头后检查 `lsusb`、`v4l2-ctl --list-devices`、格式和连续采集；当前没有摄像头设备。
3. 在开始动态 overlay/app 流程前确认 `dfx-mgrd` 的预期启用方式与 `xmutil` 权限模型；当前 FPGA/XRT 基础状态可用。

## Handoff Notes

本次结果是板卡启动约 36 分钟时的单次只读观测。基础计算、内存、存储挂载、显示和 FPGA/XRT 状态正常；网络、时间同步和相机输入尚未就绪。未执行 SD 卡全盘读写、外设压力、bitstream 加载或视频闭环测试。

## Continuation Update

- 用户提供当前登录凭据并确认其通过 PuTTY 使用 COM11 正常；凭据本身不写入此记录。
- 在直接串口的 115200-8-N-1 会话中，认证序列和只读 `id; uname -a` 查询均只收到发送字符的回显；向 COM11 发送 10 个空格加 CR/LF 也仅得到同样回显，COM12 无输出。
- 这与用户在 PuTTY 中的成功连接矛盾，说明直接串口会话未复现 PuTTY 的有效配置或会话状态。Computer Use 环境未暴露可接管的 PuTTY 原生窗口，且不支持启动该应用；下一步需要用户提供 PuTTY 的 Speed、Data bits、Parity、Stop bits、Flow control，或关闭 PuTTY 后允许以其确切配置重新连接。
- 未验证板端 Linux、存储、网络、USB/视频、FPGA manager 或日志；未改动板端配置、文件系统、bitstream 或网络。

以上 Continuation Update 的“未验证”状态已被后续 XON/XOFF Plink 会话解除，最终结果以本记录的 Contributions、Validation and Evidence 和 Handoff Notes 为准。
