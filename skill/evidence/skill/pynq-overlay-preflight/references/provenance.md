# 来源经验与限制

| 观察 | 可复用经验 | 证据级别 |
| --- | --- | --- |
| V22有bit/HWH/DTBO/bit.bin及多层清单 | 文件配对、清单和独立构建来源分别核查 | 本轮源码/字节核对；构建原始过程未重跑 |
| `kv260_overlay.py`先清失效状态、复制文件，再进入check-only分支 | 不依赖命令名判断只读性；离线检查与加载后端分离 | 本轮阅读全文；不是本轮板端执行 |
| 该加载器注释提到KV260 configfs readback问题 | 平台后端可能需fpgautil＋元数据登记 | 注释/实现可核验；本工作区尚未关联原始报错/案例，不能补写历史故障原文 |
| Q实例名保留旧名字，实际VLNV为board_scene_quantize | 同时核对FULLNAME、VLNV和寄存器契约 | 本轮HWH解析及scene_stage源码 |
| 正式live指向v2，预检仍要求旧archive入口 | 字节一致性不能证明启动流程逻辑一致 | 本轮AST＋JSON对照；不是实机报错 |
| SceneStage超时保留所有权，v2退出可能等待DMA | 材料编写不能把强制退出/释放缓冲当普通检查 | 只作为后续生命周期Skill来源；本轮未实现或验证真实DMA |

详细源文档/哈希见 [source_inventory.md](../../../source_inventory.md)，AI_Sessions独立整理工作的案例关联入口见 [ai_session_links.md](../../../ai_session_links.md)。工程架构与历史板测由交付团队完成；本轮AI贡献为资料核查、离线工具/构造测试和文档草稿。

[PYNQ官方Overlay说明](https://pynq.readthedocs.io/en/latest/overlay_design_methodology/overlay_design.html)支持bit与HWH配套及同名要求；[官方allocate说明](https://pynq.readthedocs.io/en/latest/pynq_libraries/allocate.html)支持PL缓冲地址和flush/invalidate语义。访问日期2026-10-22，latest只作概念参考，不能推断本板安装版本。
