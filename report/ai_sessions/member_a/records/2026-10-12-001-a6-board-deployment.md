# AI Session: 2026-10-12-001-a6-board-deployment
- Date: 2026-10-12
- Operator: Project owner
- AI product/model: Codex / GPT-6
- Participants: Project owner, Codex (single agent)
- Objective: 将指定 board_package_a6 完整部署到 KV260 并验证运行。
- Status: In progress
- Report candidate: no
## Context Read
依次读取 AGENTS.md、AI_DEVELOPMENT_POLICY.md、PROJECT_STATE.md、DECISIONS.md、INDEX.md；长输出截断已补读近期尾部。读取最近相关 v5 部署会话、Git 状态、A6 deployment/README/manifest 与原部署脚本。无缺失。
## Task and Constraints
用户授权上板；保留旧版回退；使用原 A6 匹配包，不改像素算法或参数，不记录凭据。
## Contributions
确认原打包器默认读取 software 子目录，不适用于此完整平铺包；采用直接归档原包并复用 installer/run.sh。
## Decisions and Adoption
采用用户指定 A6；无架构/接口/工具版本改变。
## Commands and Tools
PowerShell、SSH/PuTTY、原 installer、A6 runner。
## Validation and Evidence
当前 Git 正式/测试目录未跟踪；本地双清单及板端检查待执行。综合/实现本次未执行。
## Errors and Corrections
尚无。
## Files Changed
本记录。
## Remaining Work
本地校验、连接、备份、安装、三帧 smoke、持续运行检查。
## Handoff Notes
目标 test_workspace/v10_rtl_20261011/v10_rtl_20261011/board_package_a6，候选 20261012-v10-a6-fetch。

## Deployment Results
- 用户要求使用之前部署脚本；最终采用原 deploy_to_kv260.py。补充完整平铺包分支，按原 bundle 校验并原样归档，避免覆盖 A6 专属 runner/README/manifest；原嵌套打包逻辑保留。安装阶段使用 sudo，修正历史已发现 root-owned previous 的权限问题。
- 原包39文件归档成功；板端 preflight37项 SHA、HWH、模块内核检查 PASS。内核5.15.0-1027-xilinx-zynqmp，42GB可用。
- 原 installer 已保留 previous/current 历史，板端 current=A6，previous原版本存在。history位于 /home/ubuntu/kv260_apps/history/whiteboard_candidate/20251017T055604Z-1760680564041603609-previous 与 20251017T055606Z-1760680566185345270-current。板端时钟仍错误，目录日期不代表本次操作时间。
- FPGA manager成功加载A6，最终state=operating；相机sensor flip/RAW8配置成功。
- board_stage_acceptance首帧相机/校正ringA与恢复初始化ringB全像素检查通过（按检查顺序及异常位置判断），PL量化与quantize_rgb参考比较失败：RuntimeError: PL quantizer pixel mismatch。三帧验收未完成，live未启动；未报告 FPS/实屏效果。
- 最终 pgrep 未发现实际 run_stage_pipeline/board_stage_acceptance 进程（只有检查命令自身）。原脚本未自动重载，未绕过量化验收。
- 源码/参考/寄存器静态核对无显然参数差异；根因尚未确定，不能断言硬件或参考哪方错误。
## Errors and Corrections
- 默认沙箱SSH被拒绝，按授权请求网络权限后连接成功；OpenSSH无密钥认证失败，转原PuTTY交互认证。凭据未记录。
- 初始计划直接归档，用户指定原脚本后改为补充原脚本平铺支持并使用原流程。
- smoke失败后核实停止状态，避免将成功加载当成完整运行成功。
## Files Changed (Final)
- kv260-whiteboard-enhance/scripts/deploy_to_kv260.py
- project_workspace/kv260_deploy.local.json；kv260_deploy.before_a6_20261012.json
- 本记录、PROJECT_STATE.md、ai/INDEX.md
- 原脚本生成test_workspace/kv260_folder_deploy_staging/whiteboard_candidate.zip
- 板端current/previous/history和A6固件；A6原包源文件未修改。
## Remaining Work (Final)
采集量化实际/参考输出差异和位置，核对实际量化网表/实现来源；修复匹配后重新三帧smoke，再启动live并做持续检查。综合/时序本次未执行；完整三帧/现场质量/FPS未通过或未执行。
## Status (Final)
Partial: 文件安装与FPGA加载完成；量化smoke失败，持续应用未启动。

## Follow-up: Resolve Failed Quantizer Smoke
- 用户明确要求解决问题；继续本会话。目标保存实际量化/参考差异，定位并修复匹配问题，重跑三帧并启动持续应用。
- Status: In progress (resumed)

## Follow-up Evidence and Owner Steering
- 独立诊断首次未设置XILINX_XRT导致No Devices Found，纠正为原环境XILINX_XRT=/usr后执行成功。
- 单帧compare1 camera/rectifier、compare2 restore-init均明确equal=true；compare3量化equal=false，69604像素差异，bbox覆盖全帧；实际颜色黑/绿/白，计数27610/122785/1923205。板端证据 /home/ubuntu/a6_quantizer_debug_20261012/mismatch.npz 和 summary.json。尚未确认根因。
- 用户提供源目录，已读取该目录；随后明确先运行、不继续一致性检查。取消待执行native/再次诊断命令，停止深入定位。
- D-087采用暂缓smoke验收：内部a6_live_resume_20261012.py复用原runner检查/启动，在内存manifest置smoke=[]；包源原样不变。核对当前A6和固件逐文件匹配、FPGA operating，原EDID1080p限定override与原media配置；activate(False)无重载。
- 启动成功PID6062，RESUMED；state增加validation=quantizer_smoke_failed_user_requested_live，避免被误当已验收。
- 新文件：test_workspace/a6_quantizer_debug_20261012/capture_mismatch.py；内部ai/handoffs/a6_live_resume_20261012.py；板端同名诊断/启动脚本及原量化C++（native编译未执行）。
- 持续检查待补齐。量化一致性仍未解决，用户当前优先目标为先运行。

## Final Live and FPS Verification
- 用户暂缓量化一致性，先运行目标已完成。PID6062两次ps持续存活（51/66秒），最终只读快照仍alive，geometry locked/gen1/safe，bad_frames0，三阶段计数持续增长。
- 最近30条实际日志窗口59.061854821秒：captured1245→2391，rectified/restored209→412，quantized208→411。camera19.4034FPS；三个阶段实际完成吞吐均3.4371FPS。
- 单帧host median rectify267.4538ms/restore162.9894ms/quantize166.7164ms；reciprocal3.739/6.135/5.998FPS仅当前并行运行耗时换算，不是独立IP极限。rectify monitor26723422.5cycles/99999000Hz=267.2369ms，与host一致，当前首要耗时瓶颈是rectify。
- 最近累计output_fps3.27594含启动开销，不能替代稳态3.4371。scanout_cpu_copies0；真实实屏质量与量化一致性未验收。
- 本地证据test_workspace/a6_quantizer_debug_20261012/live_fps_summary.json与分析脚本；只读，无停止/重载。
- 无g++ native重放执行；量化问题按用户最新优先级暂缓，未宣称已修复。恢复启动无需更改原包；正常run.sh deploy仍会执行并可能阻于smoke，当前专用内部启动脚本仅用于此次授权例外。
- Status: Completed for owner-requested live startup and FPS inspection; quantizer parity unresolved/deferred.
