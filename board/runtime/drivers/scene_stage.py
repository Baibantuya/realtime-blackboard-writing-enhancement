"""Nonblocking quantize replacement, with fresh-HWH register injection.

No guessed register offsets, MMIO base, overlay load, UI startup or deployment.
The existing ring scheduler supplies the paired A/B identity; only A is scanned
by this kernel. Ring B is sampled by SceneTracker as an auxiliary v15 view.
"""
import math
import time
import numpy as np

from scene_tracking import ABI


POINTERS=('src','canvas_in','canvas_out','metadata','dst')
SCALARS=('width','height','dst_stride','frame_cookie','metadata_cookie','control',
         'order','ink_delta','erase_delta','color_margin')


def validate_registers(registers,abi,ip_vlnv):
    if abi!=ABI or ip_vlnv!='whiteboard.org:hls:board_scene_quantize:1.0':
        raise ValueError('A fresh matching scene IP/HWH is required')
    expected=set(POINTERS+SCALARS+('AP_CTRL','AP_RETURN'))
    if not expected.issubset(registers):
        raise ValueError('Incomplete scene HWH register map')
    occupied=set()
    for name in expected:
        record=registers[name]
        offset,width=record['offset'],record['width']
        if width not in ((32,64) if name in POINTERS else (32,)) or offset<0 or offset%4 or offset+width//8>0x10000:
            raise ValueError('Invalid register: '+name)
        lanes=set(range(offset,offset+width//8,4))
        if occupied & lanes:raise ValueError('Overlapping HWH register lanes')
        occupied |= lanes


def low_buffer(buffer,required):
    address=int(buffer.physical_address)
    if address%4 or address<0 or address+int(buffer.nbytes)>0x80000000 or buffer.nbytes<required:
        raise ValueError('Expected aligned, sufficiently sized low-DDR buffer')
    return address


class SceneQuantizeStage:
    def __init__(self,mmio,registers,allocate,width,height,abi,ip_vlnv,timeout=.75,clock=time.monotonic):
        validate_registers(registers,abi,ip_vlnv)  # preflight before allocations
        if width<16 or width>1920 or width%16 or not 1<=height<=1080 or not math.isfinite(timeout) or timeout<=0:
            raise ValueError('Invalid stage geometry/timeout')
        if not mmio.read(registers['AP_CTRL']['offset'])&4:
            raise RuntimeError('Quantize hardware must be idle before stage setup')
        self.ip,self.reg,self.clock=mmio,registers,clock
        self.width,self.height,self.timeout=width,height,timeout
        self.running=False;self.front=0;self.context=None;self.last_context=None
        # Quantization thresholds are PS-owned runtime parameters.  Keep the
        # defaults identical to PL R5; callers may tune them before launch.
        self.ink_delta=26
        self.erase_delta=16
        self.color_margin=16
        self.canvases=[];self.metadata=None
        try:
            for _ in range(2):
                buffer=allocate(shape=(height,width//8),dtype='uint32')
                self.canvases.append(buffer)
                low_buffer(buffer,width*height//2)
                # R6 assigns label 7 to pink. Blank/unclassified is label 0;
                # the R5 0x77777777 sentinel would render a pink HOLD canvas.
                buffer[:]=0;buffer.flush()
            self.metadata=allocate(shape=((height+15)//16,width//16),dtype='uint32')
            low_buffer(self.metadata,4*(width//16)*((height+15)//16))
            self.metadata[:]=0;self.metadata.flush()
        except BaseException:
            self.close()
            raise

    def _write(self,name,value):
        reg=self.reg[name]
        self.ip.write(reg['offset'],int(value)&0xffffffff)
        if reg['width']==64:self.ip.write(reg['offset']+4,int(value)>>32)

    def reset_canvas(self):
        if self.running:raise RuntimeError('Cannot reset an owned canvas')
        for buffer in self.canvases:
            buffer.invalidate();buffer[:]=0;buffer.flush()

    def set_thresholds(self,ink_delta=None,erase_delta=None,color_margin=None):
        """Update PS-side thresholds while the quantizer is quiescent.

        The ranges match the HLS AXI-Lite validation.  Keeping validation here
        prevents a bad runtime value from being written into a live frame.
        """
        if self.running:
            raise RuntimeError('Cannot change thresholds while quantize is running')
        ink=int(self.ink_delta if ink_delta is None else ink_delta)
        erase=int(self.erase_delta if erase_delta is None else erase_delta)
        margin=int(self.color_margin if color_margin is None else color_margin)
        if not 1<=ink<=128 or not 1<=erase<=128 or not 1<=margin<=128:
            raise ValueError('Thresholds must be in the range 1..128')
        if erase>=ink:
            raise ValueError('erase_delta must be smaller than ink_delta')
        self.ink_delta,self.erase_delta,self.color_margin=ink,erase,margin

    def launch(self,source,destination,context,packet=None,rebase=False,order=0):
        if self.running:raise RuntimeError('Quantize stage still owns its buffers')
        now=self.clock()
        if not math.isfinite(now) or now<context.capture_ts or order not in range(4):
            raise ValueError('Invalid launch time/order')
        if packet is not None and packet.context!=context:
            raise ValueError('Wrong frame/geometry/history packet')
        if self.last_context is not None:
            if context.capture_ts<=self.last_context.capture_ts:
                raise ValueError('Canvas frame is out of order')
            if context.epochs==self.last_context.epochs and context.sequence<=self.last_context.sequence:
                raise ValueError('Canvas sequence is out of order')
        stride=int(getattr(destination,'stride',self.width*2))
        if stride<self.width*2 or stride>6144 or stride%4:raise ValueError('Bad scanout stride')
        buffers=[source,self.canvases[self.front],self.canvases[1-self.front],self.metadata,destination]
        requirements=[self.width*self.height*2,self.width*self.height//2,self.width*self.height//2,
                      4*(self.width//16)*((self.height+15)//16),stride*self.height]
        addresses=[low_buffer(b,n) for b,n in zip(buffers,requirements)]
        spans=[(a,a+int(b.nbytes)) for a,b in zip(addresses,buffers)]
        for i,(start,end) in enumerate(spans):
            if any(start<other_end and other_start<end for other_start,other_end in spans[i+1:]):
                raise ValueError('Stage buffer address ranges overlap')
        hold=packet is None or packet.hold or not packet.finalized or now>packet.valid_until
        if packet is not None and (packet.metadata.shape!=self.metadata.shape or packet.metadata.dtype!=np.uint32):
            raise ValueError('Incorrect packet raster')
        if not self.ip.read(self.reg['AP_CTRL']['offset'])&4:
            raise RuntimeError('Quantize hardware is not idle')
        changed=self.last_context is not None and context.epochs!=self.last_context.epochs
        same_coordinates=changed and (context.capture_epoch,context.geometry_epoch)==(self.last_context.capture_epoch,self.last_context.geometry_epoch)
        if same_coordinates and not rebase:
            for buffer in self.canvases:
                buffer.invalidate();buffer[:]&=np.uint32(0x77777777);buffer.flush()
        elif rebase or changed:
            self.reset_canvas()
        if packet is not None:self.metadata[:]=packet.metadata
        else:self.metadata[:]=0
        self.metadata.flush()
        values=dict(zip(POINTERS,addresses))
        values.update(width=self.width,height=self.height,dst_stride=stride,frame_cookie=context.cookie,
                      metadata_cookie=context.cookie,control=int(hold),order=order,
                      ink_delta=self.ink_delta,erase_delta=self.erase_delta,
                      color_margin=self.color_margin)
        for name,value in values.items():self._write(name,value)
        self.ip.read(self.reg['AP_CTRL']['offset'])
        if hasattr(destination,'start_quant'):destination.start_quant()
        self.context,self.destination,self.hold=context,destination,hold
        self.started=now;self.running=True
        self._write('AP_CTRL',1)

    def poll(self):
        if not self.running:return False
        done=bool(self.ip.read(self.reg['AP_CTRL']['offset'])&2)
        if not done:
            if self.clock()-self.started>self.timeout:
                raise TimeoutError('Quantize timeout: A/B, canvas and scanout ownership retained')
            return False
        self.running=False
        self.host_observed_ms=(self.clock()-self.started)*1000  # not hardware busy cycles
        status=self.ip.read(self.reg['AP_RETURN']['offset'])
        if status:raise RuntimeError('Quantize status=%d; output must not be presented'%status)
        self.front=1-self.front
        self.last_context=self.context
        if hasattr(self.destination,'finish_quant'):self.destination.finish_quant()
        else:self.destination.invalidate()
        return True

    def close(self):
        if self.running:raise RuntimeError('Quiesce DMA before freeing stage storage')
        for buffer in self.canvases:buffer.freebuffer()
        self.canvases=[]
        if self.metadata is not None:self.metadata.freebuffer();self.metadata=None
