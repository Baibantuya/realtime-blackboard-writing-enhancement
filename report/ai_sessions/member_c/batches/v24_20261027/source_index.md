# V24批次来源索引

2026-10-27。输入仅在明确项目/交接路径与只读会话接口内定位；没有扫描应用数据库或读取work/logs/work.steps.log。

## 消息和工具

“项目综合”五轮原文共142条，平台ID见[messages.json](messages.json)与[可读摘录](conversation.md)。起始请求/用户修改为N001、N012、N019、N024、N028、N058；其余N编号按返回顺序。历史模型未记录，时间仅为轮次开始时间。

[命令元数据](tools.json)保存93条选定command ID、命令、状态及退出码，没有全量stdout；[历史分工](readme.md)仅引用授权/职责和活动字段。原始日志与工程副本如下，不将交接摘要充当当时回答。

## 文件证据

状态copied表示已读取字节并复制，语义审阅范围限于各案例实际引用的字段/段落，不等于全文工程审查。完整来源路径、字节数及双SHA见[清单](artifact_inventory.json)。原Word只做身份核对，未复制编辑稿。

| 包内副本 | 类型/来源性质 | SHA256前12位 |
| --- | --- | --- |
| [evidence/handoff/ai_sessions_sync.md](evidence/handoff/ai_sessions_sync.md) | handoff_or_summary_not_transcript | 26079bda48f2 |
| [evidence/handoff/pynq_sync.md](evidence/handoff/pynq_sync.md) | handoff_or_summary_not_transcript | f38eec50b5b0 |
| [evidence/handoff/v24_word_handoff.md](evidence/handoff/v24_word_handoff.md) | handoff_or_summary_not_transcript | ff0755608016 |
| [evidence/handoff/v24_old_freeze_review.md](evidence/handoff/v24_old_freeze_review.md) | handoff_or_summary_not_transcript | 42956a6c80cc |
| [evidence/word/material_audit.json](evidence/word/material_audit.json) | existing_author_audit | 56bbc0c78de1 |
| [evidence/word/model_scope_change.json](evidence/word/model_scope_change.json) | existing_author_audit | dc1f76c43ad1 |
| [evidence/word/report_fidelity.json](evidence/word/report_fidelity.json) | existing_author_audit | ce168aab3619 |
| [evidence/word/template_audit.json](evidence/word/template_audit.json) | existing_author_audit | ca48a7acbc82 |
| [evidence/word/qa_model_scope.md](evidence/word/qa_model_scope.md) | existing_author_audit | 496a49d5c72e |
| [evidence/word/qa_final.md](evidence/word/qa_final.md) | existing_author_audit | e8a18afbfce3 |
| [evidence/release/build/reports/impl/signoff_timing.json](evidence/release/build/reports/impl/signoff_timing.json) | delivery_original_not_rerun | d6a7f8a1256b |
| [evidence/release/build/reports/impl/timing_result.txt](evidence/release/build/reports/impl/timing_result.txt) | delivery_original_not_rerun | fd6771dd6d18 |
| [evidence/release/build/rebuild_vivado.tcl](evidence/release/build/rebuild_vivado.tcl) | delivery_original_not_rerun | d18a35eb7d3a |
| [evidence/release/build/rebuild_hls.tcl](evidence/release/build/rebuild_hls.tcl) | delivery_original_not_rerun | d675537c05a2 |
| [evidence/release/board/results/validation.json](evidence/release/board/results/validation.json) | delivery_original_not_rerun | 80a531380c69 |
| [evidence/release/board/runtime/config/deployment.json](evidence/release/board/runtime/config/deployment.json) | delivery_original_not_rerun | 3532bd3e7eca |
| [evidence/release/board/runtime/config/runtime_manifest.json](evidence/release/board/runtime/config/runtime_manifest.json) | delivery_original_not_rerun | 4096087e94f6 |
| [evidence/release/sim/results/v24/board_scene_quantize_cosim.rpt](evidence/release/sim/results/v24/board_scene_quantize_cosim.rpt) | delivery_original_not_rerun | 21cd75ff514f |
| [evidence/release/sim/results/v24/board_scene_quantize_csim.log](evidence/release/sim/results/v24/board_scene_quantize_csim.log) | delivery_original_not_rerun | f0418e5eeed1 |
| [evidence/release/sim/results/v24/recorded_vectors_check_20261026.json](evidence/release/sim/results/v24/recorded_vectors_check_20261026.json) | delivery_original_not_rerun | a2b3768b51ec |
| [evidence/release/sim/results/v24/whiteboard_restore_cosim.rpt](evidence/release/sim/results/v24/whiteboard_restore_cosim.rpt) | delivery_original_not_rerun | 412ca10e97a6 |
| [evidence/release/sim/results/v24/whiteboard_restore_csim.log](evidence/release/sim/results/v24/whiteboard_restore_csim.log) | delivery_original_not_rerun | 4ba621d01290 |
| [evidence/migration/README.md](evidence/migration/readme.md) | historical_execution_in_other_thread_not_rerun | 161dc533cbe4 |
| [evidence/migration/phase2_notes_20261027.md](evidence/migration/phase2_notes_20261027.md) | historical_execution_in_other_thread_not_rerun | 273612ebbfd7 |
| [evidence/migration/phase2_validation.json](evidence/migration/phase2_validation.json) | historical_execution_in_other_thread_not_rerun | 29cfa6b0fb88 |
| [evidence/migration/timing_research_20261027.md](evidence/migration/timing_research_20261027.md) | historical_execution_in_other_thread_not_rerun | 0bedcf19861f |
| [evidence/migration/restore_inferred/manifest.json](evidence/migration/restore_inferred/manifest.json) | historical_execution_in_other_thread_not_rerun | bdb2771e93f4 |
| [evidence/migration/scene_count_tree/manifest.json](evidence/migration/scene_count_tree/manifest.json) | historical_execution_in_other_thread_not_rerun | 842a83d8bae3 |
| [evidence/migration/scene_count_tree/tally_test.log](evidence/migration/scene_count_tree/tally_test.log) | historical_execution_in_other_thread_not_rerun | d8e946319fdc |
| [evidence/migration/hls_probe_luma.log](evidence/migration/hls_probe_luma.log) | historical_execution_in_other_thread_not_rerun | e766e1d83802 |
| [evidence/migration/hls_probe_inferred_luma.log](evidence/migration/hls_probe_inferred_luma.log) | historical_execution_in_other_thread_not_rerun | 04aeab4c8c68 |
| [evidence/migration/hls_restore_inline_ascii_cwd.log](evidence/migration/hls_restore_inline_ascii_cwd.log) | historical_execution_in_other_thread_not_rerun | 0cf5c668eea8 |
| [evidence/migration/restore_inferred_20261027.log](evidence/migration/restore_inferred_20261027.log) | historical_execution_in_other_thread_not_rerun | 3431b12a69b7 |
| [evidence/migration/scene_count_tree_cosim_20261027.log](evidence/migration/scene_count_tree_cosim_20261027.log) | historical_execution_in_other_thread_not_rerun | 9f6b9310d8b4 |
| [evidence/migration/startup_no_local_data_result.json](evidence/migration/startup_no_local_data_result.json) | historical_execution_in_other_thread_not_rerun | e825edbfdb4d |
| [evidence/migration/startup_no_local_data_probe.log](evidence/migration/startup_no_local_data_probe.log) | historical_execution_in_other_thread_not_rerun | 955828d04e77 |
| [evidence/migration/drive_cleanup.json](evidence/migration/drive_cleanup.json) | historical_execution_in_other_thread_not_rerun | 65bc4d604369 |
| [evidence/migration/candidate3_bd_diff.json](evidence/migration/candidate3_bd_diff.json) | historical_execution_in_other_thread_not_rerun | 4076aca53e8d |
| [evidence/migration/candidate3_hwh_diff.json](evidence/migration/candidate3_hwh_diff.json) | historical_execution_in_other_thread_not_rerun | dc5374899512 |
| [evidence/migration/candidate2_hls_contract_diff.json](evidence/migration/candidate2_hls_contract_diff.json) | historical_execution_in_other_thread_not_rerun | 430aed57fb59 |
| [evidence/migration/ps_candidate/validation_c3_win32.json](evidence/migration/ps_candidate/validation_c3_win32.json) | historical_execution_in_other_thread_not_rerun | 569c7beb0916 |
| [evidence/migration/ps_candidate/validation_c3_linux.json](evidence/migration/ps_candidate/validation_c3_linux.json) | historical_execution_in_other_thread_not_rerun | 18228540b7d4 |
| [evidence/migration/rh1/s/sim/report/whiteboard_restore_cosim.rpt](evidence/migration/rh1/s/sim/report/whiteboard_restore_cosim.rpt) | historical_execution_in_other_thread_not_rerun | 8551899d38da |
| [evidence/migration/sc1/s/sim/report/board_scene_quantize_cosim.rpt](evidence/migration/sc1/s/sim/report/board_scene_quantize_cosim.rpt) | historical_execution_in_other_thread_not_rerun | 2763b845e26a |
| [evidence/migration/impl1/timing.rpt](evidence/migration/impl1/timing.rpt) | historical_implementation_report | 038d38907a0b |
| [evidence/migration/impl1/stages.tsv](evidence/migration/impl1/stages.tsv) | historical_implementation_report | b71fcdf9f07b |
| [evidence/migration/impl1/route_status.rpt](evidence/migration/impl1/route_status.rpt) | historical_implementation_report | 65e768c83373 |
| [evidence/migration/impl1/cdc.rpt](evidence/migration/impl1/cdc.rpt) | historical_implementation_report | 204a17da228b |
| [evidence/migration/impl2/timing.rpt](evidence/migration/impl2/timing.rpt) | historical_implementation_report | 207cfa7b6dbb |
| [evidence/migration/impl2/stages.tsv](evidence/migration/impl2/stages.tsv) | historical_implementation_report | 87fdd25aaa74 |
| [evidence/migration/impl2/route_status.rpt](evidence/migration/impl2/route_status.rpt) | historical_implementation_report | 0ab98866719e |
| [evidence/migration/impl2/cdc.rpt](evidence/migration/impl2/cdc.rpt) | historical_implementation_report | 39dfd4fd3046 |
| [evidence/migration/impl3/timing.rpt](evidence/migration/impl3/timing.rpt) | historical_implementation_report | fd8e5bba5a84 |
| [evidence/migration/impl3/stages.tsv](evidence/migration/impl3/stages.tsv) | historical_implementation_report | b463fd23409c |
| [evidence/migration/impl3/route_status.rpt](evidence/migration/impl3/route_status.rpt) | historical_implementation_report | 4e01587e51bf |
| [evidence/migration/impl3/cdc.rpt](evidence/migration/impl3/cdc.rpt) | historical_implementation_report | 993a7a68ac2a |
| [evidence/pynq/evidence/20261022/v22_preflight.json](evidence/pynq/evidence/20261022/v22_preflight.json) | pynq_existing_offline_result_or_draft | 5bd8ee9f228e |
| [evidence/pynq/evidence/20261022/constructed_tests.json](evidence/pynq/evidence/20261022/constructed_tests.json) | pynq_existing_offline_result_or_draft | f23a1d3623f3 |
| [evidence/pynq/evidence/20261022/constructed_tests.log](evidence/pynq/evidence/20261022/constructed_tests.log) | pynq_existing_offline_result_or_draft | af06a41f8ee3 |
| [evidence/pynq/evidence/20261022/skill_format_validation.log](evidence/pynq/evidence/20261022/skill_format_validation.log) | pynq_existing_offline_result_or_draft | 8c5794b97e8c |
| [evidence/pynq/skill/pynq-overlay-preflight/SKILL.md](evidence/pynq/skill/pynq-overlay-preflight/skill.md) | pynq_existing_offline_result_or_draft | ac6eb64ce6b1 |
| [evidence/pynq/ai_session_links.md](evidence/pynq/ai_session_links.md) | pynq_existing_offline_result_or_draft | 5dd232d48821 |
| [evidence/pynq/pynq_codegen_audit.json](evidence/pynq/pynq_codegen_audit.json) | other_thread_actual_offline_failure | cf093b7d4fd7 |
| [evidence/received_skills/01_overlay_manager/README.md](evidence/received_skills/01_overlay_manager/readme.md) | received_candidate_document_not_proven_usage | c10195ab77c7 |
| [evidence/received_skills/02_dma_buffer_guard/README.md](evidence/received_skills/02_dma_buffer_guard/readme.md) | received_candidate_document_not_proven_usage | 4b58e9ef0062 |
| [evidence/received_skills/03_contract_codegen/README.md](evidence/received_skills/03_contract_codegen/readme.md) | received_candidate_document_not_proven_usage | 5d37fcfc76f1 |
| [evidence/received_skills/04_golden_benchmark/README.md](evidence/received_skills/04_golden_benchmark/readme.md) | received_candidate_document_not_proven_usage | eded6556fdc0 |
| [evidence/received_skills/05_troubleshooting/TROUBLESHOOTING.md](evidence/received_skills/05_troubleshooting/troubleshooting.md) | received_candidate_document_not_proven_usage | d3c21a1a7987 |
| [evidence/received_skills/06_prompt_workflows/01_algorithmic_hardware_partition.md](evidence/received_skills/06_prompt_workflows/01_algorithmic_hardware_partition.md) | received_candidate_document_not_proven_usage | 4756211e3dc5 |
| [evidence/received_skills/06_prompt_workflows/02_hls_interface_optimization.md](evidence/received_skills/06_prompt_workflows/02_hls_interface_optimization.md) | received_candidate_document_not_proven_usage | 36c5a3dec912 |
| [evidence/received_skills/06_prompt_workflows/03_arm_cpu_bottleneck_audit.md](evidence/received_skills/06_prompt_workflows/03_arm_cpu_bottleneck_audit.md) | received_candidate_document_not_proven_usage | 4e7de25aa9b6 |
| [evidence/received_skills/06_prompt_workflows/README.md](evidence/received_skills/06_prompt_workflows/readme.md) | received_candidate_document_not_proven_usage | 7171f2454df5 |
| [evidence/received_skills/README.md](evidence/received_skills/readme.md) | received_candidate_document_not_proven_usage | 0015f3cf76b4 |
| [evidence/release/build/reports/impl/combined_timing.rpt](evidence/release/build/reports/impl/combined_timing.rpt) | delivery_original_not_rerun | 248d5e025bed |

## 不公开和未覆盖范围

原文/原始日志保留了个人机器路径、W:历史映射和外部引用，当前包是本地审阅副本，没有完成公开匿名审查。旧链接不作为离线入口。未复制整个源码、测试数据、位流、DCP、厂商安装或私有UTF-8程序。

10/23原报告和消息的保护哈希见[baseline.json](baseline.json)；本批次核查见[validation.md](validation.md)。旧检查器不用于覆盖旧回执。
