# AI Session: 2026-09-22-002-vivado-log-location

- Date: 2026-09-22
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 解释 KV260 bitstream/HWH 的 Vivado 生成流程，并消除构建日志散落工作区根目录的问题。
- Status: Completed
- Report candidate: No
- Related commits: None
- Related files: `whiteboard/scripts/build_kv260_dma_threshold.ps1`

## Context Read

已读取当前根目录 AGENTS.md、AI 开发策略、项目状态、决策流水、会话索引及相关会话 014。当前根目录规范要求正式提交目录为 `kv260-whiteboard-enhance/`；本次只修正既有构建脚本和内部日志归档，未新建正式提交内容。

## Task and Constraints

- 解释前一版 bitstream/HWH 由何种 Vivado 流程生成。
- 用户明确不希望 Vivado 日志、journal 文件出现在工作区根目录。
- 不删除既有日志；应移动到可追溯测试归档目录。

## Contributions

- 确认构建流程为 Vivado 2022.2 batch：创建 KV260 board-part 工程、生成 ZynqMP/AXI DMA/SmartConnect/阈值核 Block Design、校验和地址分配、综合、实现、写 bitstream，并从 Block Design hardware handoff 生成 HWH；XSA 由 `write_hw_platform -include_bit` 生成。
- 确认根目录日志原因：旧 PowerShell 脚本直接从调用者当前目录执行 `vivado.bat`，没有传 `-log/-journal`，Vivado 默认将 `vivado.log`、`vivado.jou` 和 backup 日志相对当前目录创建。
- 修改脚本为在 `build/kv260_dma_threshold` 作为工作目录执行，并显式传入该目录下的 `vivado.log`、`vivado.jou`。
- 将已有根目录 `vivado*.log/jou` 移到 `test_workspace/vivado_root_logs_2026-09-22/`，未删除内容。

## Decisions and Adoption

- 后续 Vivado 生成物、主日志、journal 和 IP 运行日志均应位于工程 `build/` 或明确的 `test_workspace/` 子目录，不得散落工作区根目录。

## Commands and Tools

- PowerShell 文件检查、补丁修改、根目录日志归档和脚本语法解析。
- 本次未重新运行完整 Vivado bitstream 构建；只验证脚本可解析。

## Validation and Evidence

- `build_kv260_dma_threshold.ps1` PowerShell syntax check: PASS。
- 根目录当前不再有 `vivado*.log/jou` 文件。
- 旧日志已完整移动至 `test_workspace/vivado_root_logs_2026-09-22/`。
- 新脚本的下一次 Vivado 运行位置和显式日志目标为 `whiteboard/build/kv260_dma_threshold/vivado.log` 与 `vivado.jou`；尚未执行新脚本的完整 bitstream 回归。

## Errors and Corrections

- 第一次补丁上下文多包含了一行不存在的 `$LASTEXITCODE = $LASTEXITCODE`，apply_patch 未应用；根据实际脚本重定位后成功修改。

## Files Changed

- `whiteboard/scripts/build_kv260_dma_threshold.ps1`
- `test_workspace/vivado_root_logs_2026-09-22/`（移动既有日志）
- `project_workspace/ai/sessions/2026-09-22-002-vivado-log-location.md`
- `project_workspace/ai/INDEX.md`
- `project_workspace/PROJECT_STATE.md`
- `project_workspace/DECISIONS.md`

## Remaining Work

1. 下一次需要重新构建 bitstream 时，使用修正后的脚本并确认根目录仍无 Vivado 日志。
2. 将同样的日志路径约束应用到正式 `kv260-whiteboard-enhance/` 中的最终构建脚本。

## Handoff Notes

bitstream/HWH 的生成本身没有要求根目录日志；根目录日志只是 Vivado 默认 cwd 行为。修正后主工程与运行日志应集中在 build 目录。
