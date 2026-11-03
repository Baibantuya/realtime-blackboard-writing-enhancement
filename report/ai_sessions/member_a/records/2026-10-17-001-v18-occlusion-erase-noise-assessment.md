# AI Session: 2026-10-17-001-v18-occlusion-erase-noise-assessment
- Date: 2026-10-17 (Asia/Shanghai)
- Operator: Project owner
- AI product/model: Codex / GPT-6
- Participants: Project owner, Codex (single agent)
- Objective: 对照用户指定 v18 上板包及 v15/v16 源码，评估浅衣遮挡退化、擦除延迟和粉尘区噪点，并提出兼顾方案。
- Status: Completed assessment and native probes; recommendations only, production unchanged
- Report candidate: no
- Related commits: none; workspace Git status shows untracked project/test trees

## Context Read
- 按顺序读取根 AGENTS.md、AI_DEVELOPMENT_POLICY.md、PROJECT_STATE.md、DECISIONS.md、ai/INDEX.md；状态全文输出过长，重点阅读最新状态及相关恢复/量化历史，决策读取近期条目。
- 最近相关记录：2026-10-15-002、006、007 与 v15/v16 handoff；未发现 10-16/10-17 或 v18 专属内部会话记录。
- 已检查当前 Git 状态；没有提交或清理既有未跟踪文件。

## Task and Constraints
- 用户请求原因分析与解决思路；本轮不修改生产算法、不构建固件、不部署、不接触运行板卡。
- 用户现场反馈：v15 浅衣处理良好，v16/v18 浅衣边框严重且擦除失败；可擦除时存在延迟；粉尘泛白区噪点明显。属于用户观察，尚无同帧输入/中间输出序列。
- 保留原架构和两个 DDR 环；内部结论与建议仅写入 project_workspace。

## Contributions
- 只读服务器取回 v18 的 8 个 HLS 源/头文件，逐项 SHA256 与用户指定包 system_manifest.json 一致，保存于 test_workspace/v18_quality_assessment_20261017/v18_hls。
- 发现本地正式目录 v16 源码滞后，其 restore/quantize 哈希对应 v18 的 .bak；改从正式 handoff complete ZIP 读取 v15/v16 发布源码对比，保留原目录不修改。
- 用户确认比较基线为 10 月 15 日 color_cache_clear_v15 正式 handoff 包；排除 test_workspace/v15/source_v15 同名直连分支。
- 发现工作区根有旧 .Xil 及 3 个 vivado_*.backup.jou；目录时间为 9 月 27 日，本机无 vivado/xsim/xelab 进程。按工程规范将这些工件保留迁移到 test_workspace/v18_quality_assessment_20261017/root_artifacts_archive，不将它们作为本次测试证据。

## Decisions and Adoption
- D-108：建议把局部遮挡、板面可见性、新字提交、擦除提交分开；局部可见区域采用快速擦除确认，整屏 rebase 只作维护；量化按背景/成簇纹理/随机闪烁分层处理。仅建议，未实施或获得后续硬件构建授权。
- 用户确认正式 color_cache_clear_v15 为比较基线。不是 test_workspace/v15/source_v15 直连分支。

