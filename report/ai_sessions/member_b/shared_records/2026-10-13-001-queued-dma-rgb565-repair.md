# AI Session: 2026-10-13-001-queued-dma-rgb565-repair
- Date: 2026-10-13
- Operator: Project owner
- AI product/model: Codex / GPT-6
- Participants: Project owner, Codex (single agent)
- Objective: 按交接修复采集回归，保持核心架构，优先原DMA适配，真实综合/签核/匹配部署与持续采集及整链验证。
- Status: Stopped by owner; handoff completed; restoration bug unresolved
- Report candidate: yes
- Related commits: none
## Context Read
依次读取AGENTS/政策/当前状态/决策/索引及session009、采集交接；长历史部分截断，当前有关结论已从交接和最近记录核对。Git根目录项目/测试主要未跟踪，不能假设干净提交基线。
## Task and Constraints
用户2026-10-13授权修改、综合、上板，解除昨日停止实验要求。D-098核心架构保持，优先保留vendor writer及内核queued DMA；只操作本任务工程/进程，保留历史可回退包。先原DMA能力证据，再最小实现，不默认继续单帧HLS采集。
## Contributions
待记录。
## Decisions and Adoption
待核实原IP/驱动能力后冻结接口。
## Commands and Tools
本地PowerShell/Python、远程SSH/Vivado/Vitis HLS2021.2、原部署脚本。
## Validation and Evidence
当前新仿真/综合/上板未执行。
## Errors and Corrections
待记录。
## Files Changed
本记录。
## Remaining Work
原DMA能力/板态检查；实现与验证；综合实现与签核；打包部署；至少1000帧采集负载验收及整链计数/FPS。
## Handoff Notes
昨天板态未知；失败bit不得作为已运行基线。新方案仍保持共享DDR和两级环形缓冲，不把像素处理搬到PS。

## Implementation Start / D-099
官方PG278 v2.3格式表与5.15 Linux驱动无RGB565，采用camera888/PL校正输出565/下游565，保留vendor原DMA和固定框图。新候选已创建，原RGB888 fetch核复用，小窗口4/32/16words/4sets/2ways/32tokens需重新RTL测试；wrapper单独计算src_words=(pixels>>2)*3，不能误把565输出count用作888源边界。新native模型读888三字节、跨word拼接，输出pack565。运行PS以原v4l2_rgb读取uint8三通道、恢复原媒体video0配置；ABI6仅用于现有buffer lease/scanout，不加载wb565_control。
板SSH可达但密钥认证失败，已询问登录方式；未改板。服务器密钥登录成功，工具路径/既有候选已核对。本地首次脚本使用Python3.9不支持的Path.write_text newline参数失败，改open(newline)后仅本任务新候选重跑，未覆盖旧候选。rg PowerShell通配参数一次无效，改目录+glob。

## Verified Inputs and Build Progress
- Native mixed rectifier: g++ -O2 -ffp-contract=off, 20 full1920x1080 cases PASS, including crossword source decoding/output565, same-address refresh, invalid geometry atomicity and guards. Software syntax compileall PASS. Native executable/evidence located test_workspace/queued_dma_rgb565_20261013.
- Reused downstream IP source/hash gate initially found only whiteboard_restore.h comment differences vs the exact RTL-built server header. Copied exact validated header (no logic differences), then seven source hashes/398 reused artifacts matched. ABI6 wb_frame_pool.ko reused only after exact C source hash match; new kernel compile not claimed.
- HLS mixed rectifier C/RTL PASS with actual63 top calls from20+tail case and identity/invalid followups; export in progress then completed to fresh candidate IP. New HLS changed internal fetch FIFO ports; inspected generated render and updated wrapper to consume pixel-count FIFO with separate source-word count. No assumption of old p_read/p_read1 interface reuse.
- Strict RGB888 fetch and new FIFO wrapper each5 cases, total10 actual xsim PASS at selected4pending/32lookahead/16words/4sets/2ways/32tokens. C99/Python independent references and AXI accepted requests/backpressure/tails/invalid guard checks PASS. First wrapper elaboration failed due TB hierarchical dut.active vs dut.core.active; corrected TB and reran matrix. HLS C/RTL baseline and strict wrapper are separate evidence, not full hybrid-system co-sim.
- Initial strict launcher selected bundled HLS Python3.6 and failed future annotations; changed to recorded Python3.11 runtime. Initial background launch output logs directory absent; created task logs and relaunched. Old launcher ended after HLS/failed strict wait; resume only new task process.
- Discovered old565 evidence/baseline_camera.dtbo actually disables vendor writer. Replaced new candidate seed with preserved v6 original camera DTBO (enabled vendor DMA/media); added overlay gate rejecting disabled writer/media/custom master. Original old candidates untouched.
- Board authenticated using user-provided login input, not recorded/stored. Readback kernel5.15.0-1027, uptime20min, FPGA operating boot base; no currentvideo/wb nodes or old pipeline/fpgautil processes. Board recovered since yesterday; no reload/reset performed in this turn yet.
- Fresh remote system /data1/leisheng_codex/wb_queued_dma_rgb565_20261013 has verified IP closure/BD validation and is generating system targets; top synth/place/route/signoff/board remain pending. Original core architecture maintained. Capture>=1000frames PS-load gate is included before three-frame all-pixel smoke in deployment.

