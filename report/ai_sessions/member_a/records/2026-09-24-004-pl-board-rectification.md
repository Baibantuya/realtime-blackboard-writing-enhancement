# AI Session: 2026-09-24-004-pl-board-rectification

- Date: 2026-09-24
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 在 PL 端实现首个黑板/白板边框定位、几何校正和单路 1080p 主画面输出，供 PS 测试。
- Status: Local implementation and bitstream complete; KV260 PS/runtime verification pending
- Report candidate: No
- Related commits: None
- Related files: `kv260-whiteboard-enhance/rtl/board_rectify_hls.cpp`, `rtl/board_binary_demo_hls.cpp`, `pynq/kv260_board_rectify.bit/.hwh`, `pynq/board_rectify.py`, `docs/board_rectification_m0.md`, D-041

## Context Read

按规定顺序读取根 `AGENTS.md`、AI 开发策略、项目状态、决策、索引、最近 003/002 会话；随后检查正式目录和 Git 状态。根目录不是 Git 仓库，正式目录当前只有文档和空 `rtl/scripts/tb` 目录。本轮遵从根 `AGENTS.md`，正式成果写入 `kv260-whiteboard-enhance/`。

## Task and Constraints

用户要求不依赖白墙位置，优先利用金属板框附近的颜色/亮度边界；任意画面位置校正，等比撑满 1920×1080，空白为白；黑板黑底白字、白板白底黑字；只要主视频输出供 PS 测试。

## Contributions

- 建立独立 HLS 校正核：1/8 抽样亮度边界投票、四线交点、向内裁切、单应性映射、等比 1080p 白色补边，DDR 输入/输出 GRAY8；不依赖墙面颜色或板框固定位置。
- 按用户纠正把二值化拆成独立、可绕过的 PL demo IP，支持显式黑板/白板模式和阈值。校正始终先于二值化，不把 demo 策略锁进校正核。
- 添加 PL→PS `status/hint/corners` 缓冲及方向码：左右上下镜头朝向、前后移动、无法判断；无可靠完整边框时全白输出。缺边时以局部中心灰度与四边界作保守比较，不把该启发式当作已实测鲁棒算法。
- 编写 KV260 Vivado block-design 生成脚本，PS AXI-Lite 控制两个 HLS IP，五个 AXI master 连到 HPC0 DDR；生成 matching `.bit/.hwh`。添加 PYNQ 逐帧调用类和静态图/摄像头 PS smoke runner，只返回单路主画面与状态，不建立分析支路。
- 编写合成黑/白板、透视、留白、空白帧及四方向出框 host C 测试，整理正式设计/部署说明。

## Decisions and Adoption

- D-041 采纳“GRAY8 几何校正先于独立可替换增强/二值化”、PS DDR 帧原型和状态方向反馈；用户明确指出二值化仅是 demo，后续可能修改。
- 当前原型是 PS 顺序调度的 DDR 帧处理，不声称已实现 D-039/D-040 所规划的 AXI4-Stream Video、VDMA/DRM 连续 1080p30 显示链路。原 D-039 ROI packet ABI v1 不变。

## Commands and Tools

- `python kv260-whiteboard-enhance/tb/test_board_rectify.py`：主机编译两份 HLS C++ 为 DLL，生成并检查合成图，输出到 `test_workspace/board_rectify_2026-09-24/`。
- Vitis HLS 2022.2：在上述测试目录运行 `synth_board_rectify.tcl`、`synth_board_binary_demo.tcl`，各执行 `csynth_design` 和 `export_design -format ip_catalog`。
- Vivado 2022.2：`create_board_rectify_overlay.tcl` 生成 KV260 block design、综合、实现、bitstream/XSA。最初沙箱执行的子进程报 Windows `Access denied`，停止后在获允许的执行环境重跑，完成同一构建。
- 复制路由 bitstream 与硬件 handoff HWH 到正式 `pynq/`；SHA-256 比对源与目标一致。核对 HLS 驱动头中 AXI-Lite 偏移与 PS Python 调用一致；用 `ast.parse` 核对 PS Python 语法。

## Validation and Evidence

