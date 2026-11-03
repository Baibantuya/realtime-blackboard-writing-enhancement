# Real-time Blackboard Writing Enhancement — V24 / Vivado 2025.2

## Package status

本包是 2026-11-03 整理的交接审查版。主工程采用 **Vivado/Vitis 2025.2 C5**，独立源码重建记录为 **R5**；原始 V24 包保持原样。已纳入配套 RTL、HLS、Tcl、约束、生成 IP、实现报告、C5 运行包，以及三位成员的 AI Sessions 资料。

原理：树莓派 V2 摄像头采集板书；KV260 PL 执行透视校正、辅助恢复与场景量化，PS 执行低分辨率分析、流水调度与 UI；香橙派便携显示屏呈现原图、校正图或增强图。当前工程不包含神经网络与手势控制。

**先阅读 [交付审计](release_audit.md) 和 [仓库报告证据索引](report/evidence_index.md)。** 数值时序已通过，2025.2 板端验收、完整 1080p Rectify RTL 比较、部分 CDC/复位协议审查仍待完成；仓库报告尚需按评审修订。

## Directory map

```text
src/                         # 2025.2 PL/HLS/RTL、PS、UI、内核模块源码
  pl/hls/                    # 三个 HLS 核及辅助头文件
  pl/rtl/                    # BD 引用的 RTL
  pl/ip/                     # R5 实际导出的三个 IP 归档
  pl/generated_rtl/          # 可浏览的生成 RTL 与原名映射
sim/                         # 主工程测试平台和补充验证资料
build/                       # 2025.2 Tcl、约束、构建与验证入口
  reports/c5/                # 与交付硬件配套的实现报告
  reports/r5/                # 独立干净重建报告与原始日志
  reports/hls/               # 三核 HLS、C/RTL 测试报告
  provenance/                # 原始来源清单、构建结果、配套证据
board/
  runtime/                   # C5 bit/bin/HWH/DTBO、ARM UI、驱动及 PS 程序
  hardware/                  # 配套 XSA、设备树源码与导出核验
  results/legacy_v24/         # 旧 V24 实机记录，保留版本标识
data/legacy_v24/             # 旧 V24 联仿输入和输出参考
skill/                      # 当前审查工具、测试及原六模块来源
report/
  technical_report.docx      # 用户提供的仓库版报告，内容原样
  ai_sessions/               # 三位成员的来源记录、可见对话及证据
manifest.json               # 整包文件哈希
```

## Version and evidence

| Item | Result / source |
|---|---|
| Device / processing clock | `xck26-sfvc784-2LV-c` / 200 MHz |
| C5 and R5 setup | WNS +0.011 ns, TNS 0, failing endpoints 0 |
| Hold / pulse width | WHS +0.010 ns / WPWS +0.164 ns |
| Routing | 156,816 routable nets routed |
| Resources | LUT 75,317; FF 92,127; BRAM 81.5; URAM 50; DSP 839 |
| CDC / reset | Critical 0; Warning 70; LUTAR-1 4 items, review ongoing |
| Primary HLS tests | Rectify 20 × 1080p C cases; Scene 9 RTL transactions; Restore 123 RTL transactions |
| Supplemental tests | Rectify 63 small-image and 12 width/height-boundary calls; 18 reset events |
| 2025.2 board run | Pending; `legacy_v24` results retain the earlier version |

`build/provenance/r5_source_manifest.json` 保存原始 107 项输入清单。主工程算法、RTL、Tcl、约束及 PS 输入保持其哈希；本发布副本更新了根目录说明，并另附资料。AE Monitor 元数据和 DTBO 能力声明的后续候选保存在 `sim/supplemental/`，尚未并入 C5。

## Verify the package

在包根目录运行：

```text
python build/verify_submission.py
python build/verify_sources.py
python -B -m unittest discover -s skill/contract_codegen -p "test*.py"
python -B -m unittest discover -s skill/reviewed_tools/tests -p "test*.py"
python -B skill/overlay_preflight/validation/test_preflight.py
```

离线 Python 测试需要 `numpy`，UI 主机测试另需 `Pillow`、CMake 和 C/C++ 编译器。依赖版本应以目标板实际环境记录为准，部署前核对 `board/runtime/config/deployment.json`。

## Rebuild the FPGA project

Windows：将包解压到短英文路径，例如 `D:/wb_v24_2025_2`，安装 Vivado/Vitis 2025.2、K26 器件、KV260 board files 及对应 IP 许可。调整工具根目录和 Python 路径后运行：

```powershell
powershell -ExecutionPolicy Bypass -File build/run_all.ps1 -ToolRoot D:/amd/2025.2 -Python python
```

Linux：加载对应工具环境后运行 `bash build/run_all.sh`。已保存的全流程重建证据来自 Windows；Linux FPGA 工具全流程待验证。HLS 使用 `vitis-run --mode hls --tcl build/hls_r.tcl` 等 2025.2 入口。

本机已保存的 Windows 重建使用过进程级私有 UTF-8 兼容环境，调用参数为 `-VivadoOverlay`，原说明见 `build/provenance/original_readme_2025_2.md`。厂商可执行文件及兼容副本不随包分发；另一台电脑先使用正常安装的工具环境，并记录实际运行结果。

构建依次执行三核 HLS、整机综合、布局布线，输出到 `h/`、`v/`、`i/` 和 `logs/`。使用全新目录；已有 `h/v/i` 时脚本会退出。该入口到布局布线为止，位流和 XSA 导出另行执行。现成配套产物位于 `board/`，保留 C5 身份。

原 C5 导出 Tcl、配套检查脚本和执行记录位于 `build/provenance/export_history/`，保留当时实验目录约定。将新目录的 `i/routed.dcp` 接入导出流程、更新 bin/HWH/DTBO 和 runtime 清单，是下一步需要补齐的自动化环节。

## Linux software and board deployment

`bash build/build_ui.sh` 生成当前机器架构的 UI 库；WSL2/x86_64 输出用于主机验证。板端使用 ARM64 构建产物。`bash build/build_kernel.sh` 需要与目标板匹配的内核构建环境；随包模块对应 `5.15.0-1027-xilinx-zynqmp`。

在已配置 PYNQ 与系统服务的目标 KV260 上，进入 `board/runtime/`，先阅读该目录说明，再运行 `bash run.sh check`。`deploy`、`stop`、`rollback` 会改变板端状态，应由现场操作者执行。当前整理未部署到板卡。

## Naming and redistribution

仓库展开目录及交付文件名统一为小写英文、数字、下划线、连字符和扩展名分隔点。中文说明正文保留。RTL 模块名、寄存器名、厂商 IP 归档内部文件名和 LVGL 上游归档内部结构按工具约定保留；原样归档不进行破坏性重命名。

项目原创代码采用 [MIT](license.txt)，第三方组件保留原有许可。仓库为 [realtime-blackboard-writing-enhancement](https://github.com/Baibantuya/realtime-blackboard-writing-enhancement)，当前私有。目录规划见 [仓库结构](report/github_structure.md)，提交要求见 [准备说明](report/submission_requirements.md)。LVGL、字体及厂商IP的各自条款见 [第三方材料](third_party_notices.md)。

板端环境来源见 [board/environment.md](board/environment.md)。
