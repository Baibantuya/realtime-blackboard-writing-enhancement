# AI Session: 2026-09-20-006-camera-vin-vs-dovdd

- Date: 2026-09-20
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 澄清 MES-FMC-LPC-IO 的40pin电源、ZCU104 VADJ和OV5640 DOVDD之间的关系
- Status: Completed
- Report candidate: No
- Related commits: None
- Related files: `blackboard-writing-enhance/docs/ov5640_single_camera_integration.md`, internal state/decision records

## Conclusion

- `VADJ_FMC=1.8 V` 只给 ZCU104 PL Bank 67/68 供电，不会把 MES-FMC-LPC-IO 的40pin电源脚改为1.8 V。
- 子卡官方手册固定 Pin2 为A5V0、Pin39/40为A3V3；摄像头模组主输入再通过板上稳压/电源结构产生OV5640所需的AVDD、DVDD和DOVDD。
- OV5640裸芯片的DOVDD允许约1.7–3.0 V、推荐1.8 V，不代表具体双目模组已经把DOVDD及SCCB上拉设置为1.8 V，也不代表可以把整个模组的5 V/3.3 V输入替换成1.8 V。
- v2.3 FDC 将DVP、SCCB和reset全部约束为LVCMOS33，是该配套模组按3.3 V I/O使用的直接工程证据。除非原理图或断开ZCU104后的实测证明DOVDD/SCCB上拉为1.8 V，否则仍按不兼容处理。

## Evidence

- MES-FMC-LPC-IO V1.1：40pin Pin2=+5V、Pin39/40=+3.3V，其余为FPGA I/O；Bank供电必须与外设电平匹配。
- OV5640 DVP模组应用指南：AVDD约2.8 V、DVDD约1.5 V、DOVDD范围约1.7–3.0 V并推荐1.8 V。
- v2.3 Pango约束：所有 `cmos2_*` 信号为3.3 V/LVCMOS33。

## Handoff Notes

决定能否直连的测量对象是摄像头DVP输出高电平和SCCB上拉电压，而不是FMC VADJ或40pin主电源脚。测试时先与ZCU104数据线隔离。
