"""Nonblocking PL launch/poll; all interstage destinations are borrowed ring slots."""
import time
import numpy as np
from pynq import MMIO,allocate
from rectify_rgb import RectifyRGB,WIDTH,HEIGHT
from whiteboard_ip import WhiteboardIP

def low_buffer(buf):
    if int(buf.physical_address)%4 or int(buf.physical_address)+buf.nbytes>0x80000000:
        raise ValueError('Stage buffer must be aligned low DDR')

class RectifierStage(RectifyRGB):
    def __init__(self,timeout):
        super().__init__(timeout=timeout,allocate_output=False)
        self.monitor=MMIO(0x80070000,0x10000)
        if self.monitor.read(0)!=0x57424436:raise RuntimeError('Missing v6 rectify monitor')
    def launch(self,lease,dst):
        if self.in_flight or not self.generation or lease.cpu_active:raise RuntimeError('Rectifier launch ownership')
        low_buffer(dst)
        if lease.slot.size<WIDTH*HEIGHT*2:raise ValueError('RGB565 camera frame too short')
        self.pointer(0x10,lease.dma_address);self.pointer(0x18,dst.physical_address)
        for reg,value in ((0x38,0),(0x40,0),(0x48,128),(0x50,0)):self.ip.write(reg,value)
        self.ip.read(0);lease.start_pl();self.lease=lease;self.in_flight=True
        self.started=time.monotonic();self.ip.write(0,1)
    def poll(self):
        if not self.in_flight:return False
        done=bool(self.ip.read(0)&2)
        if not done and time.monotonic()-self.started>self.timeout:raise TimeoutError('Rectifier still owns source/ring')
        if done:
            self.lease.finish_pl();self.lease=None;self.in_flight=False
            self.status.invalidate()
            self.diagnostics.invalidate();self.elapsed_ms=(time.monotonic()-self.started)*1000
            self.axi_diagnostics=[self.monitor.read(4*i) for i in range(12)]
            if int(self.status[0]):raise RuntimeError('Rectifier rejected geometry')
        return done

class RestoreStage:
    def __init__(self,ring,timeout,auto_clear=True,clear_frames=8,clear_cooldown=64):
        self.timeout=timeout;self.generation=0;self.running=False
        first=True
        def allocator(shape,dtype):
            nonlocal first
            if first:first=False;return ring.slots[0].buffer
            return allocate(shape=shape,dtype=dtype)
        roi=np.zeros(((HEIGHT+15)//16,WIDTH//16),np.uint8)
        self.ip=WhiteboardIP(MMIO(0x80050000,0x10000),WIDTH,HEIGHT,roi,bgr=False,allocate=allocator,auto_clear=auto_clear,
                             clear_frames=clear_frames,clear_cooldown=clear_cooldown)
        # Output is owned by FrameRing, never freed through restoration state.
        self.ip.buffers.pop('output_r')
        try:
            for buffer in self.ip.buffers.values():low_buffer(buffer)
        except BaseException:self.ip.close();raise
    def launch(self,src,dst,geometry,clear_eligible=False):
        if self.running:raise RuntimeError('Restore busy')
        low_buffer(src);low_buffer(dst)
        if src.physical_address==dst.physical_address:raise ValueError('Restore input/output overlap')
        generation=int(geometry[1]);initialize=generation!=self.generation
        if initialize:
            ox,oy,ow,oh=map(int,geometry[4:8]);xs=np.arange(WIDTH//16)*16+8
            ys=np.minimum(np.arange((HEIGHT+15)//16)*16+8,HEIGHT-4)
            roi=((ys[:,None]>=oy)&(ys[:,None]<oy+oh)&(xs[None,:]>=ox)&(xs[None,:]<ox+ow)).astype(np.uint8)
            self.ip.buffers['roi'][:]=roi.reshape(-1);self.ip.buffers['roi'].flush()
        self.ip._pointer('input_r',src.physical_address);self.ip._pointer('output_r',dst.physical_address)
        self.ip.ip.write(self.ip.reg['initialize'],self.ip.control_word(initialize,clear_eligible))
        self.generation=generation;self.running=self.ip.running=True
        self.started=time.monotonic();self.ip.ip.read(self.ip.reg['AP_CTRL']);self.ip.ip.write(self.ip.reg['AP_CTRL'],1)
    def poll(self):
        if not self.running:return False
        done=bool(self.ip.ip.read(self.ip.reg['AP_CTRL'])&2)
        if not done and time.monotonic()-self.started>self.timeout:raise TimeoutError('Restore still owns ring slots')
        if done:
            self.running=self.ip.running=False
            self.elapsed_ms=(time.monotonic()-self.started)*1000
            status=self.ip.ip.read(self.ip.reg['AP_RETURN'])
            if status:raise RuntimeError('Restore status='+str(status))
            self.scene_state=self.ip.scene_report()
        return done
    def wait_until_idle(self):
        if not self.running:return
        while not self.ip.ip.read(self.ip.reg['AP_CTRL'])&4:time.sleep(.01)
        self.running=self.ip.running=False
    def close(self):self.ip.close()

