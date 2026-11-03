# AI Session: 2026-10-18-003-v19-200mhz-synthesis-board-trial
- Date: 2026-10-18 (Asia/Shanghai)
- Operator: Project owner
- AI product/model: Codex / GPT-6
- Participants: Project owner, Codex (single agent)
- Objective: 按用户新授权将v19处理时钟由150MHz改为200MHz，执行HLS/RTL与Vivado构建；若工具生成匹配bitstream则按用户要求继续上板测试，并保留真实时序结果。
- Status: Diagnostic checkpoint delivered — v19 capture regression localized; root transaction and repair remain open; old v17 loaded, capture stopped
- Report candidate: no
- Related commits: none; project/test trees untracked
- Related files: kv260-whiteboard-enhance/rtl/dma_rgb565_quality_v19/source

## Context Read
- 继续2026-10-18-002 v19完整会话与D-110、根AGENTS/项目政策、最新状态、决策和索引。新指令覆盖此前综合前停止点；本轮显式授权200MHz综合与最终上板。

## Task and Constraints
- 用户：“现在开始综合……最后综合的时候把频率改到200mhz，如果有时序违例，只要能正常生成比特流就无视违例，最后上板测试”。
- v19处理HLS目标与Vivado CLKOUT1改为5ns/200MHz；视频/PHY时钟沿用既有约束。严格保留路由WNS/WHS结果，并给有违例产物明确实验性标记。未经其完整bit/hwh/xsa及接口核对，不部署。
- 服务器目标仍为独立新目录/data1/leisheng_codex/wb_rgb565_quality_v19_presynthesis_20261018；禁止覆盖v18目录。

