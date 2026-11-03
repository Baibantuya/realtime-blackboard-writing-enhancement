# AI Session: 2026-09-22-009-kv260-uvc-threshold-hdmi-output

- Date: 2026-09-22
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 将已验证开发中的 UVC→PS→DMA→PL 二值化示例的结果输出目标由 Jupyter 浏览器预览改为 KV260 板载 HDMI。
- Status: Development complete; board validation pending
- Report candidate: No
- Related commits: None
- Related files: `test_workspace/kv260_fps_optimization_2026-09-22/deploy_trial1/run_threshold_hdmi.py`, `test_workspace/kv260_fps_optimization_2026-09-22/deploy_trial1/README.md`, `test_workspace/kv260_fps_optimization_2026-09-22/deploy_trial1/kv260_threshold.py`

## Context Read

已依次读取根目录 `AGENTS.md`、AI 开发策略、`PROJECT_STATE.md`、`DECISIONS.md`、AI 会话索引、最近相关会话 `2026-09-21-014-kv260-controlled-dma-overlay.md`、当前目录状态和现有 PYNQ/ Vivado 代码。工作区和正式目录均未初始化 Git；现有开发工程仍在工作区根目录 `whiteboard/`，这与“正式成果应位于 `kv260-whiteboard-enhance/`”的边界存在既有待迁移问题，本轮不擅自迁移或覆盖它。

## Task and Constraints

- 用户指定仅改变结果返回/显示目标：经 PL 二值化的相机帧通过板卡 HDMI 显示，不再返回 Jupyter。
- 保持当前 UVC MJPEG→GRAY8、PYNQ AXI DMA、PL 阈值核和 1920×1080 输入契约；不在本轮替换相机或二值化算法。
- 用户稍后自行上板；本轮不宣称 HDMI、overlay 或端到端硬件已验证。

## Contributions

已定位现有链路：`whiteboard/pynq/kv260_threshold.py` 的 `run_continuous` 每帧从 DMA 接收二值化结果后，只在可选 `preview_callback` 中交给 Jupyter；近期实际上板测速使用的是 `test_workspace/kv260_fps_optimization_2026-09-22/deploy_trial1/kv260_threshold.py` 的低复制版本。当前 Vivado bitstream 只有 PS DDR↔AXI DMA↔阈值核。

用户明确本轮仅为测试，不迁入正式目录，授权在 `test_workspace/kv260_fps_optimization_2026-09-22/deploy_trial1/` 开发测试运行入口。已恢复并修正 `run_threshold_hdmi.py`：从 `/dev/video0` 连续读 1080p MJPEG GRAY8、调用既有 `Kv260ThresholdOverlay` 完成 DMA/PL 阈值、将每个 S2MM 返回的二值帧写入 PS 显示 Linux framebuffer（默认 `/dev/fb0`）。脚本没有 Jupyter、widget 或 JPEG 预览路径。

应用户询问，新增 `kv260_threshold_hdmi.ipynb` 作为 Jupyter 启动/停止器：它检查必需文件和 framebuffer，启动 120 帧烟测或连续 `run_threshold_hdmi.py` 子进程，并从日志显示状态；不把图像回传至 notebook。

## Decisions and Adoption

经进一步核对 KV260 官方平台和设备树参考，J5 HDMI 与 J6 DisplayPort 由载板 DP/HDMI splitter 复用 ZynqMP PS DisplayPort 输出；官方参考的 PL Video Mixer 连接到 `zynqmp_dpsub`。因此当前“相机→PS→DMA→PL 二值化→PS”测试链路可以保持 bitstream 不变，由 PS/Linux 的已启用 DRM/fbdev scan-out 驱动 J5 HDMI。前提是当前 Ubuntu/PYNQ 启动镜像暴露匹配的、已激活的 1920×1080 32-bpp framebuffer；若不存在，则修复 PS 显示驱动/启动配置，而不是改 threshold PL。

## Commands and Tools

已完成：上下文、当前代码和既有工程记录的只读检查；临时脚本的 `python -m py_compile` 与帮助入口；`python -m unittest whiteboard/tests/test_pynq_stream.py -v`；Vivado 2022.2 IP catalog 检查。

## Validation and Evidence

