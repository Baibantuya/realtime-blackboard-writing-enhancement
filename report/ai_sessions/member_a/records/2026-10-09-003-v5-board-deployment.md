# AI Session: 2026-10-09-003-v5-board-deployment
- Date: 2026-10-09
- Operator: Project owner
- AI product/model: Codex / GPT-6
- Participants: Project owner, Codex (single agent)
- Objective: 按原部署脚本将 whiteboard_stage_rings_quantize_20261009/board_package 的匹配 v5 部署上 KV260。
- Status: Deployment completed; live geometry acceptance pending
- Report candidate: no
## Context Read
按序读取根 AGENTS.md、AI_DEVELOPMENT_POLICY.md、PROJECT_STATE.md、DECISIONS.md、ai/INDEX.md；长文件输出部分截断后补读当前末尾。读取最新 v5 构建记录及此前 shared-ring 上板记录、Git 状态、原部署/安装/板端运行脚本及 v5 deployment.json/README。未发现所需文件缺失。
## Task and Constraints
用户授权实际上板，复用原安装/运行流程；保留旧包/固件和回退路径，使用匹配 v5 新 bit/HWH/DTBO/PS，固定 WB 不变。不记录凭据。
## Contributions
确认 v5 新固件名、三个 PL 基址、三帧 board_stage_acceptance smoke 和 run_stage_pipeline 入口；检查原本地配置尚指向 Oct1 包。
## Decisions and Adoption
采用用户指定 v5 匹配包。无算法、架构或工具版本变更。
## Commands and Tools
PowerShell、原 deploy_to_kv260.py/kv260_install_folder.py/kv260_board_run.py、PuTTY/OpenSSH。
## Validation and Evidence
Git 顶层交付/测试目录当前未跟踪，未覆盖已有改动。初次只读 plink 连接被网络沙箱拒绝，尚未验证板端。硬件加载、smoke、live：未执行。
## Errors and Corrections
网络访问需沙箱外执行；依照工具权限流程重试只读连接。
## Files Changed
本会话记录；后续补齐。
## Remaining Work
连通与认证、板端状态/备份、匹配包安装部署、实际 smoke/live、更新状态与索引。
## Handoff Notes
目标 package 为 test_workspace/whiteboard_stage_rings_quantize_20261009，内置驱动目标 5.15.0-1027-xilinx-zynqmp。此前板端 PID 记录仅历史证据。

## Deployment Facts and Corrections
- 用户提供本次交互认证，未写入文件/命令参数/工程日志。核实板端内核 5.15.0-1027-xilinx-zynqmp，43GB 可用；sudo 需认证。
- 原33文件交付 ZIP CRC/bundle/system 两清单校验 PASS，SHA256 65ba1110c61764d875870dd0eab911533fccddf12d2eb9627e5e8a129521c994。原脚本重新生成 whiteboard_candidate.zip SHA256 66a0daf55fd18ac7ad2bf39c71a3b397fdef2074b8c1296ad8511996c6bfe624，板端 preflight31文件 PASS。
- 本地配置已备份到 project_workspace/kv260_deploy.before_v5_20261009.json，package_dir 改为 v5 根目录（原脚本读取其 deployment.json，硬件/软件取 board_package）；板端目录保持 /home/ubuntu/kv260_apps/whiteboard_candidate。
- 旧板端状态+旧固件目录完整复制到 /home/ubuntu/kv260_apps/history/before_v5_20261009，现场打印7个文件哈希；固件保留原目录。原 installer 保存 previous/current 的不可变历史，并将旧当前版本置于 whiteboard_candidate.previous。
- 原 deploy_to_kv260.py 上传完成，但普通 ubuntu 安装在 rename 旧 previous 时 Permission denied。未修改权限或删除旧包；纠正为 sudo 运行同一 kv260_install_folder.py，再执行原 run.sh deploy，成功。
- 加载新固件 wb-stage-rings-20261009，FPGA operating；31文件 preflight/HWH/kernel/check PASS。实际3帧1080p，每帧6,220,800 RGB字节，camera/rectifier/ringA、restore初始化/ringB、PL量化全像素参考均 PASS。
- 初次 PID6551 启动后退出，实际 status alive=false；live.log 为 Display needs1080p。此前启动器4秒观察不够，明确纠正初次 DEPLOY_RUNNING 不能代表持续运行成功。
- 针对显示恢复尝试远程 root 交互 shell 被自动审批拒绝（权限范围过大）；改为具体限定的恢复脚本，无需扩大权限。没有绕过拒绝开启 shell。
- 内部 v5_display_resume_20261009.py 复用历史已验证128字节 CTA1080p60 EDID，仅在 DP-1 connected 且 EDID为空时设置 debugfs override；核实已安装 v5、无活进程、FPGA operating、固件文件与包一致，调用原 prepare_check/stop_existing/activate(False)/save_state。第一次恢复 EDID读回正确，但 sysfs modes 尚未刷新，过早检查导致退出；纠正为交由原 PYNQ DisplayPort 枚举及其严格1080p检查验证，后续 sysfs已显示1920x1080。无项目像素代码或 PL 修改，无 FPGA 重载。
- 恢复激活再次实际3帧全像素 smoke PASS；PID7909、初次恢复检查 alive=true。后续持续阶段计数待最终检查。
- 板端时钟为2025-10-17（错误），历史目录/started/log使用该时间；用户本次工程记录日期为2026-10-09，不据板端时间推定当前日期。未改系统时钟。

