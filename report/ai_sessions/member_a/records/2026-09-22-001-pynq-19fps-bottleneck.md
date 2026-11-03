# AI Session: 2026-09-22-001-pynq-19fps-bottleneck

- Date: 2026-09-22
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 根据 KV260 PYNQ notebook 的实际 19 fps 和回显延迟，定位主要瓶颈并给出下一步验证/优化顺序。
- Status: Completed diagnosis; optimization not yet implemented
- Report candidate: No
- Related commits: None
- Related files: `whiteboard/pynq/kv260_threshold.py`, `whiteboard/pynq/kv260_threshold_demo.ipynb`

## Context Read

已按当前根目录 AGENTS.md 依次读取 AI 开发策略、项目状态、决策流水、会话索引和会话 014。当前工程记录存在历史目录边界矛盾：本次仅作内部诊断记录，未修改正式提交目录。

## Task and Constraints

- 用户报告 notebook 显示 `pipeline fps ≈ 19` 且有延迟。
- 不把预览刷新率误认为 PL 处理吞吐；需要区分摄像头/解码、DMA/缓存、Python 调度和浏览器 JPEG/widget 的开销。
- 未执行新的板端性能分段测量，不能伪造各阶段耗时。

## Contributions

- 依据现有代码逐段确认当前循环是严格串行的：读取完整 Gray8 帧 → PS `np.copyto` → cache flush → S2MM transfer → MM2S transfer → 两次 wait → cache invalidate → 输出再复制 → 每 3 帧 JPEG/widget 预览。
- 结合既有板测，判定第一嫌疑是 PS 侧 MJPEG→GRAY8 解码和 Python/缓存/全帧复制的串行调度，而不是阈值 RTL：先前纯 Gray8 解码已测到约 1.02x、CPU 约 96%；当前 PYNQ 路径又增加至少两次 2 MB 级软件复制、cache 同步和同步 DMA 等待。
- 判定当前输出延迟主要来自单缓冲串行流水和 UVC/FFmpeg 队列：采集、解码、DMA 和显示不能重叠，处理慢于 30 fps 时摄像头/FFmpeg 队列会积累旧帧。
- 指出每 3 帧 JPEG/widget 更新是次要但可见的抖动来源；它不跳过 PL 帧，但 callback 在主循环内同步执行，仍会阻塞下一帧。

## Decisions and Adoption

- 暂不转 CSI-2；先对当前 UVC 路线做分段测量。
- 优先顺序：无预览 synthetic/Gray8 DMA 基线 → camera decode-only → camera+DMA 无预览 → camera+DMA+preview；若 DMA/PL 基线远高于 19 fps，则优化重点放在 PS 解码、复制、cache 同步和双缓冲。
- 真正的连续低延迟实现需要至少双缓冲/流水调度；单缓冲版本只用于通路验证，不是最终性能架构。

## Commands and Tools

- Read-only inspection of `whiteboard/pynq/kv260_threshold.py` and `kv260_threshold_demo.ipynb`.
- No board-side command or new performance run executed in this session.

## Validation and Evidence

- Existing evidence: UVC 1080p30 MJPEG→GRAY8 achieved about 1.02x media time with about 96% CPU; BGRX path about 0.892x. These are decode-path measurements, not the full PYNQ loop.
- Existing code evidence: `process_frame()` contains `np.copyto`, explicit `flush`, synchronous `transfer/wait`, `invalidate`, and `np.array(..., copy=True)`; `show_frame()` performs synchronous JPEG encoding and widget assignment every third frame.
- New measured result in this session: none. The user's observed 19 fps is accepted as the current board observation but has not been independently re-measured by the AI.

## Errors and Corrections

- Do not attribute the 19 fps directly to PL frequency or threshold RTL without a no-camera/no-preview baseline; the current architecture has multiple serialized PS stages.

## Files Changed

- `project_workspace/ai/sessions/2026-09-22-001-pynq-19fps-bottleneck.md`
- No formal source or hardware files changed.

## Remaining Work

1. Add timing counters around source read, `process_frame`, and preview callback; report per-stage median/p95.
2. Run four controlled cases: synthetic DMA only, camera decode-only, camera+DMA without preview, full notebook.
3. Implement double-buffered capture/processing and reduce copies/cache operations; then reevaluate 30 fps and end-to-end latency.

## Handoff Notes

19 fps currently indicates a PS-side serialized pipeline bottleneck until measured otherwise. PL threshold processing is a streaming one-pixel-per-clock stage and should be validated independently before changing RTL.