## Findings
### Version provenance and correction
- 正式 v15/v16 complete ZIP 的 hls 文件已复制到测试子目录 v15_hls/v16_hls；v18 从 /data1/leisheng_codex/wb_rgb565_quality_v18_150mhz_20261017/hls 只读下载。v18 8 文件全部与用户指定包 source_sha256 一致，source_audit.json 保存证据。
- 正式目录的本地 v16 restore/quantize 对应早期 .bak，不能代表最终发布。最终 v16 已删除 white_changed>=5 的单块强制占用逻辑。
- v16 去掉 ink 的 writes 门控，v18 已恢复（whiteboard_restore.cpp:219）；因此“v18 仍由该门控缺失造成轮廓”这一归因不成立。
- 历史记录把 bulk_white_blocks 称为“多块连通域”不准确：实际是全 ROI 计数，只用于整屏 rebase 原因位，没有连通域分析，也没有把白块加入局部 mask。
### Occlusion and erase coupling
- v18 occupied/motion 仍排除当前及历史 chalk() 中性亮点（:412-415）；白衣若未由暗色部位形成遮挡 core，可不进入 mask，原图通过后量化将亮边缘显示为字迹。该盲点 v15 也有，不能据合成例子否认用户实际 v15 更好的观察。
- mask 为 core 周围 3x3 块；禁止写回区域为 5x5 块（guarded_state.cpp:109-117），即每块16x16时可影响80x80范围。人的局部附近即使某像素已露出板面，仍可能 writes=0，所有擦除提交通道一起被挡。
- v18 dim/color erase 新增 board_return：须 auto_clear 开启、源帧可信、存在与旧背景相近的非 chalk 样本、qu==0、所有当前样本距该样本<=quiet_delta/2（默认8），所有变化都是旧值变亮的逆转，且至少3/4样本不变（:423-437）。大范围变暗、擦后粉尘不均匀等不满足时仍可能保持旧占用。
- is_erased 与 local_erased 都受 !is_broad、writes、!mask、稳定计数等共同限制（:222-226）。泛白粉尘可仍被当成 broad/chalk，使“擦掉后必须变暗且不中性亮”的假设失效。
### Latency
- 实际包 WhiteboardIP DEFAULT_CONFIG 为 stable=3、hold=6，不能误用 guarded_restoration.py 中旧 hold=300 的默认值。clear_frames=8、cooldown=64 为整屏重建条件，不是每次局部擦除必经等待。
- 像素在首个变化处理帧 q=0，随后3次稳定比较才到 q=3；因此是按实际恢复处理帧率产生延迟，150MHz不等于150fps。邻域写保护可持续更久；不能机械把 hold、stable、clear_frames 相加。
- 本次没有板端完成率、输入到显示时间戳或当前队列深度，无法给出现实延迟数值或把延迟唯一归因到队列。
### Noise
- 已有7x7局部均值对比度与 strong=16/weak=6，不是单一绝对亮度阈值。v16增加弱点方向支持或 neighbor_count>=3；2x2亮斑各有3个同色邻点，容易互相保活。
- v18新增输出标签3x3过滤只去 same==0 的孤立点（board_quantize_rgb.cpp:205），成对/2x2团簇可保留。历史声称已经抑制2x2 Bayer噪点过强；只凭现象也不能认定粉尘区噪点全来自传感器。
- 稳定粉尘纹理属于空间误检，时间滤波不能单独清除；随机闪烁才适合短时一致性。恢复后的历史污染也可进入量化，需检查同帧各阶段。

## Recommended Design (not implemented)
1. 保留独立的遮挡置信状态。用跨块面积/形状、运动进入、已确认遮挡传播辅助白衣识别；停止运动时保持遮挡，不能把亮中性一概排除。仅恢复 white_changed>=5 会重新误杀粗字，不采用。
2. 在确认人物覆盖处禁止衣服边缘作为新字穿透；人物外可见板面保留粗字/细字显示路径。显示许可、历史写入许可和人物置信不能用同一个宽松条件替代。
3. 擦除以“该像素已可信露出板面，旧笔画对比度消失，当前观测符合局部板面分布且短时稳定”判断。板面参考从可信未遮挡邻域/历史估计，可包括灰白粉尘；不要求恢复到固定暗绿色，也不强制大部分旧字像素不变。
4. 遮挡/疑似/可见板面分状态；对有充分退出证据的局部区域采用2-3处理帧候选确认并立即提交，人物仍挡住时保持旧板书。扩大5x5写禁区可以保守，但已验证可见像素应有独立释放通道；候选阈值待实拍校准。整屏rebase不承担日常擦除。
5. 粉尘去噪先改量化前判据：已存在7x7均值，进一步评估较大尺度、排除笔画/人物污染的稳健板面估计或灰度形态学开运算估底，再提取局部笔画对比度；不能只换名字为“自适应阈值”。白顶帽等只分离尺度，不能独立解决与粉笔等尺度的粉尘。
6. 对弱候选增加较长方向支持/跨度/强种子约束，堵住2x2互相支持；允许高置信粗字/细线和独立标点保留，不能全图直接3x3开运算或按面积抹除。对低置信闪烁候选再试2/3帧或饱和计数/迟滞，高置信新字快速显示；时间状态在几何重建时同步重置。
7. 所有像素算法仍留PL，保持用户指定两DDR环/原DMA。优先复用行缓存与块状态；v18 manifest声明BRAM94.1%、CLB97.67%，新增资源和150MHz时序需重新验证，未作资源/帧率承诺。
8. 下一轮先录制同一段浅/深衣、静止/移动、粗细白/彩字、稀疏/大面积擦除、干净/泛白粉尘场景；同源帧ID保存rectified/restored/quantized及mask/writes/擦除拒绝原因。现有evidence-dir只有启动若干快照，不能代替事件序列。衡量轮廓残留、笔画保留、真实板面露出后到显示/背景提交的毫秒数，以及再次遮挡后旧字是否复现。