## Final Validation and Handoff
- 最终实际 status PID7909 alive=true；captured905→1101、inputs_sampled842→1036、bad_frames0，固定WB1.6838/1/1.5259 unchanged。DRM实际 active=1，1920x1080@60，148500kHz；connector modes1920x1080。
- 实时 detector_stage=line_fit，边缘点约[1,0,3,1]或[1,0,4,2]，failure=insufficient_consistent_edge_points，geometry_generation0/calibrating；rectified/restored/quantized均0，output_fps0。按原设计未锁定显示纯白，不能报告真实矫正/恢复画面成功或处理FPS。smoke只验证identity/恢复初始化/全像素调色板，不是现场几何/恢复历史质量验收。
- 板端bit SHA256 da2e273b4eb9ab636a7be65dfa8377ccc68e928c6e70287fe430aec61aa61ab6、HWH SHA256525a97b99e9d30b05b641d030d42bd5fd00856df0722c3fa0313eff3596dd4f8与交付一致。
- AI贡献已采用：包校验、配置目标、保留历史、sudo安装原脚本、硬件加载/6次全像素检查、限定EDID恢复、实时核验。未修改交付包、算法、PL或固定WB。
- 修改文件：本记录、ai/INDEX.md、PROJECT_STATE.md；kv260_deploy.local.json及before_v5备份；内部ai/handoffs/v5_display_resume_20261009.py。原脚本生成test_workspace/kv260_folder_deploy_staging/whiteboard_candidate.zip。板端修改：current包/state/live.log/history、新固件、DP-1临时EDID override、/home/ubuntu/v5_display_resume_20261009.py。
- 遗留：现场定位失败，另行检查实际相机视野/边缘检测；视觉颜色/真实恢复历史/长期稳定性/实际处理吞吐未验收。此次不扩大为算法修改，保留已部署版运行。
- 重启/热插拔可能丢失临时EDID；限定resume脚本要求无活进程且已加载匹配v5，不替代冷启动部署。冷启动先恢复EDID，再原run.sh deploy。
- 回退：whiteboard_candidate.previous为部署前v4；history/before_v5_20261009包含原state/固件；原run.sh rollback可使用previous。无自动反复加载/强杀DMA。用户本次部署目标完成，局限已交接。
- 记录更新第一次补丁因INDEX标题不匹配失败，读取真实标题后重新应用；未遗留部分写入。

## Follow-up: Live FPS Check
- 用户要求先查看当前帧率，采用本次部署记录继续；只读查看实际status及连续日志，区分camera采集与三阶段完成输出，不修改程序/硬件。
- 原程序日志约每2秒输出，output_fps定义为累计quantized/进程运行秒数；读取结果待补齐。
- 实读PID7909 alive=true，最近18条日志captured41070→41730、inputs_sampled38881→39535、三个PL阶段均停在16帧、bad_frames0。由各条真实output_fps和恒定quantized16反算时间（16/fps），首尾约34.05秒，采集约19.4FPS、PS输入采样约19.2FPS，最近输出0FPS；累计输出仅0.00743FPS（此前偶尔处理16帧后停顿，不能当模块处理能力）。geometry_generation已为1，状态反复held/confirming，边缘点不足；两个ring全FREE，非在途PL积压。更新之前gen0状态为历史事实。没有源码/硬件修改，未单测模块吞吐。用户本次只读查看帧率完成。

## Follow-up: Explain Geometry Hold/Confirmation

## Follow-up: Proposed Color and Localization Repair
- 用户后续明确显示BGR应记住，不每次重复验证；采纳固定显示BGR契约，撤回每部署重做颜色验证的建议。澄清仅PS可修改定位/调度及现有量化参数/通道控制，但PL像素分类/邻域逻辑若改须重构建；不擅自将量化移至PS。仅记录与解释，代码/板端未改。
- 用户报告红蓝反向反复出现、连续彩色字迹中夹黑，要求先给方案再改动。只读当前v5 pipeline_stages/quantize_reference/HLSpalette/V4L2代码，未修改源代码或板端。
- camera声明RGB24，中间按RGB，live量化bgr2交换输出、显示PIXEL_BGR；实际哪个环节与声明不一致尚未验证，不直接删swap。现有smoke bgr0不覆盖live输出/显示，参考模型同源不能证明实际颜色正确。
- palette逐像素hi>=130且hi-lo<32直接黑，可解释同笔画色度变化夹黑，需中间帧排除restore污染；当前暖色实际为橙255/128/0，不是红。方案D-078待审：物理红蓝绿参考+色条验证唯一通道契约；相对色度/强彩色种子/弱候选/限定3x3笔迹邻域色类支持，保护中性白笔黑输出和细线；暖色建议改红。定位实帧检查左右边和旧角点/搜索窗，有限扩窗恢复+可信H在短暂失败时继续，确认移动或主动校准才暂停，保留3次一致和流水排空/历史重置。人工四角兜底建议。
- 未执行新板测/中间帧捕获/算法验证；PL量化改动若采用须新构建匹配包。等用户审阅方案，不开始实现。第一次记录补丁因DECISIONS标题不匹配失败，纠正标题后重写，无部分改动。
- 读取当前v5 GeometryTracker和调度条件。日志边缘样本顺序为上/下/左/右：[7,8,0,0]表明左右边未找到；拟合每边需要至少4个一致点。连续失败>=3后暂时不传accepted给detector，重走bootstrap；bootstrap偶尔得到[8,8,8,7]有效四边，但进入confirming说明其与accepted不满足16px小变化条件（或强制校准）。候选需连续3次互差<=8px，失败即清空pending_count。
- unverified_motion一旦设置，会跨candidate=None保留，restore_safe继续False。故held只保留旧矩阵，不必然允许处理；run_stage_pipeline明确拒绝新帧入PL。日志模式与“局部跟踪失败3次→bootstrap成功确认1次→再次局部失败”相符。此为代码+日志推断，不证明真实相机移动、遮挡、阈值或旧角点具体哪项造成边缘识别失败；未采集新图像、未改代码/状态机。
