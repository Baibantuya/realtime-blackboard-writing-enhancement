"""Vendor queued DMA, two-byte YUYV transport carrying exact RGB565 payload; no YUV conversion."""
import ctypes
import errno
import fcntl
import mmap
import os
import select
import struct
import time
import threading
import numpy as np
from v4l2_types import (_V4L2Format, _ReqBufs, _Plane, _MBuf, _V4L2Buffer,
    _ioctl, _VIDIOC_S_FMT, _VIDIOC_REQBUFS, _VIDIOC_QBUF, _VIDIOC_DQBUF,
    _VIDIOC_STREAMON, _VIDIOC_STREAMOFF, V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE,
    V4L2_PIX_FMT_YUYV)

ALLOC=0xc0185740
START=0x40045741
DONE=0x40045742
VERSION=0x80045743
CPU_SYNC=0x40086200
DMABUF=4  # V4L2_MEMORY_DMABUF (USERPTR is 2, OVERLAY is 3).

def new_buffer(index=None, fd=None, size=0):
    planes=(_Plane*1)()
    b=_V4L2Buffer(type=V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE,memory=DMABUF,
                  length=1,m=_MBuf(planes=ctypes.cast(planes,ctypes.POINTER(_Plane))))
    if index is not None: b.index=index
    if fd is not None: planes[0].m.fd=fd;planes[0].length=size
    return b,planes

class SharedSlot:
    def __init__(self,pool,width,height,size):
        data=bytearray(struct.pack('<QQiI',size,0,-1,0))
        fcntl.ioctl(pool,ALLOC,data,True)
        self.size,self.dma_address,self.fd,_=struct.unpack('<QQiI',data)
        self.mapping=None;self.frame=None
        try:
            if self.dma_address%64 or self.dma_address+self.size>0x80000000:
                raise RuntimeError('Invalid low-DDR shared buffer address')
            self.mapping=mmap.mmap(self.fd,self.size,flags=mmap.MAP_SHARED,prot=mmap.PROT_READ)
            self.frame=np.ndarray((height,width),np.uint16,buffer=self.mapping)
            self.frame.flags.writeable=False
        except BaseException:
            self.close();raise
    def close(self):
        self.frame=None
        if self.mapping is not None:self.mapping.close();self.mapping=None
        if self.fd is not None:os.close(self.fd);self.fd=None

class FrameLease:
    def __init__(self,stream,index,sequence,timestamp,flags):
        self.stream=stream;self.index=index;self.slot=stream.slots[index]
        self.sequence=sequence;self.timestamp=timestamp;self.flags=flags
        self.cpu_active=False;self.pl_active=False;self.released=False
    @property
    def frame(self):
        if self.released or not self.cpu_active:raise RuntimeError('CPU frame access outside read lease')
        return self.slot.frame
    @property
    def dma_address(self):return self.slot.dma_address
    def begin_cpu(self):
        if self.released or self.pl_active:raise RuntimeError('Buffer is not available for CPU')
        if not self.cpu_active:
            fcntl.ioctl(self.slot.fd,CPU_SYNC,struct.pack('<Q',1));self.cpu_active=True
    def end_cpu(self):
        if self.cpu_active:
            fcntl.ioctl(self.slot.fd,CPU_SYNC,struct.pack('<Q',1|4));self.cpu_active=False
    def start_pl(self):
        if self.released or self.cpu_active or self.pl_active:raise RuntimeError('Invalid PL lease transition')
        fcntl.ioctl(self.stream.pool,START,struct.pack('<i',self.slot.fd));self.pl_active=True
    def finish_pl(self):
        if self.pl_active:
            fcntl.ioctl(self.stream.pool,DONE,struct.pack('<i',self.slot.fd));self.pl_active=False
    def release(self):
        if self.released:return
        self.end_cpu()
        if self.pl_active:raise RuntimeError('Cannot requeue camera source while PL is reading')
        with self.stream.condition:
            self.stream._queue(self.index);self.released=True
            self.stream.held.pop(self.index,None)
            if self.stream.consumer is self:self.stream.consumer=None