本机 `python -m py_compile` 通过；`run_threshold_hdmi.py --help` 可执行，确认参数入口不依赖 PYNQ。既有 Python 回归 2/2 通过（阈值 127/128 边界、10 帧全部处理且预览抽样不跳帧）。Vivado 2022.2 IP catalog 可定位 HDMI/Video PHY/VDMA IP，但本路径不调用它们。

`kv260_threshold_hdmi.ipynb` 已通过 JSON 解析和全部 5 个代码 cell 的本机 `compile()` 检查。

板端 HDMI、PYNQ overlay 下载、DMA 回环、PS framebuffer 和连续相机显示均未执行；未运行 Vivado 构建，也未修改 bitstream。不得据此宣称 HDMI 已打通。

板端 HDMI、PYNQ overlay 下载、DMA 回环和连续相机显示均未执行；未运行 Vivado 构建，也未修改 bitstream。不得据此宣称 HDMI 已打通。

## Errors and Corrections

曾错误地将 KV260 的 J5 HDMI 当作当前设计必须直接接入的 PL HDMI Tx/Video PHY。复核官方 KV260 平台资料后纠正：载板使用 PS DisplayPort 的 DP/HDMI splitter，当前测试目标确实可通过 PS framebuffer 输出；前提是系统 image 已启用该 PS 显示后端。相应撤销“必须改 PL”的结论，并重建 framebuffer 测试入口。

首次在 Windows 主机执行临时脚本的 `--help` 失败，原因为顶层导入了仅 Linux 存在的 `fcntl`。新版本保持延迟导入，因此主机可做语法/参数检查，板端才需要 Linux ioctl。曾因错误 PL HDMI 判断删除脚本，现已按 PS DisplayPort 架构恢复；此前的 PL-only 结论不作为本次测试依据。

首次对新 notebook 的命令行检查因 PowerShell 内嵌引号组合错误而得到检查命令自身的 `SyntaxError`，不是 notebook 内容错误；改用单引号包围 Python 命令后，JSON 和 5 个代码 cell 均通过。

## Files Changed

- `project_workspace/ai/sessions/2026-09-22-009-kv260-uvc-threshold-hdmi-output.md`
- `project_workspace/PROJECT_STATE.md`
- `project_workspace/ai/INDEX.md`
- `project_workspace/DECISIONS.md`
- `test_workspace/kv260_fps_optimization_2026-09-22/deploy_trial1/run_threshold_hdmi.py`
- `test_workspace/kv260_fps_optimization_2026-09-22/deploy_trial1/README.md`
- `test_workspace/kv260_fps_optimization_2026-09-22/deploy_trial1/kv260_threshold_hdmi.ipynb`
- `test_workspace/query_kv260_hdmi_ip.tcl`（本机 Vivado IP catalog 查询脚本及其生成的测试工程）

## Remaining Work

1. 将新脚本和现有 `kv260_threshold.py/.bit/.hwh` 上传到同一板端测试目录；以运行 notebook 的同一权限执行脚本。
2. 先检查 `ls -l /dev/fb*`、`fbset -fb /dev/fb0 -i`，确认 HDMI/DP scan-out 设备、1920×1080 和 32 bpp；若输出设备不是 fb0，传入 `--framebuffer`。
3. 先运行 `python3 run_threshold_hdmi.py --frames 120`，再运行无 `--frames` 的连续显示；记录显示器是否点亮、实际 fps、DMA/ffmpeg/fbdev 错误及 `dmesg` 摘要。
4. 若系统没有适用 framebuffer，检查并启用当前 boot image 的 PS DisplayPort DRM/fbdev；这与 threshold overlay 的 PL 二值化核无关。

## Handoff Notes

用户已明确本轮不迁入正式目录。板端运行命令为 `python3 run_threshold_hdmi.py --framebuffer /dev/fb0`；可用 `--frames 120` 进行有界烟测。若 fbdev 不存在，需要针对当前 Ubuntu/PYNQ 镜像启用 PS DisplayPort DRM/fbdev；不要加载无关的应用 bitstream 或把该问题错误归因到 threshold PL。

