"""Low-CMA DMA-BUF -> DRM PRIME scanout, standard little-endian RGB565 / RG16."""
import ctypes as C
import fcntl,mmap,os,select,struct,time
from dataclasses import dataclass
import numpy as np
from pathlib import Path
from pynq.lib.video import DisplayPort,PIXEL_RGB,VideoMode

U=C.c_uint32;P=C.POINTER
class Mode(C.Structure):
    _fields_=[('clock',U)]+[(n,C.c_uint16) for n in ('hdisplay','hsync_start','hsync_end','htotal','hskew','vdisplay','vsync_start','vsync_end','vtotal','vscan')]+[(n,U) for n in ('vrefresh','flags','type')]+[('name',C.c_char*32)]
class Resources(C.Structure):
    _fields_=[('count_fbs',C.c_int),('fbs',P(U)),('count_crtcs',C.c_int),('crtcs',P(U)),('count_connectors',C.c_int),('connectors',P(U)),('count_encoders',C.c_int),('encoders',P(U))]+[(n,U) for n in ('min_width','max_width','min_height','max_height')]
class Connector(C.Structure):
    _fields_=[(n,U) for n in ('connector_id','encoder_id','connector_type','connector_type_id')]+[('connection',C.c_int),('mmWidth',U),('mmHeight',U),('subpixel',C.c_int),('count_modes',C.c_int),('modes',P(Mode)),('count_props',C.c_int),('props',P(U)),('prop_values',P(C.c_uint64)),('count_encoders',C.c_int),('encoders',P(U))]
class Encoder(C.Structure):
    _fields_=[(n,U) for n in ('encoder_id','encoder_type','crtc_id','possible_crtcs','possible_clones')]
class Crtc(C.Structure):
    _fields_=[(n,U) for n in ('crtc_id','buffer_id','x','y','width','height')]+[('mode_valid',C.c_int),('mode',Mode)]

