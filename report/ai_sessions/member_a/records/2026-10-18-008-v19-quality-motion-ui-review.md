# AI Session: 2026-10-18-008-v19-quality-motion-ui-review
- Date: 2026-10-18
- Operator: User
- AI product/model: Codex / GPT-6
- Participants: User, Codex (single agent)
- Objective: 回答颜色不稳定、启动字迹擦不掉、背景噪声、UI PS/PL职责、大位移错位五项现场反馈，并提出方案。
- Status: Complete; review/proposals only
- Report candidate: no
- Related commits: none
- Related files: rtl/dma_rgb565_quality_v19/source; deployed archive UI

## Context Read
按序阅读AGENTS/AI政策、状态、最新决策/索引、session007、Git状态；核对当前上板来源。无需重新部署。
## Task and Constraints
本轮是分析和方案，不默认修改生产源码、综合或中断板端。代码可证明的机制与现场尚未复现的根因分开。
## Contributions
- 核对量化label()逐像素/逐帧分类、中性容差、同色支持；没有笔画主色或时间颜色锁定。C++直接包含实际量化源执行label探针：展开RGB90/105/123判蓝3，107/113/123判中性黑1。仅证明机制可导致蓝/黑分裂，不声称重放了用户现场。
- 核对初始化将首帧写入background/previous，及现有is_erased/local_erased、surface/anchor/writes/mask/freeze等条件。v19既有测试包含启动文字擦除，故不能宣称当前未实现该功能；现场仍失败，需要同帧拒绝原因证据。首帧保留文字供遮挡恢复是合理行为，修复重点是有证据的擦除能替换这份历史。
- 核对UI实际像素来源：F1是PL ISP后camera RGB565，F2为PL校正输出，F3为PL校正/恢复/量化；PS负责识别/矩阵、调度/页面及UI。F1/F2当前有PS整帧拷贝到scanout；F3优先PL直写，UI局部PS合成。三个后台阶段不因F1/F2展示而停机。
- 确认GeometryTracker失检时清pending并撤销疑似运动，旧accepted存在时restore_safe恢复true。控制流探针复现：第一次大移动safe=true；第二次一致大移动safe=false；随后None变held/safe=true并继续旧矩阵。2Hz完整识别与此策略允许失配持续，调整页依赖safe等条件所以可能不出现。
- 3x3中值合成探针：9像素长、1像素宽直线被全部消除。该例用于说明细字风险，不作为实拍滤波效果。
- 查阅OpenCV官方4.12中值/双边及特征单应文档，区分滤波定义和本项目尚待验证的设计。
## Decisions and Adoption
- D-117是AI方案，未实施/未获用户实施授权。优先修运动安全与坐标代次，然后启动擦除，再笔画颜色一致和噪声空间/弱时间确认。PS/PL职责及两DDR环保持。
- 颜色采用可靠彩色种子驱动同一局部笔画的低置信颜色；强中性白字保护保留，不全区域强制改蓝。新增/擦除/几何代次变化必须释放颜色锁。需要调整旧“中性一律保护”到区分强中性和歧义像素，属于待验证新算法，不能默认为已采用。
- 擦除分离含板书历史与板材/照明参考；从可信未遮挡邻域稳健估计板面，按原始观测、真实擦除稳定性提交。不增加重复的现有local_erased路径，不只延长/缩短TTL，避免背景同色人物被吸收。先记录gate拒绝原因再改判据。
- 噪声优先空间稳健背景/低置信条件滤波，复用现有7x7窗口；稳定粉尘不能靠时间一致性删。时间仅对几何锁定、可见板面弱置信作短确认，强笔画快通，擦除快速释放；运动/遮挡/几何换代清除或停用历史，避免拖影。保护细线/标点，禁止直接全图大核中值。
- 运动建议PS低分辨率较高频哨兵+现有精确定位：一旦强运动证据立即标记旧几何不可信，保持疑似状态直至新矩阵确认；失检不能撤销疑似，单纯短遮挡允许有界保持。停止旧代次新提交，排空/拒显旧代次输出，独立显示调整UI；确认新矩阵后边界切换/重建恢复历史。不能仅提高全分辨率识别频率或把所有失检都当移动。
## Commands and Tools
- rg/Get-Content审查source/hls和source/software；g++原生量化label探针；Python/OpenCV控制流和中值小样例。测试目录test_workspace/v19_quality_motion_review_20261018。
- 官方参考：https://docs.opencv.org/4.12.0/dc/dd3/tutorial_gausian_median_blur_bilateral_filter.html；https://docs.opencv.org/4.12.0/d1/de0/tutorial_py_feature_homography.html。
- 本轮未连接、采样、重启或部署板卡。
## Validation and Evidence
- color_probe.cpp直接调用当前C++ label，实际编译运行PASS；color_probe.log记录两种标签。
- control_filter_probe.py/control_filter_probe.json记录3步几何安全回退和细线中值结果；断言PASS。
- 源码位置：board_quantize_rgb.cpp:21/37/117，whiteboard_restore.cpp:239/244/249/318/448/460/489，board_detector.py:188-215，run_stage_pipeline_archive.py:154/169/181/218-240，archive_ui.py:145起。
- 未执行：现场同源序列、擦除gate抓取、新算法A/B、HLS/RTL/综合/时序、新部署/性能测试。上一轮85项软件/1000采集/3像素比对不证明用户五项画质问题解决。
## Errors and Corrections
- 纠正可能误解：启动字已进入历史并不意味着代码永久禁止擦除；已有本地通道和合成用例，现场失败具体gate未定位。
- 蓝黑分裂是独立硬阈值决策，不是已存在的“反复试色”。中性保护也保护白字，不能不分置信一律转蓝。
- 检测失败不能证明相机运动，但已有运动疑似后的失检也不能证明坐标安全。区分这两种情况。
## Files Changed
- 本记录、DECISIONS的D-117提案、PROJECT_STATE、ai/INDEX；test_workspace/v19_quality_motion_review_20261018探针/证据。
- 无生产源码、板包、固件或板端改动。
## Remaining Work
分析完成。后续获实施授权后先修PS运动状态门并回放；采集启动字擦除同帧gate和颜色/粉尘样例；再改PL颜色/板面擦除/条件滤波并进行新HLS/系统时序和现场A/B。资源/延迟未估测，不承诺新增逻辑可维持200MHz或现有FPS。
## Handoff Notes
上一轮板测通过的是启动/像素一致/交互，不能代替这五项实际画质验收。
