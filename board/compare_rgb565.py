"""Compare explicitly paired little-endian RGB565 frames, without hardware access."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np

def frame(path,width,height):
    data=np.fromfile(path,dtype='<u2')
    if data.size!=width*height:raise ValueError('Frame size mismatch: '+str(path))
    return data.reshape(height,width)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--reference',type=Path,required=True)
    ap.add_argument('--actual',type=Path,required=True)
    ap.add_argument('--width',type=int,required=True)
    ap.add_argument('--height',type=int,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args()
    if a.width<=0 or a.height<=0:ap.error('Positive dimensions required')
    if a.output.exists():ap.error('Preserve prior result; choose a new output file')
    x,y=frame(a.reference,a.width,a.height),frame(a.actual,a.width,a.height)
    diff=x!=y
    d={'status':'PASS_EXACT' if not diff.any() else 'FAIL_MISMATCH',
       'scope':'Exact frame comparison only. Same input, mode and state must be established separately.',
       'width':a.width,'height':a.height,'mismatch_pixels':int(diff.sum()),
       'mismatch_fraction':float(diff.mean()),
       'reference_sha256':hashlib.sha256(a.reference.read_bytes()).hexdigest(),
       'actual_sha256':hashlib.sha256(a.actual.read_bytes()).hexdigest(),
       'first_mismatches_yx':np.argwhere(diff)[:16].tolist()}
    a.output.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(d));return 0 if d['status']=='PASS_EXACT' else 1

if __name__=='__main__':raise SystemExit(main())
