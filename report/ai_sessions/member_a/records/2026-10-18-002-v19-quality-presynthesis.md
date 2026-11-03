# AI Session: 2026-10-18-002-v19-quality-presynthesis
- Date: 2026-10-18 (Asia/Shanghai)
- Operator: Project owner
- AI product/model: Codex / GPT-6
- Participants: Project owner, Codex (single agent)
- Objective: 基于匹配v18 150MHz源建立独立v19候选，修改浅衣遮挡、局部擦除及粉尘团簇去噪，完成综合前验证后停止。
- Status: Complete — STOPPED_BEFORE_SYNTHESIS; native and actual Vitis HLS C simulation PASS
- Report candidate: yes (算法反例、纠正及独立验证可供后续筛选；本轮不写参赛案例)
- Related commits: none; project/test trees currently untracked

## Context Read
- 按顺序读取AGENTS.md、AI_DEVELOPMENT_POLICY.md、PROJECT_STATE.md最新状态、DECISIONS.md近期决策、INDEX.md、2026-10-18-001及前轮已读的2026-10-17-001；检查Git、子目录AGENTS和匹配v18源。

## Task and Constraints
- 用户授权：“设备已连接，你开始修改吧，到综合这一步之前停下来”。
- 本轮允许源码实现、原生C++/Python验证；后续用户明确“允许上传，仅做 C 仿真”，授权候选归档上传到既有服务器的新独立目录并运行Vitis HLS 2021.2 C仿真。禁止启动HLS csynth/Vivado synth/实现/部署/新固件加载。
- 保留150MHz目标、现有vendor DMA、两个DDR环及PS/PL职责，原v18包和生产源不覆盖。
- 正式候选为kv260-whiteboard-enhance/rtl/dma_rgb565_quality_v19/source；本地测试输出位于test_workspace/v19_quality_presynthesis_20261018。服务器独立目录/data1/leisheng_codex/wb_rgb565_quality_v19_presynthesis_20261018，C仿真输出在其test_workspace/csim_v19。

## Contributions
- 单一Codex完成源码基线核对、候选实现、独立参考与反例回归、构建边界整理、服务器C仿真和交接记录；未使用子代理。用户提供症状、正式v15对照、综合前停止边界及服务器上传/C仿真授权。
- 从v18服务器源复制独立候选，8个关键HLS输入与用户v18包manifest逐一匹配；原包/旧候选不覆盖。runtime采用用户包runtime2-acceptance-roi-aligned修订，4个相对服务器源差异是运行时对齐，而非伪称全目录原封相同。baseline_inputs.json记录原始来源，原README/状态改名保留。
- Restore新增8160字节块证据缓冲，复用已有采样scratch，分开浅色物体、可见板面、新字和擦除提交：跨2x2块覆盖识别浅衣并保持静止保护；局部板面锚点/半径2的两个独立见证允许较大擦除；通常第3次观测提交，不等待整屏rebase。当前真正物体、全局freeze和不可信源始终否决快速提交。
- 字迹增加稀疏正向色素与方向采样支持，保留粗字内核；Restore及Quantize弱/中对比候选须5像素方向跨度，强支持点保留标点通道，避免弱2x2互相保活。保留原始RGB中性/色相，不引入邻域颜色覆盖。
- 持久块状态增加可见/写许可/浅衣标志，计数限定5bit，magic升至0x57424332；软件quality_snapshot仅空闲时显式读取诊断，不进主调度。寄存器地址/分配大小不变，但新运行时不得配旧固件。
- 全局高密度保护包含新前景；不可信源帧冻结所有提交，包括原is_erased/ink分支。保持两个DDR环和150MHz目标，不增加语义模型/全帧状态平面。
- 新建C仿真专用入口；所有活动综合/导出入口增加STOP与环境双门控，STOP即使授权环境为YES仍优先拒绝。整机脚本选择v19标识、150MHz及新输入清单；未执行这些构建入口。

## Decisions and Adoption
- D-110采用以上v19实现及状态契约，范围为综合前源码候选；不声称解决所有衣服/粉尘语义。
- HLS period 6.666667ns只是150MHz目标。新增逻辑的II、BRAM映射、资源和路由时序未测，不沿用v18硬件签核。
- source_sha256封存367文件；git_commit明确UNCOMMITTED_V19_SOURCE_SNAPSHOT，旧51a5873仅来源。STOP和manifest不参与递归输入hash；封存后核心源码无变化，仅更新STOP结果状态。

## Commands and Tools
- PowerShell/rg/Git/Python、TDM-GCC-64 g++、独立NumPy参考、SSH/SCP；未调用浏览器或子代理。
- 本地：python scripts/verify_presynthesis_v19.py --output <test_workspace下专用目录>；最终validation_accepted/presynthesis_result.json。
- 独立边界：python tests/test_presynthesis_boundary_v19.py → V19_BOUNDARY_PASS；状态更新后再次PASS。
- 上传归档1,174,630字节至服务器/tmp/wb_v19_presynthesis_20261018_9f83d69c.tar.gz；SHA256 9f83d69cfe3bfacf126fe03b01c7cc0dee314b22f9edc12faf33cf7011dde93f。拒绝覆盖已存在目录，逐成员排除绝对路径/..及链接后解包。
- 服务器直接运行/opt/Xilinx/Vitis_HLS/2021.2/bin/vitis_hls -f <candidate>/hls/csim_v19.tcl；WB_V19_CSIM_OUTPUT指定test_workspace/csim_v19；加载私有Y2K22补丁，无csynth/cosim/export。服务器时区EDT与本地日期不同，日志保留原样。

