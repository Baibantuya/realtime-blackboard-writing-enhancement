# AI Session: 2026-10-09-006-pl-quality-debug-scanout
- Date: 2026-10-09
- Operator: Project owner
- AI product/model: Codex / GPT-6
- Participants: Project owner, Codex (single agent)
- Objective: 独立v6在v5基础上实现量化质量/阴影修复、矫正ILA+整帧统计、量化无CPU搬运DP输出，服务器综合实现并上板验证。
- Status: Complete for user-revised offline delivery; final board acceptance handed off
- Report candidate: yes
## Context Read
本连续工程工作已按入口读AGENTS/policy/state/decisions/index及v5构建/定位/实测记录；本次读取serverbuild/export/HLS/接口脚本。正式成果写kv260-whiteboard-enhance，内部流水仅project_workspace。
## Task and Constraints
用户授权D-082实现、新建文件夹、原Vivado服务器综合、下载上板。保留v5/rollback；先验证DRM地址/pitch及共享能力，再冻结接口。RGB/BGR契约纠正、不重复日常颜色验收。实际质量/IP统计必须证据，未完成不称通过。不用子代理。
## Contributions
独立local test_workspace/whiteboard_quality_ila_scanout_20261009和remote /data1/leisheng_codex/wb_quality_ila_scanout_20261009已创建；旧固件移至新版baseline_artifacts避免旧bit混入新交付。量化新7x7局部对比/强弱像素/3x3同色种子、输出pitch与纯红调色板代码已修改，未综合。板端DP实际pitch5888/address0x1017f5000/fourccBG24，明确小端BG24实际RGB字节，与当前PLBGR字节不匹配；新版固定BGR字节+RG24。首次低DDR PRIME导入EINVAL，尝试新版exporter kernel vmap/量化所有权保护，交叉编译PASS，临时板测后finally恢复旧驱动/应用。
## Decisions and Adoption
D-082由用户采用，具体v6接口/方案后续记决策。校正阶段保留像素算法，加诊断不盲目优化。
## Commands and Tools
Windows filesystem/Python/PuTTY/OpenSSH；leisheng@[private_ip] Vivado/HLS2021.2；板端PYNQ5.15.0-1027。
## Validation and Evidence
新综合/仿真/板测未执行。
- 更新：量化8全HD独立窗口参考/ROI/字节顺序/pitch5760与5888逐字节0差，恢复native64x48及1920x1080连续人物/阴影/弱白色及红色笔迹属性PASS。校正HLS C/综合/60小帧RTL调用PASS，新增cache hit/miss/加载字数/跨字统计仍保持逐像素参考一致。新版PS实际指针/借用scanout/量化保护及异步FIFO/drained-stop测试PASS。
- 低DDR PRIME第一次EINVAL，增加kernel vmap后实际DMA地址0x39200000导入/AddFB2成功；完整共享扫描后端12翻页事件PASS，三个buffer0x39200000/0x39900000/0x3a000000，pitch5888，BGR字节/RG24。测试finally恢复原module及v5应用，最近PID26814历史；新FPGA未加载。
- 量化HLS CSIM/综合PASS，首次RTL编译因strong保留字失败；参数名改strong_delta/weak_delta/in_roi，算法未变，重跑中。校正RTL日志DSP库启动X值OPMODE warning未导致比较错误；不把日志warning伪装时序结果。新的整机时序/资源仍未验证。
## Errors and Corrections
先尝试用户SSH默认配置中的其他主机，publickey失败；读原构建会话确认正确服务器[private_ip]，改用正确目标。未改其他服务器。
- 一次PuTTY上传在等待认证期间远端关闭，重试成功。PRIME导入失败未隐藏，尚未证明修正成功。使用实际Linux5.15 DRM FourCC定义确认BG24/RG24内存顺序，不重复颜色实物验证。
- 用户报告当前v5初始清晰后逐渐模糊；新版v6未加载，不能将该现象归为新PL。将曝光/恢复历史时间变化与三阶段连续帧对比纳入验收，不以首帧截图替代长期效果。
- AE当前固定中心patch实际包含斜板上方墙面；同实际frame0旧均值78.92、新板内均值51.01。新版按accepted四角双线性取9patch，启动3秒几何/曝光校准后冻结；显示参数BGR字节+RG24统一。新增彩色笔迹亮度判据低于中性白笔，避免蓝色因BT601权重低被擦掉；对应native8fullHD与8小帧RTL重跑PASS。
- 新恢复57小帧RTL调用PASS并导出，校正60/量化8均PASS；整帧只读AXI计数bank RTL独立握手/等待/背压验证PASS。初始系统入口因最终量化还差46秒未ready而安全拒绝，全部验证后重启；BD首次因2021.2不支持SV顶层module-reference失败，监控实现为Verilog2001兼容代码，文件改.v后重跑。
- 本机hw_server/Vivado2022.2只读枚举未找到JTAG目标，未捕获ILA波形；异步询问连接仍待答。新增只读计数器0x80070000供PS实际读取；无JTAG不妨碍其余板测，但不能称波形验收通过。
- BD模块地址段实际叫reg0而非HLS的Reg，按唯一实际段分配；模块频率属性100000000与实际传递99999000不匹配，改匹配频率且忽略被动ctl探针的接口自动推断。设计验证通过，当前整机synth/OOC阶段。原像素算法未随诊断盲改。
- 校正新增诊断后的native20全HD用例PASS，监控只读AXI独立握手与等待/背压计数RTL PASS。native512统计字段包含12有效word和保留零区；ILA需从最终routed DCP导出LTX并核对3core。
- 为逐渐模糊问题增加可选同序号rectified/restored/quantized快照（第1/20/60/120处理帧），每次调试CPU读取单独计数，生产默认不启用。此不属于DP输出复制；正常路径仍直接PL写扫描帧。
- 新增独立颜色语义属性发现“绿底白粉笔”被纯差分通道判为红（got0000ff vs expected000000），尽管原差分参考一致。停止限定v6 Vivado进程（不动板端/其他项目），改为保护观测RGB中性白色并用3x3彩色多数支持延续弱色，保留不同色与纯中性隔离。复测语义PASS，native扩展12全HD用例全部0差；量化重新综合/RTL，旧ready改名保留，系统必须等最终IP再启动。
- 该最终量化12次RTL/导出已PASS；一次自动审批服务额度耗尽导致后续网络命令未执行，用户“继续”后审批恢复，补传最终软件并重新启动整机。当前OOC依赖综合，尚无新版bit/上板结果。
- 离线参考对早期实际rectified帧得到28615前景像素，offline_quant_preview.png；中间/右侧多数文字显现，左侧弱字仍有断点。该输入是未完成AE的旧诊断帧，不能称当前板端质量通过；需要新版板内AE稳定后的同帧/连续验证。旧native回放脚本已更新新参数/diagnostics指针，未在此步骤重复运行所有旧数据集。
- 用户问综合核数，实查服务器96逻辑CPU/负载约10，旧脚本jobs1/maxThreads2导致仅约2–3核。限定停止本v6调度器，resume_system_parallel.tcl保留100%Complete检查点，仅reset未完成OOC和顶层，launch jobs6、synth线程4/general8。实际6Vivado任务同时活动，完成数28/39后继续增长；未重跑HLS/已完成IP。切换时旧已退出进程reset警告“Attempt to kill process failed”为状态清理，非板端变更。
## Files Changed
本记录；后续补齐。
## Remaining Work
独立clone、实际scanout/稳态帧探针、实现、测试、服务器新构建/signoff、匹配交付、备份部署和实际验收。
## Handoff Notes
基线v5当前源为PS定位修复版本，已部署PID16529历史。服务器原v5PS可能旧，必须上传本地当前定位修复源。凭据不写文件。
- ETA复核：顶层综合已完成，日志进入内部ILA插入；恢复IP实际OOC约115.5个BRAM tile，K26总144，量化另13，还需摄像头/互连/ILA，存在容量超限风险。HLS总268 BRAM18（guarded_state137、render52、顶层数组55），须核查并调整存储映射后重新验证，原45–85分钟估算不再可靠。新bit及新版上板均未完成。
- 状态实查：Vivado在内部ILA插入后提前write_debug_probes，因未实现core无UUID而退出；尚未启动布局布线，当前无本v6 Vivado构建进程。应移除该提前LTX导出，保留最终实现后导出；资源映射风险仍待处理。
- BRAM根因复核：旧v5整机实际79.5 tiles，旧restore OOC42；新restore115.5。新版build_restore_quality.tcl漏掉原run_whiteboard_hls/create_whiteboard_hls_project中的config_compile -pipeline_loops 0。新guarded_state报告dec96 BRAM18，weak/core各12，出现RAM_1WNR多读副本；旧dec RTL只有单读写端口。自动流水化/展开造成邻域数组复制是主因，先恢复原编译约束并重跑验证，不应把全部增长归于质量算法或ILA。
- 用户变更交付范围：板子断开，不执行最终v6上板。本agent恢复原pipeline_loops=0约束重跑验证/服务器OOC并行综合/实现，下载完整文件并编写可读交接，由另一个agent后续执行上板。8个OOC并行任务，每个综合最多4线程，general最多8；不将其说成96核满载。
- 修复约束后HLS顶层158 BRAM18（原268）；guarded_state27（原137），dec8（原96），weak/core各1（原12），证实自动流水化复制主因。相同guarded_state源SHA与正式原源完全一致。完整HD native属性PASS；13runtime+实际controller/ring慢消费者调度回归PASS并存服务器logs/runtime_handoff_regression.log。第一次本地复测因缺cv2/脚本需--package未执行，改服务器正确模块路径；首次native编译漏WHITEBOARD_NATIVE/WB_FULL_HD，纠正后执行PASS。完整依赖427MB本地SHA dc6f66ec58b198cca6644bf5c046f5aabaeb82f2de59f8fc6b7b5cae6b08777b。最终软件源/板包shared_scanout选择60Hz差异已同步，deployment也统一。

