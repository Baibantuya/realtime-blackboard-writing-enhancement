# AI Session: 2026-10-19-021-v21-server-build-board-trial
- Date: 2026-10-19 (Asia/Shanghai)
- Operator: User
- AI product/model: Codex / GPT-6
- Participants: User, Codex; single agent
- Objective: 用户授权服务器综合/实现、低频定时检查、下载匹配板包并上板测试v21。
- Status: In progress
- Report candidate: no
- Related commits: none

## Context Read
已按顺序阅读AGENTS、AI_DEVELOPMENT_POLICY、最新PROJECT_STATE/DECISIONS/INDEX、session020及既往session012服务器构建记录；Git正式目录整体未跟踪，无更深AGENTS。已读v21 README/资源门禁；需补齐实际系统与UI流水接入，不能把仅HLS核当完整可部署系统。
## Task and Constraints
本轮明确授权解除SOURCE_ONLY构建/部署限制，远端构建、定时跟进、下载、上板均在范围内。保持v15恢复源冻结和既定PL资源上限，要求匹配源码/HWH/固件/软件及真实资源时序证据；旧v20实验时序放行不视为v21自动放行。
## Contributions
待补充。
## Decisions and Adoption
待补充。
## Commands and Tools
待补充；不得记录SSH密码/私钥/令牌。
## Validation and Evidence
新服务器/HLS/系统/板卡检查尚未执行。
## Errors and Corrections
待补充。
## Files Changed
本记录；后续补充。
## Remaining Work
服务器/构建路径核对、HLS与整机集成、实际UI双环接入、本地预检、提交后台作业和定时跟进；通过后下载、匹配封包、上板验收。
## Handoff Notes
旧板卡PID为历史事实，本轮需重新核对，不能据旧记录假定存活。

## Current checkpoint (scheduled continuation)
- 已采用：解除STOP，增加build_scene_server.sh及隔离tool_overlay/日期补丁；用户授权仍覆盖后续整机实现与上板，无需再次询问。
- 远端独立目录：/data1/leisheng_codex/wb_scene_v21_20261019/dma_rgb565_scene_v21。后台PID25249，logs/launcher.log、logs/scene_hls.log、evidence/hls_status.txt。归档test_workspace/v21_server_20261019/v21_hls_input.tar.gz，SHA256 6ed3e1d8f93d77debdcf2388252e9da926d3b4835aec15c973315033dbe4cc04，SCP后远端一致。
- 真实结果：2021.2 HLS Csim errors=0，开始csynth；RTL/cosim/export/OOC/整机route/新资源/板测未完成，不能称已综合成功。未改v15冻结算法，未切换板卡。
- 定时任务：App heartbeat id=v21 ACTIVE，15分钟一次，本线程推进全任务。首次创建缺少destination失败；修正destination=thread后成功，只有一个任务。无既有automation目录/任务可复用。已使用openai-docs技能核对定时能力，官方说明要求本地环境运行。
- 错误纠正：普通sandbox SSH被网络权限阻止，使用已授权require_escalated后成功；首次查找历史目录路径错误，后定位/data1/leisheng_codex，未改旧工程。PowerShell rg通配路径报错已纠正。大目录ls输出冗长，后续使用精确路径。
- 修改文件：正式v21 README、source/hls/build_scene.tcl、source/scripts/build_scene_server.sh、source/scripts/tool_overlay.py、source/tool_patch/.../automg_patch_20220104.tcl、删除STOP；内部本记录/STATE/DECISIONS/INDEX。新构建文件改变旧全目录哈希，正式打包前刷新证据。
- 下一步：HLS实际报告审查及必要修复；继续完整Vivado系统和真实UI主入口、A/B配对环调度与新HWH接口，之后OOC/route资源门禁与封包/板测。服务器旧v20工程在/data1/leisheng_codex/wb_rgb565_quality_v20_build_20261018（source根直接为该目录），旧v15工程亦source根直接为其目录，不是多一层/source。不要误用v20恢复核。
- 当前状态：In progress；本次主动轮结束后由heartbeat继续，尚未完成用户完整目标。
### First HLS outcome / supersedes initial running checkpoint
- 后台首轮已结束，hls_status=FAILED exit1。实际csynth完成，估算LUT43852/FF22701/BRAM_18K16(8tiles)/DSP14；估算时钟8.271ns不是route时序。明显超出量化预算LUT7837/FF5855/BRAM7，不能直接整机或上板；下一轮优先压缩5x5并行颜色/证据算术，保留功能并验证吞吐，不能放宽资源上限。报告保存test_workspace/v21_server_20261019/first_csynth.rpt。
- Csim通过；cosim在C TB生成向量阶段失败(COSIM212-360/320)，尚未运行RTL。优先检查m_axi depth按最大帧取样而测试vector仅1920x33造成越界的可能性；这是待验证原因，不是已证实结论。保留失败日志，修正testbench分配后重试。
- 当前无运行HLS进程；heartbeat继续先修复/压缩再重提。整机未提交。已如实向用户说明超预算及联仿失败。
## User status/specification clarification
用户询问是否正在修改与27万LUT；核对当前源码时间及状态，资源压缩改动尚未落盘，不能称正在后台连续修改。定时任务已安排后续继续。AMD官方DS987核对K26有256200 system logic cells、117120 CLB LUT、234240 FF；7837是替换量化核预算、73763是v15整机资源上限而非器件总量。既定不增长约束不因规格澄清自动放宽。


