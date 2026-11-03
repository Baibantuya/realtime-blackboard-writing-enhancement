---
name: v24-reviewed-tools
description: 审阅 PYNQ 交付的 HWH 寄存器契约、DMA 所有权、Overlay 副作用和性能指标，并进行无硬件的代码生成与回归。适用于交付材料核验和工具草稿维护。
---

# PYNQ 工具审阅草稿

先记录输入版本、路径、SHA256 与证据类别。原始源码、历史板测、现场反馈、计划、本轮离线结果分别标注。保留失败输入和原始输出；只修隔离副本。不得把原工具的多板兼容、历史 Session 编号或“根治”描述当作已经取得的验证证据。

选择所需路径：

- HWH/ABI/文件预检：沿用 [现有检查器](../overlay_preflight/skill.md)，选择对应版本配置。V22 与 V24 的报告不能互换。
- 契约生成：使用 [codegen.py](pynq_tools/codegen.py)。精确匹配 FULLNAME；偏移从 PROPERTY 读取，缺字段失败。用同次交付的 HLS 头文件独立交叉核对；头文件 64 位逻辑项展开成两字。指针含义由接口说明指定，不能根据 ARM 位数或后缀推断。生成代码只提供显式寄存器访问，不自动加载或启动 PL。
- DMA 候选：阅读 [生命周期约定](references/lifecycle.md) 后使用 [dma.py](pynq_tools/dma.py)。超时不是停止；在途/隔离缓冲不能复用或释放。硬件完成与恢复证明需要板级实现，mock 通过不替代板测。
- Overlay：使用 [overlay.py](pynq_tools/overlay.py) 生成只读计划。后端明确选择；本候选没有硬件执行后端。实际加载、状态清理、设备树变更及缓冲分配仍按当前用户授权范围执行。
- 性能/参考：使用 [benchmark.py](pynq_tools/benchmark.py)。明确记录事件、起点和阶段边界；阈值由需求提供。没有阈值时不写“达标”，不能将阶段耗时写成冷启动或端到端延迟。
- 排障与提示词：参考 [排障表](references/troubleshooting.md) 和 [工作流](references/prompt_workflows.md)。输出可验证假设，不补写历史对话或未经观测的因果链。

可执行入口与限制见 [README](readme.md)，来源、许可和逐平台状态见 [验证矩阵](references/validation_matrix.md)。验证仅覆盖 Windows 离线真实文件和 mock；真实板卡、PYNQ 解析器、CMA/缓存/复位、Linux 驱动及跨板行为均待验证。
