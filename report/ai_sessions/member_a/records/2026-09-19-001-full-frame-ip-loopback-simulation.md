# AI Session: 2026-09-19-001-full-frame-ip-loopback-simulation

- Date: 2026-09-19
- Operator: Codex
- AI product/model: Codex
- Participants: 用户（成员2）；Codex（设计、实现与验证）
- Objective: 在无板条件下扩展并验证可直接承接 PS/DDR→PL→PS/DDR 上板流程的整帧 IP 回环。
- Status: Completed
- Report candidate: no
- Related commits: none
- Related files: `blackboard-writing-enhance/tb/tb_enhance_axis_ip_frame.sv`, `blackboard-writing-enhance/scripts/run_ip_frame_demo.ps1`, `blackboard-writing-enhance/docs/pl_full_frame_ip_loopback.md`, `blackboard-writing-enhance/evidence/ip_frame_loopback/`

## Context Read

- 依次重读根目录 `AGENTS.md`、AI 开发规范、项目状态、决策流水、索引、最近 IP 会话记录，检查当前分支与未提交修改。
- 阅读仓库 README、接口/定点约定、验收规则，以及 Day 3 整图向量、testbench、渲染脚本和现有 AXI4-Lite＋AXIS IP 包装。

## Task and Constraints

- 用户要求按“马上能上板”的节奏扩展 PS→PL→PS 视频流处理，同时当前无板，优先运行 simulation；若真实 DDR 路径无法运行，则至少完整处理一张图并给出选择。
- 不伪造真实 DDR、VDMA、PS 驱动、板端显示、时序或硬件结果。
- 正式成果写入 `blackboard-writing-enhance/`，完整内部记录保留在外层 `project_workspace/`。

## Contributions

- 新增整帧 testbench，以 AXI4-Lite task 模拟 PS 配置和状态读取，以互相独立的 SystemVerilog 数组模拟输入/输出 DDR buffer，以握手循环模拟 MM2S/S2MM；实际被测对象是正式 `enhance_axis_ip` 包装。
- 对 S2MM 端施加确定性随机背压，检查背压期间输出稳定、每行 TLAST、帧首 TUSER、TKEEP、像素数量、帧计数和错误状态。先灰度再二值化，帧间通过 AXI4-Lite 切换模式。
- 新增一键脚本，复用现有实拍白板数据和 Python 定点参考，运行 xsim、重建 RTL 返回 PNG、重新打包 IP 并在全新 Vivado 工程中执行目录/实例化/目标生成检查。
- 新增上板替换映射和固定图首测顺序文档；生成可见证据 `evidence/ip_frame_loopback/comparison.png`。

## Decisions and Adoption

- 采用 D-012：IP 保持 AXI4-Lite＋双 AXIS 的可复用流处理边界，不在像素 IP 内实现 DDR 控制器/VDMA。无板阶段用行为模型覆盖系统侧接口；真实 DDR/VDMA 仍须上板验证。
- 当前能够比单纯算法核整图回放更进一步：整图必须经过 AXI4-Lite 包装和双 AXIS。但不把行为数组描述成真实 DDR，也不据随机背压周期数声称性能。

## Commands and Tools

- `powershell -ExecutionPolicy Bypass -File .\scripts\run_ip_frame_demo.ps1 -SkipPackageCheck`：首次修正脚本参数后通过整帧仿真和图像重建。
- `powershell -ExecutionPolicy Bypass -File .\scripts\run_ip_frame_demo.ps1`：完整整帧仿真、图像重建、IP 重打包及目录烟测通过。
- `powershell -ExecutionPolicy Bypass -File .\scripts\run_ip_checks.ps1 -SkipSynthesis`：原 AXI4-Lite/2x2/错误路径回归及 IP 目录检查通过。
- `git diff --check`：通过。

## Validation and Evidence

- Vivado 2022.2 xsim：灰度帧 76,800 像素，104,880 个含随机反压仿真循环；二值帧 76,800 像素，104,876 个循环；均完成 MM2S/S2MM 模型回环，无协议/状态错误。
- 两种 RTL 返回内存与 Python 整数参考逐像素差异均为 0。`results.json` 中灰度/二值 RTL mem SHA-256 分别为 `da8f60312db2814fb6181147cedf46e80f874273fae673579e7370b63465afbd`、`0639ec17a748c6bb1e42b3eae7111e681dd3a9ebc0443f1141fb3a1654b66da3`。
- 可见图 `blackboard-writing-enhance/evidence/ip_frame_loopback/comparison.png` SHA-256 `d677a98e8e7a4c870aaf3e89df69c21248cfd9ae2089a69694ffd63e4c1fdaaa`，人工打开确认包含输入、RTL 灰度和 RTL 二值三栏。
- IP Packager `ipx::check_integrity` 通过；全新工程发现唯一 VLNV `baibantuya.github.io:user:enhance_axis_ip:1.0`，实例化并生成 synthesis/simulation target。原包装定向 testbench仍输出 `PASS board-test IP AXI4-Lite/AXIS/status cases`。
- 未执行：真实 Zynq PS、DDR/CMA、AXI VDMA、cache 同步、驱动、中断、物理地址、带约束实现/时序、bitstream、板端显示或摄像头。

## Errors and Corrections

- 首次运行新脚本时，参数列表中误留无效的 `[ValidatePackage]` 类型声明，PowerShell 在进入仿真前退出；删除该行后完整重跑通过。该失败没有产生虚假的仿真结果。

## Files Changed

- 正式仓库：`tb/tb_enhance_axis_ip_frame.sv`、`scripts/run_ip_frame_demo.ps1`、`docs/pl_full_frame_ip_loopback.md`、`docs/pl_board_test_ip.md`、`evidence/ip_frame_loopback/`、`进度记录/progress_and_decisions.md`；重跑打包更新 `ip_repo/enhance_axis_ip_1_0/` 生成元数据。
- 内部协作：`project_workspace/DECISIONS.md`（D-012）、`PROJECT_STATE.md`、`ai/INDEX.md`、本会话记录。

## Remaining Work

- 板卡到手后由成员1建立 PS/AXI interconnect/VDMA/clock/reset BD，确认真实器件并执行实现时序；成员2审核 AXIS sideband 和寄存器连接。
- 以同一固定图执行真实 DDR 双 buffer 回环：先 S2MM 后 MM2S，cache 同步、双 DMA 完成/超时、状态计数、逐像素/CRC；通过后再接显示与连续摄像头。
- 当前算法仍只含 bypass、灰度、二值化；5x5 形态学和照度增强未实现。

## Handoff Notes

- 仓库根运行 `powershell -ExecutionPolicy Bypass -File .\scripts\run_ip_frame_demo.ps1` 可重现完整无板回环；最终图位于 `evidence/ip_frame_loopback/comparison.png`。
- testbench 的 DDR/VDMA 是行为模型，不是 AMD VDMA 仿真模型。未来真实系统仍使用同一 `enhance_axis_ip`，替换模型即可，不能沿用本次周期数作为板端吞吐。
- 本轮未修改 `rtl/enhance_axis.sv` 或 `rtl/enhance_axis_ip.sv` 的逻辑，因为现有正式 IP 已具备 PS 控制和流入/流出接口；扩展的是整帧系统侧验证与上板交接，不额外引入不属于处理核的 DDR 端口。
