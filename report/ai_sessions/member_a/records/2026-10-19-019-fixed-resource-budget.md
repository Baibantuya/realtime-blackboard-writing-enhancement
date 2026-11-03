# AI Session: 2026-10-19-019-fixed-resource-budget
- Date: 2026-10-19 (Asia/Shanghai)
- Operator: User
- AI product/model: Codex / GPT-6
- Participants: User, Codex; single agent
- Objective: 回答双核方案是否增加硬件开销，将资源不增加设为设计约束。
- Status: Complete; design clarification only
- Report candidate: no
- Related commits: none

## Context Read
AGENTS、AI_DEVELOPMENT_POLICY已读；承接session018，重读最新PROJECT_STATE、DECISIONS末段、INDEX、session018、Git状态及v15资源证据。正式方案为尚未实施的候选。
## Task and Constraints
用户要求硬件资源不能继续增加；当前只修订方案，不改生产算法、不综合、不上板。
## Contributions
明确原功能模型增加DDR且新量化可能超过v15资源，两核分工不自动省资源。以v15真实route设保守整机PL上限，旧量化OOC设局部预算；提出窗口复用、定点逻辑、PS小图/稀疏证据和不默认叠加复杂滤波。DDR容量/带宽与PS负载分列，不把缓冲复用当成已验证事实。
## Decisions and Adoption
D-127记录用户资源不增加的约束；v15基线是为落实该约束选定的保守设计口径，不是用户承诺或已验证的新实现。正式方案第9节优先于前文可选扩展，预算不可达时须报告方案尚未闭合。
## Commands and Tools
本地只读证据核对与文档编辑。
## Validation and Evidence
核对session2026-10-15-003真实route及量化OOC：整机CLB14045/LUT73763/FF87588/BRAM134/URAM8/DSP242，量化LUT7837/FF5855/BRAM7/DSP81。核对v15量化源码存在BRAM行窗口、LUTRAM FIFO及独立src/dst AXI接口；新多输入核并非零面积替换。本轮新算法仿真、HLS/OOC、实现、上板/FPS均未执行。
## Errors and Corrections
首个搜索误用whiteboard_quantize.cpp，实际文件board_quantize_rgb.cpp，按rg文件清单纠正。
## Files Changed
- kv260-whiteboard-enhance/docs/v15_frozen_restore_scene_algorithm_20261019.md
- project_workspace/ai/sessions/2026-10-19-019-fixed-resource-budget.md
- project_workspace/DECISIONS.md
- project_workspace/PROJECT_STATE.md
- project_workspace/ai/INDEX.md
## Remaining Work
在固定PL预算下完成实际职责映射、缓冲生命周期和CPU/DDR预算，再做同源离线验证；新HLS/OOC和整机实现需后续构建指令。当前不能保证画质、吞吐、v15冻结及零资源增长同时成立。
## Handoff Notes
无板端变更；未验证历史进程存活。
