# AI Session: 2026-09-21-004-kv260-camera-display-reassessment

- Date: 2026-09-21
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 因目标板切换为 KV260，重新评估小眼睛 OV5640+40-pin FMC 转接、MIPI 摄像头/转 FMC、USB 摄像头（标称 160 mA）和视频输出路线，并形成可执行选择。
- Status: Completed
- Report candidate: No
- Related commits: None (assessment/documentation only)
- Related files: `project_workspace/PROJECT_STATE.md`, `project_workspace/DECISIONS.md`, `project_workspace/ai/INDEX.md`

## Context Read

已阅读根目录 `AGENTS.md`、AI 开发政策、项目状态、决策流水、索引，以及与摄像头/输出直接相关的近期会话：`2026-09-20-006-zcu104-taobao-camera-options.md`、`2026-09-20-001-hdmi-demo-video-output-review.md`、`2026-09-19-005-zcu104-usb-overcurrent-manual-review.md`、`2026-09-19-006-camera-display-selection.md`。外层工作区不是 Git 仓库；正式仓库 `blackboard-writing-enhance/` 的状态将在结论前复核。

## Task and Constraints

- 板卡由 ZCU104 改为 KV260；不得把 ZCU104 的 FMC VADJ、D-PHY 管脚或 HDMI 结论直接套用。
- 需要同时评估电气安全、接口机械适配、参考设计/软件栈、现有 RTL 复用、首版风险及输出闭环。
- 本次为资料核验与工程选择；不进行未获授权的硬件接线、上板或采购。

## Contributions

- 核验 AMD UG1089/DS986：KV260 有 J7/J8 两个 IAS MIPI 接口、J9 树莓派 15-pin 双 lane MIPI CSI-2、J5 HDMI 输出、J6 DP 输出以及四个 USB3 端口；没有 FMC 插槽。J9 电源为 3.3 V；USB 为 5 V/900 mA 每口、全部端口合计 2.1 A。
- 因 KV260 无 FMC，判定小眼睛 Double_OV5640 的 40-pin→MES-FMC-LPC-IO 转接和 MIPI→FMC 方案在机械层即不可直接落地；不推荐通过 Pmod 等低速扩展接口拼接 8-bit DVP。
- UG1089 将 Raspberry Pi Camera Module v2 列为 KV260 功能验证外围设备；公开 KV260/PYNQ 资源可见树莓派相机 MIPI 约束与 CSI-2 RX 案例。因此推荐 J9 + IMX219 作为正式摄像头输入，代价是新建 CSI-2/RAW Bayer/最小 ISP 前端。
- AMD Smart Camera 资料将 Logitech BRIO 列为支持 USB 摄像头，并支持 HDMI/DP 显示。对用户已有标称 160 mA 的 UVC 摄像头，电流预算支持先做 USB bring-up，但实际启动浪涌、UVC格式、帧率和解码负载仍必须实测。
- KV260 官方 Vitis base platform 与 Smart Camera 文档均明确支持 DisplayPort 和/或 HDMI 显示；推荐优先 J5 HDMI、现场无 HDMI 显示器时使用 J6 DP。现有 Artix-7 TMDS demo 及 ZCU104 的器件/XDC/物理层不能迁移。

## Decisions and Adoption

形成 D-024 的 Codex 工程建议，待项目组确认：USB UVC（如现有相机通过枚举和连续性测试）作为最短端到端演示输入，J9 + Raspberry Pi Camera Module v2 (IMX219) 作为正式 MIPI 方案，J5 HDMI 作为默认显示输出；DP 是等价备选。旧 FMC 物料不进入 KV260 首版。

## Commands and Tools

- 阅读项目规范、状态、决策、索引和四份最近相关会话；检查正式仓库 Git 状态。
- 检索并阅读 AMD 官方 UG1089 接口/电源/外围设备/Vitis platform 页面、AMD Smart Camera 公开仓库，以及 KV260 的 MIPI CSI-2 参考约束资料。

## Validation and Evidence

- 资料验证：UG1089 Interfaces 明确 J5 HDMI、J6 DP、J7/J8 IAS（四 lane）、J9 RPi（两 lane）及四 USB3；UG1089/DS986 给出 USB 900 mA/端口、2.1 A合计和 RPi 相机接口 3.3 V；UG1089 Supported Peripherals 列有 RPi Camera Module v2；UG1089 Vitis Platforms 和 Smart Camera README 说明 DP/HDMI 显示与 USB 摄像头支持。
- 未执行：KV260 开机、UVC 枚举、160 mA 相机启动电流/浪涌测量、MIPI 传感器 I2C/CSI-2 采集、RAW/ISP适配、Vivado/Vitis 构建、AXIS 接入、HDMI/DP显示、帧率/功耗/连续300帧测试。

## Errors and Corrections

- 纠正“换板后继续用小眼睛 40-pin 转 FMC”这一隐含前提：KV260 载板根本没有 FMC；原先 ZCU104 的 VADJ/电平转换结论仍可作为旧板安全资料，但不构成 KV260 连通方案。
- 160 mA 仅说明标称工作电流低于 KV260 USB 预算，不能证明线缆、启动浪涌、相机是否合规或 UVC 视频格式可用，因此未把它记录为上板通过。

## Files Changed

- `project_workspace/ai/sessions/2026-09-21-004-kv260-camera-display-reassessment.md`
- `project_workspace/ai/INDEX.md`
- `project_workspace/DECISIONS.md`
- `project_workspace/PROJECT_STATE.md`

## Remaining Work

1. 到板后先以已知正常 USB 相机或该 160 mA UVC 单独接入，记录 `lsusb`、`v4l2-ctl --list-formats-ext` 和连续 300 帧结果；优先确定 YUYV 或 MJPEG的实际模式。
2. 采购/准备 RPi Camera v2 (IMX219)，从 AMD/社区 KV260 J9 MIPI 基线建立 CSI-2 RX + Bayer→GRAY/BGRX 的最小链路，再连接 `enhance_axis_ip`。
3. 先用 J5 HDMI 色条或官方显示路径证明输出，再实现 VDMA/帧缓冲/AXIS 连接；J6 DP 仅作显示器/线缆不可用时替换。

## Handoff Notes

结论是“USB 先跑通、J9 IMX219 做正式输入、HDMI 默认输出”，而非声称任一路已在 KV260 运行。DVP OV5640只有在团队决定投入定制采集硬件时才重新评估。
