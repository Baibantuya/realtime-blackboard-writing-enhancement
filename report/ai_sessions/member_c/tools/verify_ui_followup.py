"""Read-only checks of recovered UI evidence; writes archival audit reports only."""
from pathlib import Path
import hashlib
import json
import re
import struct
import sys

OUT = Path(__file__).resolve().parents[1]
PROJECT = OUT.parents[1]
checks = []

def read(p):
    return json.loads(p.read_text('utf-8-sig'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None

def add(name, ok, **detail):
    checks.append({'check': name, 'passed': bool(ok), **detail})

inv = read(OUT/'ui_history_inventory.json')
errors = []
for r in inv['files']:
    src, dst = Path(r['source']), OUT/r['copy']
    if sha(src) != r['source_sha256'] or sha(dst) != r['copy_sha256'] or sha(src) != sha(dst):
        errors.append(r['copy'])
    if 'image_size' in r and list(struct.unpack('>II', dst.read_bytes()[16:24])) != r['image_size']:
        errors.append(r['copy']+': dimensions')
add('ui_history_42_copies_and_originals', len(inv['files']) == 42 and not errors, count=len(inv['files']), errors=errors)

historical = read(OUT/'evidence/ui_history/linux/export_sha256.json')
base = PROJECT/'evidence/member_c/light_overlay_linux_20261018'
matched, errors = 0, []
for r in inv['files']:
    try:
        rel = Path(r['source']).relative_to(base).as_posix()
    except ValueError:
        continue
    if rel in historical:
        matched += 1
        if sha(OUT/r['copy']) != historical[rel]:
            errors.append(rel)
add('ui_historical_export_manifest', matched == 17 and not errors, count=matched, errors=errors)

versions, errors = [], []
for n in range(1, 6):
    suffix = '' if n == 1 else '_v'+str(n)
    root = PROJECT/'ui/camera_guidance'
    ab, pb = root/('assets_20261018'+suffix), root/('preview_20261018'+suffix)
    am, pm = read(ab/'manifest.json'), read(pb/'manifest.json')
    pairs = [(ab/k, h) for k, h in am['sha256'].items()]
    pairs += [(pb/p['name'], p['sha256']) for p in pm['pages']]
    bad = [str(p) for p, h in pairs if sha(p) != h]
    offsets = []
    for page, lines in am['text_layout'].items():
        if not page.startswith('guidance'):
            continue
        for line in lines:
            if line['role'] in ['action', 'body', 'next'] and line.get('align') == 'center':
                bounds = line['bounds']
                offsets.append(abs((bounds[0]+bounds[2])/2-1696))
    old = inv['guidance_version_checks'][n-1]
    if len(offsets) != old['selected_centered_rows'] or max(offsets) != old['max_recorded_bounds_offset_px']:
        bad.append('selected manifest-coordinate arithmetic differs from collection record')
    versions.append({'version': n, 'hash_count': len(pairs), 'errors': bad,
                     'selected_rows': len(offsets), 'max_recorded_bounds_offset_px': max(offsets)})
    errors.extend(bad)
add('guidance_five_versions_hash_and_manifest_arithmetic', not errors and sum(v['hash_count'] for v in versions) == 295,
    count=295, versions=versions, limitation='Arithmetic of recorded bounds only; layout and visible bounds are different metrics; no rendering/pixel measurement')

raw = read(OUT/'evidence/ui_history/conversation_tools_and_images.json')
messages = read(OUT/'report/ai_session/user_01_ui_linux/messages.json')
by_id = {m['message_id']: m for m in messages}
errors = []
for a in raw['attachments']:
    m = by_id.get(a['message_id'])
    copies = [r for r in inv['files'] if r['source'] == a['path']]
    if not m or m['role'] != 'user' or m['turn_id'] != a['turn_id'] or len(copies) != 1:
        errors.append(a['message_id'])
add('recovered_attachments_message_mapping', len(raw['attachments']) == 2 and not errors, count=len(raw['attachments']), errors=errors,
    limitation='Exact API localImage path plus current bytes; no independent digest embedded in historical message')

records, errors = [], []
allowed = {'thread_id','thread_title','turn_id','turn_started_at_epoch','command_id','command','status','exitCode','durationMs','output'}
for r in raw['records']:
    run = re.search(r'x11_\d+', r['command']).group()
    txt = r['output']['text']
    result = re.search(r'PASS: (\d+) interaction/capture checks', txt)
    n = int(result.group(1)) if result else None
    if (set(r)-allowed or r['turn_id'] not in {m['turn_id'] for m in messages}
            or r['output'].get('truncated') is not False or 'verify_x11_interaction.py' not in r['command']
            or '--binary' not in r['command'] or (r['exitCode'] == 0) != (n is not None)):
        errors.append(r['command_id'])
    records.append({'run': run, 'command_id': r['command_id'], 'exit_code': r['exitCode'], 'reported_checks': n})
records.sort(key=lambda r:r['run'])
success = sum(r['exit_code'] == 0 for r in records)
add('visible_x11_records_mapping', not errors and len(records) == 14 and success == 7
    and [r['run'] for r in records] == [f'x11_{i:02}' for i in range(1,15)],
    count=len(records), successful=success, failed=len(records)-success, records=records, errors=errors,
    limitation='Historical visible output; 7 failures are not an estimated product failure rate')

errors, receipts = [], []
for run, expected in [('x11_04',37),('x11_11',47),('x11_12',64),('x11_13',64),('x11_14',65)]:
    folder = 'ui_linux' if run == 'x11_14' else 'ui_history/linux'
    receipt = read(OUT/'evidence'/folder/run/'interaction_receipt.json')
    tool_count = next(r['reported_checks'] for r in records if r['run'] == run)
    if receipt['status'] != 'PASS' or len(receipt['checks']) != expected or tool_count != expected:
        errors.append(run)
    receipts.append({'run':run,'checks':len(receipt['checks'])})
for run, expected in [('full_regression_01',93),('full_regression_02',98)]:
    receipt = read(OUT/'evidence/ui_history/full_ui/evidence'/run/'validation.json')
    if receipt['status'] != 'PASS' or receipt['tests'] != expected:
        errors.append(run)
log = (OUT/'evidence/ui_history/full_ui/evidence/full_regression_02/unittest.log').read_text('utf-8-sig')
if 'Ran 98 tests' not in log:
    errors.append('full_regression_02 unittest count')
add('historical_receipt_consistency', not errors, count=7, errors=errors, x11_receipts=receipts,
    limitation='Reading existing test output is not rerunning tests')

errors = []
for link in inv['message_links']:
    msgs = read(OUT/'report/ai_session'/link['case']/'messages.json')
    m = next((m for m in msgs if m['message_id'] == link['message_id']), None)
    if not m or link['link'] not in m['content']:
        errors.append(link['message_id'])
    p = Path(re.sub(r':\d+$','',link['link']))
    if link['exists'] and not p.is_file():
        errors.append(link['link'])
    if link['sha256_if_read'] is not None and sha(p) != link['sha256_if_read']:
        errors.append(link['link']+': changed bytes')
add('original_message_file_links', not errors, count=len(inv['message_links']), errors=errors)

case = (OUT/'report/ai_session/ui_main_case.md').read_text('utf-8')
visible = '\n'.join(m['content'] for name in ['user_01_ui_linux','user_02_ui_guidance','user_03_ui_pipeline']
                    for m in read(OUT/'report/ai_session'/name/'messages.json'))
quotes = [line[2:].strip() for line in case.splitlines() if line.startswith('> ') and not line.startswith('> 审阅稿')]
bad = [q for q in quotes if q not in visible]
add('main_case_quoted_original_text', bool(quotes) and not bad, count=len(quotes), errors=bad)

result = {'review_date':'2026-10-23', 'scope':'Read-only evidence identity, mapping, receipt reading and arithmetic; no project execution',
          'checks':checks, 'passed_checks':sum(c['passed'] for c in checks), 'total_checks':len(checks),
          'all_checks_passed':all(c['passed'] for c in checks)}
(OUT/'ui_followup_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
lines = ['# UI历史材料补充核对', '', '检索/复制日期：2026-10-22；本次文件核对：2026-10-23。仅读取原件、比较哈希、核对消息和历史回执、复算manifest字段；没有执行工程、重新渲染、训练或板端测试。', '',
         '| 核对项 | 本轮结果 |', '| --- | --- |']
for c in checks:
    lines.append('| '+c['check']+' | '+('通过' if c['passed'] else '待处理')+'，'+str(c['count'])+'项 |')
lines += ['', '新增42份文件为原字节副本，其中两张为原用户消息附件。17份Linux导出文件同时匹配既有export manifest；这是一致性核对，不是独立签名认证。五版295个文件做哈希核对，只有代表页和必要记录入包，不能称295份全部离线归档。', '',
          '14条历史X11可见输出均未标截断，保留7条非零退出。37/47/64/64/65取自各版汇总和对应回执；中间单帧93/98项是另外的软件测试集合。没有把历史通过改写为本轮复测。', '',
          'v3选定排版边界109行偏差0，v4/v5选定可见边界各84行最大0.25px；这是记录字段的算术核对。v4历史validation对100行给出最大0.5px，范围不同，保留原结果；约7px仍仅作为历史消息中的分析。', '',
          '原附件没有平台嵌入的独立历史哈希，早期回执没有二进制SHA，中间源码快照/逐次差异及完整会话仍未齐；当前也没有对应版本的KV260验证。详见[缺项清单](missing_items.md)。', '',
          '[机器可读结果](ui_followup_verification.json) · [新增副本与原件路径](ui_history_inventory.json) · [UI主案例](report/ai_session/ui_main_case.md) · [工作区综合核对](validation_report.md)', '']
(OUT/'ui_followup_verification.md').write_text('\n'.join(lines),'utf-8')
print(json.dumps({'passed':result['passed_checks'],'total':len(checks),'failed':[c for c in checks if not c['passed']]},ensure_ascii=False))
sys.exit(0 if result['all_checks_passed'] else 1)