## Contributions
- 将v19处理时钟设为200MHz（HLS目标5ns、Clock Wizard输出5ns），保留视频/PHY基线时钟；执行fresh HLS综合/RTL协同仿真与整机Vivado综合、实现、路由和签核。
- 在用户授权范围内允许时序失败的实验性bitstream继续导出；保留routed timing报告并在证据、manifest、包名和软件预检路径中设置experimental标志。
- 从候选已哈希的`vivado/base_camera.dts`重建缺失的`evidence/baseline_camera.dtbo`，完成overlay配套检查；封包并核对53项文件哈希。
- 尝试通过SSH和JTAG hw_server上板；设备服务未能建立可用会话，未传输、编程或启动板端包。
## Decisions and Adoption
- D-111: 200MHz处理核与HLS周期；允许可生成bitstream且匹配的负裕量候选用于明确标记的板端实验；不将其记为时序签核PASS。
## Commands and Tools
- 本地PowerShell、Python zipfile/hashlib；SSH/SCP到授权构建服务器`leisheng@[private_ip]`；远端Vitis HLS/Vivado 2021.2；本机Vivado 2022.2只读hw_server探测。
- 以16个并行job运行整机综合与实现；每约2–3分钟读取构建日志状态。
## Validation and Evidence
- Fresh Restore/Quantize HLS综合、C/RTL co-sim PASS；整机top synthesis PASS；route net verification PASS；`write_bitstream`和`write_hw_platform`均成功，生成bit与XSA。
- 最终修正时钟签核`evidence/signoff_timing.json`：WNS=-1.822ns、WHS=+0.010ns、33个setup failing endpoints，`result=FAIL`；未声称200MHz时序通过。约束要求200MHz处理输出时钟。
- 封装结果`MATCHED_V17_BOARD_PACKAGE` PASS，53项包内文件清单，资源：LUT 66.45%、寄存器40.42%、BRAM 96.18%、URAM20.31%、DSP27.16%、CLB98.20%。包SHA256=`31094e3130b8dd85769d2b5535554150cddd7d1f3dbc09948401f68f86ba935d`；本地对ZIP内manifest列出的board文件逐个复算，零哈希错误。
- 板测未执行：本机SSH在TCP连接后被`[private_ip]:22`关闭；Vivado hw_server对`[private_ip]:3121`返回无法连接；HTTP探测超时；构建服务器到该地址各服务TCP连接超时。没有bit传到板端，板上状态未被本轮修改。
- 构建主机运行`verify_manifest.py`未执行通过：该脚本导入PYNQ运行时模块，构建环境无`pynq`；这是宿主依赖缺失，不能当作包哈希或接口失败。板端的软件预检仍待可达后运行。
- 证据复制到`test_workspace/v19_quality_presynthesis_20261018/server_evidence_200mhz/`；正式包与报告位于`kv260-whiteboard-enhance/rtl/dma_rgb565_quality_v19/board_package/`及`evidence/`。
## Errors and Corrections
- 构建脚本原先锁定150MHz且package强制timing PASS；更新为200MHz并以experimental_timing_trial记录负裕量，确保只能在明确授权条件下通过软件预检。
- 首次build尝试分别遇到shell CRLF、cosim testbench原型不匹配、testbench m_axi数组小于接口深度；按保存日志逐项修复并保留失败attempt归档，retry4完成HLS和系统实现。
- 自动导出首轮因缺`evidence/baseline_camera.dtbo`失败；使用候选manifest内的`vivado/base_camera.dts`及Vitis所带dtc生成基线overlay，运行`prepare_overlay.py`及导出检查PASS。
- `verify_manifest.py`在构建主机因缺PYNQ模块退出；随后用Python标准库逐项验证ZIP内`board_sha256`，全部通过。正式板端预检仍未执行。
- 初次hw_server探测脚本传入Vivado不支持的`-timeout`选项，属探测命令错误；以支持语法重试后确认硬件服务器仍不可连接。
## Files Changed
- `kv260-whiteboard-enhance/rtl/dma_rgb565_quality_v19/source/`中的候选时钟、构建、实验性时序、导出/包预检文件及更新后的hash manifest；通过后另建候选`board_package/`、`evidence/`和ZIP。
- `test_workspace/v19_quality_presynthesis_20261018/server_evidence_200mhz/`保存服务器构建、时序、包与只读连接探测证据。
- `project_workspace/DECISIONS.md`、`PROJECT_STATE.md`、`ai/INDEX.md`与本会话记录。
## Remaining Work
- 恢复KV260 SSH/XVC可达后，按已授权包部署；运行package preflight和板端短时采集、擦除延迟、浅衣边缘、灰白粉尘观感检查；保存帧和日志。此候选仅用于实验，不作为时序合格发布。
## Handoff Notes
- 用户已明确授权此轮综合、时序失败时只要bitstream生成成功就继续实验上板。原v18与v19旧150MHz source/bit untouched。本轮因设备服务不可达而停止在已封包、未部署状态；连通后可延续授权。

## SSH deployment continuation — 2026-10-18
- 用户恢复网络并要求继续上板，随后明确没有JTAG、仅使用SSH。SSH ubuntu@[private_ip]成功，kernel5.15.0-1027；免密sudo可用。板端时钟落后到2025-10-17，用户侧日期以2026-10-18为准。
- 纠正板包README的综合前陈旧描述，并重新封装manifest/bundle，53项ZIP全部hash通过；新ZIP SHA256 `c37ba29e20864434a5c4c0d885061c741d3db7adea68f9a96bfe6d00e9773235`，硬件字节未改。
- 项目安装器完整归档current/previous并切换候选目录。板端run.sh check PASS，51项board文件、HWH/bit/DTBO及PYNQ/内核检查通过。FPGA manager加载v19 bit和overlay成功。
- 首次部署的transport smoke遇到5秒Camera frame timeout，同时CSI记录一次`Stream Line Buffer Full`（uptime12315.697315）。没有启动live；后续没有新增溢出且没有设备占用。
- 独立v4l2 mmap采集3帧成功，每帧4147200字节，间隔33.324/33.327ms。随后单独transport_acceptance PASS：红/绿/蓝中值精确[255,0,0]/[0,255,0]/[0,0,255]，传感器控制恢复。
- 当时决定先在已加载硬件上执行1000帧采集和smoke；后续重复启动复现，转入下述故障诊断。不能把启动溢出直接归因到时序违例。

