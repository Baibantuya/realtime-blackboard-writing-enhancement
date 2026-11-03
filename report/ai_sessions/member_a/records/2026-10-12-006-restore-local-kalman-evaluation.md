# AI Session: 2026-10-12-006-restore-local-kalman-evaluation
- Date: 2026-10-12
- Operator: Project owner
- AI product/model: Codex / GPT-6
- Participants: Project owner, Codex (single agent)
- Objective: 在不修改代码的前提下，评估恢复局部化、DDR burst 搬运与卡尔曼思路对帧率和静止人物阴影问题的可行性，并纳入硬件资源开销约束。
- Status: In progress
- Report candidate: no
- Related commits: none
- Related files: 待评估；不计划修改正式源码

## Context Read
已按 AGENTS.md 顺序读取 AGENTS.md、AI_DEVELOPMENT_POLICY.md、PROJECT_STATE.md、DECISIONS.md、ai/INDEX.md，并读取近期 A6/B32/RGB565/v6/实际IP延迟会话。上下文确认：当前 B32 运行阶段实测三个阶段约 7.59 FPS，校正硬件约 69.98 ms；历史实测恢复约 395 ms，量化约 16 ms；B32 整机 CLB 占用约 99.8%、BRAM 约 89.6%。

## Task and Constraints
用户提出两个目标：提高帧率，缓解人物基本静止时的严重阴影遮挡；初步方向是仅恢复有遮挡区域、恢复搬运尽量用 Verilog、扩大选区以吃满 DDR burst，并评估在现有算法上融合卡尔曼滤波。用户补充硬约束：不要引入过多硬件资源。本轮只分析，不修改正式代码或硬件配置。

## Contributions
待补齐：恢复数据通路、现有 HLS/RTL/PS 结构和卡尔曼适配边界评估。

## Decisions and Adoption
待评估后填写；任何正式架构结论需同步 DECISIONS.md。

## Commands and Tools
PowerShell、rg、Get-Content、git status；未执行综合、仿真、上板或性能实验。

## Validation and Evidence
本轮计划使用已有项目记录、源码和已保存的板端/延迟证据；新硬件验证未执行。

## Errors and Corrections
暂无。

## Files Changed
仅本内部会话记录（初始记录）；正式源码不改。

## Remaining Work
读取恢复源码/接口和最近延迟记录，形成局部恢复、burst、卡尔曼、资源风险与分阶段验证建议；完成后更新状态、索引和决策日志。

## Handoff Notes
需明确区分已有实测与推断；不可把局部恢复或卡尔曼收益写成已验证性能。