## Owner Steering: Performance First / Pre-DDR Verilog Formatter
用户先要求暂停混合888源方案并指出性能目标，随后明确用Verilog在ISP后连续转565、无中间帧存储、写DDR供565校正。v12上板暂停，保留正在完成的route作为对照。新增D-100，后续独立v13实现连续AXIS位切片+vendor YUYV两字节运输（数据逻辑565）+真实V4L2格式subdev，原DMA/master预排队不替换。文档映射仅方案依据，实际byte layout必须验证；无需CPU搬帧，不回到单帧HLS。
当前B32历史稳态7.5927FPS/rectify真实69.98455ms；恢复/量化host161ms混入调度，不能倒数认定IP容量。v12未板测、不代表性能提升。板仅恢复先前1080p EDID并保存恢复前内容，未装载任何新候选。

## v13 Continuous Formatter Implementation / Verification
- Independent formal source rtl/dma_rgb565_stream_v13/source created. PL rgb888_to_rgb565_axis is combinational wire concatenation + reset/VALID/READY/SOF/TLAST passthrough; no FIFO or frame buffers, connects scaler to original vendor framebuffer writer. HAS_YUYV8=1 enables two-byte byte-preserving carrier; logical shared-DDR contents remain standardRGB565. Original VIPP and descriptor DMA retained.
- New wb_rgb565_format is format-only V4L2 subdev (RBG888 sink/UYVY16 source), no misc master, DMA scheduler, pixel memory or AP_START. Original labelled B32 camera DTS restored and linked through the format subdev, with yuyv in vendor formats. V4L2 DMA helper retains QBUF/STREAMON/DQBUF ownership, now YUYV fourcc/stride3840 and uint16 logical pixels; PS uses sparse RGB expansion. Rectifier returns to exact old565 source/IP and single-word fetch.
- New native565 fullHD20 cases PASS. Exact nine source hashes and841 IP artifacts reused from actual old565 rectifier/quantizer and P1 restore; strict565 original report preserved, not claimed as newly rerun. Formatter actual xsim200MHz65536pixel coverage/all565 values/SOF/TLAST/random gaps/backpressure PASS,21910 stalled cycles, no storage.
- First formatter elaboration lacked module timescale; added timescale and reran PASS. First kernel build found Ubuntu5.15 backported v4l2_subdev_state vs assumed older pad_config API and generic variable driver caused driver_init collision; corrected to actual header API and wb_format_driver. ARM64 build retry PASS, exact5.15.0-1027-xilinx-zynqmp vermagic; GCC10.3 versus kernel11.4 compiler warning retained, not hidden. Private150MB header clone remained task-local, no shared tool/header writes.
- v12 route/signoff actuallyPASS WNS0.483/WHS0.010ns, but remains performance-unmeasured superseded comparison and NOT deployed at owner steering.
- v13 fresh full-system build started PID48918 /data1/leisheng_codex/wb_dma_rgb565_stream_20261013. Copied v12 IP cache into new task's own .cache to reuse unchanged synthesis inputs; no old bitstream reuse. Final newroute/signoff/package/deploy/byte-layout/1000frames/FPS pending.

## v13 Integration and Acceptance Gates
- Vivado2021.2 module_ref rejected SystemVerilog top. Converted storage-free formatter source to pure Verilog .v, retained failed initial log system_before_verilog_ref_fix.log, reran same RTL test PASS and new BD/build. No function change or bypass.
- New top synth PASS0Errors/0CriticalWarnings; generated scaler->formatter->vendorDMA tenAXIS connections plus HAS_YUYV8=1 HWH check PASS, evidence/formatter_wiring.json. Placement underway; finalroute/signoff/board pending.
- Acceptance now includes actual sensor solidred/green/blue patterns resolved from this driver's menu/controlIDs, small central patch RGB565 colour/byte validation, finally restore original controls; then1000frames/mainthreadload/sequencegap+badframe checks and exact vendor fmt12/stride3840 readback; then3fullpixel rectify/init/quant reference. These board tests have NOT_RUN yet, no syntheticPASS is substituted.

