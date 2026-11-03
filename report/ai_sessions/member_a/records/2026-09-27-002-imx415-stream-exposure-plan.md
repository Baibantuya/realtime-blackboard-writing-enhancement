# AI Session: 2026-09-27-002-imx415-stream-exposure-plan
- Date: 2026-09-27
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 研究 IMX415 寄存器控制、直入 PL 的流式输入及 PL 曝光调整方案
- Status: Completed design guidance; hardware unverified
- Report candidate: No
- Related commits: None (workspace and project directory are not Git repositories)
- Related files: `kv260-whiteboard-enhance/docs/imx415_stream_exposure_plan.md`, `project_workspace/PROJECT_STATE.md`, `project_workspace/ai/INDEX.md`

## Context Read

按顺序阅读 AGENTS.md、AI_DEVELOPMENT_POLICY.md、PROJECT_STATE.md、DECISIONS.md、INDEX.md，以及相机选择、CSI 流水和近期 CSI 就绪检查记录；检查 Git 状态与相关代码。

## Task and Constraints

区分传感器光学曝光与 PL 数字亮度处理，查核公开寄存器及例程，避免把未验证的板级参数当成已可运行配置。

## Contributions

查核主线 Linux IMX415 驱动与 AMD CSI-2 RX 文档。分离真实光学曝光（VMAX/SHR0）、传感器模拟增益和 PL 数字亮度处理；形成 I²C 初始化顺序、RAW10 AXIS 视频链、统计闭环与验证门槛。记录 J9 两线与 IMX415 模组电气/排线兼容性尚未核实，现有校正核为 DDR 帧接口。

## Decisions and Adoption

未冻结新架构；建议方案待板卡模组型号与上板测试后采纳。没有更改 `DECISIONS.md`。

## Commands and Tools

本地读取相关会话、代码和 Git 状态；公开资料查核 Linux 主线 `drivers/media/i2c/imx415.c`、AMD PG232、Enclustra ZynqMP MIPI 例程。Git 检查发现根目录与正式项目均非 Git 仓库。

## Validation and Evidence

文档与公开驱动交叉核对寄存器及 AXIS 信号定义。未执行硬件、仿真、综合或性能测试。

## Errors and Corrections

初稿数字 gain 表达式中移位与加法优先级不明确；已增加显式括号。

## Files Changed

- project_workspace/ai/sessions/2026-09-27-002-imx415-stream-exposure-plan.md
- kv260-whiteboard-enhance/docs/imx415_stream_exposure_plan.md
- project_workspace/PROJECT_STATE.md
- project_workspace/ai/INDEX.md

## Remaining Work

确认模组及接线、INCK、I²C、lane 数与 mode table；建立匹配当前 KV260 软件/PL 版本的 CSI 工程；完成 RAW10 连续帧、控制生效帧及曝光质量板测。

## Handoff Notes

不得把主线驱动 mode table 直接宣称适用于未识别模组；当前仅提供设计建议。
