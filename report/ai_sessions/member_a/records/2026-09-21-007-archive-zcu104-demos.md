# AI Session: 2026-09-21-007-archive-zcu104-demos

- Date: 2026-09-21
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 将既有 ZCU104 相关演示工程集中归档，并为已到手的 KV260 留出重新开始的干净工程入口。
- Status: Completed
- Report candidate: No
- Related commits: None
- Related files: `zcu104_legacy_demos/`, `project_workspace/PROJECT_STATE.md`, `project_workspace/DECISIONS.md`, `project_workspace/ai/INDEX.md`

## Context Read

已按入口规范阅读 `AGENTS.md`、AI 开发政策、项目状态、决策流水、索引和最近的 `2026-09-21-006-kv260-project-summary-wording.md`；已检查根目录及 `blackboard-writing-enhance/` 的目录与 Git 状态。根目录是 Git 仓库；`blackboard-writing-enhance/` 是嵌套 Git 仓库，存在用户/既有未提交改动。

## Task and Constraints

- 用户明确要求把此前对 ZCU104 做的 demo 放入单独目录，并以 KV260 重新开始。
- 归档必须是移动而非删除，保留历史源码、证据与未提交状态；不改写或混入内部工程记录。
- 仅归档可识别的演示/探测工程；原始参考资料与 PDF 不作为 demo 移动。

## Contributions

- 建立 `zcu104_legacy_demos/`，归档 `whiteboard/`、`blackboard-writing-enhance/`、`24_hdmi_colorbar/`、`zcu104_ov5640_capture_test/`、`vivado_root_artifacts/`、两份 OV5640 供应商示例、`hls_demo/`、根目录 `.Xil/` 与 ZCU104 USB 手册渲染件。
- 建立空白 `kv260-whiteboard-enhance/`，其中仅有 `docs/`、`rtl/`、`scripts/`、`tb/` 和启动说明，未迁入旧源码。
- 完整保留 `blackboard-writing-enhance/.git` 及其未提交状态，作为历史工程的一部分。

## Decisions and Adoption

- 用户的“重新开始”被采纳为：保留旧工程的完整可追溯归档，在根目录新建独立 KV260 工程入口；不复用 ZCU104 的器件、约束、DVP 前端或历史构建结论。

## Commands and Tools

- 已读取规定上下文、检查目录清单和嵌套仓库 Git 状态。

## Validation and Evidence

- 已核验归档根目录包含 10 个预期项目/工件目录，`24_hdmi_colorbar/` 已恢复 `doc/`、`prj/`、`rtl/`、`sim/` 原有层级；新 KV260 入口包含 4 个空白工作子目录。
- 未运行硬件、综合、仿真或性能测试；本次只验证移动后目录清单。

## Errors and Corrections

- 首次 PowerShell 命令误用 `New-Item -LiteralPath`（该 cmdlet 不支持此参数），使首个 `24_hdmi_colorbar/` 被重命名为归档根目录，随后其 `doc/`、`prj/`、`rtl/`、`sim/` 子目录位于归档根。文件未丢失；已建立 `zcu104_legacy_demos/24_hdmi_colorbar/` 并将四个子目录恢复到该目录。

## Files Changed

- `zcu104_legacy_demos/`（新增，含已移动的旧 demo）
- `kv260-whiteboard-enhance/README.md`
- `project_workspace/DECISIONS.md`
- `project_workspace/PROJECT_STATE.md`
- `project_workspace/ai/INDEX.md`
- `project_workspace/ai/sessions/2026-09-21-007-archive-zcu104-demos.md`

## Remaining Work

1. 项目负责人确认新的 KV260 正式提交目录/仓库名称。
2. 检查 KV260 启动镜像、工具版本与可用 HDMI/DP 显示器，记录首次上电信息。
3. 确定首个可用相机输入（USB UVC 或 J9 MIPI CSI-2），再建视频基线。

## Handoff Notes

归档目录是历史参考，不是 KV260 可直接复用的实现；KV260 必须从其原生视频输入和显示基线重新建立工程。
