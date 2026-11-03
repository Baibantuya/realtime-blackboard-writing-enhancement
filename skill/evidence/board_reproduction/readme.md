# V24 slim 复现说明（离线已核查，实机步骤待授权验证）

基线：S为最终素材/submission_v24/submission_v24，R为最终素材/v24_slim_runtime_20261026/v24_slim_runtime_20261026；本工作区的 [运行快照](../evidence/20261027/runtime_v24)来自S。两处80项负载通过、35个PS Python源码/运行副本一致。输入指纹见 [核验记录](../evidence/20261027/input_review.json)。不运行快照中的启动脚本。

## 身份与结构

schema 2，version=V24-PS-SLIM-20261026，algorithm_abi=0x57425321，hardware_revision=V24-200MHz；这只是配置身份，ABI真实回读与200MHz时序仍待验证。app、drivers、ui为软件目录，hardware保存bit/bit.bin/HWH/DTBO和两个ko；config/deployment.json及runtime_manifest.json给出配置与80项SHA256。

run.sh由/usr/bin/python3执行app/manage.py；再使用配置的/usr/local/share/pynq-venv/bin/python3启动app/main.py --runtime。实际Python/PYNQ版本未知。app/main.py接入结构化多阶段流水，不沿用V22旧入口冲突结论。

| 动作 | 源码行为 | 本轮是否执行 |
| --- | --- | --- |
| run.sh无参数/deploy | 校验80项runtime负载，检查旧状态与PID/硬件哈希；停止旧进程；条件性加载，设置采集并启动主程序 | 否 |
| run.sh check | 复制硬件至/tmp；加载器处理PYNQ元数据/失效状态；不下载FPGA也会写文件 | 否 |
| deploy冷加载路径 | /lib/firmware写入、xmutil卸载、preload、fpgautil、独立pynq_runtime/overlay.bit与.hwh后登记元数据、采集设置 | 否 |
| stop | SIGTERM轮询最多30秒，检查/dev/video0占用；不会自动强杀占用进程 | 否 |
| rollback | 切换当前/previous目录并进入部署路径 | 否 |
| 本地预检工具 | 只读原件/快照，输出比较结果；不调用上述管理程序 | 已执行 |

V24 deploy没有调用check分支的prepare_check，也不自动完成系统验收；不能照搬V22执行链。即便已有状态满足复用PL条件，deploy仍涉及停启进程和采集设置。仅PS重启不得直接使用V22的restart_ps_only.py；需按V24入口、数据位置、状态/驱动及所有权重新制定方案。

## 数据与流水契约

数据默认在运行目录旁的<runtime-name>.data/，可由WB_DATA_DIR覆盖；runtime_paths对.previous后缀也有处理。全帧请求为<data-dir>/capture_full.request；几何请求为<data-dir>/geometry/capture.request。请求文件是运行行为触发器，本轮未创建。

F1–F3切模式、F4/F5浏览页、F6保存当前模式、F7请求内容重置；手动存页与自动擦除留页分开。自动留页保存Q深度增强图，页上限32，保存在运行内存中。诊断捕获写npy/JSON不能证明历史页可断电保存。

最多3对A/B；调度器在Q完成、呈现/确认后释放A/B。PS工作者持有缩图副本；几何分析2Hz独立于显示。Q使用A＋120×68区域元数据＋旧Canvas，B辅助PS同帧分析。1080p元数据为8160个uint32，即32640字节；Canvas每像素4bit，不能按RGB字节数组描述。

HWH与头文件交叉核对当前Scene指针32位、Restore指针64位拆为两字。CPU架构不决定每个核的地址宽度。运行层超时保留所有权的代码与原候选Skill的池缺陷是不同实现。

## 可复跑的本地检查

在工作区根执行（解释器换成本机已存在的Python，禁止把它替换为板端入口）：

```powershell
python -B tools/reproduce_v24_candidates.py
python -B tools/check_v24_contracts.py
python -B tools/check_v24_migration.py
python -B tools/run_v24_regressions.py
```

上述脚本只向本工作区写报告或临时测试副本。迁移脚本读取明确的本地2025.2产物；不存在时应失败，不创建工程或运行Vivado。check_v24_contracts首次生成冻结配置，后续输入变化时拒绝自动更新预期。新版必须使用新日期/新配置。

环境与安装来源见 [environment.md](environment.md)，板测方案见 [validation_plan.md](validation_plan.md)，迁移静态差异见 [migration_v24_2025_2.md](migration_v24_2025_2.md)。<span style="color:#C00000">【待核验】本说明尚无干净环境安装到冷启动的完整执行记录。</span>
