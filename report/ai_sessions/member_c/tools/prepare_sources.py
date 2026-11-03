"""Read supplied project archives; write only scoped review copies and an inventory."""
from pathlib import Path
from zipfile import ZipFile
import subprocess, hashlib, json, re

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parents[1]

def digest(b): return hashlib.sha256(b).hexdigest()

def clean(s):
    # Network host addresses are not needed to assess historical results.
    s, n = re.subn(r'(?<![\d.])(?:10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+)(?![\d.])', '<redacted_private_host>', s)
    s, m = re.subn(r'(?im)^(.*?(?:password|passwd|api[_-]?key|access[_-]?token)\s*[:=]\s*)[^\r\n]+', r'\1<redacted_sensitive_value>', s)
    return s, n+m

def write_new(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        if p.read_bytes() != data: raise RuntimeError('Refuse overwrite: '+str(p))
    else: p.write_bytes(data)

def main():
    rar = ROOT/'AI_Sessions/A/sessions.rar'
    names = subprocess.run(['tar','-tf',str(rar)],capture_output=True,check=True).stdout.decode('utf-8').splitlines()
    archives = []
    records = []
    selected_a = {'2026-09-18-001-day2-pl-protocol-and-reset.md','2026-10-20-008-v22-r4-full-release-handoff.md'}
    selected_b = {'2026-09-22-003-kv260-four-level-fps-optimization.md','2026-10-01-003-restoration-repair-test.md','2026-10-13-002-restore-freeze-investigation.md','2026-10-18-004-v19-ila-capture-buffer-full.md'}
    for archive in [rar,ROOT/'AI_Sessions/B/candidate-sessions—wt.zip',ROOT/'AI_Sessions/B/selected_cases_wt.zip']:
        archives.append({'path':str(archive.relative_to(ROOT)),'bytes':archive.stat().st_size,'sha256':digest(archive.read_bytes())})
        z = ZipFile(archive) if archive.suffix=='.zip' else None
        entries = z.namelist() if z else names
        for name in entries:
            if not name.endswith('.md') or name.startswith('__MACOSX/'): continue
            if 'work.steps.log' in name: raise RuntimeError('Forbidden member')
            b = z.read(name) if z else subprocess.run(['tar','-xOf',str(archive),name],capture_output=True,check=True).stdout
            stem = Path(name).name
            selected = (not z and stem in selected_a) or (z and (stem in selected_b or stem.startswith('CASE-')))
            rec = {'archive':str(archive.relative_to(ROOT)),'member':name,'bytes':len(b),'sha256':digest(b),'status':'content_read' if selected else 'member_bytes_hashed_only'}
            if selected:
                text,redactions = clean(b.decode('utf-8-sig'))
                category = 'team_a' if not z else ('team_b_selected' if stem.startswith('CASE-') else 'team_b_sources')
                p=OUT/'sources'/category/stem.lower()
                outb=text.encode('utf-8')
                write_new(p,outb)
                rec.update(copy=p.relative_to(OUT).as_posix(),copy_sha256=digest(outb),redactions=redactions,record_kind='structured_summary_not_raw_conversation')
            records.append(rec)
        if z: z.close()
    a={Path(x['member']).name:x for x in records if '/A/' in x['archive'].replace('\\','/')}
    overlap=[]
    for x in records:
        if 'candidate-sessions' in x['archive']:
            y=a.get(Path(x['member']).name)
            overlap.append({'member_b':x['member'],'member_a':y['member'] if y else None,'byte_identical':bool(y and x['sha256']==y['sha256'])})
    result={'review_date':'2026-10-22','archives':archives,'members':records,'overlap':overlap,'scope':'Only selected summaries copied; excluded macOS metadata. Archive/member hashes are identity checks, not proof of message provenance or experiment success.'}
    write_new(OUT/'archive_inventory.json',(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    print(json.dumps({'archive_count':len(archives),'markdown_members':len(records),'selected_read':sum('copy'in x for x in records),'overlap_count':len(overlap),'identical':sum(x['byte_identical'] for x in overlap)},ensure_ascii=False))

if __name__=='__main__':main()
