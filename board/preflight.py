"""Read-only board inventory. Never loads overlays or accesses MMIO.

Run on the actual KV260: python3 preflight.py --output /tmp/wb_preflight_unique
The output directory must not already exist.
"""
import argparse, datetime, hashlib, json, platform, subprocess
from pathlib import Path

def text_file(path):
    try:return Path(path).read_text(errors='replace').replace('\x00',' ').strip()
    except OSError:return None

def command(args):
    try:
        p=subprocess.run(args,capture_output=True,text=True,timeout=15)
        return {'argv':args,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
    except (OSError,subprocess.TimeoutExpired) as e:
        return {'argv':args,'status':'UNAVAILABLE','reason':str(e)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--package',type=Path)
    args=ap.parse_args()
    if platform.system()!='Linux' or platform.machine() not in ('aarch64','arm64'):
        ap.error('Run on the ARM64 target board. A host/WSL run is not board evidence.')
    args.output.mkdir(parents=True,exist_ok=False)
    result={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'status':'INVENTORY_ONLY_NOT_FUNCTIONAL_PASS','architecture':platform.machine(),
            'kernel':platform.release(),'model':text_file('/proc/device-tree/model'),
            'compatible':text_file('/proc/device-tree/compatible'),
            'os_release':text_file('/etc/os-release'),
            'devices':{p:Path(p).exists() for p in ['/dev/video0','/dev/media0','/dev/dri/card0','/dev/dma_heap/linux,cma']},
            'commands':[command(c) for c in [['media-ctl','-p','-d','/dev/media0'],
                ['v4l2-ctl','--all','-d','/dev/video0'],['modinfo','xilinx_csi2rxss']]],
            'board_functional_test':'NOT_RUN','hardware_loaded_by_this_script':False}
    if args.package:
        result['package_files']={}
        for pattern in ('*.bit','*.hwh','*.dtbo'):
            for p in args.package.glob(pattern):
                result['package_files'][p.name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
        result['package_pairing']='NOT_VERIFIED_COMPARE_WITH_RELEASE_MANIFEST'
    target=args.output/'preflight.json'
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(target)

if __name__=='__main__':main()