## Commands and Tools
- PowerShell Get-Content、rg、git status、Python zipfile/hashlib/difflib；SSH只读列举服务器候选和SCP取回8个源码文件；没有远端写入/构建/板卡操作。
- 编译三版本：g++ -std=c++11 -O2 -DWHITEBOARD_NATIVE -Wno-unknown-pragmas -I vNN_hls quality_probe.cpp vNN_hls/whiteboard_restore.cpp vNN_hls/guarded_state.cpp vNN_hls/board_quantize_rgb.cpp -o probe_vNN.exe；在 test_workspace/v18_quality_assessment_20261017 中运行并保存 probe_vNN.txt。
- 官方资料只作为算子定义参考：https://docs.opencv.org/4.x/d3/dbe/tutorial_opening_closing_hats.html 与 https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html；项目因果结论来自本地代码和本次probe。

## Validation and Evidence
- 已执行128x96 RGB565实际C++源码的三版本native定向回放，三个程序exit=0；这些是缺陷边界探测，不是产品验收PASS。
- 浅色边线依附暗色人物core：v15泄漏0像素，v16泄漏32像素，v18泄漏0；支持v16门控回归及v18已修复该分支。
- 纯白32x32块静止10帧：三版均sampled_occupied=0，当前白块1024像素全通过，量化形成348非白轮廓像素，epoch=0/reasons=8；说明阻止重建不等于遮挡显示成功。
- 原历史含暗淡笔画，擦成均匀板面：v18 4/16变化样本第4调用提交，16帧后残留0；8/16样本变化16帧后仍128像素残留、occupied=8/reasons=18。v15/v16两者均不提交该场景。
- 擦除20像素白线且旁边仍有人：v18 12帧后历史残留20、显示残留8；人移走后第1调用提交（目标像素此前已积累稳定计数）。故不能泛称每次人离开都固定再等3/6/8帧。
- 灰白均匀粉尘底上擦除20像素白线：v18 16帧后历史仍残留20；理由为源码提交通道阻塞，现场粉尘是否落入同一亮度条件仍待核实。
- 中性灰128背景，2x2中性亮斑名义对比度12：v15保留0，v16/v18均保留4；名义对比度32三者均保留4。v18单像素两种对比度均去除。证明弱连续性路径会引入小团簇，并非证明所有现场颗粒都是2x2。
- 证据：source_audit.json、v15_v16/v16_v18 diff、quality_probe.cpp、probe_v15/v16/v18.txt；哈希随 evidence_sha256.json 保存。
- 新板测、真实视频回放、HLS/RTL 仿真、综合、时序、FPS：未执行；未验证任何新建议的修复收益。

## Errors and Corrections
- 初次读取 v16 session006 使用不完整文件名，未读到该文件；通过 rg 找到 implementation-synthesis-deploy 完整文件名后读取。
- 历史文档中的“彻底根治”等表述不能替代本次现场质量验收。
- 初次ZIP检索要求路径前有斜杠，漏掉根hls目录；检查namelist后按hls/前缀读取，未据空结果宣布缺失。
- 首轮v18 probe完成后增加v15/v16门控对照场景，三版本重编复跑，最终txt是完整同一probe的结果。
- v18已恢复writes门控，纠正了把v16历史变更直接套到v18的潜在误判；粉尘噪点源不预设为Bayer。

## Files Changed
- 内部：本会话记录、PROJECT_STATE.md、DECISIONS.md（D-108）、ai/INDEX.md。
- 测试子目录 test_workspace/v18_quality_assessment_20261017：匹配源快照、差异、哈希、probe源码/可执行文件/输出、测试README。
- 工程清理：根 .Xil 与3个旧vivado备份journal原样迁入上述子目录/root_artifacts_archive（未删除）；路径先验证在工作区内且目标不存在。
- 用户指定v18包、正式v15/v16生产源码、固件/部署配置：未修改。

## Remaining Work
- 当前分析任务完成；新方案实现、真实场景A/B、综合/路由/板测及收益确认均未执行。
- 仍无法将用户现场的v18退化归结为唯一分支，需要同源事件序列；记录已给出可重复候选机制与优先级。

## Handoff Notes
- 不将包目录名称、旧测试 PASS 或历史记录当作当前 bitstream 与源码完全一致的证明。
- 下一步优先：匹配现场输入和状态采样；独立遮挡/板面释放方案；粉尘空间判据再加低置信时间稳定。无需改变主链路来讨论质量改进。
