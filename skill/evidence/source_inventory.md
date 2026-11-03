# 来源索引

**2026-10-27增量：当前基线改为V24 slim。下方S01–S16、L01–L03与10/22阅读范围作为历史保留。**

| ID | 来源 | 类型与本轮范围 |
| --- | --- | --- |
| S17 | [同步说明](../../report/ai_sessions/member_c/batches/v24_20261027/evidence/handoff/pynq_sync.md)、[快照](evidence/20261027/handoff/pynq_sync_v24_20261027.md) | 用户指令，全文，含最新phase2 |
| S18 | D:/2026嵌赛/最终素材/submission_v24/submission_v24 | 当前交付；总清单835项核对；runtime81文件快照；build入口确认存在未执行，不声称通读全工程 |
| S19 | D:/2026嵌赛/最终素材/v24_slim_runtime_20261026/v24_slim_runtime_20261026 | 独立运行包80项核验；S的35个Python源码/运行副本核对 |
| S20 | S18/skill，[原件快照](evidence/20261027/source_skill) | 六组40文件含14缓存；四组核心实现和05/06文档审阅/核心问题复现；作者/许可和Session归因未独立核实 |
| S21 | S18/src/pl/ip的三个HLS头文件 | 完整解析，与HWH70物理字独立交叉 |
| S22 | [交接摘要](evidence/20261027/handoff/v24_material_report_handoff_20261026.md)、[原审计](evidence/20261027/handoff/pynq_codegen_audit.json) | 先前核查材料，本轮重现67处错误 |
| S23 | [运行快照](evidence/20261027/runtime_v24) | 全文核对deployment/run.sh/manage/runtime_paths/main/verify_manifest/load_overlay/scene_registers；board/scheduler/content/geometry/scene_stage/archive_ui按调用与上下文审阅 |
| S24 | [迁移资料](evidence/20261027/migration) | README、最新阶段记录、JSON相关字段；两HWH本轮静态对照。构建/仿真和Windows/WSL适配回归为迁移方历史记录，本轮未执行 |
| S25 | S18/board/results和build/reports/impl/signoff_timing.json | 历史板测/时序；保留日期、短窗和未签核限制 |
| L04 | [输入核验](evidence/20261027/input_review.json) | 本轮80/80、35对、总清单分层核验；141输入指纹 |
| L05 | [候选失败复现](evidence/20261027/candidate_failures.json) | 67偏移、头文件0项、DMA mock复用/释放、Overlay调用顺序、性能标签 |
| L06 | [V24预检](evidence/20261027/v24_preflight.json)、[契约回归](evidence/20261027/v24_contract_regression.json) | 独立439/0/8、70字交叉、5负例、输入不变 |
| L07 | [回归运行](evidence/20261027/regression_run.json) | 31项工具＋旧23项复跑；命令/代码/输入指纹与原始日志 |
| L08 | [迁移接口](evidence/20261027/migration_interface_review.json) | 两分支26范围、选定时钟/复位/中断/视频端口及参数/寄存器；NOT_CHECKED保留 |

旧冻结v24_final_freeze_20261024的V23身份/7哈希冲突仅来自先前摘要，本轮未重新全包审计，不用于否定S/R新包。复制不等于通读，哈希不证明构建真实性。

---

接收/核查日期：2026-10-22，Asia/Taipei。项目根目录 `D:\2026嵌赛\实时板书增强系统`。以下“阅读”指本轮实际范围；字节哈希核对不等于通读源码。

