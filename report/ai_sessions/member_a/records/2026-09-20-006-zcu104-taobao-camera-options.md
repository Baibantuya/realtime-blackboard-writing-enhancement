# AI Session: 2026-09-20-006-zcu104-taobao-camera-options

- Date: 2026-09-20
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 结合 ZCU104 手册、现有项目接口和淘宝可购性，筛选可落地的摄像头模组与必要转接硬件
- Status: Completed
- Report candidate: No
- Related commits: None
- Related files: `project_workspace/PROJECT_STATE.md`, `project_workspace/DECISIONS.md`

## Context Read

已按规定依次读取根目录 `AGENTS.md`、AI 开发政策、项目状态、决策流水、内部索引、相关 OV5640/MES-FMC-LPC-IO/VID005/CS500 会话记录，并检查工作区文件和 Git 状态。外层工作区不是 Git 仓库；正式仓库位于 `blackboard-writing-enhance/`。

## Task and Constraints

- 用户要求结合 ZCU104 手册和项目要求，筛选淘宝可以买到并能用于项目的摄像头模组。
- 需同时满足或明确区分：商品可购、连接器机械兼容、电压安全、ZU7EV D-PHY/管脚合法、初始化与参考工程可获得、适配当前 720p30 DVP/AXIS RTL 的工作量。
- 淘宝动态商品页被浏览器安全策略阻止直接访问；使用公开检索到的淘宝商品 ID、厂商资料和第三方近期商品索引确认可购线索，价格和即时库存不作保证。

## Contributions

- 复核本地 UG1267：ZCU104 J5 是 FMC LPC，LA 总线位于 Bank 67/68；VADJ_FMC 出厂 1.8 V且合法值仅 1.2/1.5/1.8 V。板上另有底部 HDMI RX 和原生 PS DisplayPort 输出。
- 对照项目规范：正式首版目标为 1080p30，但当前已实现和验证的摄像头基础链路是单路 OV5640 1280×720@30、8-bit DVP RGB565；因此短期优先最小化接口变化并完成 720p30 bring-up。
- 确认小眼睛官方资料明确给出 `Double_OV5640` 淘宝商品 ID `650327894519`，支持 720p/1080p 等模式；比赛资料也指定该 DVP 双目模组。它与现有 40-pin/MES pin map 和 v2.3 配置语义最匹配。
- 找到正点原子、01Studio、黑金/ALINX、微雪等 OV5640 DVP 模组的淘宝销售或官方淘宝入口；这些可作为传感器备件，但没有与现有 MES 40-pin 的直插兼容证据。
- 识别出更完整的 ZCU104 MIPI 候选：Opsero `RPi Camera FMC OP068` 明确支持 ZCU104 LPC，并提供可构建的 ZCU104 参考设计；2022.1 版本已实现在 ZCU104 上使用 Raspberry Pi Camera v2/IMX219。其板载 I2C/GPIO 电平转换和可切换 MIPI 时钟路由针对多载板兼容设计。未找到 OP068 的淘宝销售证据，只找到 Opsero/Digi-Key/Sundance 订购渠道。
- 复核 Digilent FMC Pcam Adapter 官方兼容列表不含 ZCU104；不能因为 VADJ 支持 1.8–3.3 V 就推导 D-PHY 管脚兼容。延续此前结论，不采用 VID005+CS500 作为 ZCU104 原生 D-PHY 直插方案。
- 评估 HDMI 输出相机：淘宝可找到 IMX335/IMX415 等 HDMI 输出模组；ZCU104 确有板载 HDMI RX，AMD HDMI example design 也支持 ZCU104，但 PYNQ 文档明确重建 ZCU104 HDMI bitstream 需要相关许可。因此它是物理可接但软件/IP成本较高的备选。
- 给出 DVP 电平转换方向：D[7:0]、PCLK、VSYNC、HREF 等相机到 FPGA 推挽信号使用定向双电源转换器（例如 SN74AXC8T245 类）；SCCB 使用 PCA9306 类开漏转换器；复位/掉电/XCLK按实际方向另行分组。TI 规格表明 SN74AXC8T245 支持 0.65–3.6 V 双电源和 1.8↔3.3 V 高速传输，PCA9306适用于 1.8↔3.3 V I2C。通用 TXS0108E/BSS138 小板不作为约 42 MHz DVP 方案。

## Decisions and Adoption

形成 D-023 工程建议：淘宝采购首选保持 `Double_OV5640`，但采购目标应转向合格电平转换板；若允许非淘宝采购并接受 MIPI/ISP改造，OP068+RPi Camera v2 是更规范的 ZCU104 路线。HDMI相机、普通裸MIPI、Pcam和VID005均不作为当前低风险首选。

## Commands and Tools

读取项目上下文、相关会话、正式需求与 Git 状态；使用 `pdftotext`/`rg` 核对本地 UG1267；检索 AMD、Opsero、Digilent、TI、小眼睛、正点原子等公开资料和淘宝商品索引；尝试在浏览器中打开淘宝商品页，但被安全策略阻止后停止，没有绕过。

## Validation and Evidence

- UG1267 本地文本：Bank 67/68 为 VADJ_FMC；J5 合法电压 1.2/1.5/1.8 V；底部 P7 为 HDMI RX。
- 小眼睛 `Double_OV5640` 官方实验资料：淘宝店“小眼睛半导体”、商品 ID `650327894519`，DVP、500 万像素并列出 720p/1080p能力。
- Opsero OP068 官方资料：ZCU104 LPC 在支持列表；ZCU104 参考设计支持 4 路并标记 Vivado Standard 免费版；旧版 2022.1 文档和公开 smart-camera 实例证明 ZCU104+RPi camera v2 路线存在。
- Digilent 官方页：FMC Pcam Adapter 的明确兼容板列表为 ZedBoard、Nexys Video、Genesys 2、NetFPGA-1G-CML，不含 ZCU104。
- TI 官方规格：SN74AXC8T245 覆盖 0.65–3.6 V、1.8→3.3 V最高标称 380 Mbps；PCA9306支持 1.8↔3.3 V、400 kHz I2C/SMBus。
- 未执行：购买、卖家库存确认、转接板设计/信号完整性仿真、物理接线、上板采集、HDMI许可证测试或 MIPI reference design 构建。

## Errors and Corrections

浏览器无法直接打开淘宝商品页，因此不声称已看到实时库存/价格。搜索索引存在时间差，最终采购前须由用户在淘宝 App 复核。没有把“同为 OV5640”“FMC机械可插”或“VADJ范围匹配”误当作完整兼容证明。

## Files Changed

- `project_workspace/ai/sessions/2026-09-20-006-zcu104-taobao-camera-options.md`
- `project_workspace/ai/INDEX.md`
- `project_workspace/DECISIONS.md`
- `project_workspace/PROJECT_STATE.md`

## Remaining Work

1. 拍摄实物正反面和排针标识，确认 Double_OV5640 板载时钟、供电与 SCCB 上拉域。
2. 画出并审核 40-pin 中间电平转换板原理图，再决定购买现成模块还是打样；高速侧优先短走线、固定方向器件。
3. 到货后先只接电源/地并测各电压域，再连接控制和数据；ILA核验 PCLK/VSYNC/HREF/DVP 字节序后做 300 帧连续测试。

## Handoff Notes

用户若只问“现在下单哪个”，回答应是保留/购买小眼睛 Double_OV5640，不再买 VID005/CS500；同时明确没有合格电平转换板时不得将它经 MES-FMC-LPC-IO 直连 ZCU104。
