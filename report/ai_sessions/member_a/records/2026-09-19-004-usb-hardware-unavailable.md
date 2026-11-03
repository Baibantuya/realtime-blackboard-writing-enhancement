# AI Session: 2026-09-19-004-usb-hardware-unavailable

- Date: 2026-09-19
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 根据用户报告的 ZCU104 USB 损坏重新确定摄像头输入路线
- Status: Completed
- Report candidate: No
- Related commits: None（外层工作区不是 Git 仓库）
- Related files: `project_workspace/DECISIONS.md`, `project_workspace/PROJECT_STATE.md`

## Context Read

已按规定顺序读取入口规范、AI 政策、项目状态、决策流水、AI 索引和最近相关记录，并检查 Git 状态。此前旧 MIPI/USB 比较记录已被用户要求的记录重置删除，不再存在；以当前状态和决策为准。

## Task and Constraints

用户报告项目板卡 USB 接口损坏。该硬件事实尚未由本 AI 实物核验，但必须作为当前工程约束，不能继续把 UVC 摄像头作为可交付保底链路。

## Contributions

- 区分输入接口故障与现有 PL 算法核：固定帧、DDR/VDMA 行为模型、AXIS IP 工作不受影响。
- 将摄像头路线重新排序为 MIPI-FMC 优先候选、HDMI 许可解决后候选、离线文件/测试图仅用于开发验证。
- 保留输入源无关的 BGRX AXIS 核合同，通过前端适配层隔离摄像头接口变化。

## Decisions and Adoption

采纳 D-014：在用户报告 USB 硬件损坏的当前板卡上，停止将 USB UVC 作为系统 demo 或比赛保底输入；MIPI-FMC 成为首要实时摄像头候选，但在具体子卡和传感器完成兼容性核验前仍不宣称可用。

## Commands and Tools

读取项目规范、状态、决策、索引和相关记录；未运行硬件诊断或构建命令。

## Validation and Evidence

- USB 损坏来自用户报告，AI 未进行电气或板端枚举验证。
- 当前 PL IP 已通过的仿真和无约束综合均不依赖 USB，成果继续有效。
- MIPI-FMC、HDMI 和实体板均未接线、综合、实现或上板验证。

## Errors and Corrections

此前 D-002 至 D-005 以 USB 可用为前提；该前提现已失效。修正为停止规划 USB 摄像头测试，不删除历史决策，以便保留变更原因。

## Files Changed

- `project_workspace/ai/sessions/2026-09-19-004-usb-hardware-unavailable.md`
- `project_workspace/DECISIONS.md`
- `project_workspace/PROJECT_STATE.md`
- `project_workspace/ai/INDEX.md`

## Remaining Work

- 确认损坏的是 ZCU104 的 USB Host 数据口/供电/PHY，而不是线材、OTG 模式或单个摄像头兼容问题。
- 在采购前冻结具体 MIPI-FMC 子卡和传感器型号，核对 ZCU104 FMC LPC、电压、lane、时钟、I2C、像素格式与参考工程。
- 板卡到手后仍先做 DDR 固定帧回环，再单独 bring-up MIPI 输入。

## Handoff Notes

不要让摄像头变更阻塞现有形态学和 AXIS 流水线开发。实时摄像头接入改由独立前端适配层完成，输出继续遵守现有 PL 像素合同。
