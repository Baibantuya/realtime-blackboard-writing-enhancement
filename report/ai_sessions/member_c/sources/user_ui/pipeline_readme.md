# 多阶段流水 UI 与多版面归档候选

日期：2026-10-18。本目录独立于之前交付包，正式候选入口为 `run_stage_pipeline_archive.py`，`deployment.json` 已指向此入口。行为以本文为准；继承的其他 README、旧入口和旧测试记录仅供来源追溯。固件、HWH、DTBO、驱动及寄存器 ABI 未改变。

## 操作与保存内容

| 按键 | 功能 | F6 保存的内容 |
|---|---|---|
| F1 | 原图：摄像头输入画面 | 未校正、未恢复、未量化的摄像头帧 |
| F2 | 初步增强：仅透视校正 | 校正后的彩色画面 |
| F3 | 深度增强：校正、恢复、量化 | 原 PL 算法输出的白底文字画面；彩色笔迹沿用原量化规则 |
| F4 | 上一版面 | 在实时与已存版面中向前循环 |
| F5 | 下一版面 | 在实时与已存版面中向后循环 |
| F6 | 记录当前版面 | 保存当前已显示的实时画面，不含 UI |
| 上 / 下键 | 展开 / 收起操作栏 | 不改变视频处理 |
| F9 | 切换展开 / 收起 | 10 秒无操作自动收起 |

F1–F3 共用一块淡紫色分组底板；F4–F5 共用另一块中性底板，两组之间留有间距。记录按钮为独立暖棕色按钮。字体保留 Noto Sans SC Regular，原生 1080p、8 bpp 字形。收起时仅保留右下角上箭头。F7、F8、F10 无新动作，界面不再提供黑板/白板、手动恢复开关、恢复参数和未接入的诊断菜单。

示例：F1 下记录得到版面 1（原图），F3 下记录得到版面 2（深度增强）；F5 循环“实时 → 版面 1 → 版面 2 → 实时”，F4 反向循环。每页固定保存时的模式和像素，后来切换模式不会重新处理旧页。在历史页按 F1/F2/F3 会返回对应模式的实时画面。

F6 读取已经收到显示完成回执的当前帧。若新模式还没有显示出来，会拒绝记录，避免把旧模式画面标成新模式。UI 合成前保留被覆盖区域，保存时将其还原，因此记录不含按钮、帧率和提示。历史页禁用重复记录；定位提示页不作为板书归档。F1 不要求板面已定位，F2/F3 要求当前定位有效。

历史页是本次进程内的只读 RGB565 快照，最多 32 页（像素约 126.6 MiB），满额提示且不覆盖已有页。移动相机、重新定位或更换实时模式不会删除这些页面。**退出/重启会清空记录；本轮未提供磁盘导出或断电保存。** F6 不冻结摄像头、不重置 PL 恢复参考。恢复继续使用原自动初始化与自动清板策略。

## 调度与资源

- 恢复原来的 `r_active / s_active / q_active` 三阶段重叠调度；A/B 环形队列保留至少 3 槽。仅几何更新时等待已接纳帧排空，再改变几何与恢复代次。
- F1/F2/F3 只选择显示来源，后台继续依次校正、恢复和量化，使恢复状态在原图和历史浏览期间保持更新。F4/F5 不停止视频流水。
- 板面识别仍由异步工作线程限频至 2 Hz，UI 与视频显示独立。可选手部模型仍在恢复前采样，只做诊断，不控制恢复。
- 深度增强的实时输出优先让 PL 直接写 scanout；PL 完成后仅在 UI 包围区域执行 CPU 混合，不每帧进行全屏快照再写回。收起时 UI 区域为 84×48 像素。F1/F2 将所选原图/校正帧复制到 scanout；保存和无新视频时重绘会产生完整快照。
- 采用非阻塞 scanout 申请和提交。显示忙时跳过本次显示，量化可继续写入自身输出缓冲。这样可避免等待 UI/pageflip 阻塞整个流水，但不保证所有处理帧都显示。
- UI 数值中的实时“画面 FPS”统计收到 pageflip 回执的不同视频帧；重复刷新 UI 不计为新帧。历史页显示“实时处理 FPS”，统计后台量化完成帧，不把历史重复显示伪装成视频帧率。帧率文本每秒更新，收起后不可见。
- 原曝光策略保留：启动/重新定位时自动曝光，稳定锁定后冻结曝光。没有新增连续自动曝光或手动曝光菜单。

