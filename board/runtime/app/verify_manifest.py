"""Validate the deployed runtime payload, without hardware tests."""
import hashlib
import json
from pathlib import Path, PurePosixPath


def verify_package(root):
    root = Path(root).resolve()
    manifest = json.loads((root/'config/runtime_manifest.json').read_text())
    if manifest.get('schema') != 2:
        raise RuntimeError('Expected the structured runtime manifest')
    config = json.loads((root/'config/deployment.json').read_text())
    if config.get('algorithm_abi') != '0x57425321':
        raise RuntimeError('Wrong scene ABI')
    for name, expected in manifest['sha256'].items():
        rel = PurePosixPath(name)
        path = (root/name).resolve()
        if rel.is_absolute() or '..' in rel.parts or '\\' in name or root not in path.parents:
            raise RuntimeError('Invalid runtime resource: '+name)
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise RuntimeError('Runtime checksum mismatch: '+name)
    return manifest
