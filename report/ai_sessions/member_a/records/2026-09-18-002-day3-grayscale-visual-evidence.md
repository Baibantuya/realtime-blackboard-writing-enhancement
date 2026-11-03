# AI Session: 2026-09-18-002-day3-grayscale-visual-evidence

- Date: 2026-09-18
- Operator: Codex
- AI product/model: Codex
- Participants: 用户（成员2）；Codex（实现与验证）
- Objective: 第三天完成灰度级、真实 RTL 输出图像与端到端复现。
- Status: Completed
- Report candidate: no
- Related commits: none
- Related files: `blackboard-writing-enhance/rtl/enhance_axis.sv`, `blackboard-writing-enhance/tb/`, `blackboard-writing-enhance/scripts/`, `blackboard-writing-enhance/evidence/day3/`, `blackboard-writing-enhance/docs/pl_day3_grayscale_visual_replay.md`

## Context Read

- 已依次读取根目录 AGENTS.md、AI_DEVELOPMENT_POLICY.md、PROJECT_STATE.md、DECISIONS.md、INDEX.md、Day 2 最近会话；检查新仓库 Git 状态、成员2任务卡、接口合同、RTL、testbench、参考模型与向量脚本。

## Task and Constraints

- 保留已有未提交工作；正式代码和可视证据写 `blackboard-writing-enhance/`，内部记录留根目录 `project_workspace/`。
- 用户要求可见最终效果、工具链与逐步复现。不得把软件生成的期望图冒充 RTL 输出，也不得声称上板完成。

## Contributions

- RTL 新增 `cfg_grayscale` 输入及逐帧锁存，旁路优先，灰度输出 `0x00YYYYYY`；现有 SOF/TLAST/TKEEP/背压/错误合同不变。
- Python 整数参考新增灰度像素路径、边界测试；基于现成白板照片 01 生成 320×240 输入及灰度/二值期望向量。
- 新 Day 3 testbench 在实际输出握手时采集 RTL 像素，随机背压、帧内写模式、状态和逐像素自检；转图脚本读取实际 RTL 输出而非软件期望，生成输入/灰度/二值和三栏 PNG 及哈希/差异 JSON。
- 一键 PowerShell 脚本执行 Python 测试、向量、三套仿真、图片渲染与无约束综合；文档说明工具链和复现边界。

## Decisions and Adoption

- 采用 D-010：第三天交付灰度级及真实仿真像素可见证据，先不宣称 5×5 形态学或完整增强。`cfg_grayscale` 是直接 RTL 端口，待成员1集成时确认/封装。
- 输入采用已获许可且哈希固定的真实样本；Pillow 缩至 320×240 仅为仿真图像级验收，不作为全分辨率视觉质量评价。

## Commands and Tools

- 新仓库根目录：`powershell -ExecutionPolicy Bypass -File .\scripts\run_day3.ps1`。脚本调用 Python 3.9/Pillow 9.0.1，Vivado 2022.2 的 `xvlog.bat`、`xelab.bat`、`xsim.bat` 与 `vivado.bat`；详细展开见 Day 3 文档。
- 收尾修改仅是 testbench 增加模式优先级/帧内写检查与 Python 灰度结构检查，之后用 `-SkipSynthesis` 复跑全部单测、三套仿真与 PNG；RTL 未在综合后再改。

## Validation and Evidence

- 完整脚本首次运行退出码 0；Python 单测 3 项 PASS；原三张实拍图二值/旁路 6 组各 3072 像素 PASS；Day 2 协议/复位 PASS；Day 3 白板 01 的灰度/二值两组各 76800 像素 PASS，随机背压种子 20260918，输出与参考各 0 差异。修改测试后 `-SkipSynthesis` 脚本再次退出码 0。
- `blackboard-writing-enhance/evidence/day3/comparison.png` 为实际 RTL 输出像素构图；单独 PNG 及 `results.json` 记录输入/RTL mem SHA-256、PNG SHA-256 和差异。已打开并目视检查对照图：原输入、灰度输出与阈值二值结果可区分；尺寸 320×240。
- Vivado 2022.2 无约束 OOC 综合 `xczu7ev-ffvc1156-2-e` 成功，261 CLB LUT、181 CLB 寄存器、0 BRAM、0 DSP；`blackboard-writing-enhance/build/synth_day3/utilization.rpt` SHA-256 `0dddba7bbd9cd71a1ed1720d04548e2d709a27557c647aa520bc497e09ee09bf`。
- 未执行：带时钟约束实现/时序、USB/PS/DMA/显示链路、摄像头或开发板实测、30fps 吞吐。