- 为利用空闲服务器，限定停止等待HLS的旧调度bash32511（未停止HLS32618/RTL）。已完成综合数据建立独立whiteboard_restore_ooc_snapshot，排除运行中的sim/sim_tb；独立导出IP并8job OOC与剩余57RTL并行。最终release门槛仍检查原RTL PASS及导出完成，未将提前综合称验证通过。
- 独立快照直接export先遇2021.2不接受open_project绝对路径，改cd build后相对名；随后导出数据库状态不足返回ap_source错误，独立副本补csynth_design刷新，再导出PASS。原RTL继续未中断。服务器Vivado新整机已开始，8jobs设置将用于OOC。交接文档含实际手工120帧证据命令与packedRGB/BGR数组解读。
- 恢复约束后57次RTL复测/最终导出已完成；新HWH将64bit指针显示为*_1/*_2并将返回值命名ap_return。finalize补规范化别名及high=low+4检查，软件按实际HWH导出JSON并重测非阻塞controller PASS；无板端操作。整机OOC26依赖完成，新的routed资源/时序仍待完成。
- 原57次恢复RTL PASS及导出完成，快照/验证RTL逐文件diff零差。整机首次新生成OOC六个视频IP遇日期revision 2610090928非法整数（同旧工具Y2K22问题）；并非算法/资源失败。仅失败run内runhls.tcl加原官方补丁，6线程并行独立重新导出，再继续原项目保留成功OOC。未修改共享Xilinx安装。
- 新restore实际OOC61个BRAMtile，原异常115.5/旧v5restore42；约束修复实际下降54.5。六个视频IP并行修复全部rc0/PASS。实际用于系统的3新HLS IP元数据/RTL归档已下载并纳入本地source/generated_ip_repos；待原最后smartconnect OOC进程78715退出后guarded resume，保留所有成功检查点。
- 顶层虽综合Complete，但检查Synth8-4442发现调试scalar tap只连HLS输入+monitor输入时覆盖了原interface驱动，生成HDL丢失控制AW/AR及输入握手；限定停止本版实现，保留所有OOC。修复为显式保留接口双方+监控三端；PS M02地址实际40bits，明确xlslice低7bits给HLS/monitor，避免直接40/7宽度CriticalWarning。新增生成HDL同线检查及top日志断线拒绝门槛，未将先前Complete称接口有效。
- 三端连线修复首次重复调用connect_bd_net因already connected退出，补idempotent连接；地址LEFT/RIGHT属性此BD未提供，改依据实际已核实40bit PS地址设置slice。最终BD修复PASS，27条生成HDL同线/地址切片检查PASS；两新xlslice无像素算法变更。新顶层正在重综合，恢复/量化/校正HLS及已完成OOC保留。

- 连线修复最终BD CriticalWarning0、HDL27path PASS；受影响共享SmartConnect重OOC，其余成功核保留；新顶层综合PASS且BlackBox unconnected pin0，恢复实际实现阶段。图像HLS算法与57RTL验证未改变。
- 第一次实现opt_design拒绝ILA FIFO时钟未连。save_constraints将debug命令写回pin.xdc且顺序/首核clock序列化为自动clk，造成重放失败；错误XDC已保存在evidence/pin_with_bad_serialized_debug.xdc。恢复干净pinXDC，改内部ILA为STEPS.OPT_DESIGN.TCL.PRE内存插入，禁止save_constraints/close_design。通过工具help确认write_xdc -type timing有效，signoff改只重放时序约束并拒绝debug命令，保留物理/ILA配置。
- 内部ILA启用storagequal后工具要求ALL_PROBE_SAME_MU_CNT至少2（默认1导致IP生成拒绝），明确设2并chipscope.maxJobs2。仅重启impl_1保留顶层/OOC；pre-opt hook生成成功、0CriticalWarnings，当前进入全局布局。Hook加入utils_1以供工程归档；typed timing-only signoff避免重放debug配置。
- 最终route PASS，实际WNS/WHS/WPWS +0.306/+0.010/+0.164ns；整机LUT77109/FF93761/BRAM137/DSP267，BRAM95.14%。三个ILA实际routed core齐全，typed timing-only clockfix成功并生成匹配bit/HWH/DTBO/bin/XSA/LTX。新版未上板。补restore_ms及重校准时photometry_frozen日志准确性，13runtime/controller/慢消费者回归再次PASS；所有源已冻结同步，完整服务器归档开始。

## Final Delivery and Verification
- Formal: kv260-whiteboard-enhance/rtl/imx219_quality_ila_scanout_v6; HUMAN-readable HANDOFF.md/DELIVERY_STATUS.md, source/generated IPs/software/kernel/Vivado/HLS/tests, board_package, evidence and original deploy installer.
- Local test root: test_workspace/whiteboard_quality_ila_scanout_20261009.
- Routed/signoff: WNS+0.306/WHS+0.010/WPWS+0.164ns, LUT77109/FF93761/BRAM137/DSP267/URAM8. Internal no_clock/unconstrained endpoints/multiple_clock0; no final methodology CriticalWarning; three cores ila_rectify_stats/ila_rectify_fifo/ila_hp0 actually in LTX from finalrouteddesign. Native/HLS/RTL/software verification listed in DELIVERY_STATUS.
- 37fileboardZIP SHA1fba7fdb909d1beda2fa80cd335c2515d97f7ab0098c66d1191d727a869c60f8; CRC+bundle/system manifests everyhashPASS.
- FullZIP1913597487bytes SHA1df7281b2dba57549ca1082859b8b7b078d5fb6ed8edca78094d111058235964; CRC PASS. Includes complete server generated project/HLS files,1.368GB compressed snapshot,446833518bytes dependencies,actual IP repos and exported hardware/report archive.
- Four server downloads hashes match. Server snapshot SHA301f5bc5bac64184a0438e00b50cc5177925e1d401acb4544c4b99a31255b4ea. See evidence/download_verified.json and downloads/SHA256SUMS.
- Resource followup actualrouted hierarchy: restore61BRAM/16464LUT/60DSP; quant13/8745/103; rectify7/9440/49; threeILA+hub22.5/8039/0; sharedDDR SmartConnect0/13857/0; othercamera/control33.5/20564/55. Sourceindependentreport captured, table included HANDOFF. Compared old79.5,restore+19/quant+12/debug+22.5 maingrowth. Width/framebuffers in DDR are not BRAM. Future reduce wide statsILA orfold/narrow quant classifier; not implemented in this delivery.
- Packaging corrections: oldCentOS tar -I interpreted gzip -1 as executable, switched pipeline tar|gzip -1 and reranPASS. Windowsflatdeployment JSONCRLF differed from originalpackagerLF despiteequalJSON, canonicalizedLF beforehash. Derived .dts moved fromboard_package to evidence so manifest lists only actualboard payload. Originalrawserver snapshot retainspre-packaging JSONnewline; valuesidentical, canonicalruntime inboardZIP/formal is authoritative.
- New logging restore_ms + accuratephotometry_frozen duringrecalibration; final13runtime/controller/FIFO slowconsumer regressionPASS.

## Final Files Changed
Entire independent v6 source/board_package plus finalize_v6.py/package_delivery.py/HANDOFF.md/DELIVERY_STATUS.md, compiledmodule ABI5/kernel archive,37fileboardZIP/fullZIP/sidecar checksums; formalv6 and handoffboardZIP; project state/decisions/index/session. V5 source/firmware retained. No Gitcommit requested or made; no password/token recorded.

## Collaboration Map
| Participant | Assigned task | Output | Verification | State |
|---|---|---|---|---|
| User | Confirm design and offline handoff scope | D-082/084 authorization, board disconnected | Direct instruction | Adopted |
| Current Codex | PL/PS implementation, constrained build, local packaging, documentation | v6matched37fileboard/full1.913GBZIP/HANDOFF | Realserver/native/RTL/static/hash/CRC results | Complete |
| Future agent (not started) | Actualboard installation, quality/FPS/directscanout andJTAG validation | Future board evidence/report | Must run on connectedboard | Pending |

## Final Remaining Work
Final v6 boarddeployment, real continuousquality/colour/FPS, people/shadow/erasure acceptance and actualILA capture未执行. User explicitly delegates these to lateragent; no currentboardconnection/auth/firmware action. Follow HANDOFF and internalhandoff file, retain rollback. BRAM95.14% is materialconstraint for subsequentfeatures.
- 2026-10-10只读分类核对：自研HLS为board_rectify_rgb/whiteboard_restore(含guarded_state)/board_quantize_rgb；实际手写RTL为wb_rectify_monitor和axis_ae_status(内部axis_luma_meter/ae_controller)。Xilinx视频demosaic/gamma/frmbuf/csc/scaler此次实际由HLS生成，属于官方IP；CSI/SmartConnect/AXI基础设施/ILA为官方IP，不称团队手写RTL。rtl目录的imx219_sensor_ctrl/i2c/video_core/axis_gamma等为保留源，不等于当前顶层实例。PS黑板定位/曝光/调度/DRM翻页为Python/Linux。无源码或bit改动。
- 2026-10-10颜色分类疑问只读核对：正式v6量化label函数仍含观测RGB中性保护、局部色度门限、红蓝绿分类与邻域同色票决，输出白/黑/红/蓝/绿；未删除分类或开展RTL重写。若现场只剩黑白，尚无同帧中间图/运行包证据，不能认定具体原因；低色度可能走黑字类，或上游/运行版本需要核对。无源码/固件改动。
