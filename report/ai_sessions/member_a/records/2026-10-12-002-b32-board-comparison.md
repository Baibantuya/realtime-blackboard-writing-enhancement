# AI Session: 2026-10-12-002-b32-board-comparison
- Date: 2026-10-12
- Operator: Project owner
- AI product/model: Codex / GPT-6
- Participants: Project owner, Codex (single agent)
- Objective: 保留A6、切换指定B32并测同口径各阶段FPS。
- Status: In progress
- Report candidate: no
## Context Read
按序读AGENTS/政策/当前状态/决策/索引/近期A6会话、Git与B32板包。无缺失。
## Task and Constraints
使用之前部署脚本；保留A6完整包、固件、state和日志；沿用用户暂缓量化一致性、先运行/测帧率授权。
## Contributions
B32匹配板包检查、停A6并保留、原脚本上传安装、匹配加载、连续帧率对比。
## Decisions and Adoption
沿用同运行参数与评测口径。量化一致性暂缓不代表通过。
## Commands and Tools
PowerShell/PuTTY/原deploy_to_kv260.py与板端runner。
## Validation and Evidence
待执行；本次综合/实现未执行。
## Errors and Corrections
暂无。
## Files Changed
本记录。
## Remaining Work
保留A6、安装/加载B32、稳定窗口测量、状态更新。
## Handoff Notes
A6基线59秒3.437FPS、267.45/162.99/166.72ms。

## Switching Evidence
- B32源目录board_package与同级board_package_b32所有38项bundle内容一致，原清单PASS。原脚本归档39文件。
- A6正常stop_existing退出；完整复制到/home/ubuntu/kv260_apps/whiteboard_a6_saved_20261012，保存runtime_state_snapshot与resume_script_snapshot，逐顶层文件字节验证；源固件保留。
- 原upload脚本sudo installer保留previous/history，current=B32，previous=A6。历史目录20251017T061535Z-1760681735189958779-previous和20251017T061535Z-1760681735848954510-current；板端时间错误，不用作本次日期。
- B32 preflight37项PASS，metadata/HWH/driver检查PASS；xmutil unloadapp返回-1（无slot app），原overlay随后FPGA manager加载BIN成功，未导致部署失败。
- 使用限定b32_switch_20261012.py start，原runner activate(True)、原media配置、仅内存smoke=[]沿用用户暂缓授权；PID7404 B32_RUNNING，参数未改。
- 帧率测量待完成。程序加载成功不代表质量/像素验收；本次smoke未执行。

## Final Measurements and Handoff
- B32 second steady snapshot:30rows/61.111282288s，PID7404 alive=true，geometry locked/gen1，bad_frames0。
- captured1259→2444=19.3908548FPS；rectified353→817/restored352→816/quantized351→815，各464帧=7.5927060FPS。
- host median rectify70.174711/restore161.055206/quantize161.240358ms。rectify monitor6998385cycles/99999000Hz=69.98455ms。与A6相同live软件文件逐字节一致（run_stage_pipeline/pipeline_stages/board_detector/whiteboard_ip/shared_scanout）。
- A6基线3.43707458FPS/267.45375ms，B32整体约2.209倍，校正硬件约3.818倍速度提升；不是独立IP压测。
- host恢复/量化日志采样耗时与窗口实际吞吐的倒数不相符（161ms倒数6.21<实际7.59），因此不将耗时倒数称为IP上限/实际模块FPS。保留原事实；未为了推断更高精度暂停运行或单独压测。
- 已有第一次过渡快照27rows/53.47s，各阶段7.57-7.59FPS；第二次稳态确认全部7.5927。output_fps累计6.358含启动开销，不用作稳态。
- 本地证据test_workspace/b32_board_compare_20261012/live_fps_summary.json（板端原始摘要下载），分析脚本live_fps_summary.py；A6本地前次证据仍保留。
- B32保持当前运行；A6独立完整目录/home/ubuntu/kv260_apps/whiteboard_a6_saved_20261012、current.previous与历史、独立旧固件都保留。标准rollback会执行smoke，A6已知量化parity失败，若继续用户暂缓验收方式，应先正常stop当前，再恢复A6匹配固件并使用已保存resume脚本。不得在运行B32时直接无重载resume A6。
## Files Changed (Final)
本记录、INDEX、PROJECT_STATE、DECISIONS；内部b32_switch_20261012.py及FPS命令文件；kv260_deploy.local.json指B32源内board_package与before_b32备份；test_workspace/b32_board_compare_20261012脚本/证据；原脚本生成staging ZIP。原A6/B32源包未改。
## Status (Final)
Complete: A6已保留、B32已加载并持续运行、同口径稳态FPS比较完成。像素/视觉/长期验收按用户优先级暂缓，smoke未执行；综合/实现本次未执行。

## Follow-up Resource Inspection
用户询问B32资源；开始查匹配top-level报告，区分整机与OOC，未重新综合。

资源核对完成：匹配证据system_b32_20261012/reports/combined_utilization.rpt，Vivado2021.2/Routed/xck26；证据bit与部署包SHA一致。B32 LUT100456/117120=85.77%，FF107434/234240=45.86%，BRAM129/144=89.58%，URAM8/64=12.50%，DSP197/1248=15.79%；CLB14610/14640=99.80%。A6 LUT72879/FF88801/BRAM129.5/DSP199/URAM8；B32增27577LUT、18633FF。报告数据非本次重新综合；无板端变更。
