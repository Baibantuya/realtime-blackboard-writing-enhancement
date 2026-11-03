"""Read-only package identity check. No PYNQ import, MMIO, deployment or network."""
from pathlib import Path, PurePosixPath
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def main():
    errors=[];manifest=json.loads((ROOT/'manifest.json').read_text('utf-8'))
    for n,v in manifest['files'].items():
        rel=PurePosixPath(n);p=(ROOT/n).resolve()
        if rel.is_absolute() or '..' in rel.parts or not p.is_relative_to(ROOT) or not all(re.fullmatch('[a-z0-9_.-]+',x) for x in rel.parts):
            errors.append({'path':n,'error':'invalid path'});continue
        if not p.is_file():errors.append({'path':n,'error':'missing'});continue
        if p.stat().st_size!=v['bytes'] or digest(p)!=v['sha256']:errors.append({'path':n,'error':'hash/size mismatch'})
    rt=ROOT/'board/runtime';d=json.loads((rt/'config/runtime_manifest.json').read_text('utf-8'))
    for n,h in d['sha256'].items():
        p=(rt/n).resolve()
        if not p.is_relative_to(rt) or not p.is_file() or digest(p)!=h:errors.append({'path':'board/runtime/'+n,'error':'runtime identity mismatch'})
    r={'status':'PASS' if not errors else 'FAIL','package_files':len(manifest['files']),'runtime_files':len(d['sha256']),
       'errors':errors,'scope':'Package bytes and paired runtime identity; hardware execution is separate'}
    print(json.dumps(r,ensure_ascii=False,indent=2));return bool(errors)
if __name__=='__main__':sys.exit(main())
