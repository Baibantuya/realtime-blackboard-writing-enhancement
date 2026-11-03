# AI Session: 2026-10-12-009-rgb565-regression-review
- Date: 2026-10-12
- Operator: Project owner
- AI product/model: Codex
- Participants: Project owner, Codex (single agent)
- Objective: 对照已运行RGB888基线，审查RGB565采集失败、writer不读和反复修复不收敛的原因。
- Status: In progress; read-only code review, documentation only.
- Report candidate: no
## Context Read
AGENTS、AI_DEVELOPMENT_POLICY、PROJECT_STATE、DECISIONS、INDEX；大历史输出曾截断，另读当前相关D-089至D-097与session004/008及当日采集交接。Git当前根目录主要为未跟踪项目/测试目录，不能用干净提交差异假设复原版本。
## Task and Constraints
只分析与记录，不启动新的PL构建、部署、板卡恢复或软件修复，遵守当天停止实验要求。
## Contributions
核对原B32与新候选采集控制、HLS数据路径、已有验证边界。
## Decisions and Adoption
待完成；不改变既定架构。
## Commands and Tools
本地PowerShell读取/rg静态检索。
## Validation and Evidence
待补全；本次硬件运行、综合、时序测试、功能仿真均未执行。
## Errors and Corrections
区分已确认的控制契约缺陷与尚未抓到时间线的现场唯一根因。
## Files Changed
本会话记录；完成时更新PROJECT_STATE与INDEX。
## Remaining Work
完成源代码交叉核对与分析。
## Handoff Notes
不把三帧smoke当持续运行通过，不把RGB565格式本身判为不可行。

## Completed Review / Owner Architecture Constraint
- Status: Completed static review/documentation; runtime regression remains unresolved.
- 原B32 v4l2_rgb.py初始化把至少四个slot全部QBUF后STREAMON；新capture565_stream.py每帧从Python deque选slot，写dst/AP_START，sleep(.0005)轮询AP_DONE，再开始下一帧。软件有四个slot不等于硬件已预排队四个目的地址。
- capture_rgb565.cpp一次调用只消费一帧；DATAFLOW FIFO仅服务该次任务。交接引用生成RTL闲置TREADY0，本次本地未找到生成ingest RTL，未声称重新读取了该RTL。
- D-093先arm后启源只能修启动次序；增FIFO仅吸收活动期有限DDR阻塞；显式burst提高活动期写效率，均没有消除逐帧重新启动间隙。AP_CTRL=1只证明未完成，不能证明正在读像素，也无法区分等SOF/等像素/等DDR。
- 首帧超时与最终21帧后停流不能用同一个未经采样的PS调度根因包办；CSI bufferfull说明链路无法持续排空，阻塞起点仍需要握手时间线。最后bit timing FAIL另增不确定性。
- 本地再次核对capture HLS build_capture565.tcl为10ns，BD视频域为200MHz，最后board_trial_result_checked.json为WNS -0.505ns/15端点、smoke3帧PASS、live21帧后失败且三个输出阶段均0。
- 初始以builtin framebuffer无直接565接口/vendor源加密为由换自写writer，缺少原DMA复用不可行的证明；单帧HLS简化了数据转换验证却丢失原连续采集调度能力，是未充分评估的设计选择。
- 用户提供核心架构图并要求不改。已写D-098，固定PL四阶段、相机共享DDR、两级DDR环形缓冲、PS曝光/矩阵和显示输出职责。优先保留原成熟DMA控制；具体原IP能否直接565仍待核实。
- 反复不收敛：格式迁移同时替换采集控制/媒体master/所有权并叠加恢复P1；没有先做新采集独立连续负载验收；用单帧仿真/三帧smoke回答连续运行问题；未先区分idle/rearm与active-DDR阻塞便反复综合；打包遗漏close修复、DMA所有权误用quantizer、驱动移除生命周期缺陷又引入独立故障。
## Adoption / Verification / Remaining Work (Final)
架构冻结已采用；原DMA适配优先作为后续排查方向，具体实现未决定。全链565的数据表示已有局部验证，持续采集/真实处理质量/稳态性能未验证。本次没有运行测试、综合、上板、恢复板卡或改变源码。后续先恢复板卡/匹配基线，核实原DMA格式能力，再按固定架构做最小改动及连续采集验收；不在本次启动。
## Files Changed (Final)
本记录、DECISIONS.md、PROJECT_STATE.md、ai/INDEX.md。错误：检索候选source/docs不存在，未据此推断无文档；生成ingest RTL本地未找到，以明确标注的先前交接为来源。

## Handoff Update Requested by Owner
用户要求更新交接文档，已完成 ai/handoffs/rgb565_capture_regression_handoff_20261012.md 的实质修订：新增最高优先级架构冻结/固定数据链；补全换DMA依据不足、四slot不等于预排队、反复修改不收敛原因、writer不读证据边界及RGB565降级边界；重写下一步顺序，原DMA复用优先，替代writer仅条件性评估。既有失败、时序、包哈希和未知板态保留。验证：回读新增章节与修订任务顺序，确认无代码/构建/部署操作；硬件/仿真测试未执行（文档修改）。本次修改文件为交接文档、本session、PROJECT_STATE及INDEX；D-098已存在，无新增架构决定。
