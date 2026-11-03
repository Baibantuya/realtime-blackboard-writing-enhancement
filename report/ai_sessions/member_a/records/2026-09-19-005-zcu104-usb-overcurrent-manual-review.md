# AI Session: 2026-09-19-005-zcu104-usb-overcurrent-manual-review

- Date: 2026-09-19
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 阅读本地 ZCU104 手册，解释 USB 摄像头接入后过流的板级机制与排查方向
- Status: Completed
- Report candidate: No
- Related commits: None（外层工作区不是 Git 仓库）
- Related files: `ug1267-zcu104-eval-bd.pdf`, `project_workspace/PROJECT_STATE.md`, `project_workspace/DECISIONS.md`

## Context Read

已按规定顺序读取入口规范、AI 政策、项目状态、决策、索引、最近 USB 故障记录和 Git 状态；已完整读取 PDF 技能说明。

## Task and Constraints

以工作区中的 `ug1267-zcu104-eval-bd.pdf` 为主要依据，查找 USB Host/OTG、VBUS 供电和过流相关设计。用户报告 USB 摄像头接上后过流，但尚无端口、指示现象和测量数据。

## Contributions

- 阅读 UG1267 第 35-37 页 USB0/J96、Figure 3-4 和第 68 页 LED 表。
- 确认 J96 的 VBUS 由 U121 MIC2544 高边可编程限流开关保护；过流或芯片热关断时开漏 FLG 点亮 DS51。
- 从 Figure 3-4 读取 U121 的 RSET 电阻 R915 标值 `191`、1%；结合 MIC2544 数据表 `RSET=230 V / ILIMIT`，推算名义限流约 1.20 A。这是原理图与器件公式推算，不是实板测量，且器件限流精度/温升会形成范围。
- 区分 J96（PS USB 3.0/2.0 Micro-AB）与 J164（FT4232 JTAG/UART）；USB 摄像头必须接 J96，并使用正确的 OTG/Host 转接。
- 给出从外设、转接线到板端 VBUS/U121 的断电排查顺序，避免反复触发保护。

## Decisions and Adoption

修订 D-014 的故障口径：USB UVC 暂停作为方案输入仍成立，但现象只能确认 J96 VBUS 保护触发，不能仅据此断言 USB PHY/数据链路永久损坏。

## Commands and Tools

使用 `pdfinfo`、`pdftotext -layout` 提取本地手册相关章节；用 `pdftoppm` 渲染 PDF 第 36-37 页并目视检查 Figure 3-4；查阅 Microchip MIC2544 数据表的 RSET 公式。

## Validation and Evidence

- UG1267 p.35：ZCU104 的 USB0 共用 J96 Micro-AB，USB3320 PHY 支持 host-only mode。
- UG1267 p.36：U121 MIC2544 在过流或热关断时通过 FLG 点亮 DS51。
- UG1267 Figure 3-4 / PDF p.37：J96 VBUS 经 U121，R915 标为 `191`、1%。
- UG1267 p.68：DS51 含义为 `PS USB 3.0 ULPI VBUS power error`。
- Microchip DS20005725B：MIC2544 的名义限流由 `RSET=230/ILIMIT` 决定；191 ohm 对应约 1.20 A。
- 未执行摄像头电流、J96 VBUS、电阻、温升、USB 枚举或示波器测量。

## Errors and Corrections

此前把用户所说“USB 坏了”直接固化为硬件损坏范围过大。手册证据仅能解释为电源保护检测到过流或 U121 热关断；故障可能位于摄像头、线材/OTG 转接、J96、电源开关或板端电源网，USB PHY 是否损坏尚未知。

## Files Changed

- `project_workspace/ai/sessions/2026-09-19-005-zcu104-usb-overcurrent-manual-review.md`
- `project_workspace/PROJECT_STATE.md`
- `project_workspace/DECISIONS.md`
- `project_workspace/ai/INDEX.md`

## Remaining Work

- 明确实际亮的是不是 J96 附近、SW4 附近的 DS51，并确认摄像头接的是 J96 而非 J164。
- 断电后分别检查摄像头、OTG 转接线和 J96；先在另一台主机验证摄像头，再以已知良好的低功耗 USB 设备和正确 OTG 适配器测试板卡。
- 如仍触发，测量空载/接载 J96 VBUS、断电 VBUS 对 GND 电阻以及 U121 温升；需要硬件人员检查连接器和 U121 周边，禁止用短接保护或提高限流的方式试错。

## Handoff Notes

DS51 亮并不等于数据 PHY 已坏；它是 VBUS 过流/热保护指示。故障未定位前仍暂停 USB 摄像头路线，但不要据此立即采购替代前端。

## Follow-up: Software-Controlled Power Question

用户确认摄像头在其他设备上正常，并询问能否通过软件给 USB 增加供电。Figure 3-4 显示 `USB0_POWER`/PHY 控制的是 U121 的使能路径，而限流阈值由 U121 外部 RSET 电阻 R915 硬件设定。软件可以影响 VBUS 开关状态和 USB host 初始化，但不能提高 5 V 电源能力或修改电阻设定的限流值。

如果摄像头仅因启动浪涌或实际功耗超过板端能力而触发保护，可评估合规的自供电 USB 3.x Hub，由 Hub 自己给摄像头供电，同时避免上行口向 J96 反向灌电。不能使用 Y 线向 J96 VBUS 并联注入 5 V，也不能短接 U121；使用 Hub 前仍应确认空载 J96 不亮 DS51、连接 Hub 空载不亮、再接摄像头逐步测试。
