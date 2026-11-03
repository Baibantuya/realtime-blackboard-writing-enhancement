"""Print board environment evidence without changing hardware or system settings."""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import platform
import re
import shutil
import struct
import subprocess
import sys
from datetime import datetime, timezone


def collect():
    root = Path(__file__).resolve().parent
    versions = {}
    for name in ('pynq', 'numpy', 'opencv-python', 'opencv-python-headless'):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    os_info = {}
    path = Path('/etc/os-release')
    if path.is_file():
        for line in path.read_text().splitlines():
            name, sep, value = line.partition('=')
            if sep and name in ('ID', 'VERSION_ID', 'PRETTY_NAME'):
                os_info[name] = value.strip('"')
    modules = {}
    for name in ('wb_frame_pool.ko', 'wb_rgb565_format.ko'):
        path = root / 'runtime/hardware' / name
        if path.is_file():
            data = path.read_bytes()
            modules[name] = {
                'sha256': hashlib.sha256(data).hexdigest(),
                'vermagic': [v.decode('ascii') for v in re.findall(rb'vermagic=([^\x00]+)', data)],
                'elf_machine': struct.unpack('<H', data[18:20])[0] if data[:4] == b'\x7fELF' else None,
            }
    packages = {}
    if shutil.which('dpkg-query'):
        for name in ('xrt', 'xilinx-xrt', 'xmutil', 'fpgautil', 'python3-opencv'):
            try:
                result = subprocess.run(['dpkg-query', '-W', '-f=${Version}', name], capture_output=True, text=True, timeout=5)
                packages[name] = result.stdout.strip() if result.returncode == 0 else None
            except subprocess.TimeoutExpired:
                packages[name] = {'status': 'timeout'}
    return {
        'captured_at_utc': datetime.now(timezone.utc).isoformat(),
        'system': platform.system(), 'kernel': platform.release(),
        'architecture': platform.machine(), 'os': os_info,
        'python_executable': sys.executable, 'python': platform.python_version(),
        'python_packages': versions, 'system_packages': packages,
        'tools': {n: shutil.which(n) for n in ('fpgautil', 'xmutil')},
        'packaged_modules': modules,
        'hardware_actions': 'none',
        'os_image_source': None, 'os_image_sha256': None,
    }


if __name__ == '__main__':
    print(json.dumps(collect(), indent=2, ensure_ascii=False))
