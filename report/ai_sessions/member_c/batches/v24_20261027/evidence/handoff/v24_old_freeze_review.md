# V24 整合包核验与报告依据

日期：2026-10-25；本次为单代理本地只读核验与文档更新。用户提供 `D:\QQ文件下载\v24_final_freeze_20261024.zip`，反馈此版 PL、PS 基本运行良好，并确认暂时没有额外的最终时序报告、完整回归源码或原始日志。

没有连接服务器／KV260、加载 Overlay、运行工程脚本、复跑测试、训练模型、综合或修改归档。本次所有“通过／失败”必须注明是文件一致性、原始报告还是交付方汇总。

## 1. 归档身份及核验范围

- 大小：1,268,374,010 byte。
- SHA256：`9f2e27f5099ca56a898a1d984c7b4585acd3a40d16d70012204ab9fcf7adc489`。
- ZIP 文件成员 4,107 个；外层发布清单列 4,106 项，排除清单自身。
- 4,106 项大小与 SHA256 全匹配；未发现缺项、未列文件或重复成员名。
- 12 份 `source/ps/ps_runtime_v2/` Python 文件与运行副本一致；`run_tests.py`、`scene_tracking.py` 另有一致副本。`prepare_runtime.py` 不存在同名运行副本，不将其算作不匹配。
- 六份顶层硬件／驱动文件与 runtime 副本一致。
- 哈希一致只证明这些内容与当前清单相符，不能证明来源认证、程序可启动或硬件签核。

机器可读结果、清单及部分原文存于 `报告/报告模板/_build/v24_review_20261025/`：`archive_audit.json`、`archive_inventory.json`、`inner_hw_inventory.json`、`runtime_manifest_checks.json`、`selected/`。这不是正式提交数据集；敏感日志未读取或复制。

## 2. 当前实现与旧背景的区别

| 项目 | V24 源码依据 | 可写入报告的结论 |
|---|---|---|
| 主入口 | `board/runtime/deployment.json`；`capture_runtime.py:15–103`；`ps_runtime_v2/__main__.py` | 捕获适配器包装当前 v2 主循环，保留多阶段调度；不代表直接兼容旧包 |
| 数据流 | `ps_runtime_v2/board.py:212–260` | Rectify 得 A，Restore 得 B；内容服务 prepare A／refine A+B；Q 仍读 A＋元数据＋Canvas |
| 调度与几何 | `scheduler.py:28–64`；`geometry.py`；`board.py:169–182` | 默认最多三对 A/B、80 ms 内容等待预算；几何 2 Hz、原图角点位移门槛 2 px。6 px 是板面内裁边距，不能混写成运动发布门槛 |
| 遮挡 | `geometry.py` 中候选／锚点／运动／OCCLUDED 分支 | 抑制不可靠边缘候选，仍允许可靠锚点或运动证据更新；不是“有人便绝对锁死矩阵” |
| 曝光与内容 | `sensor.py`、`scene_tracking.py` | 保留持续 AE；增加 OpenCV 数组差分及中性阴影筛选。不是已接入手势神经网络，也不直接证明 NEON 加速倍数 |
| 热插拔 | `board/runtime/scene_input.py` | 约 1 s 周期重扫，按能力枚举键盘及相对指针设备；现场全部场景通过仍缺日志 |
| 翻页笔 | `scene_input.py` 的 KEYS/NAV | 未显式映射 PageUp 104／PageDown 109；实际笔若发送其他已支持键可能可用，需设备实测 |
| 自动存页 | `board.py:121,272–291`；`content.py:10–144` | 已接入 Q 完成路径；最多 2 Hz 检查；主入口 loss_fraction=.15，类默认 .30 与旧注释不能覆盖实际参数 |
| 保存语义 | `content.py:93–99`；`archive_ui.py` 的 save_snapshot／pages | 自动保存擦除前完整深度增强页，手动 F6 保存当前模式；页面进内存列表，未见该路径落盘 |
| 找板提示 | `board.py:149–166` | 当前入口直接发 search/confirming；方向资源存在不等于逐方向逻辑已联调 |
| 模型 | 当前 v2 主循环与服务实例 | 未见神经推理和手势状态机实例化；本报告离线模型数值明确取自 10/19 资料，不代表冻结了其他窗口的后续训练进度 |

自动存页阈值含义：ROI 元数据中可见且未阻挡占比至少 97%、无初始化块；每 4 像素采样非白笔迹，容许邻域偏移；笔迹损失比例到 5% 后冻结已有页面，到主入口设定的 15%、满足最少样本数并连续两次有效确认后保存。15% 是保留笔迹样本的损失比例，**不是 15% 黑板面积**。新书写／部分擦写有重新准备逻辑。曝光代次改变不单独重置此存页比较，坐标身份前两项改变才重置；不要沿用类注释中“任何 sensor epoch 都使比较无效”的笼统描述。

## 3. 硬件与时序

