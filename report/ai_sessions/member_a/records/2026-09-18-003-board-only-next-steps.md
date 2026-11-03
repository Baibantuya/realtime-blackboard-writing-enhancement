# AI Session: 2026-09-18-003-board-only-next-steps

- Date: 2026-09-18
- Operator: Codex
- AI product/model: Codex
- Participants: 用户（成员2）；Codex（建议）
- Objective: 在摄像头未到货、仅板卡在手时排序成员2的后续开发与验收。
- Status: Completed
- Report candidate: no
- Related commits: none
- Related files: `project_workspace/PROJECT_STATE.md`, `project_workspace/ai/INDEX.md`

## Context Read

- 沿用本任务已读取的根目录规范、当前项目状态、D-002/D-007/D-009/D-010 与 Day 3 实现事实；查阅 AMD ZCU104 UG1267、AXI VDMA PG020（2022 年 v6.3）及 2022.2 ZCU104/PetaLinux 教程。

## Task and Constraints

- 摄像头未到货；用户称板卡已在手。假定仍是计划中的 ZCU104，板卡实际料号、启动镜像、系统软件与显示设备未核验。
- 不把建议记录为已执行硬件结果；本轮不修改正式仓库、不开启板卡或生成 bitstream。

## Contributions

- 建议先核对实板/启动/工具版本，再完成带时钟约束的核心综合与 AXI4-Lite/VDMA 接口交接；优先固定图片 PS/DDR→PL→PS/DDR 回环并逐像素/CRC 验证；显示是下一层，不以摄像头为前置条件。
- 成员2可并行推进 5×5 形态学级，但必须先取得/审阅成员3整数参考和边界向量；不以板端集成等待阻塞算法验证。

## Decisions and Adoption

- 该排序是 Codex 建议、待用户/成员1确认的执行计划；没有新增架构决定。仍遵循既有 D-002 固定帧先于连续视频的路线。

## Commands and Tools

- Web 阅读 AMD 官方 UG1267、PG020 和 2022.2 ZCU104/PetaLinux 教程。未执行板端命令。

## Validation and Evidence

- 官方资料支持 ZCU104 含 JTAG/SD 配置与 PS DisplayPort；AXI VDMA 视频流使用 SOF `TUSER[0]` 并支持帧缓冲同步；具体板端连接与可用镜像未实测。
- 板端运行、DMA、显示、时序、帧率：未执行。

## Errors and Corrections

- 无。仅提供计划，不把先前 xsim 图像当作板端结果。

## Files Changed

- 根目录内部：本会话记录、`project_workspace/PROJECT_STATE.md`、`project_workspace/ai/INDEX.md`。

## Remaining Work

- 用户/成员1确认板卡实际版本、现有启动栈、可用显示设备和各方集成分工；成员2准备可集成 IP 与板端固定帧验证。

## Handoff Notes

- 首个可核查硬件里程碑应是固定 320×240 或 720p BGRX 图的 PS→PL→PS 回环：保存输入/输出、配置、DMA 状态、错误/帧计数、逐像素差异；显示成功后再谈连续视频与摄像头。
