# AI Session: 2026-09-20-005-zcu104-vadj-no-jumper

- Date: 2026-09-20
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 核实 ZCU104 是否可通过跳线或其他方式把 FMC VADJ 改为 3.3 V
- Status: Completed
- Report candidate: No
- Related commits: None
- Related files: `blackboard-writing-enhance/docs/ov5640_single_camera_integration.md`, internal decision/state records

## Context Read

沿用既有项目上下文，复核 ZCU104 UG1267 的 I/O Voltage Rails、FMC LPC 和 Board Power System 章节，并查阅公开的 ZCU104 VADJ 使用讨论。

## Conclusion

- ZCU104 没有用于选择 `VADJ_FMC` 的跳线帽。
- FMC LPC 的 PL Bank 67/68 由 IRPS5401 U180 的可编程 `VADJ_FMC` 供电，默认 1.8 V；官方有效值只有 1.2、1.5、1.8 V。
- PMBus、系统控制器/FSBL 或 USB005 可以在允许范围内改变/恢复 VADJ，但不能把这些 HP I/O Bank 变成 3.3 V，也不能解决 v2.3 `LVCMOS33` 相机信号的过压问题。
- 因此 OV5640＋MES-FMC-LPC-IO 不能作为 3.3 V 直连方案使用；必须增加电平转换，或确认并改造摄像头模组使全部 DVP/SCCB/reset 信号实际工作在 1.8 V。

## Validation and Evidence

- UG1267 Table 3-2：Bank 67/68 为 `VADJ_FMC`，出厂 1.8 V。
- UG1267 FMC LPC/Board Power System：有效 VADJ 值为 1.2/1.5/1.8 V；U180 IRPS5401 Phase D 产生该电源，可通过 PMBus 管理。
- 未执行硬件测量或上板连接。

## Handoff Notes

不再搜索跳线帽方案。后续硬件选择限定为主动电平转换或相机模组 1.8 V I/O 改造；在此之前不连接摄像头数据线。
