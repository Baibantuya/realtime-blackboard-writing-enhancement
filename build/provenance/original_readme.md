# V24 2025.2 source-only candidate: clean reproduction

状态：候选验证中，尚非发布包；板卡目前不可用，未执行板测。

器件 xck26-sfvc784-2LV-c；Vivado/Vitis HLS 2025.2，处理时钟200 MHz。源代码取自保留的 v24，并包含已记录的恢复核资源绑定、窗口求和树、量化计数树修改和 PS control_r 别名适配。没有神经网络或手势依赖。

## 从干净目录构建

仅复制 src、sim、build、board、report 和本说明到纯英文短路径的新目录；不要复制 h、v、i、logs 或 build/work 的既有结果。创建空 logs 目录。

Windows PowerShell：`powershell -ExecutionPolicy Bypass -File build/run_all.ps1 -ToolRoot D:/Xillinx/2025.2`。
Linux：加载已安装的AMD工具环境后运行 `bash build/run_all.sh`；入口按顺序执行三核HLS和整机Vivado，并分别保存日志。须安装相应 K26 器件、KV260 board files 和所用 IP 的授权。Linux入口已准备，尚未在完整Linux版2025.2工具链上执行。

脚本重建三颗 HLS 核；Restore/Scene 执行原 C/RTL 测试，Rectify 执行原20组1080p C测试（不是RTL联仿）。Vivado 禁用 IP 综合缓存，从源码生成全部 OOC 和顶层，再执行布局布线。不会自动生成或加载位流，进程退出0不代表时序通过。

本机 Windows 存在单独记录的中文主机名相关 Vivado 原生崩溃，需要进程级私有 UTF-8 manifest 试验才能完成此前构建。`-VivadoOverlay` 仅供这台机器的已验证环境使用，不随此目录提供厂商可执行文件；这限制了本机对原生 Windows 可移植性的结论。Linux完整工具链尚未验证。

## 软件与板级边界

`bash build/build_ui.sh` 编译当前机器架构的 UI 库；x86_64 WSL 输出不能直接上 ARM 板。`bash build/build_kernel.sh` 必须在与目标板内核匹配的构建环境执行。不要使用 WSL 内核头生成 KV260 驱动。

board 目录只提供后续检查流程，不包含旧 bit/HWH 冒充新硬件。PS源码不是已经组装好的可启动runtime：部署配置、资产、DTBO及内核适配需要与最终产物配对后再验收。实际运行记录与失败结果保留在 logs、v/reports、i 中；最新状态写入report，不能仅凭源代码说明判断发布状态。