## Updated user constraint (D-130)
用户明确允许使用器件剩余LUT，覆盖D-127旧核/旧整机资源不增长门槛；以整机可布线、时序和帧率稳定为准。开始修改实际资源门禁、定时任务与联仿缓冲；不改冻结恢复逻辑。

### D-130 Use available device resources; prioritize routability and sustained FPS (2026-10-19)
- 用户明确允许使用剩余LUT，以整机能布线和帧率稳定为主，覆盖D-127及D-129中的旧核/旧整机资源不增长限制。v15资源只作历史参考，不再作为门禁。
- 资源报告门禁改K26器件上限CLB14640/LUT117120/FF234240/BRAM144/URAM64/DSP1248；核OOC只是容量预检，不代替整机route、时序、拥塞和板端持续吞吐。允许资源增长，不为压回7837LUT牺牲吞吐。v15恢复冻结不变，setup/hold要求仍保留。
- 已修改manifest、资源门禁说明和回归，8项门禁测试PASS；完整m_axi depth测试缓冲已落盘、上传，远端第二轮HLS后台PID34087，首轮工程/日志保留attempt1。联仿修复效果待实际结果，不声称PASS。heartbeat v21已更新新约束，避免下一轮重复执行旧上限。
本轮改动新增：manifest资源门禁改容量并存历史值、resource_gate说明、8项门禁测试、test_scene_hls完整depth分配。实测8项PASS，上传测试及manifest，后台重提PID34087；完整RTL/route/板测未执行完成。

