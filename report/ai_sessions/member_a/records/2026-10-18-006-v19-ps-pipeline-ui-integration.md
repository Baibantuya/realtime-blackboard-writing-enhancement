# AI Session: 2026-10-18-006-v19-ps-pipeline-ui-integration
- Date: 2026-10-18
- Operator: User
- AI product/model: Codex / GPT-6
- Participants: User, Codex (single agent)
- Objective: 将指定 v16_ps_pipeline_ui_20261018 的最新 PS/UI 融入正式 dma_rgb565_quality_v19。
- Status: Complete (local integration; no board deployment)
- Report candidate: no
- Related commits: none; workspace files untracked before work
- Related files: formal rtl/dma_rgb565_quality_v19; test_workspace/ps_pipeline_ui_20261018/v16_ps_pipeline_ui_20261018

## Context Read
按序阅读 AGENTS.md、AI_DEVELOPMENT_POLICY.md、PROJECT_STATE.md 当前与历史检查点（长输出被截断）、DECISIONS.md 最新决策及索引、INDEX.md、2026-10-18 session005/session004、Git status 及相关目录。必需文件均存在；未找到该 UI 对应的既有内部会话记录。

## Task and Constraints
保留 v19 新硬件、质量算法、ABI 和固件身份；仅迁移最新 archive UI 入口及必需依赖。测试输出放独立 test_workspace 子目录。原 UI 输入目录只读；不在本次任务中部署、综合或修改运行中的板卡。

## Contributions
- 按 START_HERE.md 确认最新入口为 run_stage_pipeline_archive.py，迁移 archive UI、2Hz识别/方向引导、LVGL9.6.0字体/离线依赖、Linux输入、非阻塞scanout与可选但默认关闭的模型诊断依赖。没有采用来源包的旧固件/驱动/算法/清单或多代旧UI入口。
- 新入口采用v19候选和0x57424332门禁；保留原pipeline_stages.py、whiteboard_ip.py、quantize_reference.py及旧无UI入口不变，继续传入16px border inset，保持两DDR环、三阶段重叠和原AE/固定WB。
- 更新deployment.json的live/preflight，增加verify_runtime.py，包内路径哈希扩展至资源子目录。保留v19固件身份、smoke及内核接口。
- 增加PS-only封包刷新脚本，更新完整构建打包器以包含资源。源代码、board_package和同级ZIP同步，增加来源哈希/操作说明。
- 原公共安装器只支持纯平铺ZIP；在目标内新增install_board_package.py，支持规范相对路径、bundle校验、暂存解包和history/previous。公共安装器未改。
- 静态检查发现来源scanout把旧discardframe改名；补回兼容入口及回归，避免旧v19无UI runner回退。

## Decisions and Adoption
- D-115 已采用。F1/F2/F3选择原图/校正/深度增强，F4/F5浏览历史，F6保存pageflip确认且不含UI的像素；最多32页、仅进程内保存，退出清空，浏览和记录不重置恢复历史。
- 2Hz识别、30Hz展示是调度目标，不是实测板卡FPS。深度模式优先PL直写scanout并局部叠UI；原图/校正/保存等场景有CPU拷贝，不能泛称全程零拷贝。
- 可选模型仅作诊断，默认关闭，不控制恢复；没有进行真实推理验收。
- 200MHz既有时序FAIL保持实验标记，不能用软件PASS代替硬件签核。

## Commands and Tools
- PowerShell、Python、Git、rg、SHA256/ZIP/AST检查。
- WSL2 Ubuntu x86_64，Python3.8.10、GCC10.5、CMake3.30.5、NumPy1.24.4、OpenCV4.11、LVGL9.6.0。依赖及新版CMake仅安装于本次测试目录，系统环境未改。
- build_ui.py --cmake 指向本次测试目录的绝对路径；最终cmake --build native/build --parallel 16完成。x86共享库未放入板包。
- validate_linux.py --output test_workspace/v19_ps_ui_merge_20261018/linux_validation，BOARD_UI_LIBRARY指向本次共享库。
- source/scripts/refresh_ps_ui_package.py；测试目录audit_package.py；最终包verify_runtime.py和--ui-library预检。

