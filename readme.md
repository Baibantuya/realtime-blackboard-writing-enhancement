# Real-time Blackboard Writing Enhancement

基于 AMD Kria KV260 的实时板书增强系统。树莓派 V2 摄像头采集板书，PL 执行透视校正、恢复辅助处理和场景量化，PS 负责缩略图分析、流水调度与 UI，香橙派便携显示屏呈现原图、校正图和增强图。

## PL version

工程使用 **Vivado / Vitis 2025.2**。配套硬件版本为 **C5**，独立源码重建记录为 **R5**；目标器件 `xck26-sfvc784-2LV-c`，处理时钟 200 MHz。三个 HLS IP、RTL、BD Tcl、约束、实现报告及配套硬件按该版本组织。项目继续使用原有功能与操作方式。

## Directory map

| Directory | Content |
|---|---|
| `src/pl/` | 2025.2 RTL、HLS、IP归档及生成RTL浏览副本 |
| `src/ps/`、`src/kernel/` | PS、UI和驱动源码 |
| `sim/` | 测试平台与补充验证记录 |
| `build/` | Tcl、约束、构建入口和校验程序 |
| `build/reports/c5/` | 与交付硬件配套的实现报告 |
| `build/reports/r5/` | 独立源码重建报告与工具日志 |
| `build/reports/hls/` | 三个HLS核的综合与测试报告 |
| `board/runtime/` | C5 bit/bin/HWH/DTBO、PS运行程序、ARM UI与驱动 |
| `board/hardware/` | 配套XSA、设备树源码和导出记录 |
| `board/results/legacy_v24/` | 原V24现场运行记录 |
| `data/` | 测试输入及参考输出 |
| `skill/` | 可复用工具、说明和测试 |
| `report/` | 仓库报告、团队AI Sessions、照片和附件 |

历史AI记录和Skill跨版本测试样本保留原版本标识；主工程从 `src/pl/` 与 `build/` 构建。

## Implementation results

| Item | C5 / R5 |
|---|---|
| Tool / design state | Vivado 2025.2 / Routed |
| WNS / TNS | +0.011 ns / 0 ns |
| WHS / WPWS | +0.010 ns / +0.164 ns |
| LUT / FF | 75,317 / 92,127 |
| BRAM / URAM / DSP | 81.5 / 50 / 839 |

原始时序、CDC、DRC和资源结果见各自报告目录。报告文件保留工具输出内容，配套关系和哈希见 `build/provenance/`。

## Verify files

```text
python build/verify_submission.py
python build/verify_sources.py
python -B -m unittest discover -s skill/contract_codegen -p "test*.py"
python -B -m unittest discover -s skill/reviewed_tools/tests -p "test*.py"
python -B skill/overlay_preflight/validation/test_preflight.py
```

`manifest.json` 为完整交付文件清单；`build/source_manifest.json` 为源码构建输入清单；运行包内部清单位于 `board/runtime/config/runtime_manifest.json`。

## Build

将源码放在短英文路径，配置 Vivado / Vitis 2025.2、K26 器件及 KV260 board files。Windows：

```powershell
powershell -ExecutionPolicy Bypass -File build/run_all.ps1 -ToolRoot D:/amd/2025.2 -Python python
```

Linux 加载工具环境后执行 `bash build/run_all.sh`。HLS入口使用 `vitis-run --mode hls --tcl build/hls_r.tcl` 等命令。构建依次执行三核HLS、综合和布局布线，输出到 `h/`、`v/`、`i/` 和 `logs/`；脚本使用全新构建目录。

C5硬件导出Tcl与记录位于 `build/provenance/export_history/`；现成配套硬件位于 `board/`。已保存的Windows构建使用过进程级UTF-8兼容环境，实际参数见 `build/provenance/original_readme_2025_2.md`。

`bash build/build_ui.sh` 生成当前架构的UI库；板端使用ARM64产物。`bash build/build_kernel.sh` 使用目标内核构建环境；随包驱动对应 `5.15.0-1027-xilinx-zynqmp`。运行入口及环境见 [board/readme.md](board/readme.md)。

## Reports and license

- [仓库技术报告与AI资料](report/readme.md)
- [实物照片](report/photos/readme.md)
- [MIT License](license.txt)
- [Third-party notices](third_party_notices.md)
- [GitHub repository](https://github.com/Baibantuya/realtime-blackboard-writing-enhancement)

展开目录与文件名使用小写英文、数字、下划线、连字符和扩展名分隔点；厂商IP归档内部沿用工具原生名称。
