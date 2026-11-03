# AI Session: 2026-09-21-005-kv260-csi2-camera-and-hdmi-ip

- Date: 2026-09-21
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 比较 KV260 可用的约 5 MP（2592×1944）、Raspberry Pi Camera v2（IMX219，8 MP）和 v3（IMX708，约 11.9 MP）CSI-2 相机，并审查 `24_hdmi_colorbar` 能否解决 KV260 HDMI 输出。
- Status: Completed
- Report candidate: No
- Related commits: None
- Related files: `24_hdmi_colorbar/`, `project_workspace/PROJECT_STATE.md`, `project_workspace/DECISIONS.md`, `project_workspace/ai/INDEX.md`

## Context Read

已按项目规范阅读入口规范、AI 开发政策、项目状态、决策流水、索引和最近的 `2026-09-21-004-kv260-camera-display-reassessment.md`；已检查正式仓库 Git 状态和 `24_hdmi_colorbar` 的关键 RTL/XDC/工程描述。

## Task and Constraints

- 只有分辨率不足以证明 CSI-2 模组能接 J9；必须以传感器料号、15-pin pinout、I2C/供电、lane rate、驱动及初始化表判断。
- 本次只做评估，不假称已在 KV260 建立 HDMI 或相机采集。

## Contributions

- 对照 Raspberry Pi 官方硬件表，确认 5 MP 相机为 OV5647、2592×1944（并非“1944×2552”），已停产；v2 为 IMX219、3280×2464、8 MP；v3 为 IMX708、4608×2592、11.9 MP、RAW10、相位自动对焦。v3 的 11.9 MP 不是 11.2 MP。
- 对照 AMD UG1089，J9 的功能验证外围设备只列 Raspberry Pi Camera Module v2，因此 v2 是当前唯一具备明确 KV260 板级验证的三者。
- 静态检查 `24_hdmi_colorbar`：`hdmi_color.xpr` 目标是 `xc7a35tfgg484-2`；`serializer_10_to_1.v` 实例化 `OSERDESE2`；XDC 锁定 Artix-7 板级 TMDS_33 管脚。因此不兼容 KV260 的 K26/板载 HDMI 路由。
- KV260 J5/J6 是板载 HDMI/DP 输出；AMD 官方 Vitis platform、Smart Camera 和 Kria-PYNQ 都有 HDMI/DP显示路径。因此输出应在 KV260 设计中以 AXI video + VDMA/frame buffer + 显示/KMS基线完成，而不是自行从 PL 生成 TMDS。

## Decisions and Adoption

形成 D-025 Codex 工程建议，待团队确认：购买 RPi Camera v2 (IMX219) 作为首版 CSI-2 相机；Camera v3 (IMX708) 仅在确需自动对焦和更大视场/裁切细节、并愿意承担新驱动与 RAW10/Quad-Bayer 适配时升级。HDMI 输出通过 KV260 板载显示链路实现；`24_hdmi_colorbar` 仅保留学习参考。

## Commands and Tools

- Read local project context and inspect `24_hdmi_colorbar` RTL/XDC/Vivado project metadata.
- Read AMD UG1089/Kria-PYNQ/Smart Camera resources and Raspberry Pi official camera documentation.

## Validation and Evidence

- 静态代码验证已执行：工程 part、XDC I/O 标准和 7-series 原语均可定位。
- 文档验证已执行：AMD 已验证 J9 的 Camera v2；Raspberry Pi 官方确认三款候选的型号、分辨率、视频模式、焦点特性与 v3 RAW10。
- 未执行：KV260 synthesis/implementation、HDMI 或 DP 显示、IMX219/OV5647/IMX708 I2C 驱动、CSI-2采集、VDMA/DRM接入、自动对焦、帧率、图像质量或连续性测试。

## Errors and Corrections

- 将用户给出的 `1944×2552` 归一为官方列出的 `2592×1944`；若用户所指是另一个非 OV5647 模组，需要补充精确传感器料号后重新评估，不能仅按分辨率套用本结论。
- 纠正“有 HDMI 色条 RTL 就能在 KV260 输出 HDMI”：该代码是 Artix-7 直接 TMDS 发射器，而 KV260 的输出连接结构和器件原语不同。

## Files Changed

- `project_workspace/ai/sessions/2026-09-21-005-kv260-csi2-camera-and-hdmi-ip.md`
- `project_workspace/ai/INDEX.md`
- `project_workspace/DECISIONS.md`
- `project_workspace/PROJECT_STATE.md`

## Remaining Work

1. 团队确认是否需要“自动对焦/远距离裁切”足以抵消 v3 的软件风险；否则订购 IMX219 v2。
2. 在 KV260 首先运行官方/PYNQ HDMI 或 DP 基线，再建立 VDMA/frame-buffer→DRM显示。
3. 从 IMX219 MIPI RX/RAW Bayer最小链路开始接入 `enhance_axis_ip`；真实输入分辨率先降至720p或1080p再作性能验收。

## Handoff Notes

相机购买应写明“官方 Raspberry Pi Camera Module v2 / IMX219、15-pin”，避免买到只同尺寸但没有传感器驱动资料的兼容模块。若考虑 v3，应先把它单列为驱动/自动对焦验证任务，而不阻塞首版演示。

## Follow-up: Camera v2 Focus Clarification

- Raspberry Pi 官方当前硬件表给出 IMX219 v2 镜头焦距 3.04 mm、F/2.0、水平视场 62.2°，标称对焦范围约 10 cm 至无穷远；这里的“焦距”固定，不能通过软件改变。
- 官方资料对焦描述有“Fixed-focus lens”和“Adjustable”两种表述。工程上按**无电机、无 I2C/软件自动对焦，出厂预调焦**处理；其镜头组件可在拆除/松开固定胶后用机械旋转方式重新手动调焦，但会改变出厂标定，且并非可靠的运行时调焦方案。若白板与相机距离会频繁变化，应选 Camera v3 的电动自动对焦，或固定安装距离后一次性手调 v2。
