# AI Session: 2026-10-18-011-v20-joint-source-implementation
- Date: 2026-10-18
- Operator: User
- AI product/model: Codex / GPT-6
- Participants: User, Codex (single agent)
- Objective: Implement all five authorized fixes as an independent v20 source candidate; no synthesis.
- Status: Complete (source candidate and local verification; synthesis prohibited and NOT_RUN)
- Report candidate: no
- Related commits: none

## Context Read
Root AGENTS, AI policy, current state, D-118/119, index, session010, Git status read in order. No nested project AGENTS found last turn.
## Task and Constraints
User explicitly authorizes source modification and prohibits synthesis. No HLS synthesis, RTL cosimulation, Vivado build, bitstream creation or deployment. Preserve v19 and running board. Local native compilation/reference/software tests allowed.
## Contributions
- 从v19复制独立v20源码，保留原有RTL/驱动源码/PS UI资源，移除副本中的预编译.ko，不复制固件/板包；v19源447文件SHA256最终逐项一致。
- PL Restore新增独立32bit/block板材状态，初始化使用邻块原始候选共识及局部样本支持，解决首样本/半块字导致的底色误选；局部擦除按像素确认/提交，显示与未提交历史一致，细化稳定迟滞和淡字色差，擦后不召回旧字；新增16-word诊断与新ABI。
- PL Quantize新增可靠彩色种子传播及兼容笔画支持，保护中性色与异色；在原7x7窗口内加入关闭/条件高斯/范围加权/条件中值四模式，默认2。保留原RGB色相；不添加多帧RGB平均/持久颜色锁。
- PS新增FrameContext和可撤销AdmissionGate、Ring B逐槽QualityMeta、Restore/Quantize控制寄存器及严格匹配校验，防止在途跨帧元数据错配。
- 采集侧10Hz稀疏运动线程采用分布式光流/鲁棒仿射，精确定位接受帧提供参考；运动与失检状态修正、旧代次接纳/显示/归档门控、独立调整UI与排空切换。
- 六种真实事件FPS，F1 CAP/F2 RECT/F3 ENH及DISP区分，历史STATIC，停流归零/重绘去重。原生C复制/混合、dirty overlay缓存与原生ABI验证；继续采用同步有界显示操作和现有最新帧采集策略，无新增异步借用源缓冲。
- 新增软件安全/显示/实际主循环运动回归，C++启动部分/淡字擦除及颜色测试、逐帧元数据/全高清/四滤波参考对照、合成噪声实验、native-only验证器与正式README/证据。
## Decisions and Adoption
- D-120：用户授权五项源码实施并明确禁止综合。独立v20 source-only，STOP、Tcl/继承shell构建入口和部署均拒绝执行；没有新板包/固件，不操作运行中板卡。
- 算法ABI0x57425120，场景magic0x57424340，帧池ABI6保持。新增QualityMeta每B槽32640B，三槽97920B DDR；持久板材32640B DDR，复用block_memory/gmem0 AXI，不新增像素环。
- 先使用空间滤波，不增加可拖延擦除的时间像素状态；原生C显示性能与真实粉尘效果留待ARM/现场验收。新增循环/动态归一化的II、资源和时序未知，不能假设可在拥挤的200MHz设计中通过。
- 新寄存器是显式源码规范，尚无生成HWH核验；不得把本地native PASS当作HLS/RTL或板端PASS。
## Commands and Tools
- Windows g++原生构建/C++与ctypes NumPy参考；WSL x86_64 LVGL9.6真实CMake编译及Linux软件测试；Python/rg源码复核与哈希审计。没有SSH/SCP、服务器或板端操作。
- Native命令：source/scripts/verify_presynthesis_v20.py --output test_workspace/v20_joint_source_20261018/native_release。
- Linux命令：source/software/validate_linux.py --output .../linux_release；UI库位于.../ui_build/libboard_ps_ui.so，使用既有本地依赖，未联网安装。
## Validation and Evidence
- 最终99项Linux软件/UI测试PASS，0失败/错误/跳过，包含三阶段同时在途的大移动旧代次丢弃、逐槽元数据配对、帧率/归档/原生C像素等价；linux_release/validation.json。
- 最终24项native检查PASS：新画质专项、旧画质回归、Restore局部/场景/1080p、12组标量栅格、82组颜色语义、36组NumPy栅格（4组1080p）、32组元数据四滤波模式、4次1080p带元数据Restore及哨兵隔离、控制器/队列/调度/syntax；native_release/presynthesis_result.json。
- 新专项对4种启动笔迹做局部擦除，持续120次轻微板面变化后再遮挡，不召回被擦部分且保留未擦部分。
- 五档合成RGB颗粒，默认滤波误前景31/215/866/1825/4057 -> 0/16/121/302/1672（约58.8%-100%减少）；各档142像素线与4像素标点全部保留。不是实拍粉尘、真实蓝字准确率或硬件FPS指标。
- LVGL x86_64实际编译PASS，双FPS离线截图目视检查，示例数值明确标为非板端测量；ui_rates.png。
- v19源447文件前后SHA256完全一致；正式v20 evidence包含精选报告，完整原始失败和复测保留在独立test_workspace。
- HLS工具C仿真、HLS综合、RTL协同仿真、Vivado综合/实现、bitstream、ARM、板测/FPS全部未执行。
## Errors and Corrections
- 初版色相传播使旧白字红色保护用例失败，收紧红/绿歧义偏置后82组全部通过；旧标量oracle需更新新色相支持规则，保留关闭滤波下独立栅格对照。
- 新淡字用例发现半块文字/板面平票仍可误选底色，改为跨邻块共识+局部支持+距离代价消歧后通过；降低像素擦除所需色差但保留明确向板材靠近的证据。
- 初版滤波旁路与前景接纳条件相同，合成实验发现四模式误检完全相同，证明滤波没有影响幸存噪声。改为更严格笔画旁路，复测各档显著改善，初始失败数据保留。
- 无关缩小WB_FRAME_WORDS破坏原1080p尾哨兵用例，恢复原安全缓冲容量；实际DDR分配仍按RGB565像素数，未增加运行时帧内存。
- WSL普通权限访问被拒，按环境权限使用wsl前缀批准执行；WSL缺cv2时复用既有本地依赖。无综合权限请求/执行。
- 第一轮软件93项中两项未传新metadata的旧ABI契约用例失败，更新为新接口及拒绝旧ABI后通过；后续98与最终99项均0失败。
- Windows rg通配路径未展开，改为目录/glob方式；README v20提醒首次追加到末尾，最终移至开头。
## Files Changed
- 正式rtl/dma_rgb565_quality_v20/（source、README、evidence），docs/v20_quality_motion_display_execution_plan_20261018.md状态更新。
- 内部session011、D-120、PROJECT_STATE、ai/INDEX；test_workspace/v20_joint_source_20261018全部测试/渲染/审计材料。
- v19源码/固件/板包和运行进程无改动。
## Remaining Work
- 按用户指令停在已修改且本地验证的源码候选。新HWH导出核对、HLS/RTL/整机/时序资源、ARM编译、匹配封包和现场五项验收需后续新的构建/部署指令。不能为这些未执行项填PASS。
- 实拍固定粉尘、弱孤立标点、初始化大遮挡、强粉尘与笔画像素同形及实际显示吞吐仍需验证；既有v19 200MHz实验时序FAIL未改变。
## Handoff Notes
Do not synthesize. All scene-quality/FPS/resource improvements require later hardware validation.
