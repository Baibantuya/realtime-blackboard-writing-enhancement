"""Validate the 2026-10-27 archival batch without running engineering code."""
from pathlib import Path
import hashlib,json,re,sys
from urllib.parse import unquote

OUT=Path(__file__).resolve().parents[1]
B=OUT/'batches/v24_20261027'
def load(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
checks=[]
def add(name,passed,**data):checks.append(dict(check=name,passed=bool(passed),**data))

inventory=load(B/'artifact_inventory.json')['files']
errs=[r['copy'] for r in inventory if r['status']!='copied' or sha(B/r['copy'])!=r.get('copy_sha256')]
add('copied_file_identity',not errs and len(inventory)==74,count=len(inventory),errors=errs)
changed=[r['source'] for r in inventory if sha(Path(r['source']))!=r['source_sha256']]
add('selected_sources_still_match_read_snapshot',not changed,count=len(inventory),changed=changed,
    limitation='Other active tasks may later change source documents; copies retain this batch identity')
baseline=load(B/'baseline.json')['protected']
errs=[r['path'] for r in baseline if sha(Path(r['path']))!=r['sha256']]
add('old_messages_receipts_word_latex_preserved',not errs,count=len(baseline),errors=errs)

new=load(B/'messages.json')['messages'];old=[]
for f in (OUT/'report/ai_session').glob('*/messages.json'):old+=load(f)
ni=[m['message_id'] for m in new];oi=[m['message_id'] for m in old]
nt={m['turn_id'] for m in new};ot={m['turn_id'] for m in old}
add('platform_id_deduplication',len(ni)==len(set(ni)) and not set(ni).intersection(oi) and not nt.intersection(ot),
    old_messages=len(old),new_messages=len(new),combined_unique_messages=len(set(ni+oi)),
    old_turns=len(ot),new_turns=len(nt),combined_unique_turns=len(nt|ot),
    limitation='Selected visible turns only; A/B overlap uses one message record')
transcript=(B/'conversation.md').read_text('utf-8')
errs=[m['organizer_id'] for m in new if m['content'].rstrip('\n') not in transcript or m['message_id'] not in transcript
      or m['role'] not in ['user','assistant'] or m['phase'] not in [None,'commentary','final_answer'] or m['turn_status']!='completed']
add('visible_text_mapping',not errs,count=len(new),errors=errs)
raw=load(B/'tools.json');cmds=raw['commands'];events=raw['coordination']
add('selected_command_metadata',len({x['command_id'] for x in cmds})==len(cmds) and all(x['turn_id'] in nt and x['output_status'].startswith('NOT_REQUESTED') for x in cmds),
    count=len(cmds),output_retrieval='Not requested; command wrapper exit status is not child build signoff')
add('historical_limited_delegation_provenance',len([e for e in events if e['kind']=='started'])==3
    and any(m['organizer_id']=='N037' and m['role']=='user' and '三份补充材料' in m['content'] for m in new),
    activity_records=len(events),started_agents=3,scope='Historical material review only; no delegation in this archival task')

phase=load(B/'evidence/migration/phase2_validation.json')
def timing(path):
 s=path.read_text('utf-8-sig');part=s[s.index('WNS(ns)'):]
 row=next(l for l in part.splitlines()[1:] if re.match(r'^\s+-?\d+\.\d+\s+-?\d+\.\d+\s+\d+',l))
 v=row.split();return {'WNS_ns':float(v[0]),'TNS_ns':float(v[1]),'setup_failing_endpoints':int(v[2]),'hold_failing_endpoints':int(v[6])}
rows=[];errs=[]
for run in ['impl1','impl2','impl3']:
 f=B/'evidence/migration'/run/'timing.rpt';actual=timing(f);expected=phase['implementations'][run]['post_route']
 if any(actual[k]!=expected[k] for k in actual) or sha(f)!=expected['sha256']:errs.append(run)
 rows.append({'run':run,**actual})
add('migration_raw_timing_reports',not errs,count=3,rows=rows,errors=errs,
    engineering_status='All three have negative setup slack; archival checks do not make timing pass')
v24=timing(B/'evidence/release/build/reports/impl/combined_timing.rpt')
small=load(B/'evidence/release/build/reports/impl/signoff_timing.json')
case=(B/'case_a_release.md').read_text('utf-8')
add('v24_summary_disagreement_recorded',v24['setup_failing_endpoints']==8069 and small['setup_failing_endpoints']==100 and '100' in case and '8069' in case,
    full_report=v24,summary_setup_count=small['setup_failing_endpoints'],status='DISAGREEMENT_PENDING_SOURCE_OWNER_REVIEW')

matched=[];errors=[]
for rec in inventory:
 if not rec['copy'].startswith('evidence/migration/'):continue
 key=rec['copy'].removeprefix('evidence/migration/')
 found=next((v for k,v in phase['artifacts'].items() if k.replace('\\','/')==key),None)
 if found and found.get('sha256'):
  matched.append(key)
  if rec['source_sha256']!=found['sha256']:errors.append(key)
add('migration_prior_manifest_selected_hashes',not errors and bool(matched),count=len(matched),errors=errors)
word=load(B/'evidence/word/model_scope_change.json')
add('word_scope_revision_identity',sha(Path(word['report']))==word['after_sha256'],current_matches_historical_after=True,
    limitation='Identity comparison only; no DOCX edits or new page rendering')
pynq=load(B/'evidence/pynq/evidence/20261022/v22_preflight.json')
status={}
for c in pynq['checks']:status[c['status']]=status.get(c['status'],0)+1
tests=load(B/'evidence/pynq/evidence/20261022/constructed_tests.json')
audit=load(B/'evidence/pynq/pynq_codegen_audit.json')
add('skill_receipt_scope',status=={'pass':429,'not_checked':7} and tests['tests_run']==23 and tests['successful'] and audit['total_register_count']==70 and audit['total_offset_mismatch_count']==67,
    v22_check_status=status,constructed_tests=23,codegen_checked=70,codegen_mismatches=67,
    limitation='Existing receipts read, not rerun; current S candidates are separate from V22 preflight and the live PS driver')

# Publish a source index with all copied artifact identities; original source links
# inside raw copies and transcripts remain historical data, not package navigation.
lines=['# V24批次来源索引','','2026-10-27。输入仅在明确项目/交接路径与只读会话接口内定位；没有扫描应用数据库或读取work/logs/work.steps.log。','',
       '## 消息和工具','','“项目综合”五轮原文共142条，平台ID见[messages.json](messages.json)与[可读摘录](conversation.md)。起始请求/用户修改为N001、N012、N019、N024、N028、N058；其余N编号按返回顺序。历史模型未记录，时间仅为轮次开始时间。','',
       '[命令元数据](tools.json)保存93条选定command ID、命令、状态及退出码，没有全量stdout；[历史分工](readme.md)仅引用授权/职责和活动字段。原始日志与工程副本如下，不将交接摘要充当当时回答。','',
       '## 文件证据','','状态copied表示已读取字节并复制，语义审阅范围限于各案例实际引用的字段/段落，不等于全文工程审查。完整来源路径、字节数及双SHA见[清单](artifact_inventory.json)。原Word只做身份核对，未复制编辑稿。','',
       '| 包内副本 | 类型/来源性质 | SHA256前12位 |','| --- | --- | --- |']
for r in inventory:lines.append(f'| [{r["copy"]}]({r["copy"]}) | {r["kind"]} | {r["copy_sha256"][:12]} |')
lines+=['','## 不公开和未覆盖范围','','原文/原始日志保留了个人机器路径、W:历史映射和外部引用，当前包是本地审阅副本，没有完成公开匿名审查。旧链接不作为离线入口。未复制整个源码、测试数据、位流、DCP、厂商安装或私有UTF-8程序。','',
        '10/23原报告和消息的保护哈希见[baseline.json](baseline.json)；本批次核查见[validation.md](validation.md)。旧检查器不用于覆盖旧回执。','']
(B/'source_index.md').write_text('\n'.join(lines),'utf-8')

# Machine-readable reverse mapping keeps exact message IDs alongside local labels.
by_n={m['organizer_id']:m for m in new}
mapping=[]
for skill,caseid,ns,artifact,env,result,limits in [
 ('ui-evidence-validation','U01-U03',[],None,'Windows/WSL historical; 10/23 structure check','STRUCTURE_ONLY_FOR_NEW_SKILL','No independent transfer task'),
 ('controlled-model-comparison','C01-C03',[],None,'Historical model experiments','HISTORICAL_RESEARCH','Out of current deployment scope'),
 ('pynq-overlay-preflight','A02/V24-A',[],'evidence/pynq/evidence/20261022/v22_preflight.json','V22 offline Windows','429 PASS, 7 NOT_CHECKED; 23 constructed tests','Not V24/board/cross-board validation'),
 ('01_overlay_manager','V24-A',[],'evidence/received_skills/01_overlay_manager/README.md','Candidate source/document review','EXECUTION_RECEIPT_NOT_OBTAINED','Side effects and cross-board claims unverified'),
 ('02_dma_buffer_guard','V24-A',[],'evidence/received_skills/02_dma_buffer_guard/README.md','Candidate source/document review','EXECUTION_RECEIPT_NOT_OBTAINED','In-flight buffer isolation after timeout unproven'),
 ('03_contract_codegen','V24-C',['N042','N057'],'evidence/pynq/pynq_codegen_audit.json','Other thread actual offline HWH parser test','FAIL: 67/70 offsets','Not the current board runtime driver; original child transcript not archived'),
 ('04_golden_benchmark','V24-A',[],'evidence/received_skills/04_golden_benchmark/README.md','Candidate documentation','EXECUTION_RECEIPT_NOT_OBTAINED','Event definitions/acceptance thresholds need evidence'),
 ('05_troubleshooting','V24-A',[],'evidence/received_skills/05_troubleshooting/TROUBLESHOOTING.md','Document received','UNVERIFIED_AS_TRANSFER','No per-rule original-message mapping'),
 ('06_prompt_workflows','V24-A',[],'evidence/received_skills/06_prompt_workflows/README.md','Template received','NO_MATCHED_HISTORICAL_USE','Do not present new templates as historical prompts')]:
 mapping.append({'skill_id':skill,'case_id':caseid,'source_message_ids':[by_n[n]['message_id'] for n in ns],
                 'source_message_labels':ns,'source_tool_log':artifact,'artifact_hash':sha(B/artifact) if artifact else None,
                 'test_environment':env,'actual_result':result,'limitations':limits,
                 'older_message_source':None})
for row, case_dirs in [(mapping[0],['user_01_ui_linux','user_02_ui_guidance','user_03_ui_pipeline']),
                       (mapping[1],['session_01_detection','session_02_model_selection','session_03_rgb565'])]:
 row['older_message_source']=['../../report/ai_session/'+n+'/messages.json' for n in case_dirs]
 for name in case_dirs:
  ms=load(OUT/'report/ai_session'/name/'messages.json')
  chosen=[next(m for m in ms if m['role']=='user'),next(m for m in reversed(ms) if m['role']=='assistant')]
  row['source_message_ids'] += [m['message_id'] for m in chosen]
  row['source_message_labels'] += [name+':'+m['organizer_id'] for m in chosen]
 row['source_tool_log']='../../validation_results.json'
 row['artifact_hash']=sha(OUT/'validation_results.json')
(B/'case_skill_map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n','utf-8')

prose=[p for p in B.glob('*.md') if p.name not in ['conversation.md','validation.md']]
prose += [OUT/p for p in ['readme.md','missing_items.md','source_inventory.md','report/ai_session/readme.md','report/ai_session/team_review.md','report/ai_session/version_and_contribution.md','report/ai_session/ui_main_case.md','skill/README.md']]
prose += list((OUT/'report/ai_session').glob('session_*/summary.md'))
pending={B/'validation.md',B/'validation.json'};errors=[];count=0
for f in prose:
 for target in re.findall(r'\[[^\]\n]*\]\(([^)\n]+)\)',f.read_text('utf-8')):
  if re.match(r'^[a-zA-Z]+://',target) or target.startswith('#'):continue
  count+=1;t=unquote(target.strip('<>').split('#')[0]);p=(f.parent/t).resolve()
  if not p.exists() and p not in pending:errors.append({'file':str(f.relative_to(OUT)),'target':target})
add('generated_navigation_links',not errors,count=count,errors=errors,excluded='Raw transcript and copied source links; not complete offline engineering reproduction')
bad=[str(p.relative_to(B)) for p in B.rglob('*') if not p.name.isascii() or ' ' in p.name]
add('batch_english_child_paths',not bad,errors=bad,limitation='Chinese parent workspace path remains; not a final submission root audit')
hits=[]
for f in B.rglob('*'):
 if f.suffix not in ['.md','.json','.log','.txt','.rpt','.tsv','.tcl']:continue
 if f.name in ['validation.json','validation.md']:continue
 s=f.read_text('utf-8-sig',errors='replace')
 for no,line in enumerate(s.splitlines(),1):
  if re.search(r'\bsk-[A-Za-z0-9_-]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\b(?:10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+)\b',line):hits.append({'file':str(f.relative_to(B)),'line':no})
add('obvious_secret_private_host_scan',not hits,locations_only=hits,limitation='Limited pattern scan; personal paths remain, not public anonymization approval')
errs=[]
for f in B.rglob('*.json'):
 if f.name=='validation.json':continue
 try:load(f)
 except Exception as e:errs.append({'file':str(f.relative_to(B)),'error':str(e)})
add('batch_json_parse',not errs,errors=errs)

result={'date':'2026-10-27','batch':'v24_20261027','scope':'Archival identity/mapping/link/report-field checks only; no engineering execution',
        'checks':checks,'passed_checks':sum(c['passed'] for c in checks),'total_checks':len(checks),'all_checks_passed':all(c['passed'] for c in checks),
        'engineering_acceptance':'NOT_PASSED: negative timing, no new bit/XSA/board tests; summary discrepancy remains'}
(B/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
lines=['# 2026-10-27增量归档核查','','本次只读核对文件身份、消息ID、相对链接、报告字段和既有回执；没有执行工程、仿真、训练或板测。10/23核查报告未覆盖。','',
       '| 检查 | 结果 |','| --- | --- |']
lines += ['| '+c['check']+' | '+('通过' if c['passed'] else '需处理')+' |' for c in checks]
lines += ['',f'新增74份副本；142条／5轮消息与旧182条／24轮按ID去重为{len(set(ni+oi))}条／{len(nt|ot)}轮。93条命令只有可见元数据，7条子代理活动只支持当时有限材料审阅。保护快照覆盖旧原文/回执及当前Word、LaTeX。','',
          '原V24完整时序报告8069个setup失败端点与signoff摘要100不一致，已作为待核验项保留。三轮2025.2原始时序与阶段审计哈希/字段匹配，但第三轮仍WNS−0.219、TNS−84.981、624个失败端点。此处“通过”指归档检查通过，绝不代表工程签核通过。','',
          '当前Word哈希与历史范围修订after_sha256一致；未重渲染。V22检查器429/7及23构造测试、候选生成器67处错误来自既有回执，本轮未重跑。没有调用可能写文件或加载硬件的run.sh/check。','',
          '新增英文子路径检查不覆盖中文父目录。原始路径、外链和用户可见消息仍保留；未完成公开匿名/许可审查，也未发布。未读取work/logs/work.steps.log。','',
          '[机器记录](validation.json) · [来源索引](source_index.md) · [Skill机器映射](case_skill_map.json) · [10/23历史核查](../../validation_report.md)','']
(B/'validation.md').write_text('\n'.join(lines),'utf-8')
print(json.dumps({'passed':result['passed_checks'],'total':len(checks),'failed':[c for c in checks if not c['passed']]},ensure_ascii=False))
sys.exit(0 if result['all_checks_passed'] else 1)
