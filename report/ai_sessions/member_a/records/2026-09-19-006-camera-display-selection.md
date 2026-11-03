# AI Session: 2026-09-19-006-camera-display-selection

- Date: 2026-09-19
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 比较 CS500 与 IMX415 MIPI 摄像头，并确定 ZCU104 显示和交互方式
- Status: Completed
- Report candidate: No
- Related commits: None（外层工作区不是 Git 仓库）
- Related files: `project_workspace/PROJECT_STATE.md`, `project_workspace/DECISIONS.md`

## Context Read

已按规定顺序读取入口规范、AI 政策、项目状态、决策、索引、最近 USB 过流会话和 Git 状态。

## Task and Constraints

这是采购决策。需核对 `CS500` 的确切含义和两种相机模组的接口/参考设计，不能只按传感器像素参数选择。显示需考虑 ZCU104 的现成 DisplayPort、FMC 被摄像头占用、USB 过流未解决以及触摸交互是否确有必要。

## Contributions

- 识别用户所称 `CS500` 很可能是米联客 `CAM001-CS500`，其传感器需卖方书面确认是否为思特威 `SC500AI`，不能仅凭商品简称冻结规格。
- 比较 SC500AI 级 5MP 1620p 方案与 IMX415 8.46MP 4K 方案；结合项目当前 720p30 必达、1080p30 扩展和白板场景，推荐优先低带宽的 CS500 套件。
- 指出两者均通常输出 RAW Bayer，现有 BGRX AXIS 核前需增加 CSI-2 接收和最小 ISP/格式适配；首版可用线性模式，避免多曝光 HDR 增加复杂度。
- 比较 FMC 上的 MIPI-DSI/RGB 小屏与 ZCU104 原生 DisplayPort 外接显示器；推荐外接 DP 显示器，交互使用以太网 Web UI，不把触摸屏作为首版依赖。
- 形成采购前必须向卖方确认的 ZCU104 兼容性清单。

## Decisions and Adoption

提出 D-017 工程建议，尚待用户团队采纳：CS500 优先、IMX415 仅在明确需要 4K 细节且参考工程同等完整时采用；显示用 ZCU104 DisplayPort，首版不采购 MIPI 触摸屏。

## Commands and Tools

读取项目上下文；检索米联客 FMC-VID005/CAM001/CAM002 产品页、思特威 SC500AI 官方资料、Sony IMX415 官方资料和相关套餐信息。

## Validation and Evidence

- 米联客产品页/商品信息表明 FMC-VID005 套餐提供 CAM001-CS500、CAM002-IMX415 和 7 寸 MIPI 屏选项，但公开文字未证明 ZCU104/Vivado 2022.2 已验证。
- 思特威官方：SC500AI 为 5MP、16:9、1620p，强调高灵敏度和 HDR；产品 flyer 给出 2888x1628、2.0 um、MIPI RAW、1/2/4 lane、最高 60 fps。
- Sony 官方：IMX415 为 8.46MP、推荐 3840x2160、1.45 um、2/4 lane CSI-2、RAW10/RAW12，并支持裁剪/2x2 binning及多曝光/DOL HDR。
- ZCU104 本地 UG1267 已确认板载 PS DisplayPort 为 source-only，可作为不依赖 HDMI TX IP 的外接显示路线。
- 未采购、接线、综合、实现、验证 MIPI lane rate/ISP、显示或触摸。

## Errors and Corrections

避免仅以像素数判断：更高分辨率会增加 lane rate、像素时钟、ISP 和缓存压力；对当前 720p/1080p 白板处理，4K 的额外细节只有在镜头视场和 OCR/裁剪实测需要时才有价值。另纠正“RGB 小屏等于 MIPI 屏”的混用：并行 RGB、MIPI-DSI 和触摸 I2C/USB 是三条不同接口。

## Files Changed

- `project_workspace/ai/sessions/2026-09-19-006-camera-display-selection.md`
- `project_workspace/PROJECT_STATE.md`
- `project_workspace/DECISIONS.md`
- `project_workspace/ai/INDEX.md`

## Remaining Work

- 向卖方确认 CAM001 的确切传感器料号、镜头/FOV、Bayer 顺序、线性模式寄存器、lane rate和供电。
- 要求卖方提供 FMC-VID005 对 ZCU104 FMC LPC、VADJ=1.8 V、Vivado 2022.2 的 XDC/原理图/初始化源码/可综合工程；否则不采购。
- 确定产品是否必须完全脱离电脑独立操作；只有必须本机触摸交互时才重新评估 DSI 屏和触控控制器。

## Handoff Notes

现有 `enhance_axis_ip` 不因相机选择改变。相机前端负责把 RAW Bayer 转换为项目约定的 BGRX，或团队修订合同增加 Bayer/GRAY 入口；该接口变化必须在采购后、参考工程确认后冻结。
