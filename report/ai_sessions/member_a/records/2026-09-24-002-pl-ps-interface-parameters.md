# AI Session: 2026-09-24-002-pl-ps-interface-parameters

- Date: 2026-09-24
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 按项目负责人给出的分辨率/抽帧率/矩形框要求，冻结剩余 PL/PS 接口实现参数。
- Status: 参数及接口实现基线完成；RTL/驱动实现和硬件验证待进行
- Report candidate: No
- Related commits: None
- Related files: `kv260-whiteboard-enhance/docs/pl_ps_interface_spec.md`; `project_workspace/DECISIONS.md` D-039; `project_workspace/PROJECT_STATE.md`。

## Context Read

- 复用本任务前序已读取的根 `AGENTS.md`、AI 开发策略、项目状态、决策、索引，以及 D-036 架构会话、CSI-2 接口记录、四周计划和首版接口规范。
- 项目工作区没有 Git 元数据，无法提供 Git 状态。

## Task and Constraints

- 项目负责人指定 1920×1080、2 fps 分析抽帧、仅矩形框；框不绘制到输出画面，供遮挡区域历史数据拼合使用。
- 项目负责人授权 Codex 决定前版规范第 3、4、5 项未定参数。
- 需保留接口建议与未经验证的事实区分；不得声称 RTL、仿真或硬件工作已完成。

## Contributions

- 固定主流 1920×1080@30，分析支路 1920×1080 GRAY8@2 fps，每 15 个主流帧抽帧；用 3 槽 ring 保存约 1.5 秒数据。
- 固定最多 8 个矩形框、置信度门限 166/255、源帧后最多 15 帧有效；预测框须有显式标志。
- 固定 PL 侧 clean-board 冻结及历史帧矩形拼合，边缘 8 px 线性羽化；框不绘制。低置信/过期/历史帧无效时关闭该区域拼合并冻结其历史更新。
- 选定 AXI VDMA S2MM + Linux DMA-BUF/CMA 分析帧路径；队列满丢弃分析帧、不反压视频主路。
- 补齐 AXI-Lite `0x00–0x54` 语义表、64-bit 写入顺序、轮询策略及 2 秒 heartbeat timeout。
- 冻结结果 packet ABI v1：64-byte header、最多 8 个 16-byte ROI、最大 192 bytes、64-byte 地址对齐、doorbell 发布/ACK 确认；M0 不带像素 mask 或可变参数 payload。
- 将草案状态改为项目负责人授权的实现基线，并登记 D-039。

## Decisions and Adoption

- 以上参数由用户明确授权 Codex 决定，作为实现基线采纳；准确率/吞吐性能尚无实测证据。
- 未在本轮实现 PS 应用、驱动、RTL 或 UI；未引入像素 mask。

## Commands and Tools

- 阅读现有接口规范、D-039、会话 001 及项目状态；用本地补丁更新 Markdown 规格与记录。

## Validation and Evidence

- 文档交叉核查并确保状态、D-039、会话和项目状态一致。
- 未运行测试、仿真、综合、时序、带宽实测或板端验证。

## Errors and Corrections

- 将原“候选框只能冻结、历史恢复关闭”的早期建议更新为用户要求的矩形历史拼合；明确框不叠加显示，并加置信度、帧龄、历史帧有效性检查与边缘羽化。
- 2 fps 人体位置可能在两次检测间显著变化；规范限制结果最长 15 帧，并要求 PS 跟踪预测显式标记，列为主要待验证风险。
- 复核 packet 字段字节数时发现原计数少算了 4-byte reserved 字段；修正为 64-byte 对齐头部、192-byte 最大包，并同步决策和状态记录。

## Files Changed

- `kv260-whiteboard-enhance/docs/pl_ps_interface_spec.md`
- `project_workspace/DECISIONS.md`
- `project_workspace/PROJECT_STATE.md`
- `project_workspace/ai/INDEX.md`
- `project_workspace/ai/sessions/2026-09-24-002-pl-ps-interface-parameters.md`

## Remaining Work

1. 实现 AXI VDMA 分析抽帧/三槽缓冲、驱动 DMA-BUF 导出与 PS 检测流程。
2. 实现带帧号的框消息 mailbox、AXI-Lite ABI 和 PL clean-board 框区域冻结/拼合。
3. 测量 PS 检测延迟，验证 15 帧有效窗口和跟踪预测质量；评估 8 px 羽化及 clean-board 图像陈旧导致的拼合伪影。
4. 完成接口仿真、综合、时序和 KV260 上板连续运行验证。

## Handoff Notes

完整实现基线见 `kv260-whiteboard-enhance/docs/pl_ps_interface_spec.md`；架构决策 D-039。主风险是 2 fps 检测与快速移动教师之间的时空偏差，安全策略为低置信或过期时不做历史拼合。
