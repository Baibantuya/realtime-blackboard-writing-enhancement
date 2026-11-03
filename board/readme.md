# Board package

`runtime/` 为 2025.2 C5 配套运行包，`hardware/` 保存 XSA、设备树源码及导出记录。运行包使用统一前缀 `imx219-v24-2025-2-c5`，配置入口为 `runtime/config/deployment.json`，文件哈希见 `runtime/config/runtime_manifest.json`。

## Runtime entry

在已配置项目环境的 KV260 上，进入 `runtime/` 后使用：

```bash
bash run.sh check
sudo bash run.sh deploy
bash run.sh status
```

`stop` 停止服务，`rollback` 使用已有回退版本。具体行为见运行包说明及脚本。硬件文件、HWH、设备树、驱动和运行程序按同一配套包使用。

## Environment and results

[环境信息](environment.md)汇总历史配置与随包二进制字段。`results/legacy_v24/` 保存原V24实测记录，并保留原版本标识。当前C5/R5实现结果位于 `../build/reports/`。

`preflight.py` 提供只读环境采集；`compare_rgb565.py` 比较两份相同尺寸的RGB565输出。例：

```bash
python3 compare_rgb565.py --reference reference.bin --actual actual.bin --width 1920 --height 1080 --output compare.json
```