用户随后要求在 `whiteboard/pynq/` 本体提供便捷 notebook。已新增 `whiteboard/pynq/kv260_threshold_dp_demo.ipynb`：检查依赖与同目录 overlay 文件；同步执行 120 帧烟测并输出日志；提供连续运行单元和 Jupyter interrupt 清理；视频仅发往 DisplayPort/HDMI，不回传 Jupyter。`whiteboard/pynq/README.md` 已增加此 notebook 和 runner 说明。尚未在板端执行。

## Follow-up: Use Existing PYNQ DisplayPort Runner (2026-09-24)

用户指出 `whiteboard/pynq` 中已有重写后的可运行文件。已检查 `run_camera_dp.py`、`run_camera_dp4.py` 与其依赖：优先选 `run_camera_dp.py`，因为它使用 `pynq.lib.video.DisplayPort.configure(VideoMode(...), PIXEL_RGB)` 设置目标视频模式，并依次将每个 PL 二值输出复制到 RGB scan-out frame；无需 `/dev/fb0` 固定为相机分辨率。它依赖匹配的 `kv260_threshold.bit/.hwh`、`kv260_threshold.py`、NumPy、PYNQ video API 和 FFmpeg。

`run_camera_dp4.py` 为额外低延迟版本，需再上传 `v4l2_capture.py`，并要求 OpenCV、PYNQ allocate 和多缓冲路径；本轮 HDMI 首测暂不选它。

测试目录已加入 `run_camera_dp.py`，`kv260_threshold_hdmi.ipynb` 改为同步执行 120 帧该脚本、输出日志，以及在连续模式中启动并管理子进程；README 已同步为此上传方式。板端尚未验证 PYNQ DisplayPort mode configure 是否接受 1920×1080、`writeframe` 是否成功及 J5 HDMI 是否出图。上传清单：`kv260_threshold_hdmi.ipynb`、`run_camera_dp.py`、`kv260_threshold.py`、匹配 `.bit`、`.hwh`。

## Launcher Follow-up (2026-09-24)

用户询问 DMA 双缓冲版本的运行方式后，已在 `whiteboard/pynq/kv260_threshold_dp_demo.ipynb` 增加可选 120 帧 `run_camera_dp4.py` 单元（`--frames 120 --warm 10 --nbuf 3`），同时补充 `run_camera_dp4.py`/`v4l2_capture.py` 文件检查。README 增加终端运行命令及 `--serial` 单缓冲对照方式。尚未板测。

## Continuous Double-Buffer Follow-up (2026-09-24)

用户明确要直接运行 DMA 双缓冲版本并持续输出，不要求先执行 smoke/simple runner。已把 `run_camera_dp4.py` 的 `--frames` 默认设为 `None`，省略该参数则持续运行；退出路径停止 decoder thread、关闭 V4L2 stream，并释放第二组 ping-pong CMA 缓冲。Notebook 顶部新增直达说明，依赖检查覆盖 DP4 所需脚本；双缓冲 cell 以 `Popen` 前台等待持续运行，Jupyter interrupt 时发送 SIGINT，超时才回退 terminate/kill。README 终端命令更新为 `python3 run_camera_dp4.py --warm 20 --nbuf 3`，增加有限帧方式和停止说明。主机静态审查/检查执行情况见交接；未上板测试，持续 HDMI 输出仍待用户实机验证。

## Files Changed in Follow-up

- `whiteboard/pynq/run_camera_dp4.py`
- `whiteboard/pynq/kv260_threshold_dp_demo.ipynb`
- `whiteboard/pynq/README.md`
- `project_workspace/PROJECT_STATE.md`
- `project_workspace/ai/sessions/2026-09-22-009-kv260-uvc-threshold-hdmi-output.md`

用户报告连续运行 cell 出现 `RuntimeError: Stop the current process first.`。原因是旧流程将 120 帧烟测以后台 `Popen` 启动，单元立即返回；连续模式单元若在烟测进程结束前执行，就会触发保护。

已修改 `kv260_threshold_hdmi.ipynb`：烟测改为同步 `subprocess.run()`，完成后输出退出码和日志；连续模式单元持有并等待子进程，收到 Jupyter 中断时 terminate，5 秒后仍未退出再 kill；停止单元作为残留子进程兜底。请重新上传最新版 notebook。旧 kernel 中可能已有烟测 child，更新前用旧停止单元终止它；若旧 kernel 已丢失变量，则在板端按 PID 检查并停止对应 `run_threshold_hdmi.py`。