多阶段重叠已用实际 PS 主入口和硬件替身验证，但真实 KV260 吞吐、延迟、CPU、CMA、DMA/DP 和 USB 输入仍待上板。不能由 WSL 窗口帧率推断板卡帧率。

## 板上准备与运行

解压到独立目录，保留旧包。需使用匹配原工程的 KV260 Linux/PYNQ、驱动和摄像头环境。包内为源码及离线 LVGL 依赖，**必须在目标架构编译，不能使用 WSL x86_64 的共享库**。

```bash
cd v16_ps_pipeline_ui_20261018
python3 build_ui.py --jobs 2
sudo /usr/local/share/pynq-venv/bin/python3 verify_runtime.py --board
ls -l /dev/input/by-id/*-event-kbd
```

编译需要 C/C++ 编译器、CMake ≥ 3.18、make、Python3。`build_ui.py` 校验并解包附带的 LVGL 9.6.0，不下载依赖，生成 `ui_native/build/libboard_ps_ui.so`。

原 overlay、驱动和采集链路已启动时，先停止旧视频程序，再运行唯一的新入口：

```bash
set -o pipefail
sudo /usr/local/share/pynq-venv/bin/python3 -u run_stage_pipeline_archive.py \
  --hwh ./imx219-quality-ila.hwh --buffers 4 --ring-slots 3 \
  --warmup 3 --display-hz 30 2>&1 | tee pipeline_ui.log
```

若无 by-id 键盘链接，补充 `--input-device /dev/input/eventN`，N 必须是实际键盘节点。前台 Ctrl+C 退出；SIGUSR1 重新定位，已有归档保留。保留旧启动器的 `sudo bash run.sh check/deploy/status/stop` 流程，`deploy` 会停止其跟踪的旧程序并可能加载 FPGA，不能与前台入口同时运行；本轮未在板上执行该流程。

## Linux 验证

`validate_linux.py` 运行原识别/方向/模型测试及本轮新增测试；需先编译共享库。`tests/test_archive_pipeline.py` 执行实际主循环，使用可检查所有权的摄像头、PL、DRM 替身，验证三阶段同时在途、几何安全边界、三模式像素来源及历史页期间持续处理。`tests/test_archive_ui.py` 使用实际 LVGL，验证归档不含叠加层、循环、模式切换、页数限制、自动收起和鼠标键盘。DMA-BUF 同步单测验证编辑用 READ|WRITE、归档用 READ，不能代替板上内核验证。

```bash
export BOARD_UI_LIBRARY="$PWD/ui_native/build/libboard_ps_ui.so"
python3 validate_linux.py --output evidence/my_regression
python3 replay_archive_ui.py --video /实际路径/板书视频.mp4 \
  --library "$BOARD_UI_LIBRARY" --output evidence/my_window --seconds 25 --scripted
```

回放使用真实视频和 LVGL/Tk 窗口，但三个模式都使用未增强的视频像素，**只验证交互，不模拟或证明 PL 图像增强效果**。画面标注“离线验证 · 无板卡”。输出目录须不存在。中文字体已编入 C 源码，板端无需字体安装或 Tk 桌面。

上板重点：逐一核对 F1 原图/F2 校正/F3 恢复量化的真实差异；分别记录并浏览；确认画面没有 UI 污染；历史页停留时后台 FPS 持续；切换/重新定位时没有花屏或旧帧错标；对比旧无 UI 入口的帧率、CPU、内存和连续运行稳定性。
