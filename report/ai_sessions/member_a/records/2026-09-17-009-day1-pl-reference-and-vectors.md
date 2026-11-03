# AI Session: 2026-09-17-009-day1-pl-reference-and-vectors

- Date: 2026-09-17
- Operator: Codex
- AI product/model: Codex
- Participants: 用户（成员2）；Codex（本次实现与自检）
- Objective: 执行第一天任务：可讨论的 PL 内部接口、整数二值化参考、可复用数据源调查、向量及 AXIS 测试入口。
- Status: Completed
- Report candidate: no
- Related commits: none
- Related files: `blackboard-writing-enhance/docs/`, `blackboard-writing-enhance/rtl/`, `blackboard-writing-enhance/tb/`, `blackboard-writing-enhance/tests/`

## Context Read

- 已按根目录要求读取 AGENTS.md、AI_DEVELOPMENT_POLICY.md、PROJECT_STATE.md、DECISIONS.md、INDEX.md、上一会话和新仓库接口草案；当前分支干净。

## Task and Constraints

- 用户授权第一天开发，并要求能找到现成数据集时优先复用。
- 新仓库是用户指定的正式成果位置；根目录旧规范中的 `whiteboard/` 路径属于前项目布局，本次遵从用户明确的新仓库要求。内部记录继续留在根目录 `project_workspace/`。

## Contributions

- 搜索并复用 Daniel Rosehill 的 Whiteboards 数据集三张原始白板照片（01/07/13），记录上游提交、CC BY 4.0 署名和 SHA-256；未自行生成替代照片。
- 编写 Day 1 BGRX/AXIS/二值化说明、Python 整数参考、向量生成脚本、SystemVerilog 最小核和 testbench。
- 生成三组 64×48 像素输入/期望向量；testbench 对每组执行二值化与旁路，在随机输出背压下检查像素、SOF、行尾 TLAST、TKEEP 和停顿稳定性，并测试帧内阈值写入不改变当前帧。

## Decisions and Adoption

- 采用 D-008：8 位亮度阈值默认 128，`Y<threshold` 输出黑色；该阈值不是后续 `ink_threshold=12`。
- 原计划中“普通 AXI DMA 固定帧直接接视频核”的说法不够准确：当前核的 TLAST 是行尾，普通 AXI DMA 的 TLAST 是包尾。连续视频使用 VDMA/视频 DMA；普通 DMA 须有显式适配器。
- 第一版 RTL 只做像素运算和握手，AXI4-Lite包装、帧尺寸/异常检查和状态计数未采纳为已完成。

## Commands and Tools

- 数据源调查：Whiteboards 数据集卡和上游 GitHub 仓库；克隆版本 `c0e3455f7ea616894eabb24cd998f2a4173830a1`，下载三张 `samples/flat/*.webp`。
- `python -m unittest discover -s tests -p 'test_*.py' -v`
- `python scripts/make_day1_vectors.py`
- `build/sim` 中运行 `xvlog.bat -sv -work xil_defaultlib ../../rtl/enhance_axis.sv ../../tb/tb_enhance_axis.sv`，`xelab.bat xil_defaultlib.tb_enhance_axis -s tb_enhance_axis_sim`，`xsim.bat tb_enhance_axis_sim -runall -sv_seed 20260917`。

## Validation and Evidence

- Python 3.9 / Pillow 9.0.1：3 项单元测试通过；三组输入各 3072 像素并生成对应 BGRX 输入/期望文件，默认位置 `build/day1_vectors/`（忽略构建目录）。
- Vivado Simulator 2022.2：xvlog/xelab 成功；固定随机种子 20260917 后，xsim 对 01/07/13 三张图各执行二值化与旁路，六组均 PASS；每组 3072 像素。01组周期 4155/4149；07组 4150/4154；13组 4144/4155，均含模拟背压，不代表板端时延。
- 源图片 SHA-256 和采样许可见 `tests/fixtures/whiteboards/README.md`；向量 manifest 含输入与期望 SHA-256、Pillow 版本。
- 未执行：综合、实现、时序、资源估计、USB/DMA/显示和上板；异常帧与中途复位尚未验证。

## Errors and Corrections

- 首次运行因 Pillow 9.0.1 没有 `Image.Resampling` 失败；改为兼容旧版枚举后 Python 测试和向量生成均通过。
- 首次 xelab 因 RTL 缺少 `timescale` 失败；加入后 elaboration 通过。
- xsim 2022.2 对所尝试的文件路径 plusargs 返回参数解析错误；testbench 改用相对 `build/sim` 的固定向量路径，随后六组仿真通过。
- 曾从尚未创建的 `build/sim` 启动命令导致工作目录无效；先建立目录后继续。

## Files Changed

- 新仓库：`docs/pl_day1_interface.md`、`rtl/enhance_axis.sv`、`tb/tb_enhance_axis.sv`、`src/board_enhance/{__init__,binarize_ref}.py`、`scripts/make_day1_vectors.py`、`tests/test_day1_reference.py`、`tests/fixtures/whiteboards/{01,07,13}.webp`、`tests/fixtures/whiteboards/README.md`、`进度记录/progress_and_decisions.md`。
- 根目录内部：`project_workspace/DECISIONS.md`（D-008）、`project_workspace/PROJECT_STATE.md`、`project_workspace/ai/INDEX.md` 和本会话记录。

## Remaining Work

- 补中途复位、无 SOF、过早/缺失 TLAST 和错误帧丢弃策略的自检与 RTL 状态逻辑。
- 与成员1确认 VDMA、板级时钟/复位、显示像素布局及缓存同步；加入 AXI4-Lite 包装和配置版本关联。
- 与成员3独立核对整数参考和向量；未来画质评测需多来源、彩色与独立真值数据。

## Handoff Notes

- 从 `blackboard-writing-enhance/docs/pl_day1_interface.md` 的命令复现 Python 与 xsim。源照片可定位，生成向量在 `build/` 下按脚本重建。当前代码未提交、未推送。

## Collaboration Map

| Participant | Assigned task | Input | Output | Verification | Accepted by |
|---|---|---|---|---|---|
| 用户/成员2 | PL 算法负责人，审查接口与后续集成 | 本次任务要求 | 待审查 Day 1 产出 | 本机仿真已由 Codex 执行 | 待用户审查 |
| Codex | 实现参考、最小 RTL 与自检 | 当前接口草案、公开数据 | 本次新增文件 | Python/xsim 如上 | 待用户审查 |
| 成员1、成员3 | 后续板级接口/独立参考复核 | 待交接 | 尚未参与本次实现 | 未执行 | 未定 |

## Conflicts and Resolution

- 旧根目录规范写正式目录为 `whiteboard/`；用户当前明确指定新仓库 `blackboard-writing-enhance/` 为项目位置。本次正式成果写入新仓库，内部 AI 流水仍写根目录 `project_workspace/`。

## Integration Result

- 平台无关 PL 像素数据面完成 Day 1 仿真；团队审查和系统集成待执行。
