# 底部操作栏、历史页与 PS 联合候选

日期：2026-10-18。新增入口为 `run_stage_pipeline_ui.py`；旧候选和此前交付 ZIP 均保留。本目录的 `deployment.json` 已改指新入口。继承的旧 README、diff、测试记录只作为来源资料，本阶段以本文和新 `runtime_manifest.json` 为准。

## 已接入的行为

- 原有 1080p Noto Sans SC Regular / 8 bpp LVGL 底栏，通过 C 共享库绑定到 PS 主线程，合成 RGB565 后交给原 `SharedScanout`。无需 X11、Wayland、SDL 或桌面，不与第二个显示程序争用 DP。
- 默认只显示右下角上箭头；上键展开、下键收起，F9 也可切换。10 秒无操作自动收起，确认弹窗和等待回执期间暂停计时。键盘输入使用 Linux evdev，默认发现 `/dev/input/by-id/*-event-kbd`，可显式指定设备。
- F1 原图：显示透视校正后的彩色画面，跳过量化。如果历史恢复已开启，原图同样经过恢复，界面会提示关闭恢复可查看未经恢复的画面。
- F2 初步增强：现有 PL 量化器使用 `weak_delta=ink_level`，提高弱笔画进入条件；F3 深度增强使用原参数（默认 `ink_level=16, weak_delta=6`）。这是同一已有 IP 的两个参数档位，不新增 HLS 算法。效果仍需实景比较。
- F6 记录当前板面：等待已接纳帧完成并收到显示 pageflip 回执，冻结对应的校正原帧；确认后将该帧写入 CMA，由 PL 执行 `initialize=1`。只有 PL 完成且状态成功才确认记录。取消不写入。记录后恢复保持关闭。
- F5 历史恢复：关时跳过恢复 IP；开时才调用恢复 IP。未记录、几何变化、定位失效时不能开启。模式和恢复切换在帧边界执行，等待新路径画面完成 pageflip 后回执，不能只改按钮颜色。
- F8 历史板书／返回实时：左侧展示最近一次人工记录的真实校正帧，右侧保留当前原画面对照；没有记录则显示空状态。查看历史不自动开启恢复。
- F7 恢复参数：差分阈值→`delta`、保持帧数→`hold`、稳定阈值→`quiet_delta`、稳定帧数→`stable_r`（1～15）。仅在 IP 空闲时写寄存器并回读；应用后清除旧记录有效性，需重新记录。写入策略使用当前硬件的固定策略，不提供虚假的 W0/W1 切换。
- 白板按钮禁用；F4 请求白板会被拒绝。当前硬件及定位逻辑没有经过白板模式适配，不能仅改变 UI 标签。F10 诊断页保留“待接入”，没有将模型诊断伪装成当前显示帧的结果。
- 保留最新移动提示页及 2 Hz 异步识别；可选 `--hand-model/--hand-log` 仍从恢复前校正帧取样，只做诊断，不控制恢复。

历史记录目前是**本次进程的一张参考帧**，不是多页归档。几何改变、识别结果过期、主动重新定位、参数改变及进程退出都会使记录失效；重启后重新记录。自动清板重建在这个入口关闭，防止覆盖用户确认的参考帧。移动和旋转仍需人工调整相机。

## 调度与性能边界

为使手动记录、参数更新、恢复开关的帧边界可核验，新入口每次只接纳一帧，使用非阻塞轮询推进校正、可选恢复和可选量化。它**尚未恢复旧入口的三阶段重叠流水**。UI 刷新和 2 Hz 识别分别调度；处理期间可继续刷新最近画面，但这不代表有新的相机帧到达。

全屏 UI 合成增加 CPU 快照和 RGB565 写回；显示目标默认 30 Hz，实际处理吞吐、CPU、内存、DP 帧率和模型并行性能尚未在 KV260 上测量。不能沿用旧入口的零 CPU 拷贝或吞吐结论。板上若负载高，先使用 `--display-hz 15` 对比。上一版无底栏的入口保留用于性能对照。

CPU 写入 scanout 时增加 WRITING/PL 空闲所有权检查，并使用 DMA-BUF 的 WRITE/WRITE|END 同步标志。未修改 bitstream、DTBO、HWH、驱动二进制或硬件寄存器 ABI。

## 队友上板步骤

请使用匹配原工程的 KV260 Linux/PYNQ/驱动/摄像头环境。解压到新目录，保留原工程。本包交付源码，**不要将 WSL 的 x86_64 `.so` 拷到 ARM 板卡**。

首次在 KV260 上构建 LVGL 库：

```bash
cd v16_ps_full_ui_20261018
# 需已有 C/C++ 编译器、CMake >= 3.18、make、Python3。
# 如果缺少工具，在能联网的 Ubuntu 上由维护者安装：
# sudo apt-get update && sudo apt-get install build-essential cmake
python3 build_ui.py --jobs 2
```

