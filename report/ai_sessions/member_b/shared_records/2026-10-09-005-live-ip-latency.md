# AI Session: 2026-10-09-005-live-ip-latency
- Date: 2026-10-09
- Operator: Project owner
- AI product/model: Codex / GPT-6
- Participants: Project owner, Codex (single agent)
- Objective: 优先查实际低帧率由哪个IP导致，并记录两侧笔迹缺失的诊断范围。
- Status: Completed; actual bottleneck measured and runtime restored
- Report candidate: yes
## Context Read
本连续工作已读取AGENTS/policy/currentstate/decisions/index及sessions003/004、v5源码；定位已上板成功，最新实测约1.64输出FPS，三个阶段持续工作。
## Task and Constraints
用户主要要求定位低FPS来源；两边文字淡/未识别若需PL修改先说明，不修改PL或量化。只进行实际阶段计时，临时安全停止再恢复当前版本，不强杀、不加载FPGA、不假定IP瓶颈。
## Contributions
计划真实1080p相机帧逐阶段计时，区分首次恢复初始化/稳态处理；同一输入/输出环和寄存器参数，重复多帧，不将单阶段串行测试当重叠流水FPS。
## Decisions and Adoption
诊断测量，无实现/架构变化。
## Commands and Tools
PuTTY、板端PYNQ Python、原stage controller和安全stop/resume。
## Validation and Evidence
真实1080p8次launch，首帧恢复initialize23.72ms排除，后7帧稳态中位数：rectify603.130752ms(603.050112–603.834769)、restore395.093332ms(395.000360–395.317424)、quantize16.169482ms(16.156041–16.300273)。控制器launch到完成含短轮询/完成同步开销，非精确硬件周期。Camera已有完成帧acquire中位0.01974ms不是sensor帧周期。三IP串行隔离计时+后台相机持续采集，不将时长求和当重叠流水FPS。rectify单实例上限约1.66FPS与实流水1.64FPS吻合，restore下一个上限约2.53FPS，quantize非主因。
- JSON与rectified/restored/quantized实际NPY及PNG保存test_workspace/ip_latency_20261009，板端ps_ip_latency_20261009。照片是诊断初始8帧/AE未更新，ISP刚启动历史初始化可能含WB过渡，不能把所见恢复绿色块当当前steady-live故障证据；字迹质量未验收。
- 实测后按原流程prepare/media/3frame smoke PASS，无FPGA重载，PID16529 alive=true；后续gen1locked/safeTrue/edges8each，quantized76→83/bad0，恢复持续输出。固件/量化/交付处理代码不变。本会话新综合/资源/硬件周期计数未执行。
## Errors and Corrections
明确恢复初始化仅23.72ms不能代表395ms稳态；最短cameraacquire只是队列已有帧，不能推断50000FPS。未把串行总耗时1.014秒当流水帧率，未将未测AXI stall归因为DDR带宽耗尽。
## Files Changed
test_workspace/ps_localization_20261009/benchmark_ips.py和ip_latency_20261009证据；内部session/state/index。板端诊断脚本/证据与运行state/log更新，处理源码未改。
## Remaining Work
本次IP定位完成。优先改PLrectify流水/访存，再评估restore优化；用户要求需要改PL先说明，尚未实施。量化阈值/真实steady笔迹丢失与红蓝反向另行修正，PS可配置通道/阈值，邻域判色需要PL。
## Handoff Notes
定位版PID15508为本会话前最新进程，后续停止/恢复时以state为准。

## Follow-up: Why Warp Is Slow; Color Still Reversed

## Follow-up: Owner Architecture Diagram Check

## Follow-up: Proposed Stroke Continuity and Shadow-Ghost Repair

## Follow-up: PL Direct Write to DP Scanout

