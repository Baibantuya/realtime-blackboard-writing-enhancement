# 2025.2迁移的PYNQ接口审阅

2026-10-27。只读本地HWH和迁移记录，未运行Vivado/HLS、访问服务器或替换PS/PL。源记录位于D:/2026嵌赛/v24_2025_2；最新phase2记录覆盖同步文件前段的旧阶段状态。

两分支分别为upgrade_with_xci保留旧HLS RTL，以及c3/b/design_1/hw_handoff/design_1.hwh重建候选。输入路径、SHA256和全部描述差异见 [接口JSON](../evidence/20261027/migration_interface_review.json)。比较保留26条MEMRANGE记录及全部属性，不通过去重缩小范围。

| 项目 | 保留旧HLS分支 | c3重建分支 | 结论边界 |
| --- | --- | --- | --- |
| 地址范围 | 26/26一致 | 26/26一致 | 不证明所有寄存器语义 |
| 三自定义核寄存器 | 15＋20＋35描述完全一致 | CTRL、IER/ISR字段变化；Scene control→control_r，0x68不变 | 旧分支结论不可转移 |
| 自定义核时钟/复位/中断 | 选定端口全部属性及同SIGNAME连接端点一致 | 同左 | 不验证实际频率、波形、GIC路由或中断投递 |
| MIPI 5.1→6.0 | 两差分时钟引脚SIGIS由undef变clk；方向/信号/连接端点相同 | 同左 | 标记变化不等于实体行为验证 |
| 帧缓存写入2.3→3.0 | 不再列原未连线的s_axis_video_TKEEP | 同左 | 需版本资料/驱动验证，不能自动判等价或故障 |
| HLS AXI数据端口 | 选定端口无变化 | 每核选定4项移除，表现为不使用的读写方向描述收紧 | 不等于RTL等价性证明 |
| MIPI/帧缓存寄存器 | 0对0 | 0对0 | <span style="color:#C00000">【待核验】NOT_CHECKED_NO_REGISTER_METADATA</span> |

当前主包scene_registers.py使用PROPERTY解析并要求完整接口；c3的control_r需对应适配。迁移目录ps_candidate已有别名适配和Windows/WSL静态回归，为交付记录，本轮未重跑或替换主包。新工具保留实际名称，不自动把control_r改成control。

剩余外设核验：版本对应官方寄存器/接口资料、Linux驱动compatible/API、设备树时钟/复位/中断与firmware-name、像素格式/步长、同帧完整性。本地HWH不足以解除这些项，本轮不升级依赖或试载候选产物。

历史阶段记录：恢复核通过3处资源绑定调整完成C测试/HLS/123次Verilog联仿及导出；Scene计数树候选9次RTL联仿；Rectify有20组1080p C测试和导出，尚缺其RTL联仿。本轮未重跑，小尺寸联仿不是1080p实景覆盖。

三轮post-route WNS分别为−1.014、−1.411、−0.219ns；第三轮TNS−84.981ns，setup失败624、hold失败0，CLB约94.49%。实现后CDC-11消失且无waiver，但CDC-6两项/CDC-15六十八项警告仍需审阅；no_clock=0、内部无约束端点=0不能覆盖4输入/2输出delay缺项。

<span style="color:#C00000">【待核验】第三轮尚未时序/CDC/外设签核，没有新bit、XSA或板测。禁止将候选HWH配旧2021.2 bit/DTBO，禁止将现役板测归到迁移候选；PS参数优化不能修复PL setup违例。</span>
