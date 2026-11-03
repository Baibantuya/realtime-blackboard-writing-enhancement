"""Validate a prebuilt module for this exact running kernel before loading it."""
import argparse
import os
import subprocess
from pathlib import Path
from runtime_paths import HARDWARE

def check():
    root=HARDWARE;module=root/'wb_frame_pool.ko'
    if not module.is_file():raise RuntimeError('Missing wb_frame_pool.ko; rebuild supplied kernel sources for this kernel')
    vermagic=subprocess.check_output(['modinfo','-F','vermagic',str(module)],text=True).split()[0]
    if vermagic!=os.uname().release:raise RuntimeError('Module kernel %s differs from running %s; rebuild kernel_sources.tar.gz'%(vermagic,os.uname().release))
    version=subprocess.check_output(['modinfo','-F','version',str(module)],text=True).strip()
    if version!='6.0':raise RuntimeError('Queued camera and shared scanout require frame-pool module6.0')
    bridge=root/'wb_rgb565_format.ko'
    if not bridge.is_file():raise RuntimeError('Missing matched continuous formatter media subdev')
    if subprocess.check_output(['modinfo','-F','vermagic',str(bridge)],text=True).split()[0]!=os.uname().release:raise RuntimeError('Formatter module kernel mismatch')
    return module

def ensure_loaded():
    module=check()
    if not Path('/sys/module/wb_frame_pool').exists():subprocess.run(['insmod',str(module)],check=True)
    if Path('/sys/module/wb_frame_pool/version').read_text().strip()!='6.0':raise RuntimeError('Loaded frame-pool is not ABI6')
    bridge=HARDWARE/'wb_rgb565_format.ko'
    if not Path('/sys/module/wb_rgb565_format').exists():subprocess.run(['insmod',str(bridge)],check=True)
    if not Path('/dev/wb_frame_pool').exists():
        raise RuntimeError('No shared frame device: check new DTBO, HP0 device binding, and kernel log')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--load',action='store_true');args=ap.parse_args()
    if args.load:ensure_loaded()
    else:print('MODULE_KERNEL_MATCH',check())
