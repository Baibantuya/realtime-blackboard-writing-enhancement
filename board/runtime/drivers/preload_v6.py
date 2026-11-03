"""Load exact ABI6 exporter before the new full overlay creates its device."""
import subprocess
from pathlib import Path
from ensure_kernel import check
from runtime_paths import HARDWARE
root=Path(__file__).resolve().parent
# The camera pipeline owns the DP CRTC; a desktop compositor can replace its mode.
if subprocess.run(['systemctl','is-active','--quiet','display-manager']).returncode==0:
    subprocess.run(['systemctl','stop','display-manager'],check=True)
subprocess.run(['/usr/local/share/pynq-venv/bin/python3',str(root/'set_ps_widths.py'),__import__('sys').argv[1]],check=True)
module=check()
if Path('/sys/module/wb_frame_pool').exists():subprocess.run(['rmmod','wb_frame_pool'],check=True)
subprocess.run(['insmod',str(module)],check=True)

if not Path('/sys/module/wb_rgb565_format').exists():subprocess.run(['insmod',str(HARDWARE/'wb_rgb565_format.ko')],check=True)
