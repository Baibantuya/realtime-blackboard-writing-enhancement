# 来源、许可与验证矩阵

输入来自用户指定 S=`D:/2026嵌赛/最终素材/submission_v24/submission_v24` 的 `skill/`。40 个文件包含 14 个缓存文件；工作区保留 26 个非缓存原件快照。作者身份、原始许可授权和 Session 引用尚未独立核实；不得补写 MIT/Apache 许可或宣称全部历史案例已证实。本轮修改由本对话单代理在用户授权范围内完成。

| 来源组 | 当前输出 | 输入/输出与副作用 | 失败边界/证据 |
| --- | --- | --- | --- |
| 01_overlay_manager | `pynq_tools/overlay.py`；寄存器检查并入 codegen | 文件、哈希、明确后端→计划；只读 | 缺文件、哈希/后端/元数据目录不符失败。没有硬件执行后端 |
| 02_dma_buffer_guard | `pynq_tools/dma.py` | 显式分配器/Lease/IP句柄→完成或隔离；真实使用会分配/访问硬件 | 本轮均mock；真实CMA、缓存、MMIO超时和复位未测 |
| 03_contract_codegen | `pynq_tools/codegen.py` | HWH＋明确指针→新Python文件及测试；CLI写指定输出 | 70真实字/三份头文件交叉通过；缺字段/实例歧义/宽度等失败 |
| 04_golden_benchmark | `pynq_tools/benchmark.py` | 事件/阶段时延、数组→统计/差异；报告写指定目录 | 时钟注入与数组负例通过；实景样本和阈值待提供 |
| 05_troubleshooting | [排障表](troubleshooting.md) | 观测→假设/待验证动作；文档不执行命令 | 原稿“已验证根治”及 Session 编号保留为未核实来源声明 |
| 06_prompt_workflows | [工作流](prompt_workflows.md) | 版本与约束→分析问题与验证方案；不授权部署 | 人工审阅，未取得跨平台任务实测证据 |

原件指纹：[input_review.json](../../evidence/evidence/20261027/input_review.json)。失败复现：[candidate_failures.json](../../evidence/evidence/20261027/candidate_failures.json)。修订代码指纹与31项日志：[regression_run.json](../../evidence/evidence/20261027/regression_run.json)。V24预检和5个负例：[v24_contract_regression.json](../../evidence/evidence/20261027/v24_contract_regression.json)。

| 环境 | 验证内容 | 状态 |
| --- | --- | --- |
| Windows 本机 Python 3.12.14 | 文件/XML/JSON、真实 V24 HWH/头文件、mock API、CLI/生成测试 | 本轮通过；不是板端 Python 版本 |
| 原版 V24 KV260/2021.2 | 交付方历史运行记录 | 仅引用原记录，本轮未上板；不能用于证明本修订工具 |
| 2025.2 c3 + KV260 | 静态 HWH 对照 | 描述差异已记录；没有匹配新 bit/XSA/板测 |
| Linux/WSL 与板端 Python/PYNQ | 本修订工具的实际环境兼容 | <span style="color:#C00000">【待核验】未测；迁移目录的PS别名适配回归不是本工具回归</span> |
| PYNQ-Z2、KR260、ZCU104、Versal及其他内核/版本 | 通用性 | <span style="color:#C00000">【待核验】目标候选，未取得跨板证据</span> |

源码通读/测试粒度不相同；本轮阅读四组核心实现、测试与说明、排障/提示词原稿，不声称审阅了S整个工程。协议层工具可复用，V24专用配置、设备树、加载后端必须独立绑定版本。
