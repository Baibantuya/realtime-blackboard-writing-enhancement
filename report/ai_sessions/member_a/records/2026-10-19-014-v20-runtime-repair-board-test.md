# AI Session: 2026-10-19-014-v20-runtime-repair-board-test
- Date: 2026-10-19 (Asia/Shanghai)
- Operator: User
- AI product/model: Codex / GPT-6
- Participants: User, Codex (single agent)
- Objective: 修复 v20 发布/UI/预检问题，并上板测试。
- Status: Complete; repaired candidate remains running on board
- Report candidate: no
- Related commits: none (untracked workspace)

## Context Read
沿用本对话已读取的 AGENTS/AI policy/INDEX，重新读取最新 PROJECT_STATE、DECISIONS D-122、session013、Git 状态和相关代码。
## Task and Constraints
用户明确授权继续修改并上板。保留失败包/旧目录及日志；修正检查而不绕过检查。优先 PS/发布修复，使用既有匹配 v20 固件，保留实验 timing FAIL。
## Contributions
- 修复HWH拆分指针高低字校验，将NativeUI/输入初始化前置到显示和DMA创建之前。
- 独立封包脚本从原始ZIP验证并保留9项硬件/驱动物料，递归包含UI原生源码、字体、图片及离线LVGL；恢复真实部署预检和验收。
- 三帧与PL功能脚本同步逐槽QualityMeta参数，量化全像素参考使用实际本帧metadata和filter_mode。
- 安装独立whiteboard_candidate_v20_fixed_20261019，实际2路ARM编译UI，99项软件回归复测全部PASS，完成真实硬件短时验收。
- 完整真实验收结束后启动UI，45秒监测、evdev三模式/记录/历史通过，用户确认实屏正常；结束回F3并保留运行。整理正式测试报告、证据与交接状态。
## Decisions and Adoption
- D-123记录授权与接口/发布决策。当前PS修复使用原v20固件，无新综合，原timing FAIL保留。
## Commands and Tools
- PowerShell/Python/rg/SSH/SCP；没有使用子AI，没有密码/令牌记录。
- `source/scripts/package_runtime_v20.py --package ... --archive ...`：从原始ZIP复制匹配硬件，封完整运行包；`test_workspace/v20_runtime_repair_20261019/verify_release.py`：真实HWH/20损坏指针/双清单/CRC/LF验证。
- 安装随包install_board_package.py到独立候选；板端`build_ui.py --cmake .../v19_ui_trial_staging_20261018/tools/cmake/data/bin/cmake --jobs 2`；`python3 -B -m unittest discover -s tests -p 'test_*.py' -v`使用新ARM库。
- `sudo bash run.sh check/deploy/status`为正式入口，无空预检、true-smoke或pass-HWH；原部署执行capture1000/全像素3帧/PL合成保护后启动。
- `test_predisplay_failure.py`板上阻断构造器验证旧库提前失败；monitor_trial.py读日志单调计数45秒；exercise_keys.py通过evdev只注入功能键，结束F3。与用户真实肉眼“画面和菜单正常”反馈分开记录。
- final_snapshot.py只读抓取运行/ABI/固件证据；summarize_result.py据真实日志生成正式JSON。
## Validation and Evidence
- 本地真实HWH/ZIP/清单PASS；20个指针高字偏移/位宽损坏用例全部拒绝。最终ZIP当前SHA256=2e32154072d9cda63fb1ff01aa5669832307be0662d61d90063e749d5e18eb1a，共134文件。
- 板端实际编译ARM UI成功；旧库故障验证中显示/DMA构造次数0；99项ARM软件替身测试PASS。正式preflight及PYNQ元数据检查PASS。
- 原流程加载FPGA成功；真实RGB565红绿蓝运输测试PASS；1000帧capture PASS，29.92465FPS，bad_frames=0，sequence_gaps=0。3/3全像素PASS，每帧4147200bytes，Restore仅初始化恒等验收；合成PL颜色4组、清场2epoch及人物/白衣/不可信门控/新字保留PASS，不能替代完整现场画质验收。
- 真实运行46.917秒窗口PASS：capture25.2785FPS，rectify3.7300、restore3.6873、quantize3.6660FPS；CPU127.2%单核口径（多线程），坏帧不增，新增Buffer Full/soft lockup/DMA timeout各0。
- 用户确认画面菜单正常。evdev测试0→3页，历史浏览期间quantized+17，返回F3；非人类物理按键验收。最后证据快照163.5秒/增强588帧、locked/safe、bad0、history3，PID51654/alive，FPGA operating。
- native ABI0x20，库SHA aeafae8c0e87db37eca4ea7f31487108f3e1f160330ae3a925d3015998e8bdf4；实际6个固件/模块哈希与包/原版一致。未重新综合/签核；200MHz时序FAIL仍在。
- 正式evidence/runtime_repair_board_test_20261019.json、docs/v20_runtime_repair_board_test_20261019.md；完整原始/失败与最终日志在本轮test_workspace。短试不等于长时间稳定、五项现场画质或v19/v20性能严格A/B。
## Errors and Corrections
- 初次WSL软件回归缺cv2失败，改在板端使用已编译ARM库执行原有99项软件测试；未安装系统依赖。
- 初次正式预检发现run.sh CRLF使pipefail选项失败。源码shell和打包输出统一LF，失败包/日志保留，复测预检PASS。
- 首轮99项软件回归4个导入错误，原因是测试替身未提供新增check_register_layout；补齐替身依赖，99项全部复测PASS。实际HWH正/负验证独立执行，不用替身代替。
- 为纳入文档/行尾/测试替身修正多次重封包，所有早期候选保存在test_workspace，原始f30713...失败ZIP未覆盖。
- 历史诊断脚本原来引用当前软件目录；修复后会失去复现原失败条件。改为从保留的原ZIP读取历史输入，并使用本轮保留的原始解压目录快照；历史审计复跑成功，原诊断与后续修复不混淆。
## Files Changed
- v20/source/software：hardware_abi.py、run_stage_pipeline_archive.py、board_stage_acceptance.py、board_v15_feature_acceptance.py、run.sh、configure_raw8.sh（LF）、deployment.json、README_PS_UI.md、tests/pipeline_harness.py。
- v20/source/scripts/package_runtime_v20.py；v20/board_package递归同步134文件、delivery新runtime_fix ZIP及sha256；原始失败ZIP不动。
- v20/README、evidence/runtime_repair_board_test_20261019.json；正式docs/v20_runtime_repair_board_test_20261019.md及原诊断后续链接。
- 内部本记录、D-123、PROJECT_STATE、INDEX；本轮test_workspace、历史audit_startup.py复现输入固定。
- 板端新独立目录ARM编译/日志/运行/3页内存归档；原失败v20和旧v19目录未覆盖。正式source HLS/RTL/bitstream未修改。
## Remaining Work
本次启动修复与短时上板任务完成。后续按现场需要做五项画质、同源PS/PL吞吐分析（当前约3.7FPS）与长时稳定验收；没有为这些未执行项填PASS。
## Handoff Notes
当前板端目录whiteboard_candidate_v20_fixed_20261019，PID51654保留运行，F3。F9菜单/F1-F3模式/F4-F5历史/F6记录；3页仅内存，退出清空。停止先用新目录run.sh stop，回旧v19需另行执行旧目录deploy，不能双开。板端墙钟2025不作日期/FPS依据；原生库必须v20 ARM，不复制v19库、不关闭预检。最终包SHA2e321...；不使用旧f30713...ZIP作可运行新包。
