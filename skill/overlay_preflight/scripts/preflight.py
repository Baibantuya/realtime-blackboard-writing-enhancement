"""Offline file/contract comparison. Reads inputs, emits JSON to stdout only.

No PYNQ imports, board access, shell calls, device probing, or loader execution.
PASS_OFFLINE is not a hardware compatibility or functional acceptance verdict.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import platform
import re
import sys
import xml.etree.ElementTree as ET


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def within(root, relative):
    if not isinstance(relative, str) or not relative:
        raise ValueError('Expected nonempty relative POSIX path')
    p = PurePosixPath(relative)
    if p.is_absolute() or '..' in p.parts or '\\' in relative or ':' in relative:
        raise ValueError('Path must remain below input root: ' + relative)
    resolved = (root / relative).resolve()
    if root not in resolved.parents:
        raise ValueError('Resolved path escapes input root: ' + relative)
    return resolved


def number(value):
    if isinstance(value, bool):
        raise ValueError('Boolean is not an integer')
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value, 0)
    raise ValueError('Expected integer or 0x-prefixed string')


def keys(obj, allowed, required=()):
    if not isinstance(obj, dict):
        raise ValueError('Expected object')
    extra, missing = set(obj) - set(allowed), set(required) - set(obj)
    if extra or missing:
        raise ValueError(f'Unknown fields {sorted(extra)}, missing fields {sorted(missing)}')


def load_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(path.read_text(encoding='utf-8-sig'), object_pairs_hook=unique)


def validate_config(c):
    keys(c, ('schema', 'release', 'backend', 'target_part', 'files', 'manifest',
             'identity', 'ips', 'environment', 'provenance'),
         ('schema', 'release', 'backend', 'files', 'ips'))
    if c['schema'] != 1 or isinstance(c['schema'], bool):
        raise ValueError('Unsupported schema')
    for field in ('release', 'backend'):
        if not isinstance(c[field], str) or not c[field]:
            raise ValueError(field + ' must be nonempty text')
    if not isinstance(c['files'], dict) or not {'bit', 'hwh'} <= c['files'].keys():
        raise ValueError('files must include bit and hwh')
    paths = []
    for spec in c['files'].values():
        keys(spec, ('path', 'sha256', 'size'), ('path', 'sha256'))
        if not isinstance(spec['sha256'], str) or not re.fullmatch('[0-9a-f]{64}', spec['sha256']):
            raise ValueError('Expected lowercase SHA256')
        if 'size' in spec and (type(spec['size']) is not int or spec['size'] <= 0):
            raise ValueError('size must be a positive integer')
        paths.append(spec['path'])
    if len(paths) != len(set(paths)):
        raise ValueError('File roles must have distinct paths')
    if not isinstance(c['ips'], list) or not c['ips']:
        raise ValueError('At least one explicit IP contract is required')
    for ip in c['ips']:
        keys(ip, ('fullname', 'vlnv', 'registers', 'address'), ('fullname', 'vlnv', 'registers'))
        if not isinstance(ip['registers'], dict) or not ip['registers']:
            raise ValueError('Nonempty register contract required')
        for reg in ip['registers'].values():
            keys(reg, ('offset', 'width', 'access', 'fields'), ('offset', 'width'))
            if number(reg['offset']) < 0 or number(reg['width']) <= 0:
                raise ValueError('Invalid expected register dimensions')
            if 'fields' in reg:
                if not isinstance(reg['fields'], dict):
                    raise ValueError('fields must be an object')
                for field in reg['fields'].values():
                    keys(field, ('offset', 'width'), ('offset', 'width'))
                    if number(field['offset']) < 0 or number(field['width']) <= 0:
                        raise ValueError('Invalid expected field dimensions')
        if 'address' in ip:
            keys(ip['address'], ('interface', 'base', 'high'), ('interface', 'base', 'high'))
            if not 0 <= number(ip['address']['base']) <= number(ip['address']['high']):
                raise ValueError('Invalid expected address range')
    if 'manifest' in c:
        keys(c['manifest'], ('path',), ('path',))
    if 'identity' in c:
        keys(c['identity'], ('path', 'fields'), ('path', 'fields'))
        if not isinstance(c['identity']['fields'], dict) or not c['identity']['fields']:
            raise ValueError('Identity fields required')
    if 'environment' in c:
        keys(c['environment'], ('expected', 'record'), ('expected',))
        if not isinstance(c['environment']['expected'], dict):
            raise ValueError('Environment expected must be an object')


def properties(element):
    pairs = [(p.get('NAME'), p.get('VALUE')) for p in element.findall('./PROPERTY')]
    if len({p[0] for p in pairs}) != len(pairs):
        raise ValueError('Duplicate XML properties')
    return dict(pairs)


def inspect(root, config):
    root = Path(root).resolve()
    checks = []

    def add(code, status, detail):
        checks.append(dict(code=code, status=status, detail=detail))

    def compare(code, actual, expected):
        add(code, 'pass' if actual == expected else 'fail', dict(actual=actual, expected=expected))

    def attempt(code, fn):
        try:
            return fn()
        except (OSError, ValueError, TypeError, KeyError, ET.ParseError) as error:
            add(code, 'fail', str(error))
            return None

    c = attempt('config', lambda: load_json(Path(config)))
    if not checks:
        attempt('config_schema', lambda: validate_config(c))
    if not checks and not root.is_dir():
        add('input_root', 'fail', 'Input root is not a directory')
    if checks:
        return result(c, checks)
    paths = {}
    for role, spec in c['files'].items():
        p = attempt('path:' + role, lambda: within(root, spec['path']))
        if p is None:
            continue
        paths[role] = p
        if not p.is_file():
            add('file:' + role, 'fail', 'Missing regular file: ' + spec['path'])
            continue
        compare('nonempty:' + role, p.stat().st_size > 0, True)
        if 'size' in spec:
            compare('size:' + role, p.stat().st_size, spec['size'])
        value = attempt('read:' + role, lambda: sha(p))
        if value is not None:
            compare('sha256:' + role, value, spec['sha256'])
    bit, hwh = paths.get('bit'), paths.get('hwh')
    if bit and hwh:
        compare('bit_suffix', bit.suffix, '.bit')
        compare('hwh_pair_name', str(hwh), str(bit.with_suffix('.hwh')))
    if 'manifest' in c:
        def manifest():
            m = load_json(within(root, c['manifest']['path']))
            if not isinstance(m, dict) or not isinstance(m.get('files'), dict):
                raise ValueError('Manifest requires an object with a files object')
            compare('manifest_release', m['release'], c['release'])
            for role, spec in c['files'].items():
                p = paths.get(role)
                if p is None or not p.is_file():
                    continue
                entry = m['files'].get(spec['path'])
                if entry is None:
                    add('manifest_entry:' + role, 'fail', 'File is not listed')
                    continue
                compare('manifest_sha256:' + role, sha(p), entry['sha256'])
                compare('manifest_size:' + role, p.stat().st_size, entry['size'])
        attempt('manifest', manifest)
    else:
        add('manifest', 'not_checked', 'No release manifest configured')
    if 'identity' in c:
        def identity():
            record = load_json(within(root, c['identity']['path']))
            if not isinstance(record, dict):
                raise ValueError('Identity record must be an object')
            for field, expected in c['identity']['fields'].items():
                compare('identity:' + field, record.get(field), expected)
        attempt('identity', identity)
    else:
        add('identity', 'not_checked', 'No release identity configured')
    if hwh and hwh.is_file():
        def inspect_hwh():
            if hwh.stat().st_size > 32 * 1024 * 1024:
                raise ValueError('HWH exceeds supported 32 MiB limit')
            raw = hwh.read_bytes()
            # Supported dialect is UTF-8 XML; reject DTD/entity expansion.
            xml = raw.decode('utf-8-sig')
            if '<!DOCTYPE' in xml.upper() or '<!ENTITY' in xml.upper():
                raise ValueError('DTD/entities are not supported')
            tree = ET.fromstring(xml)
            for element in tree.iter():
                element.tag = element.tag.split('}')[-1]
            modules = list(tree.iter('MODULE'))
            if not modules:
                raise ValueError('HWH contains no MODULE')
            add('hwh_xml', 'pass', {'modules': len(modules), 'attributes': tree.attrib})
            for expected in c['ips']:
                label = expected['fullname']
                found = [m for m in modules if m.get('FULLNAME') == label]
                compare('ip_count:' + label, len(found), 1)
                if len(found) != 1:
                    continue
                m = found[0]
                compare('vlnv:' + label, m.get('VLNV'), expected['vlnv'])
                registers = list(m.iter('REGISTER'))
                occupied = set()
                for name, req in expected['registers'].items():
                    regs = [r for r in registers if r.get('NAME') == name]
                    code = label + '/' + name
                    compare('register_count:' + code, len(regs), 1)
                    if len(regs) != 1:
                        continue
                    props = properties(regs[0])
                    offset, width = number(props['ADDRESS_OFFSET']), number(props['SIZE'])
                    compare('register_offset:' + code, offset, number(req['offset']))
                    compare('register_width:' + code, width, number(req['width']))
                    if width <= 0 or width > 4096 or offset < 0 or offset % 4 or width % 8:
                        raise ValueError('Unsupported register dimensions: ' + code)
                    lanes = set(range(offset, offset + width // 8))
                    compare('register_nonoverlap:' + code, not bool(lanes & occupied), True)
                    occupied |= lanes
                    if 'access' in req:
                        compare('register_access:' + code, props.get('ACCESS'), req['access'])
                    for field_name, field_req in req.get('fields', {}).items():
                        fields = [f for f in regs[0].iter('FIELD') if f.get('NAME') == field_name]
                        compare('field_count:' + code + '/' + field_name, len(fields), 1)
                        if len(fields) == 1:
                            fp = properties(fields[0])
                            compare('field_offset:' + code + '/' + field_name, number(fp['BIT_OFFSET']), number(field_req['offset']))
                            compare('field_width:' + code + '/' + field_name, number(fp['BIT_WIDTH']), number(field_req['width']))
                if 'address' in expected:
                    a = expected['address']
                    same_instances = [x for x in modules if x.get('INSTANCE') == m.get('INSTANCE')]
                    if len(same_instances) != 1:
                        raise ValueError('Ambiguous instance address attribution: ' + label)
                    ranges = {(number(r.get('BASEVALUE')), number(r.get('HIGHVALUE')))
                              for r in tree.iter('MEMRANGE') if r.get('INSTANCE') == m.get('INSTANCE')
                              and r.get('SLAVEBUSINTERFACE') == a['interface'] and r.get('MEMTYPE') == 'REGISTER'}
                    compare('address:' + label, sorted(ranges), [(number(a['base']), number(a['high']))])
        attempt('hwh', inspect_hwh)
    env = c.get('environment', {})
    if env.get('record'):
        def environment():
            observed = load_json(within(root, env['record']))
            if not isinstance(observed, dict):
                raise ValueError('Environment record must be an object')
            for field, value in env['expected'].items():
                if observed.get(field) is None:
                    add('environment:' + field, 'not_checked', 'Missing recorded value')
                else:
                    compare('environment:' + field, observed[field], value)
        attempt('environment', environment)
    else:
        add('environment', 'not_checked', 'No target-board environment record supplied')
    for code, detail in {
        'target_device': 'Declared target only; no bitstream device decode or physical board identification',
        'build_provenance': 'Hashes prove consistency against inputs, not independent build origin or authenticity',
        'dtbo_semantics': 'DTBO bytes only; firmware-name, bindings and live DT applicability not parsed',
        'driver_abi': 'No module vermagic, loaded driver or runtime ABI readback',
        'pynq_parser': 'Independent XML parser; installed PYNQ interpretation not exercised',
        'board_function': 'No load, MMIO, CMA, cache/DMA, camera, display, timing or cross-board test',
    }.items():
        add(code, 'not_checked', detail)
    return result(c, checks)


def result(c, checks):
    return {'schema': 1, 'tool': 'pynq-overlay-preflight/0.1',
            'status': 'FAIL' if any(x['status'] == 'fail' for x in checks) else 'PASS_OFFLINE',
            'release': c.get('release') if isinstance(c, dict) else None,
            'backend': c.get('backend') if isinstance(c, dict) else None,
            'target_part_declared': c.get('target_part') if isinstance(c, dict) else None,
            'checks': checks, 'host': {'os': platform.system(), 'python': platform.python_version()},
            'scope': 'Offline comparisons only; backend is descriptive and never executed'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--config', required=True, type=Path)
    args = parser.parse_args()
    report = inspect(args.root, args.config)
    report['script_sha256'] = sha(Path(__file__))
    report['config_sha256'] = sha(args.config) if args.config.is_file() else None
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report['status'] == 'FAIL' else 0


if __name__ == '__main__':
    raise SystemExit(main())