## Capture regression diagnosis continuation — 2026-10-18
- 用户要求先查原因并告知，再修改；明确要求围绕本轮改动追溯，不再扩展时序分析。设备操作仅SSH，无JTAG。
- 独立正常图像1000帧采集PASS：33.452s、29.894fps、bad=0、sequence_gaps=0；完整smoke多次在transport首帧timeout，未到三阶段/视觉验收，不能宣称板测通过。
- 故障现场gamma AP_CTRL=0x84、width=1080、height=0；正常为0x81、1920、1080。PYNQ32与busybox devmem32两种读法一致；media软件格式仍1920x1080。CSI已收到RAW8行并发生下游反压溢出，不能把buffer full当最初原因。
- 诊断期间曾两次手动尝试运行时gamma宽高/格式/AP_CTRL寄存器重写：第一次mmap/struct写法不保证MMIO访问粒度，第二次PYNQ32写后未改变异常读值，均未恢复取帧。没有修改gamma RTL、LUT、白平衡或发布包。这些失败不能作gamma根因已证实的依据；在证据不足时尝试修复并过早称根因定位是本轮错误。
- 临时打开gamma驱动单行dynamic_debug后24次启动通过；关日志后首轮即可失败。只说明启动顺序/间隔敏感，不构成修复。函数图与GPIO跟踪未发现失败前其他IP复位gamma；全部debug/ftrace设置恢复（current_tracer=nop、tracing_on=1、gpio_value=0）。恢复graph过滤器时曾因内核显示占位字符串EINVAL，已清空恢复。
- 与实际板上.previous逐文件对比：此前安装为v17 experimental 200MHz（不能误称v18）；摄像头采集/预加载/overlay/部署执行脚本及两内核模块完全相同。DTBO反编译只差固件文件名。37模块HWH仅Restore/Quantize版本号及监视器wrapper名称变化，gamma模块无差异。两次生成gamma CTRL RTL SHA256均为7ec6adf4eb1695215d52f1fbb1bf33dea36b3cb0c2f5d5600cc6a96f9a05c449。
- 当前执行受控A/B：独立load_for_ab.py调用原始加载流程，保留current/previous目录和state，不启动live；先旧版再v19，运行同一只读采集trace。诊断加载属于已授权上板测试，不是已确定修复；结果后补。
- 构建报告纠正：signoff JSON的33是get_timing_paths最大33条的返回数，并非完整失败端点计数；完整rpt为3700。停止扩展时序诊断，不将此作为本轮故障归因。原报告保留，后续补充勘误。

## A/B/A result and diagnostic handoff
- 受控加载旧v17→v19→同一旧v17，采用同一gamma_readonly_nolog.py/transport脚本，不启动live、不手动写gamma；结果24/24→第14次失败（13次通过）→24/24。v19异常宽高已在CSI溢出前出现，进一步支持新整机固件启动回归；不能冒充已查明具体AXI握手错误或唯一源码行。
- 保存三次加载/采集原始日志、package_delta.json/source_delta.json、两次失败干预日志、独立复现脚本于正式evidence/board_capture_regression；原始长跟踪仍在测试目录和板端。正式中文报告docs/v19_capture_regression_diagnosis_20261018.md逐项列出算法、运行时、构建、封包及诊断操作。
- 53项板包40相同、13不同；kernel_sources压缩内容相同。v19封存源368项对服务器v18审计296相同/72不同或新增；唯一当前hash审计差异是构建生成monitor wrapper CRLF→LF，归一内容相同，未隐瞒为全部hash通过。
- 最终FPGA manager operating，PL为旧v17，video0无占用，无live进程；目录不互换/current仍v19，未改state声称成功。核实gamma dynamic_debug关闭、current_tracer=nop、tracing_on=1、gpio_value=0。初次读trace设置未sudo遇权限错误，随后sudo只读核对成功。
- 本阶段采用D-113：交付诊断结论与完整改动记录；没有实施v19修复。尚需实际AXI控制事务/复位根因隔离、受控修正、完整流水线及三项真实视觉验收。旧版有限采集通过不能作为v19质量验收，也不能证明旧版无限次无故障。