| ID | 来源 | 类型、版本 | 本轮范围与用途 |
| --- | --- | --- | --- |
| S01 | [启动提示词](../../report/attachments/history/pynq_new_chat_prompt_20261022_831e9bfd.md) | 用户指定任务 | 全文；操作边界与持续维护规则 |
| S02 | [准备指南](../../report/attachments/history/pynq_submission_preparation_20261022_606b1a21.md) | 先前整理摘要 | 全文；作为定位入口，不代替源码/原始对话 |
| S03 | [AMD赛题.pdf](../../../赛题信息/AMD赛题.pdf) | 本地赛题文件 | PDF 文件页22–25/印刷页19–22，提取阅读3.3；重点3.3.2和3.3.5。非联网核对最新赛事修订 |
| S04 | [V22架构更新](../../report/ai_sessions/member_c/sources/background/v22_review.md) | 先前源码核查摘要 | 全文；V22硬件＋PS v2 r4架构、旧结论边界 |
| S05 | [V22核验JSON](../../report/ai_sessions/member_c/evidence/team_v22/local_prior_audit.json) | 先前本地测试记录 | 全文结构化记录；647/174项、工程内层哈希等为先前结果，本轮未全量复跑 |
| S06 | [V23更新](../../report/ai_sessions/member_c/sources/background/v23_scope.md) | 用户转述现场反馈及计划 | 全文；V23 PL已更新/主要问题解决为反馈，V24颜色改进为计划 |
| S07 | [V22原始ZIP](../../工作空间/A和B发送的资料/V22/v22_ps_runtime_v2_r4_20261020.zip) | 2026-10-20交付 | ZIP目录、允许列表33个条目读取（含MANIFEST）；外层重算哈希；未展开完整工程/内层板包 |
| S08 | [外置HANDOFF](<../../工作空间/A和B发送的资料/V22/HANDOFF (1).md>)、[CHANGELOG](../../report/attachments/history/changelog_1a01fc17.md) | 交付说明 | 全文；与 `docs/HANDOFF.md`、`docs/CHANGELOG.md` 字节一致 |
| S09 | S07 的发布身份与清单 | 原始JSON | release_identity 全文；MANIFEST、bundle、system_manifest解析并核对选定条目，未验证全部647项 |
| S10 | S07 的启动工具 | 已核验源码 | 全文：`run.sh`、`kv260_board_run.py`、`kv260_overlay.py`、`verify_runtime.py`、`verify_manifest.py`、`ensure_kernel.py`、`tools/restart_ps_only.py`、`tools/verify_release.py`、deployment.json |
| S11 | S07 的运行层 | 已核验源码 | 全文：`run_ps_runtime_v2.py`（81字节入口已确认转入v2）、`ps_runtime_v2/__main__.py`、`scene_stage.py`、`hardware_abi.py`；`board.py`读取前90行及PYNQ/缓冲/释放检索；`baseline_stages.py`、`shared_scanout.py`、`whiteboard_ip.py`只检索相关调用，未通读全部 |
| S12 | S07 的硬件文件 | 二进制与HWH | bit/bit.bin/HWH/DTBO、两个ko逐字节哈希；独立XML解析HWH三IP、70寄存器和控制字段/地址。未解码bit器件或DTBO绑定，未加载驱动 |
| S13 | S07 的 `evidence/VALIDATION.md`、`r4_validation.json` | 交付方历史测试 | 全文；PC/ARM、短窗运行和未验收范围；`board_identity.json`、`hardware_export.json`仅复制/哈希，未展开分析全部内容 |
| S14 | [AI指南](../../report/attachments/history/ai_session_preparation_20261022_4763338b.md)、[模板](../../report/attachments/history/ai_session_case_template_18cd4bbc.md)、[索引](../../report/attachments/history/ai_session_material_index_20261022_53c6b163.md) | 准备文件 | 阅读全文；不是原始AI session导出。本轮不读取其他聊天存储 |
| S15 | [PYNQ Overlay官方文档](https://pynq.readthedocs.io/en/latest/overlay_design_methodology/overlay_design.html)、[allocate官方文档](https://pynq.readthedocs.io/en/latest/pynq_libraries/allocate.html) | 官方概念依据，2026-10-22访问 | 配对命名/HWH、地址与缓存同步语义；latest不代表本板软件版本 |
| S16 | 本对话2026-10-22用户补充：AI_Sessions已有独立对话推进 | 用户直接明确的职责分工 | 本工作区只维护工程证据与案例索引关联，不重复索取原文；未读取另一对话，不判断其完成状态 |
| L01 | [collection.json](evidence/20261022/collection.json)、[source_review.json](evidence/20261022/source_review.json) | 本轮本地验证 | 完整选定条目哈希、源文档指纹、清单对照、入口冲突AST复核 |
| L02 | [v22_preflight.json](evidence/20261022/v22_preflight.json) | 本轮离线测试 | 429 pass/0 fail/7 not_checked；范围只到配置的9文件与3IP |
| L03 | [constructed_tests.json](evidence/20261022/constructed_tests.json)、[日志](evidence/20261022/constructed_tests.log) | 本轮构造测试 | 23项；不代表真实历史故障或跨板实测 |

S07 身份：大小 `1514967469` 字节，SHA256 `0f61f9865931e94cd7571236a4ac45a3dbe03ba6cfdca72bb41b3e8bd5a78eed`。本轮与S05一致；外部发布方 `.sha256` 仍缺，不能当作独立真实性认证。

S03 SHA256：`c6ad82acd4f7bdcd13bd412e232ed85d05f2a87dd5e2cdd04f9d219f88b569fc`。[局部文本提取](evidence/20261022/competition_section_3_3.txt)只供本地核对，不是修改后的赛题。

S07 包内根目录为 `v22_ps_runtime_v2_r4_20261020/`；本工作区副本省略该一级目录，余下路径不变。完整条目路径见 [archive_entries.json](evidence/20261022/archive_entries.json)。源文件复制不表示其内容已逐行审阅。

禁止素材 `work/logs/work.steps.log` 未读取、未复制；未展开可能含历史日志的 `engineering/server_project.tar.gz`。没有读取无关用户目录、整份环境变量或凭据配置。

后续新增来源分配新ID，记录接收日、资料生成日、提供者角色、版本/哈希、资料类型、实际阅读范围。反馈与源码冲突时并列记录，不直接提升状态。
