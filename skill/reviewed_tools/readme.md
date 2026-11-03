# V24 候选工具的隔离修订副本

2026-10-27。源包 `S/skill` 保持不变；本目录是审阅后形成的新 API 草稿，不可直接替换当前板端主流水驱动。使用普通 Python 包 `pynq_tools`，消除编号目录与 README 导入名不一致的问题。未安装为全局 Skill。

在本目录执行以下命令，只读输入并在明确输出位置生成文件，不加载 PYNQ/FPGA：

```powershell
python -B examples/offline_demo.py
python -B tests/test_offline.py
python -B -m pynq_tools.codegen --input ../../evidence/20261027/runtime_v24/hardware/imx219-fusion-v24.hwh --ip /board_quantize_rgb_0 --pointers examples/scene_pointers.json --class-name SceneIP --output scene_driver_local.py --generate-test
python -B test_scene_driver_local.py
```

`python` 指用户选择的本机 Python；本轮实际解释器与命令保存在 [回归记录](../evidence/evidence/20261027/regression_run.json)。代码/测试要求 Python 3.10+；本轮验证 Python 3.12.14。只有数值参考比较需要 NumPy；没有新增安装。第三、四条在隔离临时目录使用不同输出文件名实际通过测试；命令再次执行遇到已有输出会拒绝覆盖。生成文件不属于已获板测批准的驱动。

`--input` 是当前 CLI；不提供不存在的 `--hwh` 参数。HWH 是生成输入；`parse_hls_header()` 用于交叉核对，不从缺少访问属性的头文件独立生成可写驱动。原工具的宽松 JSON/头文件生成路径未保留。生成驱动使用 `write_register(name, value)`、`read_register(name)`、`write_pointer(name, address)`；Scene `control` 是 0x68 的算法参数，不能当作 0x00 的 CTRL 而跳过。64 位地址必须提供低/高两字，32 位地址溢出直接拒绝。

修订范围：

| 原候选 | 本副本处理 | 本轮验证 |
| --- | --- | --- |
| 03 契约生成 | PROPERTY/属性解析、精确实例、缺字段失败、真实头文件、访问/宽度/重叠约束、正确测试文件导入 | 三核 70 字与头文件一致，错误输入、32/64 位地址及 CLI/mock 回归 |
| 02 DMA | 显式分配器/Lease；启动前保留所有权；超时/读写异常隔离；关闭拒绝在途缓冲 | 超时、已生效启动写失败、GC 强引用、显式恢复、分配失败等 mock |
| 01 Overlay/寄存器检查 | 自动平台探测、全局状态清理、Full 卸载被移出通用工具；检查只返回计划；寄存器操作使用明确契约 | 检查前后文件不变、不创建元数据目录、不导入 PYNQ、拒绝未知后端 |
| 04 参考/性能 | 独立记录启动至首事件、阶段时延、帧间隔；按阈值评价；拒绝 NaN/空参考 | 注入时钟与数组负例；无阈值 NOT_EVALUATED |
| 05/06 文档 | 去除未经证实的“根治”、自动通用及历史案例归因 | 本轮人工审阅；提示词未做跨用户任务验证 |

31 项工具回归、另 5 项 V24 预检负例不代表整机覆盖率。原 V22 检查器 23 项测试独立保留并复跑。对应日志及输入指纹在 [证据目录](../evidence/evidence/20261027)。完整状态见 [验证矩阵](references/validation_matrix.md)。