## Errors and Corrections

- 初版 Day 3 仿真和 PNG 已通过；随后发现模式锁存与旁路优先级未被明确覆盖，补充帧内切换 `cfg_grayscale` 的刺激与旁路+灰度同高测试，再次仿真 PASS。
- 最终检查发现 `process_pixels` 的新旁路快路径会绕过原先由逐像素函数执行的阈值/字长校验；已在帧入口统一校验并增加负例测试。随后 Python 单测、Day 3 向量生成和从既有 RTL mem 的 PNG/差异重建再次通过，证据哈希未变化；RTL 无需重跑。
- Vivado 启动时报告本地 Tcl store 不可写并回退安装目录；综合完成。无约束综合有 parallel synthesis criteria 普通警告，不影响该次综合成功；不能由此推断时序。

## Files Changed

- 新仓库：`rtl/enhance_axis.sv`、`tb/tb_enhance_axis.sv`、`tb/tb_enhance_axis_protocol.sv`、`tb/tb_enhance_axis_day3.sv`、`src/board_enhance/binarize_ref.py`、`tests/test_day1_reference.py`、`scripts/make_day3_vectors.py`、`scripts/render_day3_output.py`、`scripts/run_day3.ps1`、`evidence/day3/{input,grayscale,binary,comparison}.png`、`evidence/day3/results.json`、`docs/pl_day1_interface.md`、`docs/pl_day2_protocol.md`、`docs/pl_day3_grayscale_visual_replay.md`、`进度记录/progress_and_decisions.md`。
- 根目录内部：`project_workspace/DECISIONS.md` (D-010)、`PROJECT_STATE.md`、`ai/INDEX.md`、本会话记录。

## Remaining Work

- 成员3独立提供/审阅 5×5 形态学定点与边界向量；成员2逐级实现 max/min/open/close 后再集成。
- 成员1确认新模式端口与物理寄存器/VDMA 配置；带时钟约束实现及板端单帧闭环仍未做。

## Handoff Notes

- 当前分支 `b/pl-lower-pipeline`，未提交/推送。仓库 `evidence/day3/comparison.png` 可直接打开，`docs/pl_day3_grayscale_visual_replay.md` 为复现入口；`build/` 被忽略，使用脚本重建。
- 当前可视图仅证明 xsim 中的单帧像素输出，不能代替摄像头 HDMI/DP 演示；后续需 PS/PL 集成与上板证据。

## Collaboration Map

| Participant | Assigned task | Input | Output | Verification | Accepted by |
|---|---|---|---|---|---|
| 用户/成员2 | 审核第三天 RTL、视觉结果及板端后续 | 成员2任务卡 | 待人工审核 | Codex 本机脚本/仿真/综合 | 待用户审核 |
| Codex | 灰度级、可视证据、复现链 | Day 1/2 核与现成图片 | 本次代码/证据/文档 | Python/xsim/OOC synth | 待用户审核 |
| 成员1、成员3 | 后续板端集成、独立定点参考 | 待交接 | 本次未参与 | 未执行 | 未定 |

## Conflicts and Resolution

- 根目录旧规范仍指向原 `whiteboard/`；用户已在之前明确指定新仓库与根目录内部记录，本次继续按该授权布局。

## Integration Result

- PL 灰度/二值单核在本机具备图像级 RTL 仿真可视复现证据；系统视频闭环未开始。
