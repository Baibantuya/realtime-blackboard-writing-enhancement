# 环境与安装来源（草稿）

2026-10-27更新：当前基线为V24-PS-SLIM-20261026。下表板端版本仍需现场采集；本机Python见 [回归记录](../evidence/20261027/regression_run.json)。神经网络与手势控制不在本阶段，不安装推理框架或补权重。

| 项目 | 已有依据 | 当前状态 |
| --- | --- | --- |
| 板卡/器件、输入 | KV260/K26、xck26-sfvc784-2LV-c、IMX219，S08 | 交付记录；尚未现场采集确认 |
| 内核 | 5.15.0-1027-xilinx，S08 | 历史记录，不是当前板端探测 |
| PYNQ Python入口 | /usr/local/share/pynq-venv/bin/python3，deployment.json | 源码配置；Python/PYNQ实际版本未知 |
| OS镜像/安装来源 | Ubuntu板端描述 | 镜像下载来源、版本/校验和、项目修改待补 |
| Python依赖 | 源码使用PYNQ、NumPy、OpenCV等 | 精确版本、安装源与系统库待采集；不是只复制venv |
| fpgautil/XRT/xmutil | 加载工具源码引用 | 安装包来源/版本待补，不由官网latest推断 |
| 驱动 | V24 hardware目录中的wb_frame_pool.ko、wb_rgb565_format.ko；build/build_kernel.sh | 两ko负载哈希通过；实际vermagic/运行内核/ABI待验证；旧kernel_sources.tar.gz说明仅属V22 |
| UI | AArch64动态库、LVGL依赖 | 完整包存在性来自交付说明；精确依赖和构建/许可待补，WSL库不可代替AArch64库 |
| 构建工具 | 原V24为2021.2；2025.2迁移独立分支 | S/build的rebuild_vivado.tcl、rebuild_hls.tcl、build_ui.sh、build_kernel.sh入口已确认未执行；完整重建、工具理由及匹配构建证据待补 |

本轮检查器运行在Windows本机，实际Python版本见 [测试记录](../evidence/20261022/constructed_tests.json)。它不依赖PYNQ，也不能说明目标板满足依赖。

## 提供给板端操作人的最小采集建议（未执行）

仅在用户安排的板端检查中运行；不导出完整环境变量、用户配置、网络凭据或用户主目录。记录真实时间、设备标识（可匿名）、运行包哈希与输出。

```bash
uname -r
cat /etc/os-release
command -v fpgautil
command -v xmutil
/usr/local/share/pynq-venv/bin/python3 - <<'PY'
import json, platform, importlib.metadata as metadata
packages = {}
for name in ('pynq', 'numpy', 'opencv-python', 'opencv-python-headless'):
    try:
        packages[name] = metadata.version(name)
    except metadata.PackageNotFoundError:
        packages[name] = None
print(json.dumps({'python': platform.python_version(), 'packages': packages}, indent=2))
PY
modinfo -F vermagic "$RUNTIME/hardware/wb_frame_pool.ko"
modinfo -F version "$RUNTIME/hardware/wb_frame_pool.ko"
modinfo -F vermagic "$RUNTIME/hardware/wb_rgb565_format.ko"
```

Python元数据缺失不能直接判为库不存在；OpenCV可能来自系统包，按实际安装来源另补版本。上述建议不执行 `insmod`、`ensure_kernel.py --load`、PYNQ Overlay或CMA分配。fpgautil/xmutil版本通过实际包管理记录/安装来源补充，不猜测命令行选项。

后续环境记录建议字段：`captured_at`、`board`、`kernel`、`os_image_source`、`python_executable`、`python`、`pynq`、`numpy`、`opencv`、`fpgautil_package`、`xrt_package`、两个驱动vermagic/version、`release_sha256`、证据路径。未知写null并列待补，不填示例数值。

安装流程尚未达到从零可执行：缺OS镜像与包来源、精确依赖、板级环境和冷启动闭环。先收集以上记录，再补固定版本安装步骤；不在本轮联网升级或自动安装板端依赖。
