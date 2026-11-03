# AI Session: 2026-09-20-002-fmc-binarize-hdmi-foundation

- Date: 2026-09-20
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 在摄像头参数未知、暂不上板测试的条件下，开发 FMC 摄像头进入 PL、二值化并以 720p30 视频输出的基础链路
- Status: Completed
- Report candidate: No
- Related commits: None
- Related files: `whiteboard/rtl/`, `whiteboard/tb/tb_fmc_camera_binary_hdmi_core.sv`, `whiteboard/docs/fmc_camera_binary_hdmi_foundation.md`

## Context Read

已按规定顺序读取根目录规范、AI 开发政策、项目状态、决策流水、内部索引，以及与输入源无关开发、摄像头/显示选择、HDMI demo 审查相关的最近会话；已检查当前 Git 状态入口和项目文件清单。外层工作区不是 Git 仓库，正式代码仓库状态仍需进入对应目录确认。

## Task and Constraints

- 用户预计次日拿到板卡和 FMC 摄像头，但当前不知道传感器型号、CSI-2 lane、RAW 位宽/Bayer 顺序、时钟、I2C 初始化、FMC 引脚和参考工程参数。
- 输出目标为 1280x720、30 fps；用户允许本次先开发、不做板级测试。
- 不得把 Artix-7 HDMI demo 的器件原语和 XDC 直接用于 ZCU104，也不得把未执行的综合、时序或板测写成通过。

## Contributions

- 实现参数化 720p30 时序发生器，默认 74.25 MHz、3300×750 总时序、正极性 HS/VS，输出 1280×720 有效区。
- 实现标准化摄像头 AXIS 输入适配：一像素一拍，支持 BGRX8888、Y8、RAW10、RAW12，按 SOF 锁存格式和阈值并输出二值像素。
- 实现双 1-bit 帧银行和跨时钟 toggle/ack 握手；只有完整帧在显示帧首切换，未完成/坏帧不提交，输入慢时重复上一帧。
- 实现板级无关顶层，输出 RGB888、HS、VS、DE，保留摄像头 D-PHY/CSI-2/I2C/XDC 和物理 HDMI TX 为实物确定后的集成边界。
- 增加 XSim 自检、Vivado OOC 综合脚本/约束和明日硬件信息采集清单。

## Decisions and Adoption

- 采纳 D-019：未知摄像头参数不阻塞中间 PL 链路；摄像头前端统一为 AXI4-Stream Video，显示端统一为并行视频。
- 采用双 1-bit BRAM 帧缓冲而非完整 RGB/灰度帧，当前 OOC 快照消耗 58 RAMB36；若需颜色/缩放或输入不支持反压，后续改为 VDMA/DDR。
- 保持 D-018：不复制 Artix-7 HDMI demo 的 XDC/OSERDESE2；实际 HDMI 物理层待硬件确认。

## Commands and Tools

- 读取项目规范、状态、决策、索引和相关会话记录。
- 检查外层 Git 状态与现有正式/参考工程文件。
- 运行 `whiteboard/scripts/run_fmc_hdmi_sim.ps1`。
- 运行 `vivado -mode batch -source .\whiteboard\scripts\synth_fmc_hdmi_core.tcl`。

## Validation and Evidence

- XSim 仿真 PASS：参数化 8×4 帧、异步摄像头/显示时钟、Y8 阈值、SOF/EOL、跨域切帧和 32 个 RGB 输出像素全部匹配；accepted=1、dropped=0、protocol_error=0。
- Vivado 2022.2 对 `xczu7ev-ffvc1156-2-e` 的 OOC 综合通过，0 error/0 critical warning；309 LUT、172 FF、58 RAMB36、1 DSP。
- OOC 约束假设摄像头 AXIS 100 MHz、显示像素 74.25 MHz，post-synthesis WNS +7.593 ns、无 failing endpoint。未执行 place/route、I/O delay、完整 Overlay、bitstream 或板测。
- `utilization.rpt` SHA-256：`3281efc540696ecefc48b70cfcea47c97bf305057a6f91c3b4bdd9c8601bd84e`。

## Errors and Corrections

- 第一版把两个大数组直接写在帧缓冲模块内，Vivado 报 `ram_style` 被忽略并准备展开为寄存器。立即停止该次综合，改成两个独立的标准简单双口 RAM 模块；复测后每银行正确推断为 29 个 RAMB36，共 58 个。
- 为避免握手数据与请求 toggle 同拍跨域造成采样次序风险，把请求/应答 toggle 比对应稳定 bank 位多延迟一级同步；仿真与综合复测通过。

## Files Changed

- `whiteboard/rtl/video_timing_generator.sv`
- `whiteboard/rtl/axis_binary_framebuffer.sv`
- `whiteboard/rtl/fmc_camera_binary_hdmi_core.sv`
- `whiteboard/tb/tb_fmc_camera_binary_hdmi_core.sv`
- `whiteboard/scripts/run_fmc_hdmi_sim.ps1`
- `whiteboard/scripts/synth_fmc_hdmi_core.tcl`
- `whiteboard/constraints/fmc_hdmi_ooc.xdc`
- `whiteboard/docs/fmc_camera_binary_hdmi_foundation.md`
- `project_workspace/DECISIONS.md`
- `project_workspace/PROJECT_STATE.md`
- `project_workspace/ai/INDEX.md`
- 本会话记录。

## Remaining Work

1. 获取摄像头/FMC 实物参数和卖方参考工程，先验证原始 CSI 图像。
2. 根据实际 RAW 打包接入或增加 unpacker/scaler/FIFO；确认源是否支持 TREADY。
3. 确认真实 HDMI TX/DP 输出硬件，补 Clocking Wizard、物理 TX、XDC 和完整实现时序。
4. 上板检查 300 帧连续运行、协议/丢帧计数、显示稳定性和阈值效果。

## Handoff Notes

明日不要先猜 lane 或寄存器。先拍下所有板卡/模组丝印并保存卖方工程；按文档第 6 节清单冻结输入格式，再把厂商 AXIS 接到 `fmc_camera_binary_hdmi_core`。如果厂商输出是 packed RAW、多像素/拍或不支持反压，不能直接连接。
