"""Read-only audit of source files; writes this workspace's audit outputs only.

Does not execute project code, train, infer, build, or contact servers/boards.
"""
from pathlib import Path
import csv
import hashlib
import json
import re
import statistics
import subprocess
import sys
from urllib.parse import unquote

OUT = Path(__file__).resolve().parents[1]
PROJECT = OUT.parents[1]
checks = []

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def add(name, passed, **detail):
    checks.append({'check': name, 'passed': bool(passed), **detail})

# Validate only explicitly selected local evidence and the supplied small archives.
selected = read(OUT/'evidence_inventory.json')['files']
selected += read(OUT/'model_additional_inventory.json')
selected += read(OUT/'phone_evidence_inventory.json')
selected += read(OUT/'ui_history_inventory.json')['files']
copy_errors, original_errors = [], []
for rec in selected:
    if rec.get('status') != 'read_and_copied':
        copy_errors.append(rec.get('source')); continue
    if sha(OUT/rec['copy']) != rec['copy_sha256']:
        copy_errors.append(rec['copy'])
    if sha(PROJECT/rec['source']) != rec['source_sha256']:
        original_errors.append(rec['source'])
add('selected_evidence_copies', not copy_errors, count=len(selected), errors=copy_errors)
add('selected_originals_unchanged_since_copy', not original_errors, count=len(selected), errors=original_errors)

archive = read(OUT/'archive_inventory.json')
bad = [x['path'] for x in archive['archives'] if sha(PROJECT/x['path']) != x['sha256']]
add('supplied_archive_identity', not bad, count=len(archive['archives']), errors=bad)
copies = [x for x in archive['members'] if 'copy' in x]
bad = [x['copy'] for x in copies if sha(OUT/x['copy']) != x['copy_sha256']]
add('teammate_source_copies', not bad, count=len(copies), errors=bad)

for label, receipt, base in [
    ('ui_linux_sources','evidence/ui_linux/validation_receipt.json','ui/lvgl'),
    ('ui_pipeline_sources','evidence/ui_pipeline/regression_03/validation.json','model_integration/v16_ps_pipeline_ui_20261018')]:
    expected = read(OUT/receipt)['source_sha256']
    bad = [p for p, digest in expected.items() if sha(PROJECT/base/p) != digest]
    add(label, not bad, count=len(expected), errors=bad)

for kind in ['assets','preview']:
    base = PROJECT/f'ui/camera_guidance/{kind}_20261018_v5'
    d = read(base/'manifest.json')
    pairs = list(d['sha256'].items()) if kind == 'assets' else [(p['name'],p['sha256']) for p in d['pages']]
    bad = [p for p,digest in pairs if sha(base/p) != digest]
    add('guidance_'+kind+'_hashes', not bad, count=len(pairs), errors=bad)

# Validate the actual archived visible-message fields without exporting tool/internal content.
case_counts, message_errors, all_ids = [], [], []
for p in sorted((OUT/'report/ai_session').glob('*/messages.json')):
    messages = read(p)
    transcript = (p.parent/'conversation.md').read_text('utf-8')
    for m in messages:
        if m['role'] not in ['user','assistant'] or m.get('phase') not in [None,'commentary','final_answer']:
            message_errors.append({'case':p.parent.name,'id':m['organizer_id'],'reason':'unexpected role/phase'})
        if m['content'].strip() not in transcript or m['message_id'] not in transcript:
            message_errors.append({'case':p.parent.name,'id':m['organizer_id'],'reason':'transcript mapping mismatch'})
        all_ids.append(m['message_id'])
    case_counts.append({'case':p.parent.name,'messages':len(messages),'turns':len({m['turn_id'] for m in messages})})
add('visible_message_mapping', not message_errors and len(set(all_ids))==len(all_ids), cases=case_counts,
    total_messages=len(all_ids), total_selected_turns=sum(x['turns'] for x in case_counts), errors=message_errors)