## Heartbeat checkpoint 2026-10-19T11:38Z
- 第二轮HLS真实完成：Csim/Csynth/C-RTL cosim PASS，export_design成功；hls_status HLS_COMPLETE 11:33:40Z。1920x33测试最大73036cycles，含HOLD及拒绝错误cookie多调用，不能直接当1080pFPS；本地second_cosim.rpt已下载。
- 新增正式source/scripts/prepare_system.py、build_system_server.sh。核对服务器v15八份冻结源与本地manifest一致，原v15恢复cosim证据PASS；复制独立恢复IP和预置校正IP，不改旧目录。新量化使用刚通过联仿的IP，保留旧BD cell名board_quantize_rgb_0但VLNV为board_scene_quantize，软件必须按新HWH，不沿用旧寄存器。
- 整机独立system_source已生成，system_inputs.json记录复用恢复及新量化component哈希和来源；不把旧v15验证冒称新整机。Vivado实际后台已启动PID51216，system_status RUNNING，日志logs/system_vivado.log；已进入BD构建。整机综合/实现/时序未完成。旧v15日志中HLS LUT31915而OOC7837，进一步说明HLS估算与实际不等价，不能据估算武断判断布不下。
- 下一轮检查system_status和日志一次；若脚本检查/集成失败修复重提，保留旧结果。若完成则核对实际利用率/route/setup/hold。重点并行继续软件主入口：v20 WhiteboardIP/RestoreStage含quality_meta新ABI不能用于v15，需采用v15控制器；最新UI框架可复用。A/B配对必须保持到Q完成，使用同ctx小图prepare/refine；新HWH解析输入scene_stage。完整UI集成和板包仍未闭合，无新板测。
- 修正build_system_server.sh显式unset WB_ALLOW_TIMING_VIOLATIONS，服务器本次未设置旧豁免；下次同步该小修正。仅单代理，无委派。
## Heartbeat checkpoint 2026-10-19T11:48Z
- 首轮整机FAILED：多个vendor HLS IP(v_frmbuf_wr/demosaic/gamma/CSC等)生成版本号2610190747超过32位有符号整数，Vivado12-8300。不是资源/route结论；根因整机启动脚本遗漏私有HLS overlay环境。已修正build_system_server.sh创建system_source自己的overlay并设置XILINX_HLS/XILINX_VITIS_HLS/XILINX_PATH/PATH；prepare_system复制tool_patch。不修改共享工具安装。失败工程保留system_source/build_2021_2_attempt1，日志system_vivado_attempt1.log；第二轮后台PID92080，待真实结果。
- 软件新增scene_registers.py：新VLNV匹配(允许旧BD实例名)、从实际component/HWH解析寄存器/控制地址、拒绝混用旧IP与缺失/冲突。真实导出component解析20寄存器PASS，src偏移24非旧16。4项HWH替身检查PASS；最终整机HWH仍未获得，不能称板端联调通过。
- scene_tracking新增RGB565Lattice和snapshot，允许主线程在拥有DMA视图时仅复制320x180x2=115200B，worker只读独立小图；防止异步任务读取回收A/B。3项生命周期/形状/prepare-refine回归PASS。实际UI主入口仍未接入，不能声称PS集成已完成。
- 验证：初次直接跑tracking遗漏WB_SCENE_NATIVE导致2个环境错误；显式指向此前同一未改HLS源码生成DLL后完整75项native/软件/接口测试PASS，0失败/错误/跳过。HLS核心未因本轮改动改变，无需重复核综合；测试DLL不能代替ARM/实拍/FPS验收。未执行新route或上板。
- 修改文件：scene_registers.py、test_scene_registers.py、scene_tracking.py、test_scene_lattice.py、prepare_system.py、build_system_server.sh、本记录和STATE。下一步：检查第二轮整机；完成UI主入口/v15软件ABI/同帧A-B保留与新Q接入，按D-130验收资源/时序/吞吐。服务器第二轮已重新开始BD构建，尚未证明内部日期错误消除。
## Heartbeat checkpoint 2026-10-19T11:58Z
- 第二轮整机PID92080仍RUNNING、等待各IP和顶层synth_1；当前没有route/时序/FPS结论，不忙轮询。
- 新增正式scene_live.py，实际恢复后不释放A；Q读取配对原图A，B仅供同帧小图refine，完成才归还A/B。prepare在Restore启动后执行以重叠PL计算；小图主线程同步执行，未声称worker异步或已达帧率。失配/提前释放/timeout保留所有权回归4项PASS。最后一次Q完成前允许下一帧Restore/PS处理，但必须上次refine完成。
- 新增assemble_runtime.py，将最新v20 UI、采集/事件FPS/运动校准框架与v15 WhiteboardIP/寄存器/baseline_stages组合，生成新主入口：恢复接口移除v20 quality_meta；B就绪队列撤销同时归还A；Q完成后释放A；新HWH/封包校验；保留原始底层完成事件FPS及UI源帧/显示帧区分。不覆盖旧runtime。staging=test_workspace/v21_runtime_20261019/attempt2，尚未封包/板端执行。
- 显式--trusted-scene-start才允许当前启动可信黑板参考，默认保持UNKNOWN，不把几何锁定直接当无人；板测需先确认无遮挡，不能伪造语义无人。后续真实UI引导/重建交互仍需审查。
- HWH解析修正：真实Vivado REGISTER偏移/位宽在PROPERTY子节点，不能只读属性。已下载当前未布线整机HWH至test_workspace/v21_server_20261019/scene_system_unrouted.hwh；实际新核20寄存器与真实IP component完全一致（src偏移24，基址80060000），v15恢复64bit指针/标量布局及采集接口均真实校验PASS。该HWH仅接口验证，不能冒称route后可部署固件。
- 完整79项native/软件测试PASS，日志test_workspace/v21_runtime_20261019/native_tests_79.log；生成主入口AST解析PASS。主入口离线硬件替身整流水、ARM/UI构建与实板未执行，不把组件测试当完整集成通过。
- 变更文件：scene_registers.py、scene_live.py、test_scene_live.py、source/scripts/assemble_runtime.py及内部STATE/本记录。下一步继续主入口整流水替身回归/ARM预检、封包流程；待整机route通过后匹配下载上板。注意staging保留最新UI的pipeline_metrics.py（API与v21 standalone不同），不可用v21模型metrics覆盖UI事件metrics。
## Heartbeat checkpoint 2026-10-19T12:08Z
- 服务器第二轮整机已通过synth/link_design，进入opt_design实现；DRC前检0Errors，PID92080仍运行。未完成place/route/最终时序，不作资源/FPS通过结论。
- 新增test_runtime_pipeline.py执行实际assemble后的主入口，使用检查所有权的PL/相机替身：A保持READING至Q完成、三阶段最大重叠3、输出顺序递增、摄像头lease完整释放，PASS。不是RTL或真实吞吐测试。validate_local现在自动装配runtime并提供WB_SCENE_RUNTIME，避免完整测试缺环境。
- 完整重新build native +有界testbench+80项软件/算法测试+100帧有真值合成回放全部PASS，证据test_workspace/v21_local_20261019/live_adapter_verified/；初始/遮挡期间/最终错配均0，退去白字448→0，八份冻结源核验。其HLS/板卡NOT_RUN表示该本地验证器不执行硬件签核，不覆盖独立远端cosim PASS事实。
- 板卡ubuntu@[private_ip]只读连接PASS，内核5.15.0-1027、Python3.10.12。软件候选独立上传/home/ubuntu/kv260_apps/whiteboard_scene_v21_staging_20261019，归档SHA33495df784918dca6a6bcbc398bff057dd90e96dc9ad14bb407b00de3cd459b3远端一致；未切换固件或旧进程。ARM build_ui.py后台PID17814，2jobs，使用既有v19 staging CMake。初始2%正常编译；import scene_live/main AST检查另SSH启动，本轮需收结果。
- 板卡系统日期比开发机旧，tar报文件未来时间，不擅自修改系统时钟；编译结果按实际receipt/日志核对。
- 下一轮：查服务器system_status/route；查板端build_ui_v21.log+receipt和进程。ARM语法/导入校验可能仍在exec会话91187中；可read-only独立重查日志不要重起现有编译。完整封包与实际新硬件板测仍待完成。
### ARM import correction
默认/usr/bin Python先读/usr/local NumPy2.2.6，与apt cv2不兼容，首次import失败；PYTHONNOUSERSITE无效（非用户site）。不降级或修改全局依赖。指定PYTHONPATH=/usr/lib/python3/dist-packages后真实ARM import/syntax PASS，numpy1.21.5/cv2 4.5.4。实际当前板上流水PID5548使用/usr/local/share/pynq-venv/bin/python3；后续正式启动必须沿用该venv并核对依赖，不用默认python3。旧流水确认仍在运行未切换。