## Freeze diagnosis resumed / owner observation
用户观察显示停留单帧、黑字红蓝交叠，随后明确优先卡死定位并要求使用现有ILA、允许重载复现。当前只读寄存器矫正AP_CTRL=1、恢复=1、量化=4，进程20256仍在，日志2/1/1未前进。现有ILA覆盖rectifier FIFO及HP0握手；本机Vivado2022.2 hw_server启动但没有JTAG targets，[private_ip]:3121 TCP失败，不能声称已抓波形。SSH已重新连接；未重载或释放在途buffer。下一步1920宽恢复非初始化RTL复现及JTAG连接确认。


用户要求板端重启程序定位，必要时修ILA。现场恢复initialize=0,width1920,height1080、参数/低DDR地址读回正常，AP_CTRL1不结束；矫正1量化4。原runner stop4秒后SIGKILL不适合在途PL，进程finally无限等idle。保存板history/v13_freeze_before_restart_20261013.log后执行板reboot安全恢复，拟同bit重新加载并板端隔离恢复。HD RTL应用户指令主动终止，COSIM FAIL是终止造成，不作为死锁证据。当前HWH/BD无AXI XVC桥，旧xvc默认0x80040000与当前矫正冲突，禁止启动旧脚本。

板reboot后网络ICMP仍响应、22拒绝，多次重连失败，已请求用户物理断电重上电。run_stage_pipeline.py增加except立即打印traceback及三核AP_CTRL，然后保留原finally安全等idle；尚未板部署/复测。真实camera直接喂RestoreStage板诊断脚本已准备，仍未执行。未重启HD仿真、未随意改恢复算法/FIFO。ILA桥接补全待准确工具接口核实，不宣称完成。

用户物理重启后SSH恢复，uptime2min，旧pid20256不存在。按原runner prepare_check39filePASS、同版固件activate reload=True启动板端恢复隔离，临时manifest只在内存中将smoke/live替换为诊断启动，不修改保存的deployment.json。输入直接原camera DMA565物理buffer，恢复初始化/正常调用，不并发校正量化、不整帧PS转换。结果待日志。

板端恢复隔离诊断修正SimpleNamespace遗漏nbytes（首次在启动前异常，不是硬件失败），重跑PID2622：initialize完成18.499575ms、initialize0超时10s/AP_CTRL1；输入持有camera DMA lease，其他两核没有启动。状态低DDR经/dev/mem及/proc/pid/mem访问被内核拒绝，未读取成功，不编造阶段进度。决定D-101，新debug_v14复制独立源码/IP，模式2XVC0x80080000，替换statsILA并添加恢复FIFO/FSM/六AXI接口握手，仅诊断改动。第一次服务器python3.6 copytree参数不支持，改兼容后复制完成，Vivado真实build启动，签核/上板波形待完成。原v13固件保留。

XVC bridgeBD实际配置2/softBSCAN1，PSM06接口、100MHzclock/reset、0x80080000分配及validate通过。独立私有tool_overlay/datepatch已配置（初始未配overlay进程在IP生成前停止并保存log后纠正重启）。恢复探针在已routed v13网表核对进行；仅顶层synthDCP中HLS内部黑盒故内部count0，不能当探针不存在结论；改最终routedDCP。serve_xvc.py要求当前PL.bitfile_name匹配、HWH桥地址及模式匹配，不可对旧bit运行。

新v14顶层synth155Infos181Warnings0Critical0Errors PASS。探针宽泛匹配在旧routed确认内部flags155/167+FSM400存在；缩到dataflow直接flags和直属FSM，AXI地址只低32bit以控制BRAM，不扩大图像架构。初次optpre因proc内部set name覆盖core name失败，改net_name并保存失败log，resume_implementation重新启动（不重跑已PASSsynth）。软件ZIP解压遇到__pycache__子目录，明确忽略生成cache再解压，仅新v14路径。当前route/signoff和真实XVC波形仍未执行完。

Vivado2021.2实现明确报：AXI-to-BSCAN bridge存在时不支持netlist debug insertion，要求instantiationflow。不是算法/时序错误。改为原恢复exported Verilog只读dbg_render64+topFSM52导出dbg_restore128，并更新IPXML输出端口；所有原HLS算法/FIFO深度/算术和AXI原端口未改。新增三份debugRTL/XML哈希与bit映射evidence/restore_debug_taps.json，不再声称这些artifact与旧IP逐字节相同。BD实例化restoreFIFO128、restoreAXI低32地址/握手、HP0握手三ILA，删除netlistprehook重新综合。原旧IP已保留before_debug_tap，正式源码增加复现patch脚本。

NativeILA首轮BD在probe44处未生成pin，已保存失败log。改为显式Native模式、RTL纯线组合每个恢复AXI接口打包80bit，只需6probe，避免高数量probe/inference问题；HLS原DDR端口只读旁路、低32地址含义见restore_axi_probe_map.json。HP0单bit握手11probes、恢复internal128probe保留。当前第三轮独立debug构建中，尚未完成硬件工具链闭环。

