# AI Session: 2026-10-19-013-v20-overlay-startup-diagnosis
- Date: 2026-10-19 (Asia/Shanghai)
- Operator: User
- AI product/model: Codex / GPT-6
- Participants: User, Codex (single agent)
- Objective: 排查用户部署 v20 后加载画面短暂黑屏、随后回到日志输出的问题。
- Status: Complete (diagnosis only; repair and restart NOT_RUN)
- Report candidate: no
- Related commits: none; initial Git status is untracked workspace files

## Context Read
按顺序读取根 AGENTS、AI_DEVELOPMENT_POLICY、PROJECT_STATE 最新检查点及历史摘录、DECISIONS 最近决策、INDEX、session012/011/007，然后检查 Git 状态。长状态/决策历史输出存在截断，未声称通读全部历史；本次相关最新记录已读取。未发现正式目录的嵌套 AGENTS。

## Task and Constraints
用户要求定位当前启动故障，并提示本地可读取 v20 改动。先检查本地源/板包一致性及可用板端日志；不凭黑屏断言 overlay 或时序根因。不启动无关综合，不覆盖旧版回退文件。

## Contributions
- SSH只读取得实际板端live.log、固件/软件哈希、UI动态符号、设备/进程/dmesg，保存快照并与本地源码/包对照。
- 确认当前退出异常为undefined symbol: ps_native_abi；板上库与v19同SHA，缺五个v20符号。源码先接管显示再创建NativeUI，finally恢复旧CRTC，解释用户现象但未目视屏幕或重现切屏。
- 发现原ZIP仅71根层文件、漏UI/原生源码/vendor等，发布入口/source_only/NOT_BUILT与manifest字段不完整；区分ZIP本身哈希一致和本地解压deployment修改后哈希失配。
- 原始HWH检查函数本地独立执行复现input_r误报；独立验证51物理寄存器（含十个64bit指针高低字）偏移/位宽匹配，定位检查器未处理_1/_2名称。记录板端已有pass/空preflight/true smoke绕过状态，不猜测操作者。
- 编写可复核只读脚本、审计脚本、正式诊断报告与机器可读证据，更新当前状态/索引/决策。

## Decisions and Adoption
- D-122采用诊断结论与证据分层，修正D-121包完整性表述；硬件构建成功不等于软件可启动。保留时序FAIL及未经验证的板端性能/画质边界。
- 修复建议尚未实施：补齐v20原生源码/资源、ARM重编、严格HWH拆分寄存器校验、UI预检前置及重新封包后真实验收。本轮用户要求排查，未扩大为板端重部署或硬件综合。

## Commands and Tools
- PowerShell、rg、Git；SSH BatchMode只读查询，无密码/令牌写入。
- `read_board.py`通过SSH stdin执行，只在本地保存board_snapshot.json；动态库使用nm -D/file/sha256验证，没有初始化UI/接管显示。
- `python -B test_workspace/v20_startup_diagnosis_20261019/audit_startup.py`：实际执行包验证器纯文件部分、AST提取纯HWH函数、XML/清单/ZIP审计，未导入硬件控制模块或访问MMIO。

## Validation and Evidence
- FPGA operating；媒体/帧池节点存在；pgrep无流水进程；安装目录6个firmware/module哈希与本地一致。状态文件PID43818为已退出历史，不当作alive。
- UI库SHA256=1d91c1107ce9efce3d0c1ff7628963c02521bbc64326a41908b35c4519ccccba，ARM aarch64，与v19库相同；五新符号全部不存在。live日志依次保留HWH误报、缺资源、缺库、错库错误。
- 原ZIP SHA=f30713...、CRC通过、双清单逐项哈希通过；71文件0嵌套。source有63项未进入包，包含必要UI物料及可选模型/测试，不把63项全称运行必需。
- 原verify_package失败KeyError interface_contract；原check_hwh失败input_r；独立51项实际HWH寄存器偏移/位宽匹配。当前本地解压deployment已与ZIP不同、且其清单哈希失配是既有状态。
- 正式证据：v20/evidence/startup_diagnosis_20261019.json；完整快照/diff/live.log/audit脚本在test_workspace/v20_startup_diagnosis_20261019。
- 本轮未执行：板端写入、ARM编译、进程重启、overlay重载、新采集/显示/三帧/性能/画质测试、HLS/Vivado构建。现有时序FAIL无改变。

## Errors and Corrections
- 初次SSH在沙箱内Permission denied；按排查授权使用require_escalated只读查询后成功，没有自动审批拒绝。
- 查找package_board.py不存在，改读取实际package_v17.py等构建脚本；不假称其为最终原包的生成路径。
- 一次诊断Python默认GBK读取UTF8代码失败；改显式UTF-8。byte级源码差异主要为CRLF/LF；归一后源与原包所有同名根层Python内容一致。
- 原始粗看把解压deployment哈希问题归于原包；追加ZIP内逐项验证纠正：原ZIP清单一致，本地解压目录已有独立修改。该区别纳入正式报告和最终审计。

## Files Changed
- 正式docs/v20_startup_diagnosis_20261019.md；rtl/dma_rgb565_quality_v20/evidence/startup_diagnosis_20261019.json。
- 内部本记录、DECISIONS D-122、PROJECT_STATE最新检查点、ai/INDEX。
- 测试工作目录read_board.py/audit_startup.py和只读证据/差异/JSON输出。
- 没有修改生产源码、板包ZIP/解压目录、板端文件、FPGA或已有进程。

## Remaining Work
实际修复和启动验证待后续实施；先完整v20 UI物料/ARM库，再恢复严格预检并修正解析/清单，最后采集/三帧/持续运行。当前包不能宣称可用，板端流水仍停止。

## Handoff Notes
板端目录whiteboard_candidate_v20，FPGA operating但应用已退出。保持原始故障证据，别复制v19库或继续关闭检查。当前源没有必要为这次UI符号错误重新综合；其余硬件功能和时序风险独立验收。板端墙钟2025，用户日期2026-10-19。
