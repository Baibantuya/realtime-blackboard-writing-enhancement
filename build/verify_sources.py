"""Check sealed inputs before/after a build, without accessing any hardware."""
import hashlib, json
from pathlib import Path, PurePosixPath

root = Path(__file__).resolve().parent.parent
data = json.loads((root/'build/source_manifest.json').read_text(encoding='utf-8'))
if not data.get('files'): raise SystemExit('Empty source manifest')
failures = []
for name, expected in data['files'].items():
    rel = PurePosixPath(name)
    path = (root/name).resolve()
    if rel.is_absolute() or '..' in rel.parts or '\\' in name or root not in path.parents:
        failures.append({'file':name,'error':'invalid path'}); continue
    if not path.is_file(): failures.append({'file':name,'error':'missing'}); continue
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        failures.append({'file':name,'error':'changed'})
result = {'status':'PASS_INPUT_HASHES' if not failures else 'FAIL_INPUT_HASHES',
          'checked':len(data['files']),'failures':failures,
          'scope':'Input identity only; not implementation or board validation'}
print(json.dumps(result, ensure_ascii=True))
raise SystemExit(bool(failures))
