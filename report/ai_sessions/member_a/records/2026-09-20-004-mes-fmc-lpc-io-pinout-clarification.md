# AI Session: 2026-09-20-004-mes-fmc-lpc-io-pinout-clarification

- Date: 2026-09-20
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 澄清 FMC 标准定义、MES-FMC-LPC-IO 固定布线和 ZCU104 电气兼容性的区别
- Status: Completed
- Report candidate: No
- Related commits: None
- Related files: `blackboard-writing-enhance/docs/ov5640_single_camera_integration.md`, internal decision/state records

## Context Read

沿用上一会话已完成的必读上下文，并复核 v2.3 FDC、官方 MES-FMC-LPC-IO V1.1 手册和 ZCU104 UG1267。

## Contributions

- 确认具体子卡型号为小眼睛科技 `MES-FMC-LPC-IO`，其 FMC→J2/J3 40pin 布线为固定且公开，不需要再等待子卡原理图才能确定逻辑信号映射。
- 由 v2.3 的 PG2L200H 封装管脚与子卡手册对照，确认当前 `cmos2_*` 使用 J2，并整理 14 根 DVP/SCCB/reset 信号的 J2 pin 与 FMC LA 名称。
- 区分 FMC 标准、载板 FPGA package pin、子卡布线和 I/O 电压四个层次；接口编号固定不等于电压自动兼容。
- 纠正上一记录中“需要由 FPGA 产生 24 MHz XCLK”的过早假设：v2.3 顶层未暴露 XCLK 端口，当前不为其分配 FMC 管脚，待实物/模组资料确认是否板载时钟。

## Validation and Evidence

- MES-FMC-LPC-IO 官方手册列出 J2 pin→FMC LA 的完整表，并明确其 I/O 电平由载板 FPGA Bank 供电决定、必须与外设一致。
- v2.3 FDC 的 `cmos2_*` PG2L200H 管脚逐项可在 J2 表中匹配；全部声明为 3.3 V/LVCMOS33。
- ZCU104 UG1267 说明 FMC LPC 位于 VADJ_FMC 域，支持 1.2/1.5/1.8 V而非3.3 V；因此映射已知，但直接电气兼容性仍不成立。

## Errors and Corrections

- 更正“转接板 pin map 未知”：具体型号确认后，J2 映射已知。
- 更正“必须生成 24 MHz XCLK”：v2.3 顶层没有该外部端口，目前仅保留为待实物确认事项。

## Remaining Work

1. 将已知 FMC LA 名称对应到 ZCU104 FMC LPC 的 package pins，形成正式板级 XDC。
2. 解决或确认 3.3 V 相机输出与 ZCU104 1.8 V FMC Bank 之间的电平兼容；接口固定不豁免此项。
3. 上板后确认摄像头模块时钟来源、SCCB 上拉电压和 J2 插接方向。

## Handoff Notes

映射问题已经收敛；当前唯一不能仅靠约束文件解决的是电压域。