d = read(OUT/'evidence/model_rgb565/server_results/three_seed_summary.json')
stats_bad, n = [], 0
for arm, values in d['arms'].items():
    for metric, v in values['metrics'].items():
        n += 1
        if abs(statistics.mean(v['values'])-v['mean'])>1e-12 or abs(statistics.stdev(v['values'])-v['sample_sd'])>1e-12:
            stats_bad.append(arm+':'+metric)
add('rgb565_summary_arithmetic', not stats_bad, count=n, errors=stats_bad)

with (OUT/'evidence/model_detection/phone/per_hand.csv').open(encoding='utf-8-sig',newline='') as handle:
    rows=list(csv.DictReader(handle))
phone_counts={k:sum(x[k]=='True' for x in rows) for k in ['original_matched','rgb565_matched','gt_crop_matched','same_crop_reduced_detail_matched','context_mask_same_scale_matched']}
add('phone_per_hand_counts', len(rows)==66 and list(phone_counts.values())==[21,19,60,58,20], hands=len(rows), counts=phone_counts)

protected=read(OUT/'protected_file_snapshot.json')
add('latex_source_unchanged',sha(Path(protected['path']))==protected['sha256'], file=protected['path'], expected_sha256=protected['sha256'])

# Fresh results from the official skill-creator checker, using an installed Python
# that already has PyYAML. The bundled Python's missing dependency is recorded.
validator=Path(r'C:\Users\32898\.codex\skills\.system\skill-creator\scripts\quick_validate.py')
validation_python=Path(r'C:\Users\32898\AppData\Local\Python\pythoncore-3.14-64\python.exe')
for name in ['ui-evidence-validation','controlled-model-comparison']:
    run=subprocess.run([str(validation_python),'-X','utf8',str(validator),str(OUT/'skill'/name)],capture_output=True,text=True,encoding='utf-8',errors='replace')
    add('skill_structure_'+name,run.returncode==0 and 'Skill is valid!' in run.stdout,
        exit_code=run.returncode,stdout=run.stdout.strip(),stderr=run.stderr.strip(),
        prior_attempt='Bundled Python lacked PyYAML; no package installed; retried with existing Python 3.14 / PyYAML 6.0.3')

# Check generated prose only. Old paths inside preserved source copies and raw
# message code fences are intentionally not converted into new package links.
prose=[p for p in OUT.rglob('*.md') if not {'sources','evidence'}.intersection(p.relative_to(OUT).parts) and p.name!='conversation.md']
prose=[p for p in prose if p.name!='validation_report.md']
link_errors, link_count, todo = [], 0, []
pending={(OUT/'validation_report.md').resolve(),(OUT/'validation_results.json').resolve()}
for p in prose:
    text=p.read_text('utf-8')
    if '[TODO:' in text: todo.append(str(p.relative_to(OUT)))
    for target in re.findall(r'\[[^\]\n]*\]\(([^)\n]+)\)',text):
        if re.match(r'^[a-zA-Z]+://',target) or target.startswith('#'): continue
        target=unquote(target.strip('<>').split('#')[0]); link_count+=1
        resolved=(p.parent/target).resolve()
        if not resolved.exists() and resolved not in pending: link_errors.append({'file':str(p.relative_to(OUT)),'target':target})
add('generated_prose_relative_links',not link_errors,count=link_count,errors=link_errors,
    excluded='Preserved sources, conversation code fences, and paths embedded in raw JSON/logs; not an offline-reproduction audit')
add('skill_and_prose_placeholders',not todo,errors=todo)

json_errors=[]
json_files=[p for p in OUT.rglob('*.json') if p.name!='validation_results.json']
for p in json_files:
    try: read(p)
    except (ValueError,UnicodeError) as err: json_errors.append({'file':str(p.relative_to(OUT)),'error':str(err)})
add('json_parse',not json_errors,count=len(json_files),errors=json_errors)
bad_names=[str(p.relative_to(OUT)) for p in OUT.rglob('*') if not p.name.isascii() or ' ' in p.name]
add('workspace_child_ascii_names',not bad_names,errors=bad_names,
    limitation='The parent project/workspace path contains Chinese; this is not a final submission repository check')

