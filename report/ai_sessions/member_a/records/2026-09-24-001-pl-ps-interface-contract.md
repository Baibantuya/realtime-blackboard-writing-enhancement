# AI Session: 2026-09-24-001-pl-ps-interface-contract

- Date: 2026-09-24
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 评估是否需要输出人物遮挡候选区，梳理额外 PL/PS 接口并拟定接口规范。
- Status: 草案完成，待项目负责人冻结 ABI 后实现
- Report candidate: No
- Related commits: None
- Related files: `kv260-whiteboard-enhance/docs/pl_ps_interface_spec.md`; `project_workspace/DECISIONS.md` D-039; `project_workspace/PROJECT_STATE.md`。

## Context Read

- 依次读取根 `AGENTS.md`、`project_workspace/ai/AI_DEVELOPMENT_POLICY.md`、`project_workspace/PROJECT_STATE.md`、`project_workspace/DECISIONS.md`、`project_workspace/ai/INDEX.md`。
- 阅读最近相关记录 D-036 对应的 `2026-09-22-007-kv260-hybrid-ps-pl-board-recovery-architecture.md` 及 `2026-09-22-006-kv260-imx219-csi2-pipeline.md`。
- 查阅正式计划 `kv260-whiteboard-enhance/docs/kv260_four_week_plan.md` 中视频流、遮挡、分析和验收约定。
- 工作区根及 `kv260-whiteboard-enhance/` 均未发现 Git 元数据，`git status` 无法执行；正式目录现阶段没有已实现 PL/PS 接口 RTL，仅有计划文档。

## Task and Constraints

- 输出的是接口设计草案，不能声称已实现或已通过硬件/仿真验证。
- 遵守正式成果放入 `kv260-whiteboard-enhance/`，内部事实记录放入 `project_workspace/`。

## Contributions

- 结论：需要把人物遮挡信息送到 PL，但候选矩形 ROI 与逐像素精确 mask 必须分开定义。ROI 可扩大后保守冻结 clean-board 更新，不可作为精确历史像素合成边界。
- 规范补充了主 AXI4-Stream Video、带 epoch/frame ID/时间戳的分析 ring buffer、分析结果消息、DDR mask 描述符和 ownership/cache 协议、AXI-Lite 控制状态与异常安全策略。
- 建议 M0 先实现视频、分析支路、ROI 冻结保护和诊断状态；后续再接 mask 恢复及自适应参数。

## Decisions and Adoption

- 已写 D-039 为 proposed，待 owner 冻结，不表示团队已正式冻结 ABI。
- 正式规范草案为 `kv260-whiteboard-enhance/docs/pl_ps_interface_spec.md`。

## Commands and Tools

- 使用 PowerShell `Get-Content`、`Get-ChildItem`、`rg` 阅读项目记录和已有规格。
- `git status --short` 与 `git -C kv260-whiteboard-enhance status --short` 均失败：目标工作区无 Git 仓库元数据。

## Validation and Evidence

- 架构/文档审查。无 RTL 修改；仿真、软件测试、综合、时序、资源、带宽、板端验证均未执行。
- 已检查草案涵盖帧匹配、结果有效期、乱序/过期拒收、ring 满降级和分析支路不反压主路要求。

## Errors and Corrections

- 初步将“候选标定区”可能理解为遮挡框；规范中明确使用候选 ROI 命名，并将 ROI 与精细 mask 拆成独立语义，避免框直接驱动错误像素覆盖。
- 寄存器表仍为语义草案，明确注明未补齐的高位寄存器、握手及平台地址约束，防止读者误认为 ABI 已可编码。

## Files Changed

- `kv260-whiteboard-enhance/docs/pl_ps_interface_spec.md`（新增接口规范草案）
- `project_workspace/DECISIONS.md`（新增 D-039）
- `project_workspace/PROJECT_STATE.md`（更新状态）
- `project_workspace/ai/INDEX.md`（登记本会话）
- `project_workspace/ai/sessions/2026-09-24-001-pl-ps-interface-contract.md`（本记录）

## Remaining Work

1. 项目负责人确认 M0 范围、候选 ROI 是否最多 8 个、mask 输出模式和失效安全策略。
2. 冻结分辨率/格式、DMA/VDMA 驱动栈、描述符 ABI、AXI-Lite 完整寄存器表、定点参数格式、门限及心跳周期。
3. 按冻结接口实现并验证帧号错配、过期/乱序结果、PS 重启、DMA 错误、分析 ring 满和显示主路连续性。

## Handoff Notes

关键建议：遮挡候选框主要保护 clean-board 不被教师污染；只有与源帧正确配对的像素 mask 才可用于精细历史恢复。草案见 `kv260-whiteboard-enhance/docs/pl_ps_interface_spec.md`，架构决策登记在 D-039。
