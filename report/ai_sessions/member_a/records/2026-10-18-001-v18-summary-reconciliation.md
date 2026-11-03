# AI Session: 2026-10-18-001-v18-summary-reconciliation
- Date: 2026-10-18 (Asia/Shanghai)
- Operator: Project owner
- AI product/model: Codex / GPT-6
- Participants: Project owner, Codex (single agent)
- Objective: 将用户新提供的v17/v18总结与上一轮清单匹配v18代码和定向回放证据合并，修正因果归因及修改优先级。
- Status: Completed review; recommendations only
- Report candidate: no
- Related commits: none

## Context Read
- 按顺序读取AGENTS.md、AI_DEVELOPMENT_POLICY.md、PROJECT_STATE.md最新条目、DECISIONS.md近期条目、INDEX.md、2026-10-17-001相关完整记录；检查当前Git状态和匹配v18源。
- rg按文件名全工作区检索，未找到用户引用的V18_150_V17_200_PERFORMANCE.md。12.7fps、186ms、57%作为用户提供的实板统计，尚未独立核对窗口、计时口径和原始证据。

## Task and Constraints
- 用户要求结合总结评估；本轮仅审核建议与内部记录，不修改生产源码、不综合、不部署。
- 保持150MHz版本作为后续算法候选基线的建议；代码改动后的时序仍须重新验证。

## Contributions
- 将用户总结与清单匹配v18源交叉核对，保留“颜色启发式缺少空间/时序语义、成簇噪点漏过过滤”的有效判断，修正下列版本与因果问题。
- Restore的chalk()和Quantize的label()不是同一个分类函数，阈值与职责不同；它们共享颜色无法独立确定语义的局限，但遮挡漏检与量化团簇误检仍可独立发生，修复一处不会自动解决另一处。
- v18 compose:219的ink已包含writes[block]，:226的笔迹提交也有写许可和stable门控。writes来自guarded_state的无邻域保护且安静，是“允许写入”，没有“已确认写字区”的语义。白衣未被识别时该许可仍可能为真。简单重复门控无收益；新面积门控还可能误伤粗字、标点及加重写入延迟，不能宣称不影响字迹保护。
- 衣服细边在!broad、writes、稳定且!freeze时可能提交，未证明所有静止衣边都提交或现场确由此固化。v18已有is_erased/local_erased局部清除路径，不能断言污染后永远不能清除、只能rebase。已有probe说明部分可提交，另一些被3/4采样点不变、均匀板面及邻域门控阻塞。
- 擦除不是quiet→置信衰减→TTL到期→rebase/cooldown固定串行链。guarded_state:100-101在weak=false时ttl=0、core=false；旧置信值不必衰减到0才退出普通局部核心。邻近core仍可保护，误判维持weak时则可能持续。局部擦除提交不读取scene cooldown；8/64仅限制整屏重建。
- 若采用用户报告12.7处理fps，3帧约0.236s、8帧约0.630s、64帧约5.039s，后两者不能作为每次局部擦除必加时长。不同计数并行积累，也不能机械相加。现有probe中人在旁站12帧后移开，第1帧就提交已稳定的目标像素。
- GeometryTracker稳态默认period=2秒，检测只在到期/强制/重校准等条件运行；用户报告的186ms单次成本不能当作每输出帧固定增加186ms。摄像头pending会被较新帧替换，latest丢旧帧旨在避免未接纳旧输入积压；57%丢帧不是额外延迟的直接量度。但低处理fps降低事件采样频度并把稳定帧计数拉长；同步PS检测也可能周期性阻塞主调度，需以时间戳衡量。
- v18 label:32-47的中性判据及色相均使用原始RGB；背景扣除向量只算contrast/light，不用于red/green/blue色相。用户“白粉尘减绿板被判红蓝”的机制不适用于这份匹配源。泛白粉尘实际含绿/偏色、ISP/565/恢复污染、色阈值边界等仍为待核实候选；不能直接归咎历史已改机制。
- 2x2相邻弱点互相支持与输出despeckle只删除孤立点得到现有probe支持。粉尘可以是稳定纹理，字迹也有抖动/噪声，不能把“粉尘闪烁/字迹静止”作为充分判据。面积只能作联合证据；单条衣边与细字在局部形状上可能相似。

## Decisions and Adoption
- D-109作为D-108的复核建议，不授权实施。推荐150MHz匹配源作为候选基线，修改后重新做HLS/整机时序签核。
- 修改顺序：1.白衣的跨块物体证据与历史遮挡保持，加显式板面可见性，把显示/新字提交/擦除提交分开；2.可信可见板面的快速擦除释放，以局部板面分布代替3/4旧采样不变等硬假设；3.量化弱团簇/空间笔画支持及低置信时间迟滞。色调上下文作为有实帧证据后的独立候选，强中性色保留原始RGB保护，弱色只从可信同色笔画传播，避免绿板主导色污染白字。
- 诊断时记录mask/writes/ink/is_broad/quiet/board_return/擦除拒绝原因及同源帧号，判清原图直通、瞬时显示和历史污染。用户总结中尚待证据的绝对断言不纳入工程事实。

## Commands and Tools
- PowerShell Get-Content、rg、git status；只读本地匹配源与既有证据。

## Validation and Evidence
- 本次未执行新native测试、真实序列回放、HLS/RTL、综合、实现、上板或FPS测试；引用10月17日已有probe并标明来源。

## Errors and Corrections
- 未找到用户引用的性能文件，不将用户摘要中的性能值标记为本轮独立测得，也不凭未获得的抓帧确认彩色噪点唯一源头。
- 修正把邻域写许可当作语义“写字区”、把rebase作为局部擦除必经阶段、把旧差分色相判据套到v18的说法。

## Files Changed
- 本记录；收尾更新PROJECT_STATE.md、DECISIONS.md与INDEX.md。

## Remaining Work
- 本次结合评估完成；现场帧/性能原始文档核对、新方案实现与A/B/综合/上板均未执行。

## Handoff Notes
- 用户文本包含对多个版本及现场数据的归因，不能将历史算法描述或用户摘要自动当作精确v18代码事实。
