# PS 提示页与 2 Hz 板面识别候选

2026-10-18。本目录在 `v16_ps_coarse_guidance_20261017` 的独立副本上完成本阶段整合。原工程、硬件文件和模型权重保留；没有连接 KV260、加载固件或修改 PL。

## 本次接入

- `deployment.json` 的 `live` 已指向 `run_stage_pipeline_frontend.py`，预检查改为 `verify_runtime.py --board`。继承的 `run.sh` 使用这份配置，因此不再默认启动旧的无前端入口。
- PS 入口默认加载 `frontend_assets_current/`，内容逐文件对应 `ui/camera_guidance/assets_20261018_v5/`：Regular 字体、可见字形居中、紧凑标签、精简说明、缩小 20% 的箭头。无需板端字体或 Pillow。
- 严格四角检测与必要时的粗定位由同一个工作线程负责，最多每 0.5 秒开始一次识别。首次寻找、重新定位、锁定后的复查均受此限制；繁忙时不积压旧帧，不补跑过期采样。原来的锁定后复查为每 2 秒一次，本候选按本次要求统一到 2 Hz，因此不声称所有运行状态的 CPU 开销都会降低。
- 严格几何仍要求 3 次确认；方向建议仍要求 2 次一致观察，允许的相邻采样间隔改为 1.25 秒。超过 1.5 秒的识别结果不可使用，旧提示撤下，暂停新几何帧进入恢复流程，并重新确认板面。重新定位会使在途旧结果失效。
- 画面刷新有独立时钟，默认目标 30 Hz，可用 `--guidance-display-hz` 调整。每次显示使用当前采集的原画面和最近有效的建议；识别工作线程不执行显示或硬件操作。目标刷新率不等于实测板端帧率。
- 相机缓冲仍由主线程持有，只在合法 CPU 访问期复制。识别和显示可共享同一份只读独立快照；释放相机缓冲后不再访问其视图。工作线程最多持有一份在途快照，无视频队列累积。
- 原有可选 `--hand-model` 异步模型支路与恢复前采样位置保留；本次不改变模型权重或让模型控制恢复。

本阶段接入的是“相机移动提示页”。底部 LVGL 操作栏、真实硬件控制回执与历史页面仍是后续整合内容。继承的 `README.md`、旧 `frontend_readme.md`、旧 manifest 和旧 diff 属于原候选材料；本阶段以本文件、`runtime_manifest.json` 和新证据为准。

## Linux 验证结果

环境：WSL2 Ubuntu 22.04，Python 3.10.12，OpenCV 4.11.0，NumPy 1.26.4。

- `evidence/wsl_regression_01/validation.json`：75 项软件测试通过，无失败、错误或跳过。覆盖原方向判断、RGB565 合成、异步模型支路以及新增识别限频、快照所有权、过期撤回、重新定位、异常和关闭行为。
- 实际 PS 主入口使用硬件替身执行，确认相机缓冲回收后的独立快照仍有效、显示次数多于识别次数；正常视频路径在模型开关两种情况下与原联合入口的输出和资源释放次序一致。
- `evidence/wsl_window_01/replay.json`：真实《测试视频1.mp4》从第 212 帧开始，WSLg 窗口回放约 8.01 秒；解码 208 帧，显示提交 208 次，识别提交／完成各 16 次；最小识别间隔 0.517 秒。窗口显示提交约 25.96 Hz，自动得到“先向上、再顺时针”提示。此数值仅为本机回放提交频率，不是显示器光学刷新率或 KV260 性能。
- 回放只调用真实 PS 识别与合成代码，不执行 PL 透视校正或历史恢复；即使几何锁定，验证窗口也继续显示引导页。

首次主入口测试暴露了测试替身在导入时遮蔽真实 `rgb565` 的问题；已修正测试导入顺序，并将原“每次显示必识别”的断言改为验证独立刷新。上述 75 项结果来自修正后的完整运行。

## 本机复现

在 Windows PowerShell 执行；每次输出目录使用新名字，避免覆盖证据：

```powershell
wsl -d Ubuntu-22.04 --exec /home/ubuntu/board-system/venvs/ui/bin/python -B "/mnt/d/2026嵌赛/实时板书增强系统/model_integration/v16_ps_ui_2hz_20261018/verify_runtime.py"

wsl -d Ubuntu-22.04 --exec /home/ubuntu/board-system/venvs/ui/bin/python -B "/mnt/d/2026嵌赛/实时板书增强系统/model_integration/v16_ps_ui_2hz_20261018/validate_linux.py" --output "/mnt/d/2026嵌赛/实时板书增强系统/model_integration/v16_ps_ui_2hz_20261018/evidence/new_regression"

wsl -d Ubuntu-22.04 --exec /home/ubuntu/board-system/venvs/ui/bin/python -B "/mnt/d/2026嵌赛/实时板书增强系统/model_integration/v16_ps_ui_2hz_20261018/replay_ui.py" --video "/mnt/d/2026嵌赛/实时板书增强系统/工作空间/A和B发送的资料/新阶段/测试视频1.mp4" --start-frame 212 --seconds 10 --window --output "/mnt/d/2026嵌赛/实时板书增强系统/model_integration/v16_ps_ui_2hz_20261018/evidence/new_window"
```

`replay_ui.py --window` 使用 Tk/WSLg 作为本地验证窗口；它不是板端显示后端。关闭按钮或 Esc 可提前退出。

## 后续上板入口

后续将整个候选目录放到匹配的板端环境，再进行检查与联调。若原 overlay、驱动和采集已就绪，可在候选目录执行：

```bash
/usr/local/share/pynq-venv/bin/python3 verify_runtime.py --board
/usr/local/share/pynq-venv/bin/python3 run_stage_pipeline_frontend.py \
  --hwh ./imx219-quality-ila.hwh --buffers 4 --ring-slots 3 \
  --warmup 3 --guidance-display-hz 30
```

既有 `run.sh deploy` 的加载与启动流程也已通过配置指向新入口，但本轮未执行。校验器检查新候选文件哈希、原硬件文件身份、既有静态接口／时序证据；`--board` 另查 HWH 与内核环境，不把通过检查当作实机运行验收。

仍需上板测量实际采集／显示帧率、识别耗时、CPU 与内存、模型并行运行、长时间稳定性以及真实 DMA／DP 所有权。默认 30 Hz 引导页需要 PS 复制和合成画面，尚未得到板端带宽或资源数据。识别降频的代价是提示确认更慢：两次建议至少间隔 0.5 秒，三次初始几何确认至少跨越 1 秒，另加采样等待和计算时间。

回退时使用此前候选目录和入口；本轮没有覆盖其文件。`baseline_sha256.json` 记录副本来源，`runtime_manifest.json` 记录当前软件候选，`evidence/integration_receipt.json` 记录原件与 UI 资源一致性核查。