离线依赖已附于 `vendor/`，构建脚本校验源文件后在本机编译，不联网下载。输出 `ui_native/build/libboard_ps_ui.so`；库只负责 LVGL 绘制和控件，不打开板端设备。此构建流程已经在 x86_64 WSL2 从交付依赖完整执行；ARM 本机构建仍待队友实测。

板上检查：

```bash
sudo /usr/local/share/pynq-venv/bin/python3 verify_runtime.py --board
ls -l /dev/input/by-id/*-event-kbd
```

若原 overlay、驱动和采集链路已就绪，按旧工程方法停止原视频进程后，运行：

```bash
set -o pipefail
sudo /usr/local/share/pynq-venv/bin/python3 -u run_stage_pipeline_ui.py \
  --hwh ./imx219-quality-ila.hwh --buffers 4 --warmup 3 --display-hz 30 \
  2>&1 | tee "full_ui_$(date +%Y%m%d_%H%M%S).log"
```

默认自动发现 USB 键盘；如果没有 by-id 链接，可补 `--input-device /dev/input/eventN`，其中 N 必须是实际键盘节点。建议首次用键盘验证。可重复指定鼠标节点，但此轮没有实测板端 USB 鼠标。

若需使用继承的整机部署流程，则在库构建成功后执行 `sudo bash run.sh check`，成功才执行 `sudo bash run.sh deploy`；随后 `sudo bash run.sh status` 和 `tail -f live.log`。部署会停止其跟踪到的旧进程，可能加载 FPGA；不要和前台入口同时运行。后台退出用 `sudo bash run.sh stop`。该部署流程本轮未在板卡执行。

前台用 Ctrl+C 退出。SIGUSR1 可请求重新定位（同时使记录失效）。回退使用之前保留的独立候选，不要直接使用未配置 `.previous` 的 `run.sh rollback`。

## Linux 验证与复现

最终记录：`evidence/full_regression_02/validation.json`，98 项通过、0 失败、0 错误、0 跳过；其中新增 23 项覆盖真实 LVGL 控制、主循环、硬件路由、evdev 解析与 scanout 写同步。`evidence/full_window_01/` 保存实际 WSLg 窗口运行时使用的合成画面及七种交互状态。`evidence/keyboard_window_02/interaction.json` 记录到一个实际 X11 下方向键事件；上下键和鼠标的完整控件行为另由原生桥接测试覆盖，不能据此声称已测试真实 USB 设备。

测试曾暴露连续接纳新帧导致记录边界饥饿，已改为先完成当前帧显示确认，再接纳下一帧；对应主入口测试先失败后通过。构建、回放和测试均在 x86_64 WSL2 执行。

WSL2 验证使用真实 LVGL/C 控件与 Python 状态机。硬件替身测试执行实际新主循环，检查记录、恢复开关、模式路由、历史页、DMA 写入标志、资源关闭。`Hardware` 的测试检查真实控制器方法调用，不声称执行过真实 PL。

`replay_full_ui.py` 为界面验证窗口：真实视频像素＋实际 LVGL，使用明确的恒等几何和离线控制替身，不检测该窗口中的板面，也不模拟 PL 增强或恢复效果。界面标注“离线验证 · 无板卡”。记录调用、历史页和交互可验证；截图不是板端恢复效果图。

```bash
python3 build_ui.py --jobs 4
export BOARD_UI_LIBRARY="$PWD/ui_native/build/libboard_ps_ui.so"
python3 validate_linux.py --output evidence/my_regression
python3 replay_full_ui.py --video /实际路径/板书视频.mp4 \
  --library "$BOARD_UI_LIBRARY" --output evidence/my_window --seconds 30
```

回放需要 NumPy、OpenCV、Pillow、Tk 和可用桌面/WSLg；PS 正式入口不依赖 Pillow/Tk。中文字体已经编译到 C 源码，无需板端安装字体。回放输出目录必须是新目录，可加 `--scripted` 重放展开、记录、恢复、历史及收起。

## 今晚上板验收

1. 先不启用手部模型：检查原画面、提示页、上下键展开/收起和 10 秒自动隐藏。
2. 定位成功后 F6，确认冻结画面无遮挡，记录后 F5 仍显示关；取消应保持原状态。
3. F5 开启/关闭，确认真实恢复效果随开关变化；F1/F2/F3 比较实际画面，记录帧率。
4. F8 查看历史，确认内容来自刚才记录，右上角原画面继续更新；再次 F8 返回实时。
5. 移动相机使定位失效或用 SIGUSR1 重新定位，确认旧恢复和旧记录被撤下。
6. 参数应用后确认需重新记录；连续运行至少 10 分钟，保存日志、屏幕录像、CPU/内存、退出重启结果。

真实 DMA/DP、USB 键盘、ARM 构建、增强效果与实时性能均待上板确认。没有进行 Vivado 综合或改变固件。
