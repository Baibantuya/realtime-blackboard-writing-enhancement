# AI Session: 2026-10-19-020-v21-local-implementation
- Date: 2026-10-19 (Asia/Shanghai)
- Operator: User
- AI product/model: Codex / GPT-6
- Participants: User, Codex; single agent
- Objective: 本地实现v15恢复逻辑冻结、恢复/量化两核分担的v21独立候选；新增/擦除/白蓝红及持续人物保护，同时施加固定资源预算。
- Status: Complete local core/driver prototype; live integration and hardware signoff pending
- Report candidate: no
- Related commits: none

## Context Read
按入口规范阅读AGENTS、AI_DEVELOPMENT_POLICY，最新PROJECT_STATE、DECISIONS、INDEX、session018/019及正式算法方案；检查Git（正式目录整体未跟踪，不能用git diff冒充来源验证）、无发现更深AGENTS；阅读正式v15量化/guarded源码及编译配置。
## Task and Constraints
用户授权本地开始修改；不综合、不上板、不启动远端构建。正式v15恢复/guarded逐字节冻结；新独立v21目录，旧v15/v19/v20不覆盖。资源不增长是门槛，未综合时不能宣称达标。
## Contributions
建立独立v21候选并冻结8份正式v15文件；实现PS小图持续对象ID/四态、可信启动、光度有界调整、prepare/refine同帧与候选失效；融合量化维护4位权威Canvas和唯一新增/擦除，支持白/蓝/红/绿、软灰继承和确认白保护。加入配对槽Restore完成/Quantize完成所有权、非阻塞新HWH注入驱动、真实完成事件FPS、固定资源预算报告门禁与一键native/合成回放。为压缩硬件/带宽，将B改为PS小图辅助，5x5四行缓存、两AXI单读单写过程、128像素块/五个64词FIFO，候选位不另开平面。未改实际UI/旧板包。
## Decisions and Adoption
D-128：采用上述实现作为本地候选，不代表现场或硬件验收。D-127的v15资源上限保留；双4位Canvas仍增加2,073,600B DDR，量化逻辑像素流量较旧量化多2,073,600B/帧，metadata/PS另算。新算法ABI0x57425321；v15恢复ABI不变，新量化寄存器只允许匹配新HWH注入，禁止猜偏移或混用旧包。UI主入口/实际双环接入仍待后续导出HWH联调。
## Commands and Tools
本地Python3.9.1、NumPy1.21.2、OpenCV4.5.5、TDM-GCC10.3.0；运行source/scripts/validate_local.py --output test_workspace/v21_local_20261019/verified_source。该脚本仅调用g++编译native DLL与有界FIFO C++testbench、unittest、100帧合成回放，未调用HLS/Vivado/远端。源码哈希、AST和SOURCE_ONLY无板包/无build边界核对；目视检查合成input/v15/newCanvas接触图。
## Validation and Evidence
- 67项native/软件/MMIO与CMA替身检查PASS，0失败/错误/跳过；含1080p边界/stride/输入不变/四通道序、暗蓝与浅红浅蓝、白夹红蓝、软灰蓝线、红蓝交叉、旧字部分擦除/重复遮挡、过期/重复/错代次/Restore写入超时保护，三衣色人物模拟≥60秒不老化。
- 独立C++testbench使用实际reader/scan/writer三个并发过程、64词有界FIFO运行1920x33（跨块行和partial row）、padding/HOLD/擦除/拒绝，errors=0；这不是RTL或真实AXI等待模型。
- 100帧有真值合成输入实际执行冻结v15与新量化；初始化、65帧人物遮挡期间和最终画布像素错配均0，退去后第二观测旧白字448像素→0；新蓝/红可显示。目视图一致。不是当前现场实拍验收。
- 正式结果候选evidence/local_validation.json；完整日志、native二进制、NPZ、preview.png在test_workspace/v21_local_20261019/verified_source/，早期失败与中间结果在同topic其它子目录保留。最终所有source SHA再次核对一致。
- HLS工具Csim/综合、RTL协仿、整机实现/资源/时序、ARM、上板/实际FPS：未执行；资源是否不增长仍为null/未知。host native耗时不等同PL耗时。
## Errors and Corrections
首轮43项中22项因ctypes把10个标量误写11个而未执行内核，修正后进入真实功能测试；暗蓝灰边缘被强阈值判裸板导致1项失败，改为有多色种支持的弱候选并补64/80/104软灰与确认白保护后通过。最终将白字中的单个高饱和红/蓝杂点也纳入白字锚点保护：无同色多种支持时不能覆盖中性笔画，新增负例通过。复查将多个共享AXI reader/writer改为单方向统一读写，规避潜在有限FIFO循环等待，并增加并发有界验证；并非实测硬件死锁。复查补齐显式Restore完成确认，mask超时/取消不能提前释放B写入者，补负例通过。v15旧历史只作辅助，不能独自阻止裸板露出。早期Python3.9不支持Path.write_text(newline=...)与补丁同名方法误匹配均在本地纠正，未改冻结基线。
## Files Changed
- kv260-whiteboard-enhance/rtl/dma_rgb565_scene_v21/README.md、run.sh、STOP_BEFORE_SYNTHESIS、evidence/local_validation.json
- 候选source/baseline_sources.json；hls/board_scene_quantize.cpp、board_scene_quantize.h、scene_stream.h、build_scene.tcl；冻结复制的8个hls基线文件（完整名单/SHA见baseline_sources.json）。
- 候选source/software/scene_tracking.py、scene_native.py、scene_stage.py、pipeline_metrics.py、replay_scene.py
- 候选source/scripts/build_local.py、resource_gate.py、validate_local.py
- 候选source/tests/test_scene_native.py、test_scene_tracking.py、test_scene_stage.py、test_resource_gate.py、test_scene_hls.cpp、generate_demo.py
- kv260-whiteboard-enhance/docs/v15_frozen_restore_scene_algorithm_20261019.md
- project_workspace/DECISIONS.md、PROJECT_STATE.md、ai/INDEX.md、本记录
- 验证生成物仅在test_workspace/v21_local_20261019/。
## Remaining Work
需要实拍粗字/近板色人物/手/阴影粉尘、多色交叉和初始遮挡反例；当前是经典形状/差异跟踪，不能宣称完整语义分割。实际UI主入口/双环需要适配新Stage与trusted启动信号；需后续真实导出的HWH联调，不能混用旧v15/v20寄存器表。资源/II/时序/CPU与DDR/实际吞吐仍待得到构建指令后验证，不把本地PASS当系统任务全部闭环。
## Handoff Notes
当前板端与历史包保持，不把旧PID作为本轮存活事实。
