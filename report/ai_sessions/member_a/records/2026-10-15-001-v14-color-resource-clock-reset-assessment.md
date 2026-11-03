# AI Session: 2026-10-15-001-v14-color-resource-clock-reset-assessment
- Date: 2026-10-15
- Operator: Project owner
- AI product/model: Codex / GPT-6
- Participants: Project owner, Codex (single agent)
- Objective: 基于指定 dma_rgb565_debug_v14 评估白字误红蓝、显式IP/集中地址、150/200MHz与无遮挡历史重置。
- Status: Completed assessment; implementation not started
- Report candidate: no
- Related commits: none
- Related files: kv260-whiteboard-enhance/rtl/dma_rgb565_debug_v14/source

## Context Read
按顺序读取AGENTS.md、AI_DEVELOPMENT_POLICY.md、PROJECT_STATE.md、DECISIONS.md、INDEX.md，最近恢复死锁与B32存储优化会话、queued DMA会话尾部。较大状态/决策文件按当前检查点与最近决策定向读取。已检查Git状态（见本轮工具输出）。

## Task and Constraints
用户最终要求先评估并告知；本轮先做源码/证据审查，不修改生产RTL、固件，不上板。保留D-098核心图、vendor queued DMA、两个DDR环。

## Contributions
进行中。

## Decisions and Adoption
待补；评估建议与已实施分开。

## Commands and Tools
PowerShell/rg/Git，官方文档核查（若使用后补）。

## Validation and Evidence
静态审查进行中。新综合、实现、仿真、上板：未执行。

## Errors and Corrections
历史状态有相互覆盖的检查点、D-102重复编号；不将旧会话瞬时PID视为今日实板状态，不将HLS理论延迟当板端实测。

## Files Changed
仅内部工程记录（完成时补齐）。

## Remaining Work
核查颜色判定、资源、时钟、计数器重置语义并给出建议。

## Handoff Notes
本轮是评估；没有新性能/修复成功声明。

## Completed Assessment (2026-10-15)
### Color evidence
- 编译并直接运行指定v14的 hls/board_quantize_rgb.cpp（g++ -O2 -std=c++14，使用其rgb565.h）；源码SHA256与包manifest声明一致：58d72235d2948eb6ee80d341caf44178c8ad8467d51bb2854de939273ee73901。
- 新64x48、绿色背景、一像素横线probe；每例检查横线内40点。pure_white(255,255,255)和gray_white(115,115,115)均black40；微偏红白(120,115,110)经565展开为(123,113,107)，red40；微偏蓝白(110,115,120)展开(107,113,123)，blue40；淡红/蓝/绿分别40点对应色。
- label的中性判据为spread*255 < max(chroma/2,24)*maxchannel。默认chroma64时，上述原888微偏白满足中性，565展开后不再满足：10*255<32*120，而16*255>32*123。量化误差可将白字跨过分类边界，复现可见症状的机制；未取得当前实屏同帧中间图，不能宣布现场唯一根因已锁定。
- 另有own==neutral时邻域hint覆盖为彩色的路径，可能进一步传播误色；该路径风险来自静态审查，本probe的红蓝误色不依赖它。RGB/BGR互换不改变黑0/白ffff，不能单独解释白字红蓝。
- 建议将RGB565每通道量化误差纳入中性置信度/迟滞，白字高置信度优先输出black，彩色延伸只使用可靠彩色种子并保护中性字；用实际白/淡彩粉笔验证避免扩大中性区吞掉真彩色。保持已有局部笔迹检测和纯PL像素处理。
- tests/test_quantize.cpp已适配565，但参考复述相同判据，不能证明白字语义正确；test_quantize_color_continuity.cpp仍按888三字节构造与读取，后续必须适配，不能直接当565颜色验证。

### Resources and addressing
- 当前system_manifest.json资源声明（本轮未重新综合）：LUT78817/67.3%，FF93560/39.94%，BRAM127/144=88.19%，URAM8/64，DSP244/1248=19.55%，CLB14449/14640=98.7%；routed WNS+.380ns/WHS+.010ns。该manifest board_validation仍NOT_RUN，与后续会话板测记录不一致，本轮不修改历史封包或据此断言今日板态。
- v14 fetch仍有cdata中转和for循环整行data拷贝，不包含另一B32 LUTRAM优化候选；可移植存储重构思路，但不能直接复用不同格式/参数RTL而不验证。
- 控制基地址校正80040000/恢复80050000/量化80060000/监测80070000/XVC80080000已连续。所有后级共享HP0低DDR窗口0..7fffffff，rectify_mem NUM_SI11/NUM_MI1；摄像头vendorDMA使用HP2。统一逻辑地址表不能指定物理RAM位置，也不会自动消除AXI主端/仲裁。
- 建议RTL关键RAM/FIFO显式XPM或Block Memory Generator、关键算术DSP48E2/MultGen等，HLS用2021.2支持的BIND_STORAGE/BIND_OP明确资源和流水，再审查映射。禁止将所有并行行缓存做单一共享双端口RAM池；优先本地分bank就近放置、集中配置/地址表、保留两DDR环。DSP并无天然MMIO地址。现有板载DDR由PS硬控制器通过HP访问，不新增MIG接管PS DDR，也不更换vendor queued DMA。