## Follow-up: Owner Requests Next PL Scope Before Work
- 提出D-082：量化局部强弱笔迹/颜色连续和阴影拒绝，若恢复历史已污染必须联动可靠提交保护；校正先诊断ILA/整帧计数而非未经证据同时大改算法；量化直接写DRM共享扫描帧需pitch/address/ownership，PS驱动配合。独立debug版本保留v5并匹配所有交付/时序验收。用户要求先说明，未开始PL/PS修改或构建。
- 用户问量化后是否可不经PS整帧复制而直接到DP输出缓存。核对当前QuantizeStage独立低DDRbuffer/32bitdst及无stride接口、历史session2026-10-01-003实际DRM stride5888/address0x1017f5000与dense5760/low31bit不兼容；这是历史证据，不冒充当前DP地址已测。
- 方案优先量化IP直接写由DRM拥有的可用扫描帧，完成后PS仅提交pageflip/地址，无CPU像素复制。需要低DDR可共享DMA-BUF/DRM导入或扩展IP及HP地址范围、量化dst_stride、固定BGR契约、cache/ownership/fence和双/三缓冲释放保护。不能只改dst地址而忽略pitch/highaddress，也不能把任意PYNQallocate帧直接交给现DrmDriver.writeframe（官方要求newframe创建，提交后禁止修改）。备选硬件二维DMA复制dense量化缓冲到DRM缓冲，仍有DDR复制但无PSmemcpy，当前尚无该搬运模块。
- 引用官方PYNQ drm API文档核验ownership；无代码/板端更改。减少finalCPUcopy不会解除当前rectify603ms首要瓶颈。
- 用户询问量化字迹淡/不连续、行人经过后黑色色块如何解决。只读quantize_reference/whiteboard_ip及formalrestore源码，未改代码/硬件。现量化ink_level130/chroma32逐像素固定绝对判据；饱和五色输出本身不淡，视觉淡可来自有效笔迹像素大量被置白/断裂。先比较实际校正/恢复/量化三阶段steady同帧，初始benchmark照片不能代替steady质量定位。
- 待审：相对局部板面亮度的强/弱笔迹阈值，强种子带动相邻弱笔迹、颜色延续且不跨背景/笔色传播；保留中性白笔黑输出，邻域判色和局部照明需要PL量化改动，PS调现有阈值只能缓解。阴影不能通过单独降低阈值解决，需区分宽区域亮度变化与细笔迹局部正对比度，背景可靠提交禁止可疑遮挡/阴影/AE变动区域，仅用干净历史显示；离开后按与可信背景一致恢复，避免人站定静止就学入背景。
- 默认restore hold300按帧计，现~1.64FPS约183秒的TTL尺度（不等于必然每次残留这么久），可能放大恢复滞留；需测实际TTL/commit/mask再调duration目标，用当前处理FPS换算帧数。PS可调现有hold/delta/quiet等参数，新的可靠提交/阴影判据需PL恢复变更。不能仅形态学开运算消块，容易抹细字；bootstrap历史必须无人且ISP/AE稳定。方案未采用/未测试，PL改动须先告知用户。
- 用户提供PL/DDR/PS架构图，核对实际run_stage_pipeline、FrameRing、auto_exposure代码。图主像素链camera→sharedDDR→rectify→ringA→restore→ringB→quantizer成立；关键差异：PSdetector/matrix生成读取相机共享lease.frame，非rectifiedringA；PL校正模块做整帧warp非求H；camera共享池4slot、两个中间环各3slot；quantizer.output后PSnp.copyto到独立DisplayPort扫描帧，最后PSDRM/DPDMA输出；restore背景/前帧/状态DDR未画出；AE经V4L2驱动控制sensorI2C，DDR不写寄存器。无实现变化。
- 用户询问校正是否只是矩阵计算并再次报告红蓝反向。读取实际HLStop：矩阵由PS/acceptedH保持；PL每帧遍历2073600输出像素，coordinates算两浮点商取得源位置，fetch按变换地址读取packedRGB888/跨32bit字，4条64byte小缓存miss时同步填16word；fetch逐像素循环无外层PIPELINE，pack循环亦无外层PIPELINE。coordinates请求II1不等于整IPII1。串行取数/缓存填充是源码明确优化点，但各具体算术/AXI stall占比未测，不能给出独占根因。
- 理想100MHz一像素一周期约20.7ms，实603ms相当29.1cycle/输出pixel（非内部单loopII或实测cyclecounter）；矩阵锁定不省每帧完整重采样。PLrectify应优先优化；单纯PS检测优化无法越过当前单IP1.66FPS上限。
- 显示BGR固定约定；此前用户授权仅定位，通道配置没变，所以红蓝不会自动修复。当前仍反向是用户实际反馈，未重复颜色验证，未擅自变更PL或猜测具体输入字节契约。通道PS修正仍待落实，与本次性能诊断分开交接。