class ScanFrame:
    def __init__(self,display,index):
        self.display=display;self.index=index;self.state='FREE';self.active=False
        request=bytearray(struct.pack('<QQiI',display.pitch*display.height,0,-1,0))
        fcntl.ioctl(display.pool,0xc0185740,request,True)
        self.nbytes,self.physical_address,self.fd,_=struct.unpack('<QQiI',request)
        if self.physical_address+self.nbytes>0x80000000:raise RuntimeError('Scanout outside HP0 low DDR')
        self.stride=display.pitch;self.handle=U();self.fb=U();self.map=None
        display.check(display.lib.drmPrimeFDToHandle(display.fd,self.fd,C.byref(self.handle)),'DRM PRIME import')
        a=U*4
        display.check(display.lib.drmModeAddFB2(display.fd,display.width,display.height,display.fourcc,
                      a(self.handle.value,0,0,0),a(self.stride,0,0,0),a(0,0,0,0),C.byref(self.fb),0),'DRM AddFB2')
    def start_quant(self):
        if self.state!='WRITING' or self.active:raise RuntimeError('Scanout buffer ownership')
        fcntl.ioctl(self.display.pool,0x40045744,struct.pack('<i',self.fd));self.active=True
    def finish_quant(self):
        if self.active:
            fcntl.ioctl(self.display.pool,0x40045745,struct.pack('<i',self.fd));self.active=False
    def fill_initial_white(self):
        # Initialization once, not a per-frame CPU copy or pixel transform.
        self.map=mmap.mmap(self.fd,self.nbytes,flags=mmap.MAP_SHARED,prot=mmap.PROT_READ|mmap.PROT_WRITE)
        raw=np.ndarray((self.display.height,self.stride),dtype=np.uint8,buffer=self.map)
        raw[:]=255;del raw
        self.map.close();self.map=None
    def write_direct_rgb565(self,rgb565_array):
        if self.active or self.state!='WRITING':raise RuntimeError('CPU write to non-owned scanout')
        if rgb565_array.dtype!=np.uint16 or rgb565_array.shape!=(self.display.height,self.display.width):
            raise ValueError('Expected full RGB565 scanout frame')
        # CPU is writing this DMA-BUF; WRITE (2), then WRITE|END (6).
        fcntl.ioctl(self.fd,0x40086200,struct.pack('<Q',2))
        mapping=None;raw=None
        try:
            mapping=mmap.mmap(self.fd,self.nbytes,flags=mmap.MAP_SHARED,prot=mmap.PROT_READ|mmap.PROT_WRITE)
            raw=np.ndarray((self.display.height,self.stride//2),dtype=np.uint16,buffer=mapping)
            raw[:,:self.display.width]=rgb565_array
        finally:
            raw=None
            if mapping is not None:mapping.close()
            fcntl.ioctl(self.fd,0x40086200,struct.pack('<Q',6))
    def snapshot(self):
        if self.active or self.state!='WRITING':raise RuntimeError('Snapshot before PL completion or after pageflip')
        fcntl.ioctl(self.fd,0x40086200,struct.pack('<Q',1))
        mapping=mmap.mmap(self.fd,self.nbytes,flags=mmap.MAP_SHARED,prot=mmap.PROT_READ)
        try:
            raw=np.ndarray((self.display.height,self.stride),np.uint8,buffer=mapping)
            frame=raw[:,:self.display.width*2].reshape(self.display.height,self.display.width,2).copy().view(np.uint16).reshape(self.display.height,self.display.width).copy()
            del raw
            return frame
        finally:
            mapping.close();fcntl.ioctl(self.fd,0x40086200,struct.pack('<Q',5))
    def snapshot_displayed(self):
        if self.active or self.state!='SCANNING' or self.display.front is not self:
            raise RuntimeError('Only confirmed front may be archived')
        fcntl.ioctl(self.fd,0x40086200,struct.pack('<Q',1))
        mapping=None;raw=None
        try:
            mapping=mmap.mmap(self.fd,self.nbytes,flags=mmap.MAP_SHARED,prot=mmap.PROT_READ)
            raw=np.ndarray((self.display.height,self.stride//2),np.uint16,buffer=mapping)
            return raw[:,:self.display.width].copy()
        finally:
            raw=None
            if mapping is not None:mapping.close()
            fcntl.ioctl(self.fd,0x40086200,struct.pack('<Q',5))
    def edit_rgb565(self,edit):
        if self.active or self.state!='WRITING':raise RuntimeError('Overlay before PL completion or after submission')
        fcntl.ioctl(self.fd,0x40086200,struct.pack('<Q',3))
        mapping=None;raw=None
        try:
            mapping=mmap.mmap(self.fd,self.nbytes,flags=mmap.MAP_SHARED,prot=mmap.PROT_READ|mmap.PROT_WRITE)
            raw=np.ndarray((self.display.height,self.stride//2),np.uint16,buffer=mapping)
            return edit(raw[:,:self.display.width])
        finally:
            raw=None
            if mapping is not None:mapping.close()
            fcntl.ioctl(self.fd,0x40086200,struct.pack('<Q',7))
    def close(self):
        if self.active or self.state not in ('FREE','WRITING'):raise RuntimeError('Closing active scanout')
        if self.fb.value:self.display.check(self.display.lib.drmModeRmFB(self.display.fd,self.fb.value),'DRM RmFB');self.fb.value=0
        if self.handle.value:fcntl.ioctl(self.display.fd,0x40086409,struct.pack('<II',self.handle.value,0));self.handle.value=0
        os.close(self.fd)

class SharedScanout:
    def __init__(self,width=1920,height=1080,count=3):
        self.width=width;self.height=height;self.pitch=((width*2+255)//256)*256
        self.fourcc=sum(ord(c)<<(8*i) for i,c in enumerate('RG16'))
        self.frames=[];self.front=None;self.pending=None;self.copy_count=0
        connector=Path('/sys/class/drm/card0-DP-1')
        if (connector/'status').read_text().strip()!='connected':raise RuntimeError('DP-1 is not connected')
        if not (connector/'edid').read_bytes():
            edid=bytearray(128);edid[:8]=bytes.fromhex('00 ff ff ff ff ff ff 00')
            edid[8:12]=bytes.fromhex('4a 8b 55 25');edid[12:18]=bytes.fromhex('01 00 00 00 01 00')
            edid[18:25]=bytes([1,4,0x80,52,29,0x78,0x0a]);edid[38:54]=bytes([1,1]*8)
            edid[54:72]=bytes.fromhex('02 3a 80 18 71 38 2d 40 58 2c 45 00 00 00 00 00 00 1e')
            edid[127]=(-sum(edid[:127]))&255
            Path('/sys/kernel/debug/dri/0/DP-1/edid_override').write_bytes(edid)
            if (connector/'edid').read_bytes()!=edid:raise RuntimeError('1080p EDID override failed')
        # Reuse PYNQ's DRM descriptor/event setup only. Configure the CRTC below
        # with the actual RG16 PRIME framebuffer, avoiding its RGB888 mode API.
        self.drm=DisplayPort()
        self.fd=self.drm._video_file.fileno();self.drm._loop.remove_reader(self.drm._video_file)
        self.lib=C.CDLL('libdrm.so.2',use_errno=True)
        declarations={
         'drmModeGetResources':([C.c_int],P(Resources)),
         'drmModeGetConnector':([C.c_int,U],P(Connector)),
         'drmModeGetEncoder':([C.c_int,U],P(Encoder)),
         'drmModeGetCrtc':([C.c_int,U],P(Crtc)),
         'drmPrimeFDToHandle':([C.c_int,C.c_int,P(U)],C.c_int),
         'drmModeAddFB2':([C.c_int,U,U,U,P(U),P(U),P(U),P(U),U],C.c_int),
         'drmModeSetCrtc':([C.c_int,U,U,U,U,P(U),C.c_int,P(Mode)],C.c_int),
         'drmModePageFlip':([C.c_int,U,U,U,C.c_void_p],C.c_int),
         'drmModeRmFB':([C.c_int,U],C.c_int),
         'drmModeFreeResources':([P(Resources)],None),
         'drmModeFreeConnector':([P(Connector)],None),
         'drmModeFreeEncoder':([P(Encoder)],None),
         'drmModeFreeCrtc':([P(Crtc)],None)}
        for name,(args,result) in declarations.items():f=getattr(self.lib,name);f.argtypes=args;f.restype=result
        r=self.lib.drmModeGetResources(self.fd)
        if not r:raise OSError(C.get_errno(),'No DRM resources')
        selected=False
        try:
            for i in range(r.contents.count_connectors):
                c=self.lib.drmModeGetConnector(self.fd,r.contents.connectors[i])
                if not c:continue
                try:
                    if c.contents.connection!=1:continue
                    modes=[c.contents.modes[j] for j in range(c.contents.count_modes)
                           if c.contents.modes[j].hdisplay==width and c.contents.modes[j].vdisplay==height]
                    if not modes:continue
                    selected_mode=next((mode for mode in modes if mode.vrefresh==60),modes[0])
                    self.mode=Mode.from_buffer_copy(bytes(selected_mode));self.connector=U(c.contents.connector_id)
                    e=self.lib.drmModeGetEncoder(self.fd,c.contents.encoder_id)
                    if not e:raise RuntimeError('Connected display has no encoder')
                    try:self.crtc=e.contents.crtc_id or r.contents.crtcs[0]
                    finally:self.lib.drmModeFreeEncoder(e)
                    old=self.lib.drmModeGetCrtc(self.fd,self.crtc)
                    self.old_crtc=Crtc.from_buffer_copy(bytes(old.contents)) if old else None
                    if old:self.lib.drmModeFreeCrtc(old)
                    selected=True;break
                finally:self.lib.drmModeFreeConnector(c)
        finally:self.lib.drmModeFreeResources(r)
        if not selected:raise RuntimeError('No connected 1080p output')
        self.pool=os.open('/dev/wb_frame_pool',os.O_RDWR)
        version=bytearray(4);fcntl.ioctl(self.pool,0x80045743,version,True)
        if struct.unpack('<I',version)[0]!=6:raise RuntimeError('Shared scanout needs frame-pool ABI6')
        try:
            for i in range(count):self.frames.append(ScanFrame(self,i))
            self.frames[0].fill_initial_white()
            self.check(self.lib.drmModeSetCrtc(self.fd,self.crtc,self.frames[0].fb.value,0,0,
                       C.byref(self.connector),1,C.byref(self.mode)),'Initial modeset')
            self.front=self.frames[0];self.front.state='SCANNING'
        except BaseException:self.close();raise
    def check(self,ret,operation):
        if ret:raise OSError(C.get_errno(),operation)
    def poll(self,timeout=0):
        if self.pending is None:return
        if not select.select([self.fd],[],[],timeout)[0]:return
        events=os.read(self.fd,4096);offset=0
        while offset+8<=len(events):
            kind,length=struct.unpack_from('<II',events,offset)
            if length<8 or offset+length>len(events):raise RuntimeError('Invalid DRM event')
            if kind==2 and length>=32:
                token=struct.unpack_from('<Q',events,offset+8)[0]
                if token==self.pending.index+1:
                    if self.front:self.front.state='FREE'
                    self.front=self.pending;self.front.state='SCANNING';self.pending=None
            offset+=length
    def newframe(self):
        deadline=time.monotonic()+2
        while True:
            self.poll()
            for frame in self.frames:
                if frame.state=='FREE':frame.state='WRITING';return frame
            if time.monotonic()>deadline:raise TimeoutError('No released scanout buffer')
            self.poll(.05)
    def try_newframe(self):
        self.poll()
        for frame in self.frames:
            if frame.state=='FREE':frame.state='WRITING';return frame
        return None
    def discard(self,frame):
        if frame.state!='WRITING' or frame.active:raise RuntimeError('Cannot discard in-flight frame')
        frame.state='FREE'
    def discardframe(self,frame):
        # Keep the existing v19 no-UI runner/acceptance API available.
        self.discard(frame)
    def try_writeframe(self,frame):
        if frame.state!='WRITING' or frame.active:raise RuntimeError('PL still owns scanout')
        self.poll()
        if self.pending is not None:return False
        self.check(self.lib.drmModePageFlip(self.fd,self.crtc,frame.fb.value,1,C.c_void_p(frame.index+1)),'Pageflip')
        frame.state='PENDING';self.pending=frame;return True
    def writeframe(self,frame):
        if frame.state!='WRITING' or frame.active:raise RuntimeError('PL has not completed scanout frame')
        deadline=time.monotonic()+2
        while self.pending:
            if time.monotonic()>deadline:raise TimeoutError('DRM pageflip did not complete')
            self.poll(.05)
        self.check(self.lib.drmModePageFlip(self.fd,self.crtc,frame.fb.value,1,C.c_void_p(frame.index+1)),'Pageflip')
        frame.state='PENDING';self.pending=frame
    def close(self):
        deadline=time.monotonic()+2
        while self.pending:
            if time.monotonic()>deadline:raise TimeoutError('Refusing to free pending scanout')
            self.poll(.05)
        if hasattr(self,'crtc'):
            old=getattr(self,'old_crtc',None)
            ret=-1
            if old and old.mode_valid and old.buffer_id:
                ret=self.lib.drmModeSetCrtc(self.fd,self.crtc,old.buffer_id,old.x,old.y,C.byref(self.connector),1,C.byref(old.mode))
            if ret:self.check(self.lib.drmModeSetCrtc(self.fd,self.crtc,0,0,0,None,0,None),'Disable before release')
        for frame in self.frames:frame.state='FREE';frame.close()
        self.frames=[]
        if hasattr(self,'pool'):os.close(self.pool)
        self.drm.close()