### Clock assessment
- BD摄像头/ISP/vendor writer和HP2已200MHz；rectify/restore/quantize及HP0共100MHz，HLS period10ns。建议后级先150MHz目标，quantize可另设200MHz候选，rectify/restore需关键路径/存储/流水验证后决定，不能承诺全系统至少150已可达。
- CLB98.7%是当前布线风险，先降低fetch寄存器/大mux，再修改HLS约束、Clock Wizard、AXI时钟/转换、复位、ILA与signoff中硬编码周期检查，执行整机route与CDC检查。单改输出时钟或用当前全局WNS外推Fmax不可靠；DDR等待/多主竞争时FPS不随MHz等比提高。

### Clean-scene epoch proposal
- 当前没有单一全局恢复年龄计数器：block_state低16 TTL、q字节low4 quiet/high4 confidence、高8 occupied，另有pixel_quiet、background、previous。现控制器仅geometry generation变动触发initialize。
- 安全无遮挡后刷新记忆起点可复用initialize=1：background/previous/output=input，block_state=stable<<16（TTL0/置信0/旧occupied0，quiet为stable），pixel_quiet各byte=stable；并非所有计数清0。保留正常稳定性语义，随后从新reference开始恢复。
- 清场判定需独立的可靠无遮挡证据+几何稳定+曝光稳定+连续有效帧/时间，不能单靠motion==0（静止人物）或mask==0/TTL耗尽。大范围擦字/光变与人物要区分。推荐低成本块统计/空间形态先验证，必要时加入人员检测证据；不承诺已有算法能可靠识别人。
- 在restore空闲、按输入帧序号选定可信帧、调度器明确旧/新历史代次后PL内部重建，清场进入只触发一次并锁存/冷却；局部无遮挡优先局部参考更新，整板clear再全局更新。0.5~1秒可作为待真实序列调定的起点，不是已验证阈值。

## Validation Outcome
- 新执行：7个语义probe、280横线像素检查，结果见test_workspace/v14_assessment_20261015/quantize_probe.txt；这是故障复现实验，不是修复PASS。
- 未执行：现场抓帧、新HLS/RTL仿真、新综合实现、CDC分析、上板、提频/FPS/恢复质量测试。
- 官方参考（与项目2021.2匹配）：https://docs.amd.com/r/2021.2-English/ug1399-vitis-hls/pragma-HLS-bind_storage ; https://docs.amd.com/r/2021.2-English/ug1399-vitis-hls/pragma-HLS-bind_op ; https://docs.amd.com/r/en-US/ug974-vivado-ultrascale-libraries/XPM_MEMORY_TDPRAM ; https://docs.amd.com/api/khub/documents/GkFgXZaPmFnM~wTnslnIwQ/content 。只作资源语义依据，不将新版能力默认为2021.2可用。

## Errors and Corrections (additional)
- 初次按惯常文件名whiteboard_quantize.cpp/pl_stages.py/stage_pipeline.py读取不存在文件；通过rg找到真实board_quantize_rgb.cpp/pipeline_stages.py，无生产文件改动。
- board_artifacts下没有timing_result.json；改读取system_manifest.json明确标注其证据层级，未虚构本轮routed报告。
- 历史D-102中流式直连建议与D-098保留两环冲突，本轮不采用；本轮D-103只记录评估提案。

## Final Files Changed
- project_workspace/ai/sessions/2026-10-15-001-v14-color-resource-clock-reset-assessment.md
- project_workspace/PROJECT_STATE.md
- project_workspace/DECISIONS.md
- project_workspace/ai/INDEX.md
- test_workspace/v14_assessment_20261015/quantize_probe.cpp, quantize_probe.exe, quantize_probe.txt

## Final Adoption / Handoff
本轮只完成评估与缺陷复现；生产源、bit、部署包、板卡未改。建议次序：颜色语义修复及同帧证据→局部显式资源/缓存减拥塞→150MHz基线及选择性200MHz→可信无遮挡历史重建。具体实现尚待后续任务，不将建议列为已实施。
- Final status: Completed assessment; implementation not started.