## Heartbeat checkpoint 2026-10-19T12:18Z
- 整机真实完成placement/physopt，进入route_design。物理优化阶段setup非负，0critical warnings/0errors，但不代替最终route时序。真实placed利用率：LUT75833/117120，FF90306/234240，CLB14274/14640(97.50%)，BRAM132/144，URAM8/64，DSP172/1248；placed_utilization.rpt已下载。旧v15上限已撤销，允许这部分增长，不因旧上限停工。
- 发现真实Vivado report重复CLB Registers两处且相等，原parser误报Duplicate FF；已改相等重复允许、冲突数值拒绝，9项资源门禁回归PASS，修正脚本已同步服务器。
- ARM UI构建完成(aarch64 receipt)，独立NativeUI ABI32/init/render/close实测PASS，不接管显示或PL；当前v20 PID5548未变。已将真实ARM so及receipt下载回本地runtime attempt2/ui_native/build，供最终匹配封包。
- 新增正式export_hardware.py，只有system_status ROUTE_SIGNOFF_COMPLETE、真实非负setup/hold、器件容量/冻结源/集成component哈希均通过才导出新bit/HWH/bin/dtbo/driver/reports，采用相对BIF及Python3.6兼容overlay helper。脚本已上传，尚未执行导出。原v15核与驱动复用明确记录，不把旧板包冒称新。
- 新增board_scene_acceptance.py真实硬件测试计划：1080p空板初始化、白/红/蓝ADD、OCCLUDED保护、两次观测ERASE、HOLD保护；使用新HWH映射并保留超时DMA缓冲。仅语法检查PASS，尚未加载新硬件执行，不声称板测通过。
- 后续：等待route完成后执行source/scripts/export_hardware.py并下载匹配硬件；完成seal_runtime/package脚本（更新deployment/verify_manifest为v21、新smoke脚本，避免旧v20量化寄存器测试），最终预检再切换上板。部署始终使用已验证/usr/local/share/pynq-venv/bin/python3(numpy1.26.4/cv2 4.12.0)。真实场景启动需明确无遮挡参考，未默认信任几何安全。
## Heartbeat checkpoint 2026-10-19T12:28Z / package preparation
- 整机route后最终签核PASS，WNS+0.447ns/WHS+0.010ns/setup failing0，12:32:17Z ROUTE_SIGNOFF_COMPLETE，最终bit/XSA完成。实际资源LUT75833/FF90306/CLB14274/BRAM132/URAM8/DSP172。export_hardware真实PASS，硬件归档fc2b4f73001a6f27afa1875a2500ab1fa4c55ba57ecb74a8cc3b73493f592814下载核对一致。
- 新增verify_scene_package.py、scene_smoke.py、seal_package.py；smoke改真实新核三色ADD/ERASE/遮挡/HOLD+transport+实际新主流水10帧，不调用旧v20量化寄存器测试。完整包已生成正式rtl/dma_rgb565_scene_v21/board_package及board_package.zip，SHA d308b3621e85c1f1fe0836770b23d8d164cb1b00355027bc674700716186691f；153文件hash+154项ZIP bundle结构本地PASS。新包包含真实aarch64 UI库与vendor源码、相机/driver/校正/恢复/新量化精确HWH，实际板测仍NOT_RUN。
- 用户已明确回复“已清空遮挡，可以初始化”，允许当前首次可信参考；sealer参数--trusted-scene-start进入live配置。SceneLive启动确认改为单次消耗，不能后续epoch/照明失效时悄悄学习人物，新增回归PASS；全部82项检查PASS，日志prepackage_tests.log。后续几何改变需重新确认无人参考，不能宣称自动语义重建完成。
- 新板包已上传并SHA一致，独立安装/home/ubuntu/kv260_apps/whiteboard_scene_v21_20261019；sudo run.sh check进行中(exec session54884)，旧v20尚未停止。待check通过后显式停止旧whiteboard_candidate_v20_fixed_20261019/run.sh，再新包run.sh deploy；保留旧包和回退能力。当前预检不可被当作新硬件已运行。
## Field failure / correction in progress
v21已上板，transport和6帧真实PL三色/擦除/遮挡/HOLD验收PASS；live PID23298，实际短窗约6~7FPS，尚不达匹配v15目标。用户现场明确首帧字厚、随后全空白，验收FAIL，不能标任务完成。真实205/783帧已下载至test_workspace/v21_field_20261019，确认首帧有黑色letterbox/边框与粗字、后帧纯白；几何1→2→5，原算法将所有epoch变更等同新场景清空，且可信初始化单次，导致永久UNKNOWN。开始修正为可信材料/Canvas在黑板规范坐标保持：仅在quiesced几何变更时由旧/新输出ROI重投影已有材料、对象和Canvas，不从当前人物重新初始化；history仅打断候选而非删除内容。首帧材料估计腐蚀偏暗，实拍离线median5替代降低黑字面积103249→59996，需保留弱字回归，ROI剔除letterbox。HLS/恢复核不改，软件修复后重新封包。