主要来源：顶层 `hardware/reports/combined_utilization.rpt`、`combined_timing.rpt`、`clocks_clock_fixed.rpt`，并核对内层 `engineering/wb_fusion_v24_hw_200mhz.tar.gz`。

| 资源 | 已用／总量 | 占比 |
|---|---:|---:|
| LUT | 84,901 / 117,120 | 72.49% |
| FF | 92,778 / 234,240 | 39.61% |
| CLB | 14,498 / 14,640 | 99.03% |
| BRAM Tile | 86.5 / 144 | 60.07% |
| URAM | 49 / 64 | 76.56% |
| DSP | 1,110 / 1,248 | 88.94% |

主要处理时钟 5 ns／200 MHz，仍含 clk_pl_0 100 MHz 等其他时钟域。LUT 百分比按原始数量重算，未采用 export JSON 的 72.40%。CLB 仅余 142 个站点，不以 LUT 未满推断布局宽裕。

原始 V24 报告：WNS **−1.588 ns**，TNS **−2182.223 ns**，setup 失败端点 **8,069**；WHS **+0.010 ns**，hold 失败端点 0，明确 `Timing constraints are not met`。未约束内部端点及无时钟端点统计为 0，但有 `no_input_delay (4)`、`no_output_delay (2)`，仍需解释外部端口约束或例外。不能据此直接认定所有接口均已正确约束。

内层签核 `FAIL_EXPERIMENTAL` 与负 WNS 一致，但端点摘要为 100，与完整报告 8,069 不同；保留差异，报告采用原始完整统计。内层 28 文件主要是硬件导出与报告，不是完整 XPR 快照。顶层 BD Tcl 检查三个自定义 HLS IP 和三个 RTL 模块，未见同脚本先设置 IP 仓库或添加 RTL，因此需补齐调用它的完整构建流程。

`board/runtime/evidence/hardware/` 中 PASS／WNS +0.559 ns，及 LUT 85,202、DSP 289 等属于 V23 R6 证据。`system_manifest.json` candidate 为 `20261021-pl-r6-resource-fusion-v23`。不能把这些旧数据作为 V24 的新报告。

## 4. 运行清单冲突

186 项内层哈希核验有七项不一致，名单详见提交清单。当前 `BoardIO.__init__` 第 72／82 行导入并调用 `verify_package`；`capture_runtime.py` 的派生类调用 `super().__init__`，没有绕过检查。

`verify_manifest.py` 仍要求 candidate 后缀 `-v23`、ABI 及旧签核条件，并逐文件校验 `board_sha256`。哈希不符会抛出 `Artifact/runtime checksum mismatch`。因此，按当前静态证据，该 ZIP 不能直接视为“在新环境按说明即可运行”的已验收发布版；本轮未为证实此点执行板端启动。现场正常运行可能使用另一个目录状态，需要对齐后判断，不擅自推断现场使用了什么补丁。

## 5. 测试与遥测证据强度

`validation/` 只有两份 JSON：

- `test_summary.json` 声称主机／ARM 各 60 项回归和 4 项修复测试通过，没有测试名单、完整命令或原始输出。
- `live_board_telemetry_pid32023.json` 记录 2026-10-24 的显示 13.0 FPS、内容耗时 22.3 ms、预算 80 ms、累计更新 32,165、fault/bad_frames 均 0、auto_saved_pages=1。它是快照，不是连续时序日志；PID 和路径为历史记录，不能据此控制当前进程。

`run_tests.py` 对源根目录下 `legacy_tests/` 和 `tests/` 做发现；两者不在对应位置。已附 `ps_runtime_v2/tests/` 以及 11 个 `tb/` 文件不等价于完整宣称测试集；部分 tb 仍导入旧 `software/` 路径，当前绑定未闭合。源码存在不等于本轮测试通过。

README 中帧率区间、耗时优化及加速倍数缺同条件原始日志；例如 50.3／1.76 与所写倍数并不吻合。不把这些宣传性汇总作为报告的定量对照。零故障快照不表示长期零故障，单次自动页计数也不表示准确保存或断电可恢复。

## 6. 文档变更及后续规则

- 原位更新 `报告/报告模板/技术文档模板.tex`：基线改为 V24；新增自动存页、热插拔和真实资源；明确负时序、清单冲突、测试缺项、遥测范围和模型未接入。
- 保留原图页眉、五部分结构、字体设置；不增加版本表或修订表。V22 原文备份为 `_build/技术文档模板_V22更新前保留_20261025.tex`。
- 新增 `报告/v24_submission_checklist_20261025.md` 和空白 `v24_test_case_template.json`；模板标为 NOT_RUN，不能当测试证据。
- 最终 PDF 应由当前 LaTeX 编译／导出，确认页码、图片、表格和无缺字后再上传；同目录旧 PDF 不自动视为新版。
- 后续若收到新位流／报告／实测，先核对哈希和版本，再逐项更新结论；保留本次失败证据，不用旧 PASS 文件替换。