## Validation and Evidence
- 总检查点：test_workspace/v19_quality_presynthesis_20261018/presynthesis_checkpoint.json。原生报告hls_csim=NOT_RUN保留该次本地运行事实，随后真实C仿真在server_evidence/csim_result.json独立记录，不能覆盖旧日志伪造同步执行。
- 本地20项检查PASS（包括编译/运行/软件语法）；quality_v19：shirts=9、erase=36、strokes=16、noise_clusters=3、source_gate、tail_guard。
- 82组颜色语义无错；12组小帧量化标量参考PASS；独立NumPy36组量化，其中4组1080p，另4次1080p恢复，bottom_partial/row_padding/atomic_reject PASS；场景重建、局部恢复、软件指针/ABI/环/调度检查PASS。软件调度为fixture验证，不是板端吞吐。
- comparison.json/probe_v19.txt与匹配v18 probe对照：合成白衣palette杂边348→0且occupied0→64；8像素宽淡字v18观察16帧仍128残留，v19第3帧提交且残留0；邻人和灰白粉尘板面擦除残留20→0；弱/中2x2噪点存活4→0。仅这些合成场景，不推及实拍帧率或视觉验收。
- 真实Vitis HLS2021.2：QUALITY_V19 PASS，CSim done with 0 errors，V19_CSIM_ONLY_PASS。server_evidence/vitis_csim.log保留完整工具日志，server_source_audit.json和csim_result.json证明仿真前后367文件hash一致。
- 核查已执行TCL命令仅open_project/set_top/add_files/open_solution/set_part/create_clock/csim_design；STOP存在，无新.bit/.dcp/.xsa或csynth报告。未执行HLS综合、RTL协同仿真、Vivado综合/实现、时序/资源/FPS、真实视频质量验收、部署或加载新固件。

## Errors and Corrections
- 初版quality回归粗笔画提交失败，加入稀疏正向写入/粗字通道；下一版弱团簇可误入粗字通道，收紧为采样方向跨度，保留强点路径。quality_first_run.txt、quality_second_run.txt及后续成功日志均保留。
- 清场回归先暴露应保留bulk-white保守否决，恢复原全局门控；随后旧状态精确相等断言不适合新诊断位，改只mask高3标志，像素验证不弱化。validation_run1/2保留失败。
- Windows无SIGUSR1导致软件fixture失败，测试mock(create=True)修正，生产Linux调度不变；validation_run3保留。扩展字形测试曾检查框线外y40，改正确y44，不为错误期望改算法。
- 初次probe占用计数未mask新增标志导致576虚值，改&31后最终64，probe_v19_initial.txt保留。更改局部RAM访问为内层顺序pipeline，避免外层展开强迫多口复制；实际II/资源未测。
- 首次README Delete+Add补丁被工具拒绝，未改文件，随后完整写入。原候选继承备份/cache移至本次测试inherited_archive，未删除旧工程。
- 自动审批曾拒绝向服务器上传，理由是尚无明确代码外传授权；没有绕过。用户随后明确“允许上传，仅做 C 仿真”，才完成上传与C仿真。该拒绝已解决，无剩余审批阻塞。
- SSH脚本末尾cat受PowerShell CRLF影响以错误路径退出1；独立读取真实工具日志确认CSim已0错误完成，未重复仿真；结果JSON明确保存此区别。SFTP不支持花括号路径，首次取回失败，改三个明确路径成功。
- 只读板卡SSH探测曾在banner超时，未停止现有运行或改板卡；用户报告设备连接不等于本轮独立验证。

## Files Changed
- 新正式树rtl/dma_rgb565_quality_v19/source：主要hls/quality_policy.h、whiteboard_restore.cpp、guarded_state.cpp、board_quantize_rgb.cpp、scene_rebase.h；software/whiteboard_ip.py、quantize_reference.py及匹配包运行时；新增/更新质量、光栅、状态及软件fixture测试。
- scripts/verify_presynthesis_v19.py、candidate_guard.tcl、require_synthesis_authorization.py、build_v19.sh；继承构建/封包入口、HLS/Vivado TCL、150MHz目标/版本配置；README.md、baseline_inputs.json、v19_source.json、STOP_BEFORE_SYNTHESIS.json。完整367文件清单在manifest，不将所有继承输入称为新算法修改。
- 内部session、DECISIONS.md D-110、PROJECT_STATE.md和INDEX.md；测试/失败/对照/封存/服务器证据全部在专用test_workspace下，无内部流水进入正式report/ai。

## Remaining Work
- 当前授权范围已完成。后续须新的综合授权：HLS综合/RTL/IP及II/资源检查→整机150MHz路由签核→匹配封包和实拍验收。本轮不启动。
- 物体/粉笔是几何启发式：大幅白色画可能类似衣服，极小遮挡、同板色人、受污染初始化仍有歧义；无可靠板面锚点时擦除保守等待。微弱孤立标点与稳定笔画状粉尘仍难区分。
- 需要带同源影像/质量状态/时间戳的真实浅衣擦除、粗细字/标点与粉尘A/B；第3次观测不能换算为未经测量的毫秒延迟。

## Handoff Notes
- 本地与服务器保留STOP，synthesis_authorized=false。封存manifest SHA256 489cf2ef2ebb7bed7999baf37f7557d0a0ab95ef332d5b16ba9aace42c94a468；上传归档反映STOP结果更新前状态，STOP刻意排除于输入hash，所有核心源一致。
- 正式README说明复现和未来构建。当前只有源码候选，无v19可部署硬件包；新软件状态magic不得配旧硬件。设备连接、旧v18时序及历史PASS均不用于v19签核。
