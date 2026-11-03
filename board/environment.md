# Board environment

更新：2026-11-03。本文汇总项目文件及 Codex“2026嵌赛”项目中相关对话，便于配套部署与复现。

| 项目 | 已找到的配置 | 依据 |
|---|---|---|
| 计算平台 | AMD Kria KV260 / K26，ARM64 | 工程器件、交付记录与 ELF 文件头 |
| 摄像头 | 树莓派 V2 摄像头，Sony IMX219 | 当前硬件设计及部署程序 |
| 显示屏 | 香橙派便携显示屏，系统使用 Linux DRM / DP 输出 | 用户提供的设备信息与显示驱动 |
| 操作系统 | Ubuntu 22.04 | “优化UI叠层”对话中的用户确认 |
| PYNQ | 3.0.1 | 同一对话中的用户确认 |
| 驱动目标内核 | `5.15.0-1027-xilinx-zynqmp` | 随包两个 `.ko` 的 vermagic |
| Python 入口 | `/usr/local/share/pynq-venv/bin/python3` | `runtime/config/deployment.json` |
| UI | LVGL 9.6.0，随包动态库为 ARM64 | vendored 源码和 `libboard_ps_ui.so` 的 ELF 头 |
| 构建工具 | Vivado / Vitis 2025.2，C5 交付硬件、R5 独立重建 | `../build/reports/` |

用户确认的系统版本属于历史运行配置；二进制字段来自本轮本机读取。机器可读结果与对话出处见 [environment.json](environment.json)，驱动和 UI 的 SHA-256 见 [二进制核验](environment_binary_inspection.json)。