## Validation and Evidence
- 实际LVGL原生编译PASS，继承的flag API有弃用警告，无编译错误；native_build_16jobs.log/native_build.json留证。
- **85项Linux软件测试PASS，0失败、0错误、0跳过，26.634s**。覆盖实际主入口三阶段同时在途/排空、三模式来源、无UI归档、模式防错标、历史浏览持续处理、32页上限、键盘/自动收起、DMA-BUF同步、v19 ROI/清板控制、安装器路径与损坏资源。
- hwh_contract.json：离线执行实际入口HWH检查器，现有HWH/寄存器通过，错误HWH拒绝；未进行硬件分配。
- ui_expanded.png/ui_collapsed.png为真实LVGL离线渲染，已目视检查，无乱码或控件裁切；不是实板照片。
- **233个受保护原文件SHA256未变**，包括硬件源码/固件/驱动/质量控制/旧无UI入口。融合前ZIP SHA256为bfce44546c0dfc5fa54011ec64f5036390abd0563c691c7334ff93df299fda5c，原ZIP与原board_package硬件一致。
- 组合硬件身份仍25fed13321efe203c81f19c54fa414ba04e5c3d77db6baa0c1b03fac1c1ccb1c；按kv260_board_run.hardware_hash组合文件名和内容计算，不是单.bit哈希。单.bit SHA256为297264abe736502ae35dcf0e9df583f9e62bf3cbca393b2585c21ab323439d62。
- 最终ZIP **128文件**，CRC、bundle集合/逐项SHA、源码/板包一致、实际全包暂存解包全部PASS。最终SHA256：e81e2c86790042c7874533e196bb2c80f892d57174ce4e3f464cfe28b36ccdc8。
- 最终包离线校验及实际LVGL共享库预检PASS；未传--board，不宣称硬件实测。
- 正式摘要：目标evidence/ps_ui_integration_20261018.json、ps_ui_linux_validation_20261018.json、ps_ui_native_build_20261018.json。完整日志、原生库、旧板包/ZIP备份和暂存解包位于test_workspace/v19_ps_ui_merge_20261018。
- **未执行**：ARM编译、KV260 DMA/DP/USB输入/画质/FPS/长时运行、新HLS/RTL/综合/实现/时序。未连接或修改板卡；历史PID不是本轮新证据。

## Errors and Corrections
- Windows rg通配路径未展开，改为目录加glob。长历史状态输出截断，后续以最新会话和决策为准。误猜package_v19.py后查明实际package_v17.py。
- Python3.9的write_text不支持newline参数、Windows默认GBK读取中文失败，改为兼容写法和UTF-8。最后长中文stdin记录脚本编码失败，改用apply_patch补全本记录；均未改变来源或硬件。
- WSL原CMake3.16低于要求，安装测试目录内CMake3.30.5；PATH未生效仍调用旧版，增加build_ui.py --cmake绝对路径选项解决。
- 初始4路编译较慢，确认实际进程树后中断自己的make调度器、复用对象16路完成。SIGINT未停非交互make，随后只对本任务已确认的三个make进程发TERM；没有操作其他进程。失败/中断日志保留，最终编译PASS。
- scanout旧API回退、旧安装器拒绝嵌套资源均已修复并验证。原生库只有API弃用警告，没有修改上游UI视觉语义。

## Files Changed
- 完整168项见测试目录files_changed.json，包含源码和板包两份资源及证据。
- source/software/新增UI入口、archive/recognition/guidance/input/model诊断依赖、ui_native/、vendor/、frontend_assets_current/、models/、board_enhance/、tests/、README_PS_UI.md、ps_ui_origin.json、verify_runtime.py和install_board_package.py。
- source/software/deployment.json、shared_scanout.py、verify_manifest.py、build_ui.py及测试适配；source/scripts/package_v17.py、refresh_ps_ui_package.py；source/README.md和根README.md。
- board_package对应源码/资源/system_manifest/bundle/说明；同级ZIP与zip.sha256；evidence/ps_ui_*三个JSON。
- project_workspace/DECISIONS.md、PROJECT_STATE.md、ai/INDEX.md、本记录。

## Remaining Work
本次本地融合已完成。后续在KV260停旧程序、安装/独立解压、ARM编译LVGL和run.sh check；验证真实三模式/归档/USB输入/几何切换，再对比FPS/CPU/CMA/长时画质。现有200MHz实验时序限制保留。

## Handoff Notes
先读目标README与board_package/README_PS_UI.md。旧公共纯平铺安装器不能装本包；使用目标内install_board_package.py或独立解压。不得把本次x86库复制到ARM。旧包位于本次测试目录baseline_board.zip及baseline_board_package/；来源UI目录未改。无提交、无上板；D-115、状态、索引已同步。
