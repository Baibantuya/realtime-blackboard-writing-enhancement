# AI Session: 2026-09-18-001-day2-pl-protocol-and-reset

- Date: 2026-09-18
- Operator: Codex
- AI product/model: Codex
- Participants: 用户（成员2）；Codex（实现与验证）
- Objective: 完成第二天 PL 核工作：复位、帧边界和错误重同步，并扩展 AXIS 自检。
- Status: Completed
- Report candidate: no
- Related commits: none
- Related files: `blackboard-writing-enhance/rtl/enhance_axis.sv`, `blackboard-writing-enhance/tb/`

## Context Read

- 已依次读取根目录 AGENTS.md、AI_DEVELOPMENT_POLICY.md、PROJECT_STATE.md、DECISIONS.md、INDEX.md，最近 Day 1 会话和当前 Git/RTL/testbench。

## Task and Constraints

- 保留 Day 1 尚未提交的用户分支工作；新项目成果写新仓库，内部流水写根目录 `project_workspace/`。

## Contributions

- `enhance_axis.sv` 增加锁存宽高、逐行 TLAST/TKEEP 检查、异常帧丢弃和 SOF 重同步；增加粘滞错误、错误事件计数、完整输出帧计数。低有效同步复位清除半帧及输出状态。
- 更新原白板图像 testbench 的配置与状态检查，新增小尺寸定向协议 testbench；覆盖孤立像素、提前/缺失 TLAST、错误 TKEEP、非法尺寸、帧中 SOF、输出背压期间复位、恢复及 1×1 帧。
- 新增协议说明与独立综合脚本；在当前规划的 ZCU104 器件上执行无约束非工程综合。

## Decisions and Adoption

- 采用 D-009 协议错误合同：坏帧检测后丢弃输入直到 SOF，但流式核已输出的部分像素只能由 PS/VDMA 侧丢弃对应缓冲。
- `frame_count` 在完整帧最后一个输出像素握手时增长；`error_count` 按异常事件饱和计数；物理 AXI4-Lite 寄存器和板端恢复尚未实现。
- 综合只用于确认可综合与记录单核资源，未把无约束综合报告当作实现时序或板端性能。

## Commands and Tools

- `xvlog.bat -sv -work xil_defaultlib ../../rtl/enhance_axis.sv ../../tb/tb_enhance_axis.sv ../../tb/tb_enhance_axis_protocol.sv`
- 分别对 `tb_enhance_axis`、`tb_enhance_axis_protocol` 执行 `xelab.bat`，再用 `xsim.bat -runall`；真实图像随机背压种子为 20260917。
- `vivado.bat -mode batch -source ../../scripts/synth_day2.tcl -nojournal -nolog`，工作目录为 `blackboard-writing-enhance/build/synth`。
- Python参考/向量生成和完整复现顺序见 `blackboard-writing-enhance/docs/pl_day2_protocol.md`。

## Validation and Evidence

- 原白板图像回归：三张现成照片各二值化与旁路，共六组，每组 3072 像素，xsim 2022.2 均 PASS，随机输出背压种子 20260917；同时检查 `frame_count=1,error_count=0`。
- 定向协议/复位：`tb_enhance_axis_protocol_sim` 在 xsim 2022.2 输出 `PASS day-2 protocol/reset cases`。
- 无约束 OOC 综合：Vivado 2022.2 对 `xczu7ev-ffvc1156-2-e` 成功，报告 253 CLB LUT、180 CLB 寄存器、0 BRAM、0 DSP。`blackboard-writing-enhance/build/synth/utilization.rpt` SHA-256 `6a8a06b710b396f382384a23f0f3f5e7769ee4b80048019de7121e0b0b625687`；此生成路径被 Git 忽略，可通过脚本重建。
- 未执行：时钟约束、实现后时序、完整 Overlay、USB/DMA/显示及实物上板测试。

## Errors and Corrections

- Vivado 启动时提示本地 Tcl store 不可写，自动使用安装目录；综合仍完成。综合另有 parallel synthesis criteria 未达到的普通警告；未影响完成状态。
- Day 1 的原 testbench 未连接新增宽高/状态端口；已更新并重跑六组回归，全部通过。

## Files Changed

- 新仓库：`rtl/enhance_axis.sv`、`tb/tb_enhance_axis.sv`、`tb/tb_enhance_axis_protocol.sv`、`scripts/synth_day2.tcl`、`docs/pl_day1_interface.md`、`docs/pl_day2_protocol.md`、`进度记录/progress_and_decisions.md`。
- 根目录内部：`project_workspace/DECISIONS.md`（D-009）、`project_workspace/PROJECT_STATE.md`、`project_workspace/ai/INDEX.md`、本会话记录。

## Remaining Work

- 与成员1确认 PS/VDMA 缓冲与错误计数关联及超时恢复；与成员3独立核对整数参考。
- 增加 AXI4-Lite 控制封装/配置版本；实际板卡时钟约束和实现后时序需再验证。
- USB 摄像头到货后继续固定帧 DMA 闭环、采集和显示集成。

## Handoff Notes

- 当前分支 `b/pl-lower-pipeline`，本次未提交/推送。Day 2 复现入口为 `blackboard-writing-enhance/docs/pl_day2_protocol.md`。`build/` 生成目录被忽略，脚本可重建向量和综合报告。

## Collaboration Map

| Participant | Assigned task | Input | Output | Verification | Accepted by |
|---|---|---|---|---|---|
| 用户/成员2 | 审核 PL 接口和后续板端交接 | Day 1 核与当前任务 | 待审核 Day 2 结果 | Codex 已完成本机仿真/综合 | 待用户审核 |
| Codex | 协议 RTL、testbench、综合检查 | Day 1 代码/数据 | 本次文件与记录 | xsim 和 OOC synth | 待用户审核 |
| 成员1、成员3 | 后续 DMA/参考复核 | 待交接 | 本次未参与 | 未执行 | 未定 |

## Conflicts and Resolution

- 当前根目录旧规范仍指向原 `whiteboard/`；用户已明确将新仓库作为正式项目且记录留根目录，本次遵从该已授权布局。

## Integration Result

- PL 单核达到 Day 2 仿真与可综合性检查门槛；PS/PL 实际 DMA 和显示闭环未开始。
