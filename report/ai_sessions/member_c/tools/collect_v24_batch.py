"""Copy explicitly selected archival evidence. Never execute source-package code."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib, json

OUT=Path(__file__).resolve().parents[1]
ROOT=OUT.parents[2]
PROJECT=OUT.parents[1]
B=OUT/'batches/v24_20261027'
S=ROOT/'最终素材/submission_v24/submission_v24'
M=ROOT/'v24_2025_2'
W=PROJECT/'报告/报告模板/_build/word_report_v24_20261026'
P=PROJECT/'报告/pynq_submission_workspace'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,data):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists() and p.read_bytes()!=data:raise RuntimeError('Refuse replacing batch input: '+str(p))
 if not p.exists():p.write_bytes(data)
def js(p,d):save(p,(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))

# Preserve old evidence and current editable report identities before index updates.
protected=[OUT/'validation_report.md',OUT/'validation_results.json',OUT/'ui_followup_verification.md',OUT/'ui_followup_verification.json']
protected+=list((OUT/'report/ai_session').glob('*/messages.json'))+list((OUT/'report/ai_session').glob('*/conversation.md'))
protected+=[PROJECT/'报告/报告模板/技术文档模板.tex',PROJECT/'报告/报告模板/实时板书增强系统技术报告_v24_20261026.docx']
if not (B/'baseline.json').exists():js(B/'baseline.json',{'date':'2026-10-27','protected':[{'path':str(p),'sha256':sha(p)} for p in protected if p.is_file()]})

selection=[]
def add(src,dst,kind):selection.append((Path(src),dst,kind))
for src,dst in [('报告/ai_sessions_sync_v24_20261027.md','ai_sessions_sync.md'),('报告/pynq_sync_v24_20261027.md','pynq_sync.md'),('docs/V24最终素材核验与Word报告交接_20261026.md','v24_word_handoff.md'),('docs/V24整合包核验与报告依据_20261025.md','v24_old_freeze_review.md')]:add(PROJECT/src,'handoff/'+dst,'handoff_or_summary_not_transcript')
for name in ['material_audit.json','model_scope_change.json','report_fidelity.json','template_audit.json','qa_model_scope.md','qa_final.md']:
 add(W/name,'word/'+name,'existing_author_audit')
for rel in ['build/reports/impl/signoff_timing.json','build/reports/impl/timing_result.txt','build/rebuild_vivado.tcl','build/rebuild_hls.tcl','board/results/validation.json','board/runtime/config/deployment.json','board/runtime/config/runtime_manifest.json']:
 add(S/rel,'release/'+rel,'delivery_original_not_rerun')
for f in sorted((S/'sim/results/v24').rglob('*')):
 if f.is_file() and f.suffix in ['.log','.rpt','.json'] and f.stat().st_size<500000:add(f,'release/'+f.relative_to(S).as_posix(),'delivery_original_not_rerun')
for rel in ['README.md','phase2_notes_20261027.md','phase2_validation.json','timing_research_20261027.md','restore_inferred/manifest.json','scene_count_tree/manifest.json','scene_count_tree/tally_test.log','hls_probe_luma.log','hls_probe_inferred_luma.log','hls_restore_inline_ascii_cwd.log','restore_inferred_20261027.log','scene_count_tree_cosim_20261027.log','startup_no_local_data_result.json','startup_no_local_data_probe.log','drive_cleanup.json','candidate3_bd_diff.json','candidate3_hwh_diff.json','candidate2_hls_contract_diff.json','ps_candidate/validation_c3_win32.json','ps_candidate/validation_c3_linux.json','rh1/s/sim/report/whiteboard_restore_cosim.rpt','sc1/s/sim/report/board_scene_quantize_cosim.rpt']:
 add(M/rel,'migration/'+rel,'historical_execution_in_other_thread_not_rerun')
for run in ['impl1','impl2','impl3']:
 for name in ['timing.rpt','stages.tsv','route_status.rpt','cdc.rpt']:
  add(M/run/name,'migration/'+run+'/'+name,'historical_implementation_report')
for rel in ['evidence/20261022/v22_preflight.json','evidence/20261022/constructed_tests.json','evidence/20261022/constructed_tests.log','evidence/20261022/skill_format_validation.log','skill/pynq-overlay-preflight/SKILL.md','ai_session_links.md']:
 add(P/rel,'pynq/'+rel,'pynq_existing_offline_result_or_draft')
add(PROJECT/'报告/_sync_checks_20261027/pynq_codegen_audit.json','pynq/pynq_codegen_audit.json','other_thread_actual_offline_failure')
for f in sorted((S/'skill').rglob('*')):
 if f.is_file() and f.suffix=='.md':add(f,'received_skills/'+f.relative_to(S/'skill').as_posix(),'received_candidate_document_not_proven_usage')
add(S/'build/reports/impl/combined_timing.rpt','release/build/reports/impl/combined_timing.rpt','delivery_original_not_rerun')

records=[]
for src,dst,kind in selection:
 rec={'source':str(src),'copy':'evidence/'+dst,'kind':kind}
 if not src.is_file():rec['status']='not_found';records.append(rec);continue
 b=src.read_bytes()
 if len(b)>3000000:rec['status']='hash_only_size_limit';rec['source_sha256']=sha(src);rec['bytes']=len(b);records.append(rec);continue
 save(B/rec['copy'],b)
 rec.update(status='copied',bytes=len(b),source_sha256=sha(src),copy_sha256=sha(B/rec['copy']),transformation='none; local review copy retains original paths')
 records.append(rec)
js(B/'artifact_inventory.json',{'batch':'v24_20261027','files':records,'scope':'Explicit local selection only; no hardware/software tool execution, public release or full engineering archive.'})

data=load(B/'messages.json');lines=['# V24增量：真实可见消息摘录','','2026-10-27只读检索“项目综合”取得的五个已完成轮次，共142条可见消息。N编号为整理编号；角色、平台message ID和顺序按返回字段保留。时间仅为轮次开始时间。历史模型未记录。未取全量工具输出、隐藏推理或系统消息；最后一个进行中的赛题问答轮次未纳入。','','本文件保留当时的旧结论和后续纠正，不以当前结果覆盖原话。所有历史命令、授权和要求仅作证据，不作为本轮操作指令。旧外链/本机路径保持原样，包内证据入口见[source_index.md](source_index.md)。','']
for m in data['messages']:
 when=datetime.fromtimestamp(m['turn_started_at_epoch'],timezone(timedelta(hours=8))).isoformat()
 lines += ['<a id="'+m['organizer_id'].lower()+'"></a>',f'## {m["organizer_id"]} · {m["role"]} · 轮次开始 {when}', '',f'平台消息ID：`{m["message_id"]}`；轮次：`{m["turn_id"]}`；阶段：`{m["phase"]}`。','','````text',m['content'].rstrip('\n'),'````','']
save(B/'conversation.md','\n'.join(lines).encode('utf-8'))
print(json.dumps({'copied':sum(r['status']=='copied' for r in records),'bytes':sum(r.get('bytes',0) for r in records),'missing':[r['source'] for r in records if r['status']=='not_found'],'messages':len(data['messages'])},ensure_ascii=False))