secret_patterns=[r'\bsk-[A-Za-z0-9_-]{20,}',r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',r'\b(?:10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+)\b']
secret_hits=[]
for p in OUT.rglob('*'):
    if p.suffix.lower() not in ['.md','.json','.log','.txt','.csv']:continue
    if p.name in ['validation_results.json','validation_report.md']:continue
    text=p.read_text('utf-8-sig')
    for line_no,line in enumerate(text.splitlines(),1):
        if any(re.search(pattern,line) for pattern in secret_patterns):
            secret_hits.append({'file':str(p.relative_to(OUT)),'line':line_no})
add('obvious_secret_and_private_host_scan',not secret_hits,locations_only=secret_hits,
    limitation='Pattern scan plus scoped manual review, not proof of complete anonymization; historical machine paths remain')

ui=read(OUT/'ui_followup_verification.json')
add('ui_followup_audit',ui['all_checks_passed'],count=ui['total_checks'],review_date=ui['review_date'],
    limitation='See separate audit for recovered images, selected tools and historical version boundaries')

result={'review_date':'2026-10-23','scope':'Documentation, file identity, visible-message mapping and arithmetic only; no project code execution/training/inference/board test',
        'checks':checks,'passed_checks':sum(x['passed'] for x in checks),'total_checks':len(checks),
        'all_checks_passed':all(x['passed'] for x in checks),
        'unresolved_material_gaps':'See missing_items.md; passing these checks does not make the submission complete.'}
(OUT/'validation_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# 本轮文件与证据核对','',
       '日期：2026-10-23。以下为本轮实际执行的只读核对。未运行UI、训练、推理、综合或板端测试。工程历史回执中的PASS保持其原有时间和平台。','',
       '| 核对项 | 本轮结果 |','| --- | --- |']
for c in checks:
    detail=str(c.get('count',''))
    lines.append('| '+c['check']+' | '+('通过' if c['passed'] else '需处理')+('，'+detail+'项' if detail else '')+' |')
lines += ['',f'六案共{len(all_ids)}条可见消息、{sum(x["turns"] for x in case_counts)}个所选轮次。核对摘录与messages.json映射，不能证明平台之外或未选轮次没有缺失。',
          '', 'Skill结构检查首次在捆绑Python中因缺少PyYAML无法运行，随后使用已安装的Python 3.14/PyYAML 6.0.3执行原校验器，两项结果见JSON；没有安装依赖或修改系统配置。启动器提示路径定位警告，但校验器实际运行、返回码为0。',
          '', '链接检查覆盖新写导读与Skill正文；sources/evidence内的原件副本和原文中的旧本机/远程引用不计作离线可用链接。明显秘密/私网地址模式未命中也不等于完成匿名审查。',
          '', '31资源/28预览哈希核对未重新渲染；17/98源码哈希核对未执行源码；三种子14项统计复算未重训；手机逐手计数重算未推理；LaTeX原件哈希与开始快照一致。V22整包历史审计未在本轮重新执行。',
          '', 'UI补充核对另覆盖新增42份副本、两张消息附件、14条历史X11记录、五版295文件哈希及单帧中间候选；详见[补充报告](ui_followup_verification.md)。综合副本数为103，不等于全量原始实验归档。',
          '', '初次消息校验把平台的final_answer误写为final白名单，已按实际API字段修正校验器；没有改动原文/消息角色。[初次检查记录](validation_initial_run.json)保留该问题。',
          '', '详见[机器可读记录](validation_results.json)、[来源清单](source_inventory.md)、[缺项清单](missing_items.md)。**这些检查通过不等于正式提交就绪。**','']
(OUT/'validation_report.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'passed':result['passed_checks'],'total':len(checks),'failed':[c for c in checks if not c['passed']]},ensure_ascii=False))
sys.exit(0 if result['all_checks_passed'] else 1)
