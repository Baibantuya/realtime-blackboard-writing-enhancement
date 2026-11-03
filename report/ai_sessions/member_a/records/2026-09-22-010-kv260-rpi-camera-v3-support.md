# AI Session: 2026-09-22-010-kv260-rpi-camera-v3-support

- Date: 2026-09-22
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 核实 Raspberry Pi Camera Module v3（IMX708）能否替代 KV260 J9 上难以购买的 Camera Module v2（IMX219），并定位官方支持说明。
- Status: Completed official-support assessment; hardware validation pending
- Report candidate: No
- Related commits: None
- Related files: `project_workspace/PROJECT_STATE.md`, `project_workspace/DECISIONS.md`, `project_workspace/ai/sessions/2026-09-21-005-kv260-csi2-camera-and-hdmi-ip.md`, `project_workspace/ai/sessions/2026-09-22-006-kv260-imx219-csi2-pipeline.md`

## Context Read

- 已依次阅读根目录 `AGENTS.md`、`project_workspace/ai/AI_DEVELOPMENT_POLICY.md`、`PROJECT_STATE.md`、`DECISIONS.md`、`ai/INDEX.md`，以及与 CSI-2 相机相关的最近会话 `2026-09-22-006` 和 `2026-09-21-005`。
- 工作区根目录不是 Git 仓库；未对项目代码执行修改。

## Task and Constraints

- 仅形成基于官方资料的可行性与支持边界结论；不把资料兼容性表述为已上板验证。

## Contributions

- AMD UG1089 v1.4（2025-06-25）说明 KV260 J9 是 Raspberry Pi 15-pin、直连 MPSoC HPA bank 的双 MIPI-lane 接口；其“Functionally Tested Peripherals”表只列 `Raspberry Pi camera module v2`，没有 Camera Module 3。
- Raspberry Pi 官方 Camera Module 3 产品页/产品简介说明：v3 为 IMX708，使用 15×1 mm FPC、CSI-2、I2C，输出 RAW10；其 PDAF 自动对焦机构同样需要 I2C 控制。PCB 尺寸和安装孔与 v2 相同，但厚度更高。
- 结论分层：v3 与 J9 在接头、双 lane CSI-2 和 I2C 层面具备工程可行性；但 AMD 未把 v3 写入 KV260 功能验证清单，项目已有的 IMX219/v2 初始化表和示例不能直接驱动 IMX708。v3 是“可采购、需自行适配并先 bring-up”的替代品，不是“官方已支持的即插即用替换”。
- 建议标准可见光、普通视场 v3 作为 v2 缺货时的主采购候选。先以 1080p、RAW10、关闭 HDR 的保守模式验证 I2C ACK/芯片识别、MIPI D-PHY lock/CSI RX、Bayer 图样、1080p30 连续帧和 HDMI；自动对焦/HDR/全分辨率后置。

## Decisions and Adoption

- 本次不改写 v2 的官方验证基线，亦不把 v3 标为“官方支持”。若项目负责人因供应因素选择 v3，应作为风险受控的 IMX708 bring-up 任务采纳，并保留 UVC fallback；首个 CSI-2 采集通过后再升级选型状态。

## Commands and Tools

- 本地只读查阅项目记录。
- 在线查阅 AMD UG1089 `Interfaces` 和 `Supported Peripherals`；Raspberry Pi Camera Module 3 产品页、产品简介和相机文档；Kria-PYNQ README（现有示例为 Digilent Pcam 5C，而非 IMX708）。

## Validation and Evidence

- 文档核验完成。未执行 v3 实物插接、供电、I2C、D-PHY/CSI-2、传感器寄存器初始化、自动对焦、图像/帧率或 HDMI 测试。
- 证据：AMD UG1089 v1.4 `Supported Peripherals`（J9 功能验证仅 `Raspberry Pi camera module v2`）；UG1089 `Interfaces`（J9 为 15-pin 双 lane）；Raspberry Pi Camera Module 3 产品说明（IMX708、15×1 mm FPC、CSI-2/I2C/RAW10/自动对焦）。

## Errors and Corrections

- 不能把“物理接头与 CSI-2 协议兼容”表述为“AMD 官方已验证支持”；两者不等价。

## Files Changed

- `project_workspace/ai/sessions/2026-09-22-010-kv260-rpi-camera-v3-support.md`（创建）。

## Remaining Work

1. 项目负责人决定是否采购 v3；若采购，记录具体 SKU（标准/广角、NoIR 与否）和线缆长度。
2. 为 IMX708 准备可核查的寄存器初始化/模式表、I2C 控制和可选焦点控制；避免混用 Raspberry Pi Linux 的 `imx708` overlay。
3. 在 HDMI 测试图点亮后，完成保守 1080p RAW10 CSI-2 bring-up，再决定是否启用 AF/HDR 或高分辨率。

## Handoff Notes

- v2 仍是 AMD 文档中 J9 唯一的功能验证 Raspberry Pi 相机；v2 难采购时，v3 可行但应按新传感器适配工作排期，不能影响测试图→HDMI 主线。