ILA原生接线曾出现NULLsource：手动观察接口pin会覆盖原BD接口连接，必须显式补SmartConnect原peer。已停止仅本任务两次build进程（一次最初cwd精确筛选没匹配旧process，随后按已核对PID纠正），没有动其他工程；重启只一个build。现在AXI三端同网生成HDL gate拒绝断连/常量，避免调试bit更改DDR功能。最终2ILA，不手工tap HP0。全部失败日志保留；当前板PID2622仍保持真实恢复单独卡住，调试bit未部署。

NativeBD现在实际完成，无NULLsource再发生；生成HDL restore_axi_three_endpoint_checks=70 PASS，internal128 + sixAXI80共7probes已连接两ILA，原monitor生成AXI check继续PASS。新真实synth开始，截止当前新时序、XVC枚举/波形未执行。

当前native整机所有OOC/顶层synthPASS，opt_design/DebugHub生成及DRC0Errors完成，place_design仍进行。进度措辞纠正：globalplacement已完成不代表整个place_design完成，详排/legalization还在进行，尚未route/signoff。板恢复隔离PID2622持续51min仍STALLED，无并发校正量化。

Native最终流程place完成、route实际完成0Errors/0CriticalWarnings，DDR三端debuggatePASS70；routedDRC完成无错误。最终timing/signoff/nativebit+HWH+LTX导出仍在进行，勿用估计WNS或syn黑盒util0当最终证据。板端根因还未确定，已隔离到恢复normal路径，不宣称修好。

保存restore_isolate_before_debug_v14板historylog后执行sync/reboot-f，板30秒左右恢复22并重新登录；旧诊断buffers随整个SoC复位释放，没有先SIGKILL释放在途buffers。这次直接复位成功，未再次要求物理断电。Native route实际完成292Infos21Warnings0Critical0Errors；初始routed reportWNS+.797/WHS+.010（真实PSclock约束复核尚待完成，不能当最终signoff）。开始bitstream写出，XVC实际捕获仍待进行。

新v14真实PSprimary-clock finalsignoff PASS WNS+.797/WHS+.010/0failing，log新值与重新写出的timingjson核对，不是复制v13旧+.079。ROUTED_DEBUG_CORES实际dbg_hub+ila_restore_axi+ila_restore_fifo。Routed实际LUT77535/FF92770/BRAM118/URAM8/DSP240/CLB14328(97.87%)。最终bitstream生成完成0Critical0Errors，正在最后XSA/export/package。localdeployconfig切v14，before_v14备份保存；新波形根因尚未得到。

上板v14初始sealedSHA484c22... 42files/板preflight40PASS，bitmanager载入PASS，restore-only重现initialize18.4973ms/normal超时。PYNQDebugBridge要求ReprDict而Overlay传普通dict，独立history服务先ReprDict适配后端口ready；local2022.2仍不能枚举，改精确recv/sendall、满字32bit移位的独立history rawXVC服务（不改vendor库/FPGA）。经PC反向SSH2543至server，serverVivado2021.2/hw_server3123成功枚举两ILA、触发并导出各1024实际samples，CSV/ILA已下载。不能把host/OS也变化的对比证明为仅版本根因。用户接JTAG后local识别xck26，但当前debugbridgeC_BSCAN_MUX1禁用fallback，JTAG无hub；用户随后明确不再补，使用可用路径分析。已停止XVCserver/hwserver仅本任务进程，未改JTAG配置/FPGA。最终wave：topfsm0x400000=state23等render；neutral/eroded/opened/broad_full_n0，pixel/thin有数据，所有外AXIVALID0/READY1。compose内流水读使能不按颜色门控，类别集中内部AXI事务等待；具体条件还未确认。拟同bit真实board宽度对比，已保存script，复位重新加载待执行。

Owner stopped further work and requested findings/handoff to nextAI. Same v14 realboard width32,height16 initialize1.1249ms/status0 PASS; normal10s timeout, later widthlist NOT_EXECUTED. This rejects fullHD-only long-row/FIFO theory. Subsequent XVC re-enumeration failed afterreset and3123 bindoccupied; do not infer only toolversion cause. Final handoff restore_freeze_ila_handoff_20261013.md includes actual raw/decoded1024samples, exact unresolved composewait, currentstuckPID2699/XVC2660, artifact/servicehashdifferences, safe reset, owner stop/noJTAGchange. Investigation halted; bug NOT_FIXED, live/FPS NOT_VALIDATED. External AXIidle does not prove all outstanding transactions retired; earlier categorical DDR-exclusion corrected.