- 合成图 C 测试最终 PASS：黑板与白板四角为 `[(296,183),(1647,150),(1753,852),(243,890)]`，对应输入标称四角误差小于 65 px；白色留白/处理极性/校正灰度检查通过。空白帧 `status=1,hint=64`；右/左/上/下出框分别返回 `hint=2/1/4/8`，均不接受为有效裁切。生成图在 `test_workspace/board_rectify_2026-09-24/`，人工查看 `output_0.png/output_1.png` 符合白底黑字/黑底白字。
- HLS 2022.2 对 `xck26-sfvc784-2LV-c` 两核综合及 IP 导出完成；校正核 HLS 估计 60 BRAM18、212 DSP、29,474 FF、49,762 LUT（非实际布局资源/帧率）。
- Vivado 2022.2 完成顶层综合、布局布线、DRC 和 bitstream/XSA。路由 timing summary：WNS +2.663 ns、WHS +0.010 ns、TNS/THS 0、setup/hold 失败端点 0；放置资源 40,206 LUT、45,285 FF、33.5 BRAM tiles、212 DSP。证据：`test_workspace/board_rectify_2026-09-24/vivado_overlay/kv260_board_rectify.runs/impl_1/kv260_board_rectify_wrapper_timing_summary_routed.rpt` 与 `kv260_board_rectify_wrapper_utilization_placed.rpt`。
- bit SHA-256 `121F5829C4E86DD43F93FF0939C37777A58FC01D27A80359A97A6D09EC7E0331`，HWH SHA-256 `13C968DA83311B9A9C4532836339D01B3747299827052840C624E23619FC8C77`；源/交付哈希一致。
- 未执行：KV260 加载本 overlay、PS DMA 实际读写、相机真实场景定位/提示准确率、连续帧率、HDMI 显示。Vivado 时序满足仅证明约束下的电路实现，不证明 30 fps 或实拍正确性。

## Errors and Corrections

- 初稿把阈值二值化合入校正核；用户指出处理顺序及 demo 可替换性后拆分为两个独立 IP，并重建 overlay。
- 增加四向测试发现中央字迹污染三点灰度估计，“上方出框”误报向下。改用 3×3 中位灰度后，四向复测均 PASS。先前生成的旧 IP/进行中的实现已停止并重新构建，不作为交付物。
- 第一次 Vivado 在沙箱中启动并行综合子进程报 `rundef.js ... Access denied`；停止后用允许的执行权限重跑，子进程成功启动，最终构建完成。
- 本机 Vitis HLS 启动时出现 MSYS `tee` signal-pipe Win32 error 5 输出，但主进程退出码 0、HLS 合成/IP 导出报告均完成；未把该诊断误记为 HLS 综合失败。

## Files Changed

- 正式：`kv260-whiteboard-enhance/README.md`、`docs/board_rectification_m0.md`、`rtl/board_rectify_hls.cpp`、`rtl/board_binary_demo_hls.cpp`、`scripts/synth_board_rectify.tcl`、`scripts/synth_board_binary_demo.tcl`、`scripts/export_board_rectify_ip.tcl`、`scripts/create_board_rectify_overlay.tcl`、`tb/test_board_rectify.py`、`pynq/board_rectify.py`、`pynq/test_board_rectify_ps.py`、`pynq/kv260_board_rectify.bit`、`pynq/kv260_board_rectify.hwh`。
- 内部：本会话、`project_workspace/DECISIONS.md` D-041、`project_workspace/PROJECT_STATE.md`、`project_workspace/ai/INDEX.md`。
- 测试与构建产物仅在 `test_workspace/board_rectify_2026-09-24/`；未修改辅助资料。

## Remaining Work

1. 在 KV260 PS 加载 matching `.bit/.hwh`，用静态 1080p GRAY8 图验证 DMA 结果、状态/方向码及 cache 同步，再用真实黑板和白板视频测试。
2. 测量逐帧 PL 执行耗时、PS 相机解码与整体 fps；若未达到目标，优先把浮点单应性/随机 DDR 读取改为定点和更适合视频的缓存结构。
3. 在真实场景评估反光、复杂背景、遮挡、板面与背景同色、超过当前线斜率范围（约 ±0.75）时的误检和方向提示；校正策略通过后接到持续 AXI4-Stream Video/VDMA/HDMI 主链路。

## Handoff Notes

正式设计与 PS 测试命令见 `kv260-whiteboard-enhance/docs/board_rectification_m0.md`。板端把 `pynq/` 下 `.bit/.hwh`、`board_rectify.py`、`test_board_rectify_ps.py` 放同一目录；先用 `--gray` 看校正灰度与 status，再开 demo 二值化。当前环境根目录及正式目录均无 Git 元数据，无法提供 commit 或 diff 状态。
