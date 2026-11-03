# AI Session: 2026-09-19-003-zcu104-throughput-feasibility

- Date: 2026-09-19
- Operator: Codex
- AI product/model: Codex
- Participants: 用户（成员2）；Codex（性能口径纠正与可行性评估）
- Objective: 解释整帧仿真的 2.1 ms 含义，并评估 ZCU104 完成最终实时板书增强项目的吞吐、DDR 和资源可行性。
- Status: Completed
- Report candidate: no
- Related commits: none
- Related files: `blackboard-writing-enhance/tb/tb_enhance_axis_ip_frame.sv`, `blackboard-writing-enhance/docs/pl_full_frame_ip_loopback.md`

## Context Read

- 沿用本日已读取的项目接口、算法、仿真和状态记录；核对整帧日志为两帧累计约 2.098 ms、100 MHz testbench 时钟、S2MM 约 25% 随机反压。
- 查阅 AMD 官方 ZCU104 UG1267、Zynq UltraScale+ 产品资源表和 AXI VDMA PG020。

## Task and Constraints

- 用户担心 320x240 已耗时 2.1 ms，分辨率和算法复杂度提高后 ZCU104 无法完成最终项目。
- 必须区分 RTL 模拟时间、单帧核心吞吐、随机背压和真实板端端到端延迟；不得把无板仿真作为板端性能实测。

## Contributions

- 纠正口径：2.1 ms 是灰度和二值两帧累计仿真时间，不是单帧；单帧约 1.049 ms，包含人为 S2MM 随机反压。当前核无停顿吞吐为 1 pixel/clock，320x240 在 100 MHz 下理论 active-pixel 时间 0.768 ms。
- 给出 720p/1080p 在 100/150 MHz、无停顿和当前压力模型比例下的缩放预算，并计算 BGRX 输入＋输出 DDR 流量。
- 建议最终强制所有新增 PL 阶段保持 II=1、单次流式级联，5x5 方形形态学采用可分离水平/垂直 max/min 与行缓存，照度状态使用粗图 BRAM/上一帧状态，避免每级 DDR 往返和逐像素迭代除法。

## Decisions and Adoption

- 性能建议（待用户/团队确认）：720p30 作为必达规格；1080p30 作为在 150 MHz、板端 VDMA/DDR/PS 解码实测有余量后开启的扩展规格。
- 不能以流水级数直接乘帧时间；只要 II=1，增加级数主要增加首像素延迟和资源，不降低稳态像素吞吐。若某级 II>1 或多次回 DDR，则必须重新计算并可能降级。

## Commands and Tools

- AMD 官方网页/文档检索：ZCU104 UG1267、Zynq UltraScale+ MPSoC 产品表、AXI VDMA PG020。
- 依据实测仿真循环和像素数做确定性算术预算，未运行新 RTL、综合或硬件测试。

## Validation and Evidence

- 当前整帧日志：每帧 76,800 像素，灰度 104,880 循环、二值 104,876 循环；testbench 10 ns 时钟。两帧总模拟时间约 2.098 ms。
- 纯 1 pixel/clock active-pixel 预算：720p 在 100/150 MHz 分别 9.216/6.144 ms；1080p 分别 20.736/13.824 ms。按当前约 1.3656 cycles/pixel 压力比例，100 MHz 下约 12.586/28.318 ms，150 MHz 下约 8.390/18.878 ms。该压力模式不是 VDMA 实测。
- BGRX 单次输入读＋输出写在 30 fps 的有效载荷：720p 约 221 MB/s，1080p 约 498 MB/s；若显示再读一次输出，分别约 332/746 MB/s，未含协议、cache 和 PS 解码额外流量。
- 未执行：最终形态学/照度 RTL、带约束实现、真实 Fmax、DDR/VDMA sustained bandwidth、MJPEG 解码、端到端 30 fps。

## Errors and Corrections

- 无工具错误。主要纠正是把用户观察到的 2.1 ms 从“单帧处理时间”改为“两帧＋随机反压的模拟时间”。

## Files Changed

- `project_workspace/DECISIONS.md`（D-013 性能门槛建议）
- `project_workspace/PROJECT_STATE.md`
- `project_workspace/ai/INDEX.md`
- 本会话记录

## Remaining Work

- 将整帧 testbench 扩至 720p/1080p，增加无停顿 II/周期断言。
- 每新增算法级做 OOC 综合和 100/150 MHz 带约束实现，记录 WNS、LUT/FF/BRAM/DSP 和 II。
- 板卡到手后实测 VDMA/DDR、cache 和 PS MJPEG 解码，再决定是否把 1080p30 升为正式目标。

## Handoff Notes

- 当前结论为架构预算，不是板端性能承诺。720p30 的 active pixel rate 为 27.648 Mpixel/s，1080p30 为 62.208 Mpixel/s；后续必须围绕这一输入速率验收每一级。
