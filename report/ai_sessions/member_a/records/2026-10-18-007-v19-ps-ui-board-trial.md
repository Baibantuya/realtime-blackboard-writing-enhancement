# AI Session: 2026-10-18-007-v19-ps-ui-board-trial
- Date: 2026-10-18
- Operator: User
- AI product/model: Codex / GPT-6
- Participants: User, Codex (single agent)
- Objective: 按用户“上板试试看”授权部署并实测已融合的 v19 PS/UI。
- Status: Complete; new UI remains running on board
- Report candidate: no
- Related commits: none; workspace initially untracked
- Related files: rtl/dma_rgb565_quality_v19; test_workspace/v19_ps_ui_board_20261018

## Context Read
按序重读AGENTS/AI政策、状态最新检查点、D-115/最新决策、索引、session006及部署说明，核对Git状态和工具。历史板卡PID只是先前记录，需要重新探测。

## Task and Constraints
用户已授权上板。先查板卡和运行进程，保留旧包/历史，编译目标ARM原生库，预检后部署，记录真实结果。不新综合，不改变硬件算法/频率。

## Contributions
- 通过SSH密钥认证连通KV260，确认sudo无需交互；旧程序PID49134、固件组合身份25fed133...。旧版目录whiteboard_candidate完整保留。
- 安装已核验e81e2c...板包到独立/home/ubuntu/kv260_apps/whiteboard_ui_trial_20261018，未覆盖旧版。板端缺CMake且无外网DNS，改由工作站下载ARM64 CMake3.30.5 wheel离线上传，安装于独立staging/tools。
- 在KV260用GCC11.4、2路实际编译LVGL9.6.0，产物ELF64 aarch64。板端Python3.10、NumPy1.26.4、OpenCV4.12；内核5.15.0-1027-xilinx-zynqmp。
- 用户接入SEMICO USB键盘，检测到event1/event4。正式预检通过后安全停止旧程序，原部署脚本加载同一硬件，执行1000帧/3帧全像素/PL功能验收并启动新UI。
- 初始板框未锁定，增强计数为0；用户按提示调整画面，随后geometry locked、安全，增强开始出帧。
- evdev注入F1/F2/F3/F6/F5并恢复F3，验证各模式可记录、浏览期间后台继续处理。用户另行确认“菜单正常，已调整画面”。结束保留新进程运行。
## Decisions and Adoption
沿用D-115；本轮用户“上板试试看”授权撤销此前仅本地验证边界，D-116记录部署事实。未新综合或改变硬件算法/频率；200MHz实验时序FAIL保持。独立目录试运行，原目录可回退。
## Commands and Tools
- PowerShell/Python/SSH/SCP；通过原有SSH密钥和sudo-n，不使用或记录密码。
- board_snapshot.py记录前后状态；monitor_trial.py使用日志单调时钟计数差计算FPS和内核错误增量；exercise_keys.py只注入F功能键，证据明确区分模拟注入和真实人类按键。
- 板端build_ui.py --cmake staging/tools/cmake/data/bin/cmake --jobs 2；sudo bash run.sh check；原目录run.sh stop；新目录run.sh deploy。
- 完整日志/脚本/离线wheel位于test_workspace/v19_ps_ui_board_20261018；远端构建与staging位于kv260_apps下的专用目录。
## Validation and Evidence
- ARM真实编译PASS；共享库SHA256见arm_library.sha256和正式证据。HWH/内核/126个包文件/原生UI预检PASS。未在ARM重跑本地85项全套替身回归，不能混称85项板测。
- 1000帧真实采集PASS：29.9073FPS，bad_frames=0，sequence_gaps=0；3帧全像素量化对照PASS；PL功能探针V15_PL_FEATURES_PASS（4组量化语义、2次清场、静止人物/白衣/不可信门控/新字合成场景）。不等于现场各类人物/画质全面验收。
- 初始59.343秒监测FAIL：几何未锁定、quantized_fps=0，摄像头29.624FPS、错误增量0；原始live_monitor.json保留。摄像头调整后锁定，第一个60秒交互窗口PASS，处理8.172FPS。
- 模式/记录/历史evdev注入测试PASS：起始0页、结束4页（期间用户也操作键盘，不能把总页数误称仅三次注入产物）；历史浏览期间quantized增加47。用户现场确认菜单正常。未从进程中导出三种归档像素作板上逐像素去UI比对；该语义的85项本地回归与本次实际可记录证据分开。
- 交互结束后30.253秒窗口PASS：quantized=10.5776FPS，rectified=10.5776FPS、restored=10.5445FPS；进程CPU约62.48%单核口径。最新2秒显示滚动值11.32FPS与30秒均值口径不同。
- 部署前后Stream Line Buffer Full、soft lockup、DMA timeout新增均0；最终bad_frames=0、geometry locked/safe，已存4页。原启动等待期导致累计output_fps较低，最终性能使用单调时间窗口差值。
- 最终进程PID65039，目录/home/ubuntu/kv260_apps/whiteboard_ui_trial_20261018，硬件组合身份仍25fed13321efe203c81f19c54fa414ba04e5c3d77db6baa0c1b03fac1c1ccb1c，保留运行。原目录未覆盖。
- 正式证据：kv260-whiteboard-enhance/rtl/dma_rgb565_quality_v19/evidence/ps_ui_board_trial_20261018.json；原始日志/构建receipt/按键记录/前后快照/dmesg在本次测试目录。
- 结束前再次status确认alive=true；运行382.30秒时quantized2664、bad_frames0、geometry locked/safe、滚动显示11.29FPS。用户继续操作，历史页已增至5；此前证据快照的4页是采样时点值。
- 未执行：新HLS/RTL/综合/实现/时序、长时间稳定性、广泛实际画质验收、严格控制相同ROI的旧/新UI性能A/B。新旧相机位置/ROI和测量窗口不同，不能直接用原寿命均值14.1与新10.6判定单独UI代价。
## Errors and Corrections
- 默认沙箱首次SSH拒绝，按用户上板授权使用网络执行权限后连通；没有自动审批拒绝。
- 板端pip联网失败（DNS），保留日志，改工作站下载ARM64离线wheel后安装成功，不改系统Python工具。
- 一次SSH内嵌python-c引号转义失败，未执行硬件操作；后续统一正式预检/文件脚本。
- 编译未完成时一次条件式预检未运行；库完成后正式预检PASS。
- 初始未锁定监测FAIL不是进程崩溃，也不能删掉；用户调整摄像头后两次复测PASS。
- 板端墙钟仍为2025，未擅自修改系统时间；用户日期采用2026-10-18，FPS均用单调时钟。
## Files Changed
- 正式evidence/ps_ui_board_trial_20261018.json、根README；内部D-116/PROJECT_STATE/INDEX/本记录；test_workspace/v19_ps_ui_board_20261018脚本与证据。
- 无生产PS源码、板包ZIP或硬件源码变化。板端独立安装、ARM构建/日志/新进程状态；原目录仅正常停止留下原日志/状态。
## Remaining Work
本次上板试运行已完成，留新UI供用户使用。后续按现场需要测试粉笔/白衣/擦除画质、长期资源/FPS及严格同源性能对照。4页只在当前进程内存，退出会清空。
## Handoff Notes
当前运行目录whiteboard_ui_trial_20261018、PID65039；F9展开底栏，F1/F2/F3切模式、F4/F5浏览、F6记录。旧whiteboard_candidate保留；回退先sudo bash新目录/run.sh stop，再sudo bash旧目录/run.sh deploy，不能双开。板卡时钟不准不影响本次单调FPS。硬件时序仍实验FAIL，不新增通过声明。