## Field repair r2 applied / pending observation
- 已实际部署首包：旧v20停止，新硬件成功加载；相机RGB565 transport三色PASS；1920x1080真实新Q六帧ADD/ERASE/OCCLUDED/HOLD全PASS，host观察29~33ms，不是纯busycycle。首轮livePID23298，短窗6~7FPS，实际几何多次1→2→5；用户报告首帧很粗、后续全白，现场验收明确FAIL。
- 实拍205/783帧和几何下载到test_workspace/v21_field_20261019，已目视确认；原代码把几何/history变更当场景换掉清Canvas并耗尽初始化，且ROI未屏蔽白色letterbox/背景min腐蚀估计偏暗。禁止把硬件PASS冒称画质通过。
- r2软件根因修正：scene_geometry.py按旧/新黑板规范ROI映射类别Canvas/Surface/对象/visibility，只在全部DMA归还时执行，不读当前人物重新学习；重投影清pending擦除高位、保留类别。history-only变化只清短期候选，cap/未知geom变化仍拒绝旧坐标。小图median5替代min腐蚀初始化、全tile限制ROI，live color_margin24。恢复/newQ HLS源与bit完全不改，不重新综合。
- 更新主入口生成器在排空边界调用set_geometry；SceneTracker ROI屏蔽outside物体/照明统计，原状态/类型保持。完整86项+有界C++和100帧合成回放PASS（0错配），field_fix_r2/证据；实拍离线初始白类面积约103249→59996，外侧黑色letterbox剔除；不是现场画质已过。真实后续epoch持久性还需上板观测。
- r2匹配包board_package_r2.zip SHA cfe11016093778bffbb4d2f54fdb016104556b9c12792412419a04324fc0502e，安装新路径/home/ubuntu/kv260_apps/whiteboard_scene_v21_r2_20261019，154hash/ABI/UI预检PASS。为仅重启软件，将真实r1进程state复制至r2新state（此前不存在），部署器校验同硬件hash后可skip_load；r2后台部署PID24589，日志deploy_v21_r2.log。不覆盖原包/失败记录，可信初始化仍沿用用户明确确认并要求期间无遮挡。
- 待验证：r2运行/重定位不白屏、粗细/颜色/添加擦除/人物现场反馈，持续FPS及瓶颈。若仍失败继续修复，不能停定时或标完成。当前尚无r2 live通过结论。
## PS r3 field diagnosis and r4 repair
- 用户明确已有字擦不掉、人物触发板框丢失，现场验收仍FAIL。r3当前真实PID25748，约869秒累计5.31FPS，遮挡3596/3776tile；无bad_frames不能代替画质通过。
- 实拍3852原图有新增白笔而Q缺失；错误PS前景覆盖3093tile，其中2845tile实际接近可信板面。根因使用连通域外接矩形充满对象，以及先闭运算再腐蚀将字网变为人物核心。
- r4修复：只赋值连通域实际形状，原始变化图7x7实心核心，可信板面再现排除对象；可信启动inpaint+median推断原字下材料，移除+24亮度钳制；板框锁定后停止重复检测撤销，独立物理边框环带光流监测位移。PL和冻结v15恢复未改，不重新综合。
- 初轮foreground测试失败2项并有fixture previous_ids未初始化错误，已保留失败日志并修复。最新material_and_frame_r4完整92项0失败/错误/跳过、有界C++、100帧合成回放PASS；不等于现场通过。
- 用户本轮回复“可以”明确允许重新无遮挡初始化。r4包SHA b26bf3c14d25b50359db22035446e7ce6d5db796aca630a7b39a0d9838becf3a，已独立安装whiteboard_scene_v21_r4_20261019，硬件仍匹配原签核bit。预检进行，待软件切换/真实smoke/现场与FPS。
- 文件：source/software/scene_tracking.py、scene_board_recognition.py、motion_guard.py、scripts/assemble_runtime.py、seal_package.py、tests/test_scene_foreground.py、test_scene_board_lock.py及正式board_package_r4。参与者用户/本AI，无委派；采用上述PS修复，最终现场结论待验证。

