"""Read-only overlay planning. Hardware backends intentionally not implemented here."""
import hashlib
from pathlib import Path


def inspect_overlay(bitfile, *, backend, expected_hashes, dtbo=None, metadata_dir=None):
    """Validate explicit files without importing PYNQ, clearing state or creating files.

    expected_hashes must come from a reviewed release. Matching them is identity
    checking, not proof of common build origin or compatibility.
    """
    if backend not in ('kv260-fpgautil', 'pynq-native'):
        raise ValueError('explicit supported target backend required; no platform guessing')
    bit = Path(bitfile).resolve()
    if bit.suffix != '.bit':
        raise ValueError('.bit expected')
    files = {'bit': bit, 'hwh': bit.with_suffix('.hwh')}
    if backend == 'kv260-fpgautil':
        if dtbo is None or metadata_dir is None:
            raise ValueError('KV260 plan requires explicit dtbo and isolated metadata directory')
        files.update(bit_bin=bit.with_suffix('.bit.bin'), dtbo=Path(dtbo).resolve())
        metadata = Path(metadata_dir).resolve()
        if metadata == bit.parent or metadata in bit.parents or any(metadata.glob('*.dtbo')):
            raise ValueError('metadata directory must be isolated and free of dtbo files')
    elif dtbo is not None or bit.with_suffix('.dtbo').exists():
        raise ValueError('native backend with neighboring DTBO is not reviewed')
    hashes = {}
    for role, path in files.items():
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if expected_hashes.get(role) != actual:
            raise ValueError(f'{role}: missing or mismatched expected hash')
        hashes[role] = actual
    return {'backend': backend, 'files': {k: str(v) for k, v in files.items()}, 'sha256': hashes,
            'metadata_directory': str(Path(metadata_dir).resolve()) if metadata_dir else None,
            'side_effects_performed': [], 'hardware_compatibility': 'NOT_CHECKED',
            'hardware_execution': 'UNIMPLEMENTED',
            'required_backend_checks': ['exclusive process/device ownership', 'all DMA masters quiescent',
                'reviewed reset/clock/device-tree sequence', 'bounded subprocess execution and failure handling',
                'isolated metadata bit/hwh pair with no adjacent dtbo', 'explicit stale-state decision']}


def execute_overlay(*args, **kwargs):
    raise NotImplementedError('offline candidate has no hardware backend; use a separately reviewed and authorized board procedure')
