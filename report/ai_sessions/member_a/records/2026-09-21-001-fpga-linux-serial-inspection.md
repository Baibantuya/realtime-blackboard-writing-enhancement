# AI Session: 2026-09-21-001-fpga-linux-serial-inspection

- Date: 2026-09-21
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 通过已连接的串口检查 FPGA 板上 Linux 系统，并形成可复现的检查指南
- Status: Completed
- Report candidate: No
- Related commits: None
- Related files: `project_workspace/PROJECT_STATE.md`, `project_workspace/ai/INDEX.md`

## Context Read

已按顺序读取根目录 `AGENTS.md`、AI 开发政策、项目状态、决策流水、内部索引和最近的硬件相关会话记录，并检查正式仓库 Git 状态。外层工作区不是 Git 仓库；正式仓库 `blackboard-writing-enhance/` 当前存在既有未提交改动，本任务不修改这些改动。

## Task and Constraints

- 用户已通过串口连接 FPGA，要求检查板上 Linux，并给出可复现指南。
- 用户说明登录用户名和密码均为常见的 Xilinx 默认值；内部记录不保存密码。
- 只做系统识别、启动状态、存储、内存、网络、设备树、内核日志等低风险只读检查，不修改板端配置。

## Contributions

- 枚举 Windows 串口并确认 FPGA Linux 控制台位于 `COM8`、115200-8-N-1；其余候选串口没有控制台响应。
- 在已登录的 `xilinx@pynq` 控制台执行只读身份、发行版、CPU、内存、存储、网络、启动、systemd、内核警告、FPGA manager、UIO/DRM 和 PYNQ 版本检查。
- 确认系统为 ZCU104 RevC、PynqLinux 3.0、Linux 5.15.19、PYNQ 3.0.1，FPGA manager 为 `operating`。
- 识别出 SD 卡文件系统非正常卸载/错误、系统时间错误、网口 down 和 DHCP 服务失败等现场问题，并整理正式复现及安全后续指南。

## Decisions and Adoption

无架构或接口决定。板端只读检查结果被项目状态采用；文件系统修复和服务配置尚未执行或决定。

## Commands and Tools

- 读取项目规定上下文和正式仓库 Git 状态。
- Windows PowerShell/.NET 串口枚举和直接串口访问；没有自动化终端应用 UI。
- Linux 侧执行 `whoami`、`id`、`uname`、`os-release`、`lscpu`、`free`、`df`、`lsblk`、`ip`、`systemctl`、`dmesg`、FPGA manager 和 PYNQ 版本等只读命令。

## Validation and Evidence

- 实板型号：`ZynqMP ZCU104 RevC`。
- 系统：PynqLinux 3.0（Ubuntu 22.04）、内核 `5.15.19-xilinx-v2022.1`、AArch64、4 核 Cortex-A53。
- 资源：1.9 GiB RAM、511 MiB swap；SD 59.5 GiB；根分区 14 GiB、使用 66%。
- FPGA manager `operating`，存在 `/dev/uio0`–`/dev/uio4` 和 DRM 节点；Python 3.10.4、PYNQ 3.0.1。
- 风险证据：EXT4 根分区挂载时报告错误；FAT boot 分区未正常卸载；journal 非正常关机后替换；板端时间为 2026-02-05、RTC 接近 1970且未同步；`eth0` down，两个 DHCP server 单元失败，systemd 为 `degraded`。
- 未执行：离线 fsck、网络连通、NTP 同步、服务配置修改、重启复测、bitstream/overlay 加载或算法应用测试。

## Errors and Corrections

Computer Use 技能禁止自动化终端应用，因此不通过 Windows 串口终端 UI 输入凭据；改用直接串口设备访问。
首次详细检查的结束标记也出现在终端命令回显中，导致采集循环过早结束；修正为固定时长采集后重跑并获得完整输出。

## Files Changed

- `project_workspace/ai/sessions/2026-09-21-001-fpga-linux-serial-inspection.md`
- `project_workspace/ai/INDEX.md`
- `project_workspace/PROJECT_STATE.md`
- `blackboard-writing-enhance/docs/fpga_linux_serial_check.md`

## Remaining Work

1. 关机后在另一台 Linux 主机上备份 SD 卡，并对未挂载的 boot/root 分区执行离线文件系统检查；之后重启复测。
2. 接入或配置网络，校正系统时间并确认 NTP 同步。
3. 明确本镜像是否需要 DHCP server；若不需要，再由项目所有者决定是否禁用失败服务。

## Handoff Notes

本轮没有修改板端。下一位操作者应先阅读正式指南，避免在已挂载根分区上运行 `e2fsck`；所有修复前先备份 SD 卡。
