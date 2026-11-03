# AI Session: 2026-09-19-002-vivado-gui-full-frame

- Date: 2026-09-19
- Operator: Codex
- AI product/model: Codex
- Participants: 用户（成员2）；Codex（GUI 仿真适配与说明）
- Objective: 让昨日 Vivado GUI 工程可以直接运行整帧 IP 回环验证。
- Status: Completed
- Report candidate: no
- Related commits: none
- Related files: `blackboard-writing-enhance/tb/tb_enhance_axis_ip_frame.sv`

## Context Read

- 沿用同日上一会话已读取的项目规范、状态、决策、IP RTL、整帧 testbench 与验证结果；重新核对 XSim 2022.2 `--testplusarg` 命令行支持。

## Task and Constraints

- 用户希望复用昨日 Vivado 图形工程进行整帧验证，需要明确最小修改和可见验收结果。
- 不修改综合 RTL/寄存器合同，不把 GUI 仿真称为真实 DDR/板端验证。

## Contributions

- 将整帧 testbench 的输入/期望/RTL 输出目录改为 `VECTOR_DIR_<path>` plusarg 可配置，默认仍兼容批处理目录。
- 一键脚本显式传入同一 plusarg，使 GUI 和批处理走同一种已验证路径机制；文档补充 GUI Simulation Settings 和等价 Tcl 属性写法。
- 梳理昨日工程的最小改动：保留两份 Design Sources，新增整帧 Simulation Source、切换 simulation top、生成向量、设置 XSim More Options、Run All、渲染输出图。

## Decisions and Adoption

- 不要求重建 IP、Block Design 或修改综合 RTL。旧 2x2 testbench 可保留但不作为当前 simulation top。
- GUI 工程只用于仿真，不把工程生成目录提交进正式 `ip_repo`；后续建议把临时 Vivado 工程放在忽略的 `build/` 下。

## Commands and Tools

- `xsim.bat -help`：确认 2022.2 提供 `--testplusarg`。
- 多次最小 XSim 命令核对参数格式；记录失败的等号形式和通过的下划线分隔形式。
- `powershell -ExecutionPolicy Bypass -File .\scripts\run_ip_frame_demo.ps1 -SkipPackageCheck`：用显式 `VECTOR_DIR_../ip_frame_vectors` 完整重跑。

## Validation and Evidence

- Vivado 2022.2 编译/展开通过；XSim 日志显示 `INFO full-frame vector directory: ../ip_frame_vectors`。
- 灰度/二值各 76,800 像素再次通过，Python 参考差异均为 0；输出图哈希保持 `d677a98e8e7a4c870aaf3e89df69c21248cfd9ae2089a69694ffd63e4c1fdaaa`。
- 本轮没有重新执行综合、板端或真实 DDR/VDMA。

## Errors and Corrections

- 首先尝试 XSim 常见写法 `-testplusarg VECTOR_DIR=...`，XSim 2022.2 在运行 RTL 前报 `Expected a switch`；`--testplusarg=...` 也失败。改为 testbench 匹配 `VECTOR_DIR_%s`、命令传 `-testplusarg VECTOR_DIR_<path>` 后复测通过。

## Files Changed

- `blackboard-writing-enhance/tb/tb_enhance_axis_ip_frame.sv`
- `blackboard-writing-enhance/scripts/run_ip_frame_demo.ps1`
- `blackboard-writing-enhance/docs/pl_full_frame_ip_loopback.md`
- `project_workspace/PROJECT_STATE.md`、`project_workspace/ai/INDEX.md`、本会话记录

## Remaining Work

- 用户在昨日 GUI 工程中按步骤运行并反馈 Tcl Console/波形；若工程字段名称因布局不同，再按截图定位。
- 真实板级工作仍按 D-012 执行。

## Handoff Notes

- GUI XSim More Options 使用 `-testplusarg VECTOR_DIR_E:/code/fpga-competition/blackboard-writing-enhance/build/ip_frame_vectors`，必须用正斜杠，`VECTOR_DIR_` 后无等号。
- 仿真顶层为 `tb_enhance_axis_ip_frame`，不是昨日的 `tb_enhance_axis_ip`。点击 Run All 才能完成约 2.1 ms 的两帧仿真。
