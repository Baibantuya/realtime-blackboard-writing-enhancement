"""Rotate at the sensor, propagate actual Bayer order, then set AE starting point."""
import json
import re
import subprocess
from pathlib import Path
from auto_exposure import sensor_node
from ensure_kernel import ensure_loaded
from runtime_paths import CONFIG

def run(args):return subprocess.run(args,check=True,capture_output=True,text=True).stdout
def set_pad(entity,pad,fmt,size='1920x1080'):
    run(['media-ctl','-d','/dev/media0','--set-v4l2','"%s":%d [fmt:%s/%s field:none]'%(entity,pad,fmt,size)])

def configure():
    ensure_loaded()
    sensor=sensor_node()
    entity=(Path('/sys/class/video4linux')/Path(sensor).name/'name').read_text().strip()
    run(['v4l2-ctl','-d',sensor,'--set-ctrl=horizontal_flip=1,vertical_flip=1'])
    set_pad(entity,0,'SRGGB8_1X8')
    actual=run(['media-ctl','-d','/dev/media0','--get-v4l2','"%s":0'%entity])
    match=re.search(r'(S(?:RGGB|BGGR|GRBG|GBRG)8_1X8)/1920x1080',actual)
    if not match:raise RuntimeError('Cannot determine flipped sensor RAW8 Bayer format: '+actual)
    raw=match.group(1)
    for p in (0,1):set_pad('80002000.mipi_csi2_rx_subsystem',p,raw)
    set_pad('a0010000.v_demosaic',0,raw);set_pad('a0010000.v_demosaic',1,'RBG888_1X24')
    for name in ('a0030000.v_gamma_lut','a0040000.v_proc_ss_csc','a0080000.v_proc_ss_scaler'):
        for p in (0,1):set_pad(name,p,'RBG888_1X24')
    set_pad('rgb565_format_adapter',0,'RBG888_1X24')
    set_pad('rgb565_format_adapter',1,'UYVY8_1X16')
    run(['v4l2-ctl','-d','/dev/video0','--set-fmt-video=width=1920,height=1080,pixelformat=YUYV'])
    run(['v4l2-ctl','-d',sensor,'--set-ctrl=vertical_blanking=1648'])
    config=json.loads((CONFIG/'deployment.json').read_text())['restore_photometry']
    run(['v4l2-ctl','-d',sensor,'--set-ctrl=exposure=%d,analogue_gain=%d'%(config['exposure'],config['analogue_gain'])])
    controls=run(['v4l2-ctl','-d',sensor,'--get-ctrl=horizontal_flip,vertical_flip,exposure,analogue_gain'])
    values={k.strip():int(v.strip()) for k,v in (line.split(':',1) for line in controls.splitlines() if ':' in line)}
    expected={'horizontal_flip':1,'vertical_flip':1,'exposure':config['exposure'],'analogue_gain':config['analogue_gain']}
    if values!=expected:raise RuntimeError('Sensor controls readback mismatch: %r'%values)
    for name,p in (('80002000.mipi_csi2_rx_subsystem',0),('a0010000.v_demosaic',0)):
        reported=run(['media-ctl','-d','/dev/media0','--get-v4l2','"%s":%d'%(name,p)])
        if raw not in reported:raise RuntimeError('Downstream Bayer format mismatch: '+reported)
    print(json.dumps({'sensor':sensor,'rotation180':'sensor_registers','bayer':raw,'controls':values}))

if __name__=='__main__':configure()
