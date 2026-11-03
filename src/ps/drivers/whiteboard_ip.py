"""PYNQ launch controller for the complete restoration IP.

Accepts a CMA buffer of dense corrected RGB565 pixels packed into 32-bit words. Does no restoration
pixel processing on the CPU. Board integration is a separate validation step.
"""
import json,time
from pathlib import Path
from runtime_paths import HARDWARE
import numpy as np
DEFAULT_CONFIG=dict(delta=24,quiet_delta=16,dense=5,weak=2,hold=6,stable=3,quiet_max=2,chalk_min=100,chalk_spread=55)

class WhiteboardIP:
    def __init__(self,ip,width,height,roi,bgr=False,config=None,allocate=None,registers=None,
                 auto_clear=False,clear_frames=8,clear_cooldown=64):
        if not 16<=width<=1920 or width%16 or not 1<=height<=1080:raise ValueError('Geometry')
        if allocate is None:
            from pynq import allocate
        if registers is None:
            registers=json.loads((HARDWARE/'whiteboard_registers.json').read_text())
        self.reg=registers['registers'];self.ip=ip;self.width=width;self.height=height
        if not 1<=clear_frames<=255 or not 1<=clear_cooldown<=65535:raise ValueError('Clear confirmation/cooldown')
        self.auto_clear=bool(auto_clear);self.clear_frames=clear_frames;self.clear_cooldown=clear_cooldown
        self.ready=False;self.running=False;self.closed=False;self.words=width*height//2
        if not (self.ip.read(self.reg['AP_CTRL'])&4):raise RuntimeError('IP must be idle before controller setup')
        shape=((height+15)//16,width//16);r=np.asarray(roi)
        if r.shape!=shape or np.any((r!=0)&(r!=1)):raise ValueError('ROI')
        self.buffers={}
        try:
            for name,count,typ in [('output_r',self.words,'uint32'),('background',self.words,'uint32'),
                ('previous',self.words,'uint32'),('pixel_quiet',width*height//4,'uint32'),
                ('block_state',r.size+(4 if self.auto_clear else 0),'uint32'),('roi',r.size,'uint8')]:
                self.buffers[name]=allocate(shape=(count,),dtype=typ)
            self.buffers['roi'][:]=r.reshape(-1);self.buffers['roi'].flush()
            parameters=DEFAULT_CONFIG.copy() if config is None else (dict(config) if isinstance(config,dict) else vars(config))
            if not 1<=int(parameters.get('stable',3))<=15:
                raise ValueError('stable must be 1..15: low nibble is shared with block confidence')
            cfg=dict(width=width,height=height,bgr=int(bgr),**parameters,fine_min=100,fine_spread=55,red_bias=6)
            cfg['weak_threshold']=cfg.pop('weak');cfg['stable_r']=cfg.pop('stable')
            for name,value in cfg.items():self.ip.write(self.reg[name],int(value))
            for name,buffer in self.buffers.items():self._pointer(name,buffer.physical_address)
        except Exception:
            self.close();raise

    def control_word(self,initialize,eligible=False):
        if not self.auto_clear:return int(bool(initialize))
        return int(bool(initialize))|2|(4 if eligible else 0)|(self.clear_frames<<8)|(self.clear_cooldown<<16)

    def scene_report(self):
        if not self.auto_clear:return {'enabled':False}
        state=self.buffers['block_state'];state.invalidate()
        magic,packed,epoch,reasons=map(int,state[-4:])
        if magic!=0x57424331:raise RuntimeError('v15 clean-scene metadata missing; wrong restore IP')
        return dict(enabled=True,streak=packed&255,armed=bool(packed&256),cooldown=packed>>16,
                    epoch=epoch,reasons=reasons&255,rebased=bool(reasons&256))

    def _pointer(self,name,address):
        offset=self.reg[name];self.ip.write(offset,int(address)&0xffffffff);self.ip.write(offset+4,int(address)>>32)

    def _launch(self,frame,initialize,timeout,flush_input,read_output):
        if self.closed or self.running:raise RuntimeError('Controller closed or previous launch still running')
        if frame.dtype!=np.uint32 or not frame.flags.c_contiguous or frame.size!=self.words or not hasattr(frame,'physical_address'):raise ValueError('Expected packed uint32 CMA frame')
        a=int(frame.physical_address);end=a+frame.nbytes
        for buffer in self.buffers.values():
            b=int(buffer.physical_address)
            if a<b+buffer.nbytes and b<end:raise ValueError('Input overlaps persistent/output memory')
        if flush_input:frame.flush()
        self._pointer('input_r',a);self.ip.write(self.reg['initialize'],self.control_word(initialize))
        self.running=True;self.ip.write(self.reg['AP_CTRL'],1);deadline=time.monotonic()+timeout
        while not (self.ip.read(self.reg['AP_CTRL'])&2):
            if time.monotonic()>=deadline:
                self.ready=False
                raise TimeoutError('IP still owns buffers; reset/quiesce hardware before releasing them')
            time.sleep(.001)
        self.running=False
        status=self.ip.read(self.reg['AP_RETURN'])
        if status:raise RuntimeError('whiteboard_restore status='+str(status))
        if read_output:self.buffers['output_r'].invalidate()
        return self.buffers['output_r']

    def initialize(self,clear_frame,timeout=5,flush_input=False,read_output=True):
        self.ready=False
        output=self._launch(clear_frame,1,timeout,flush_input,read_output);self.ready=True
        return output

    def process(self,corrected_frame,timeout=5,flush_input=False,read_output=True):
        if not self.ready:raise RuntimeError('Initialize from a clear board frame first')
        return self._launch(corrected_frame,0,timeout,flush_input,read_output)

    def close(self):
        if self.running:raise RuntimeError('Wait for hardware or reset it before freeing DDR buffers')
        for buffer in self.buffers.values():buffer.freebuffer()
        self.buffers.clear();self.closed=True;self.ready=False

    def after_hardware_reset(self):
        """Caller has reset/quiesced the IP and its outstanding AXI transfers."""
        if self.closed:raise RuntimeError('Controller closed')
        if not (self.ip.read(self.reg['AP_CTRL'])&4):raise RuntimeError('IP has not reached idle')
        self.running=False;self.ready=False
