"""ABI4 direct homography controller; source is a held camera DMA-BUF."""
import time
import numpy as np
from pynq import MMIO,allocate
WIDTH,HEIGHT=1920,1080

class RectifyRGB:
    def __init__(self,address=0x80040000,timeout=10,allocate_output=True):
        self.ip=MMIO(address,0x10000);self.timeout=timeout;self.buffers=[];self.in_flight=False
        self.lease=None;self.generation=0
        try:
            for name,shape,dtype in (('dst',(HEIGHT,WIDTH),np.uint16),('status',(1,),np.uint32),
                ('hint',(1,),np.uint32),('corners',(4,),np.uint32),('geometry',(20,),np.uint32),('diagnostics',(16,),np.uint32)):
                if name=='dst' and not allocate_output:continue
                buf=allocate(shape,dtype=dtype);self.buffers.append(buf);setattr(self,name,buf)
                if buf.physical_address+buf.nbytes>0x80000000:raise RuntimeError('CMA destination exceeds HP0 low DDR')
            if not self.ip.read(0)&4:raise RuntimeError('Rectifier is not idle')
            for offset,name in ((0x18,'dst'),(0x20,'status'),(0x28,'hint'),(0x30,'corners'),(0x58,'geometry'),(0x60,'diagnostics')):
                if hasattr(self,name):self.pointer(offset,getattr(self,name).physical_address)
        except BaseException:self.close();raise
    def pointer(self,offset,address):
        address=int(address)
        if address<0 or address>=0x80000000 or address%4:raise ValueError('Invalid low DDR pointer')
        self.ip.write(offset,address&0xffffffff)
    def set_geometry(self,words):
        if self.in_flight:raise RuntimeError('Geometry update during a frame')
        if words.shape!=(20,) or words.dtype!=np.uint32 or words[0]!=0x57424734:raise ValueError('Geometry ABI mismatch')
        np.copyto(self.geometry,words);self.geometry.flush();self.generation=int(words[1])
    def process(self,lease,binary=False,threshold=128):
        if self.in_flight or not self.generation:raise RuntimeError('Rectifier unavailable or uncalibrated')
        if lease.cpu_active:raise RuntimeError('End CPU sampling before starting PL')
        if lease.slot.size<WIDTH*HEIGHT*2:raise ValueError('Capture allocation too small')
        self.pointer(0x10,lease.dma_address)
        for offset,value in ((0x38,int(binary)),(0x40,1),(0x48,threshold),(0x50,0)):self.ip.write(offset,value)
        self.ip.read(0);lease.start_pl();self.lease=lease;self.in_flight=True
        self.ip.write(0,1);deadline=time.monotonic()+self.timeout
        while not self.ip.read(0)&2:
            if time.monotonic()>=deadline:raise TimeoutError('PL timeout: source lease and DMA buffers retained')
            time.sleep(0.0005)
        lease.finish_pl();self.in_flight=False;self.lease=None
        for b in (self.dst,self.status,self.hint,self.corners):b.invalidate()
        status=int(self.status[0])
        if status:raise RuntimeError('PL rejected geometry: %d'%status)
        return self.dst,{'status':status,'geometry_generation':self.generation,
            'corners':[(int(v)&65535,int(v)>>16) for v in self.corners]}
    def wait_until_idle(self):
        if not self.in_flight:return
        while not self.ip.read(0)&4:time.sleep(0.01)
        if self.lease is not None:self.lease.finish_pl()
        self.in_flight=False;self.lease=None
    def close(self):
        if self.in_flight:return
        for b in self.buffers:b.freebuffer()
        self.buffers=[]
