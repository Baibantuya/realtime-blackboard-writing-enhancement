# 验证范围

2026-10-22，Windows本机。Python确切版本、脚本/测试文件SHA256见 [constructed_tests.json](../../../evidence/20261022/constructed_tests.json)，详细 [日志](../../../evidence/20261022/constructed_tests.log)。

- **真实归档副本对照**：[V22输出](../../../evidence/20261022/v22_preflight.json)，9文件/3IP/70寄存器，429项pass、0 fail、7 not_checked。期望值来自V22已知清单和冻结HWH快照，不是独立硬件功能判定。
- **23项构造测试**：`python validation/test_preflight.py`（在技能根目录执行）。包含正常输入且读前后目录/文件哈希不变，以及缺文件、位流字节变化、HWH名称/解析/IP/VLNV/寄存器/字段/地址变化、重复模块、XML实体拒绝、路径越界、未知字段、空契约/null配置、清单/发布/环境不符、CLI成功与失败退出码。
- **参数化证据**：合成例使用另一个IP名称、VLNV、寄存器地址、backend标签。它只说明核心不依赖V22硬编码，没有真实第二块板或第二个工程验收。
- **无硬件副作用**：源码只使用标准库读文件/XML和输出JSON；不调用原包加载器。构造测试检查输入文件集及内容未改变；它不是对所有可能文件系统副作用的形式化证明。

未覆盖：真实PYNQ XML解析兼容性、bit设备解码、DTBO解析/实际应用、驱动vermagic/已加载ABI、FPGA重载、CMA/cache/DMA、相机/显示、硬件性能、跨板使用。输入支持UTF-8 HWH，最大32MiB，DTD/实体被拒绝；未穷尽所有恶意/畸形输入。

原发布入口冲突的AST比较另见 [source_review.json](../../../evidence/20261022/source_review.json)，不包含在“23项检查器构造测试”里，不把它写成已修复或实际板测失败。