### r4 deployed / actual checks
155项预检PASS，同bit软件切换FPGA_reloaded=False，live PID27602。相机三色transport及1920x1080新Q六帧真实PL合成测试PASS，量化host29~33ms。现场初始化完成后27.9秒日志valid3776/visible3776/occluded0、holdFalse、needs_bootstrapFalse，短窗采集30/恢复8/量化8/显示8.5FPS；启动累计3.12FPS含约18秒校准，不能冒充持续8FPS。MotionGuard few_features，真实大位移检测仍待验证。已SIGUSR2请求安全抓帧；用户现场新增/旧字擦除/人物遮挡复测已请求，结果待定。

`n## r4 field result and person leakage`n用户确认新增擦除全部正常；剩余静止/板边人物黑头发与红皮肤影，整体尚未通过。继续同会话PS漏检诊断，SIGUSR2抓帧并请求板边静止复现；PL未改。

## r5 PS dark-board foreground repair / verification
- 用户补充为黑板暗部更严重，不是单指暗衣服；已纠正理解。按要求延迟10秒安全抓取真实板边静止人物11649/12063，保存test_workspace/v21_person_r5_20261019；5762/8368为无遮挡参照，不冒充人物。
- 实拍r4 metadata人物遮挡为0；左右局部surface绿色中位约60.7/81.0，绝对28阈值加7x7核心导致暗部零碎差值全部漏种子。离线5x5连续核心检查可识别，但直接放宽曾导致正常字网误前景，已改核心自身连通面积>=4，而非相邻字交叉点累加。
- r5增加冻结foreground_reference防止缓慢进入被逐帧吸收；已识别对象的窄轮廓以相近外观续接，保留面积>=原对象8%防人离开后少量同色字错误续接；局部可信材料亮度缩放对比阈值18..28（标称80），不从当前人物估计；遮罩小图保护5x5，类别/bit不改。额外anchor为320x180x3约173KB PS内存，额外小图比较/连通域CPU成本需实板测量；无PL资源增加。
- 失败轨迹保留：validation两项擦除/释放失败，retest单测94PASS但合成final错配256；retest2修正释放后PASS；retest3降低核心导致字网单测失败；retest4连续核心修正后94PASS；dark_board_validation最终95项PASS、有界C++/100帧真值回放0错配/第2观测擦除PASS。实拍同图离线遮罩0→88800像素，不等于所有人物范围语义已通过。
- 用户明确回复可以无遮挡初始化。r5匹配包152b8c5d12ac1b9f28a1642ca79404ba24cc4836c410d853793cb9cf9d4c63f9；独立安装whiteboard_scene_v21_r5_20261019，复制真实r4进程state以同bit安全停旧启新，deploy_v21_r5.log进行中。新板测和用户暗部验证待定。
- 修改scene_tracking.py、scene_geometry.py、test_scene_foreground.py与board_package_r5；v15八源及新PL源哈希仍验证一致。最终现场结果待更新，未完成。
### r5 real deployment
预检/transport/真实1080p六帧Q smoke PASS，FPGA_reloaded=False，livePID29285。15.9秒时初始化完成，holdFalse/visible3776/occluded0、bad_frames0、短窗处理与显示7.5FPS；额外PS运算已进入真实运行，持续帧率仍需观察。已请求用户复测黑板暗部边缘静止人物、退去及写擦，现场结果待定。

## r5 user acceptance checkpoint / close active repair loop
- 用户现场反馈：基本全部解决。采用为本轮新增/初始擦除/暗部板边静止人物残影的基本通过反馈，不外推为所有光照/长期/相机移动全通过。
- 再次真实核查r5 PID29285存活；175.17秒1296输出，含启动累计7.398FPS，近期恢复/量化8FPS、显示7.5FPS、bad_frames0，geometry_generation1。保存accepted_r5_live.log。当前无人时3776可见/0遮挡，不能当成人物语义验证证据，人物通过依据用户操作反馈与已保存实拍诊断。
- v21 automation.toml实际已PAUSED，本轮核实，无需重复创建/继续轮询。板端r5保持运行，未停止程序。保留r1-r4与失败日志。
- 正式README更新r5包/hash/验收范围和性能；顶层run.sh改选r5，避免默认部署失败的r1。不修改sealed r5内容及其哈希。
- 任务本轮现场修复收尾。未完成扩展验证：长时间运行、不同光照完整覆盖、真实大相机位移；MotionGuard仍few_features，不能称这项已通过。PL签核与冻结恢复保持。
