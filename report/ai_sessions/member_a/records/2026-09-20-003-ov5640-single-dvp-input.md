# AI Session: 2026-09-20-003-ov5640-single-dvp-input

- Date: 2026-09-20
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 将已知的双目 OV5640、40-pin 转 FMC 硬件收敛为单摄像头 DVP 输入，并接入现有二值化/720p30基础链路
- Status: Completed
- Report candidate: No
- Related commits: None
- Related files: `blackboard-writing-enhance/rtl/ov5640_dvp_rgb565_axis.sv`, `blackboard-writing-enhance/rtl/ov5640_camera2_binary_hdmi_core.sv`, binary framebuffer/video timing RTL, testbenches, scripts, constraints and integration docs

## Context Read

已按规定顺序读取根目录规范、AI 开发政策、项目状态、决策流水、内部索引、上一轮 FMC/二值化/视频输出会话及当前 Git 状态。

## Task and Constraints

- 用户确认摄像头为双目 OV5640，通过 40-pin 转接板再转 FMC 接入 FPGA，本阶段只使用其中一路。
- 公开竞赛资料描述该配套摄像头通过 DVP 接口传输；具体 40-pin/FMC pin map、I/O 电压、两路 SCCB 和时钟连接方式仍需转接板原理图确认。
- 不伪造板级 XDC。用户随后指定 `OV_SD_PCIe_200h_v2.3` 为参考；按该工程确认的 RGB565 而非先前假设的 YUV422 实现。
- 用户明确弃用旧 `whiteboard/`，要求有效成果全部整理到 `blackboard-writing-enhance/`；旧目录保留给用户稍后删除。

## Contributions

- 审阅 v2.3 顶层、357 项寄存器配置、SCCB、上电延时、DVP 8→16-bit 组包和 FDC，确认只使用 `cmos2_*`、RGB565 高字节优先、1280×720@30、24 MHz XCLK、约 42 MHz PCLK、SCCB 地址 `0x78`。
- 新增单路 OV5640 DVP→BGRX AXIS 适配，生成 SOF/EOL/TKEEP，并在下游无法接收或几何异常时丢弃当前帧。
- 接入二值化、双 1-bit 帧缓存和 74.25 MHz/3300×750 的 720p30 RGB888+HS/VS/DE 输出。
- 将 5 个 RTL、2 个 testbench、4 个脚本、2 个 OOC 约束和 2 份文档迁入正式仓库，更新 README 和正式项目进度记录。

## Decisions and Adoption

- 采纳 D-020：首版只使用双目模组第二路，不做立体处理；不复用 Pango 专用时钟原语。
- 当前 wrapper 以 `cmos2_init_done` 为采集门槛；v2.3 SCCB 表尚未移植为 ZU7EV 自包含控制器。
- 将转接板电平转换列为硬件连接前强制门槛：v2.3 相机接口为 3.3 V，ZCU104 FMC VADJ 不支持 3.3 V。

## Commands and Tools

- 读取项目上下文与 Git 状态。
- 检索 OV5640 数据手册、竞赛硬件说明和同类 40-pin 双目模块资料。
- 使用 Vivado Simulator 2022.2 从正式仓库运行基础帧缓存和 OV5640 DVP 两组自检。
- 使用 Vivado 2022.2 对 `xczu7ev-ffvc1156-2-e` 执行完整 camera2 核 OOC 综合和时序摘要。

## Validation and Evidence

- `scripts/run_fmc_hdmi_sim.ps1`：PASS，异步输入/输出时钟下完成二值整帧无撕裂交接。
- `scripts/run_ov5640_dvp_sim.ps1`：PASS，验证 RGB565 高/低字节、RGB888 展开和 AXIS 帧标志。
- `scripts/synth_ov5640_camera2_core.tcl`：0 error、0 critical warning；354 LUT、268 FF、58 RAMB36、1 DSP；两个时钟组均无 setup 失败端点，pixel clock 组最差 setup slack +9.668 ns。未执行实现、板级 I/O 时序或板测。
- utilization/timing 报告 SHA-256 分别为 `4f2057283114ac1c139d5019fc2db759a278c94b9d1ac17523f3d286251ea8c4`、`6ac2eddaa8dff193f3590919cf7781f6b35eb23b4dc3adb2c880be4b75bdfe9f`；构建目录被 `.gitignore` 排除。

## Errors and Corrections

- 首次 DVP testbench 每个输入字节错误保持两个 PCLK 周期，导致字节相位错位和超时；删除多余等待后仿真 PASS。RTL 无需为该 testbench 错误修改。
- 最初在型号未知时按 YUV/CSI 通用边界描述；读取 v2.3 后纠正为 DVP RGB565，并保留通用 AXIS 核作为可复用中间层。
- 成果最初落在旧 `whiteboard/`；收到用户目录决策后迁移到 `blackboard-writing-enhance/`，修改文档命令并从新位置重跑验证。

## Files Changed

- 正式仓库新增：`rtl/video_timing_generator.sv`、`rtl/axis_binary_framebuffer.sv`、`rtl/fmc_camera_binary_hdmi_core.sv`、`rtl/ov5640_dvp_rgb565_axis.sv`、`rtl/ov5640_camera2_binary_hdmi_core.sv`。
- 正式仓库新增：对应两个 `tb/`、四个 `scripts/`、两个 `constraints/`、两份 `docs/`；更新 `README.md` 和 `进度记录/progress_and_decisions.md`。
- 内部更新：本会话、`PROJECT_STATE.md`、`DECISIONS.md`、`ai/INDEX.md`。

## Remaining Work

1. 获取转接板型号/照片/原理图，先确认 40-pin→FMC pin map 和 3.3 V↔1.8 V 电平转换；不满足则禁止连接。
2. 移植 v2.3 的 OV5640 SCCB 配置、24 MHz XCLK 和 reset/power-down 时序，并按实际 pin map 编写板级 XDC。
3. 确定 ZCU104 实际 HDMI/DisplayPort 物理输出方案，完成时钟 IP、实现时序和板测；连续验证至少 300 帧。

## Handoff Notes

代码已集中在 `blackboard-writing-enhance/`，不依赖旧 `whiteboard/`。当前可作为数据面开发基础，但不能直接生成可安全上板的 bitstream；最先需要的是转接板原理图/料号。
