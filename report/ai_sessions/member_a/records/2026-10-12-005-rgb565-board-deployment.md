# AI Session: 2026-10-12-005-rgb565-board-deployment
- Date: 2026-10-12
- Operator: Project owner
- AI product/model: Codex / GPT-6
- Participants: Project owner, Codex (single agent)
- Objective: 将 A6 修改后的独立 RGB565/B16 匹配文件上板 KV260，并完成部署与板端验收。
- Status: In progress
- Report candidate: yes
- Related commits: none
- Related files: `kv260-whiteboard-enhance/rtl/imx219_rgb565_b16_v11/board_package`, `project_workspace/kv260_deploy.local.json`

## Context Read
已按 AGENTS.md 顺序读取项目政策、当前状态、决策、索引及 A6/B32/RGB565 最近会话；确认现有 B32 正在板上运行，RGB565 包已完成匹配构建和下载校验，尚未上板。

## Task and Constraints
使用原 `deploy_to_kv260.py` 流程；切换前保留 B32/A6 历史；不得记录凭据；不得把部署准备误报为板端成功。

## Contributions
待补齐。

## Decisions and Adoption
采用独立 `20261012-v11-rgb565-b16` 平铺包，按 deployment.json 执行 preflight、FPGA 加载、媒体配置、三帧 smoke 和 live。

## Commands and Tools
待执行：PowerShell、原部署脚本、PuTTY SSH/SCP、板端 run.sh。

## Validation and Evidence
部署前本地包清单已读；板端验证待执行。

## Errors and Corrections
待补齐。

## Files Changed
本记录；部署配置是否更新待记录。

## Remaining Work
保留并停止 B32，上传安装 RGB565 包，执行板端检查/加载/smoke/live，记录实际结果并更新项目状态。

## Handoff Notes
若 smoke 或 RGB16 DRM/媒体绑定失败，保留失败证据并恢复已保存 B32，不宣称完整运行成功。
