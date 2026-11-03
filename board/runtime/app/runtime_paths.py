"""Locations shared by runtime, device setup and child processes."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARDWARE = ROOT / 'hardware'
CONFIG = ROOT / 'config'
UI = ROOT / 'ui'
DATA = Path(os.environ.get('WB_DATA_DIR', str(ROOT.parent / (ROOT.name.removesuffix('.previous') + '.data')))).resolve()