class V4l2Rgb565Stream:
    def __init__(self,device='/dev/video0',width=1920,height=1080,nbuf=4):
        self.fd=None;self.pool=None;self.slots=[];self.held={};self.streaming=False
        self.closed=False;self.captured=0;self.dropped=0;self.bad_frames=0
        self.last_sequence=None;self.sequence_gaps=0
        self.condition=threading.Condition(threading.RLock())
        self.stop_event=threading.Event();self.worker=None;self.pending=None;self.consumer=None;self.error=None
        try:
            self.pool=os.open('/dev/wb_frame_pool',os.O_RDWR)
            value=bytearray(4);fcntl.ioctl(self.pool,VERSION,value,True)
            if struct.unpack('<I',value)[0]!=6:raise RuntimeError('Frame pool ABI6 mismatch')
            self.fd=os.open(device,os.O_RDWR|os.O_NONBLOCK)
            fmt=_V4L2Format(type=V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE)
            fmt.fmt.pix_mp.width=width;fmt.fmt.pix_mp.height=height
            fmt.fmt.pix_mp.pixelformat=V4L2_PIX_FMT_YUYV;fmt.fmt.pix_mp.field=1
            _ioctl(self.fd,_VIDIOC_S_FMT,fmt)
            self.width=fmt.fmt.pix_mp.width;self.height=fmt.fmt.pix_mp.height
            self.stride=fmt.fmt.pix_mp.plane_fmt[0].bytesperline
            self.sizeimage=fmt.fmt.pix_mp.plane_fmt[0].sizeimage
            # This board's Xilinx VIPP reports num_planes=0 for RGB3 despite
            # using one MPLANE plane (the same legacy-driver quirk as before).
            if ((self.width,self.height)!=(width,height) or fmt.fmt.pix_mp.num_planes not in (0,1)
                or fmt.fmt.pix_mp.pixelformat!=V4L2_PIX_FMT_YUYV or self.stride!=width*2
                or self.sizeimage<width*height*2):
                raise RuntimeError('Camera must negotiate one dense RGB565 payload in YUYV carrier plane (stride width*2)')
            req=_ReqBufs(count=nbuf,type=V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE,memory=DMABUF)
            _ioctl(self.fd,_VIDIOC_REQBUFS,req)
            if req.count<4:raise RuntimeError('Four buffers required: PL + latest + two camera slots')
            self.nbuf=req.count
            for i in range(self.nbuf):
                self.slots.append(SharedSlot(self.pool,width,height,self.sizeimage));self._queue(i)
            typ=ctypes.c_int(V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE)
            _ioctl(self.fd,_VIDIOC_STREAMON,typ);self.streaming=True
            self.metrics=None;self.motion_guard=None;self.capture_epoch=0
            self.worker=threading.Thread(target=self._capture,name='camera-descriptor-drain',daemon=True)
            self.worker.start()
        except BaseException:
            self.close();raise
    def _queue(self,index):
        b,p=new_buffer(index,self.slots[index].fd,self.slots[index].size)
        _ioctl(self.fd,_VIDIOC_QBUF,b)
    def acquire(self,timeout=5):
        if self.closed:raise RuntimeError('Capture is closed')
        until=time.monotonic()+timeout
        with self.condition:
            if self.consumer is not None:raise RuntimeError('Release the previous capture lease first')
            while self.pending is None:
                if self.error is not None:raise RuntimeError('Capture worker failed') from self.error
                remaining=until-time.monotonic()
                if remaining<=0:raise TimeoutError('Camera frame timeout')
                self.condition.wait(remaining)
            self.consumer=self.pending;self.pending=None;return self.consumer
    def _capture(self):
        try:
            while not self.stop_event.is_set():
                if not select.select([self.fd],[],[],0.05)[0]:continue
                with self.condition:
                    for _ in range(self.nbuf):
                        b,p=new_buffer()
                        try:_ioctl(self.fd,_VIDIOC_DQBUF,b)
                        except OSError as e:
                            if e.errno==errno.EAGAIN:break
                            raise
                        index=int(b.index);sequence=int(b.sequence);self.captured+=1
                        if index>=len(self.slots) or index in self.held:raise RuntimeError('Camera returned an owned/invalid slot')
                        if self.last_sequence is not None:
                            gap=(sequence-self.last_sequence)&0xffffffff
                            if 1<gap<0x80000000:self.sequence_gaps+=gap-1
                        if self.last_sequence is not None and sequence<self.last_sequence and self.last_sequence-sequence>0x80000000:self.capture_epoch+=1
                        self.last_sequence=sequence
                        if b.flags&0x40 or p[0].data_offset!=0 or p[0].bytesused<self.width*self.height*2:
                            self.bad_frames+=1;self._queue(index);continue
                        current=FrameLease(self,index,sequence,b.timestamp.tv_sec+b.timestamp.tv_usec/1e6,int(b.flags))
                        current.capture_epoch=self.capture_epoch
                        if self.metrics is not None:self.metrics.add('capture_completed',(self.capture_epoch,sequence))
                        self.held[index]=current
                        if self.motion_guard is not None:self.motion_guard.sample(current,time.monotonic())
                        if self.pending is not None:self.pending.release();self.dropped+=1
                        self.pending=current;self.condition.notify_all()
        except BaseException as exc:
            with self.condition:self.error=exc;self.condition.notify_all()
    def close(self):
        if self.closed:return
        with self.condition:
            if any(lease.pl_active for lease in self.held.values()):
                raise RuntimeError('Refusing to close a source still owned by PL')
            self.stop_event.set()
        if self.worker is not None:self.worker.join(timeout=2)
        if self.worker is not None and self.worker.is_alive():raise RuntimeError('Capture worker did not stop')
        for lease in self.held.values():lease.end_cpu()
        self.held.clear()
        if self.fd is not None:
            if self.streaming:
                _ioctl(self.fd,_VIDIOC_STREAMOFF,ctypes.c_int(V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE))
            os.close(self.fd);self.fd=None
        for slot in self.slots:slot.close()
        self.slots=[]
        if self.pool is not None:os.close(self.pool);self.pool=None
        self.closed=True
