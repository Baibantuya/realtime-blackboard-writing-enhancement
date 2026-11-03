"""View/archive control independent of PL. Manual saves use confirmed scanout; automatic saves use owned clean snapshots."""
import ctypes as C
from collections import deque
from dataclasses import dataclass
from pathlib import Path
import time
import numpy as np
from pipeline_metrics import PipelineMetrics


class NativeUI:
    def __init__(self,library=None):
        self.lib=C.CDLL(str(Path(library or Path(__file__).parent/'libboard_ps_ui.so').resolve()))
        signatures={'ps_init':([],C.c_int),'ps_tick':([C.c_uint],None),'ps_key':([C.c_int],None),
            'ps_nav':([C.c_int],None),'ps_pointer':([C.c_int]*3,None),'ps_take':([],C.c_int),
            'ps_state':([C.c_int]*3+[C.c_double]+[C.c_int]*2,None),'ps_scope':([C.c_int],None),
            'ps_collapsed':([],C.c_int),'ps_render':([C.POINTER(C.c_uint8)],None),'ps_close':([],None)}
        for name,(args,returns) in signatures.items():
            f=getattr(self.lib,name);f.argtypes=args;f.restype=returns
        self.lib.ps_native_abi.restype=C.c_uint
        if self.lib.ps_native_abi()!=0x20:raise RuntimeError('Rebuild v20 native UI; ABI mismatch')
        self.lib.ps_render_changed.argtypes=[C.POINTER(C.c_uint8),C.c_uint];self.lib.ps_render_changed.restype=C.c_uint
        self.lib.ps_rates.argtypes=[C.c_int,C.c_int,C.c_int,C.c_double,C.c_double]
        if hasattr(self.lib,'ps_rectify_compute'):
            self.lib.ps_rectify_compute.argtypes=[C.c_double,C.c_int,C.c_double]
            self.lib.ps_rectify_compute.restype=None
        self.lib.ps_blend565.argtypes=[C.c_void_p,C.c_size_t,C.c_void_p,C.c_size_t,C.c_void_p,C.c_uint,C.c_uint]
        self.lib.ps_copy565.argtypes=[C.c_void_p,C.c_size_t,C.c_void_p,C.c_size_t,C.c_uint,C.c_uint]
        self.lib.ps_blend565.restype=self.lib.ps_copy565.restype=None
        if not self.lib.ps_init():raise RuntimeError('LVGL is already owned or cannot initialize')
        self.previous=None;self.overlay=np.zeros((320,1920,4),np.uint8)
        self.patch=None;self.revision=0

    def tick(self,now):
        ms=int(now*1000);self.lib.ps_tick(0 if self.previous is None else max(0,min(ms-self.previous,60000)));self.previous=ms

    def render(self):
        revision=int(self.lib.ps_render_changed(self.overlay.ctypes.data_as(C.POINTER(C.c_uint8)),self.revision))
        if not revision:return
        self.revision=revision
        ys,xs=np.nonzero(self.overlay[:,:,3])
        self.patch=None if not len(xs) else (int(ys.min())+760,int(xs.min()),
            self.overlay[ys.min():ys.max()+1,xs.min():xs.max()+1].copy())

    def blend(self,image):
        """Modify only UI bounding rectangle; return original pixels for clean archives."""
        if self.patch is None:return None
        y,x,rgba=self.patch;h,w=rgba.shape[:2];region=image[y:y+h,x:x+w]
        original=np.empty((h,w),np.uint16)
        self.lib.ps_blend565(region.ctypes.data,region.strides[0],rgba.ctypes.data,rgba.strides[0],original.ctypes.data,w,h)
        return y,x,original

    def copy(self,destination,source):
        if source.dtype!=np.uint16 or destination.dtype!=np.uint16 or source.shape!=destination.shape:
            raise ValueError('RGB565 display copy shape/dtype')
        if source.strides[1]!=2 or destination.strides[1]!=2:raise ValueError('Noncontiguous rows')
        self.lib.ps_copy565(destination.ctypes.data,destination.strides[0],source.ctypes.data,source.strides[0],source.shape[1],source.shape[0])

    def close(self):self.lib.ps_close()


@dataclass(frozen=True)
class FrameInfo:
    mode:int
    sequence:int
    page:int=0
    kind:str='video'
    identity:object=None


@dataclass(frozen=True)
class Page:
    pixels:np.ndarray
    mode:int
    sequence:int
    reason:str='manual'


class Rate:
    def __init__(self):self.times=deque();self.last=None
    def add(self,now,identity):
        if identity!=self.last:self.times.append(now);self.last=identity
    def value(self,now):
        while self.times and now-self.times[0]>2:self.times.popleft()
        return (len(self.times)-1)/(self.times[-1]-self.times[0]) if len(self.times)>1 and self.times[-1]>self.times[0] else 0.


class Presentation:
    """Nonblocking display ownership. Stages continue when history is visible.

    Video pixel copies occur for raw/rectified scanout or explicit save/repaint.
    Deep mode writes from PL directly to scanout and blends only the UI region.
    """
    def __init__(self,display,native,hz=30,metrics=None):
        if not np.isfinite(hz) or not 1<=hz<=60:raise ValueError('display Hz must be 1..60')
        self.frame_epochs=None;self.metrics=metrics or PipelineMetrics();self._last_state=None;self.last_presented=None
        self.display=display;self.native=native;self.interval=1/hz;self.last_submit=-1e9
        self.mode=2;self.page=0;self.pages=[];self.front=None;self.pending=None;self.safe=False
        self.video_rate=Rate();self.processing_rate=Rate();self.notice=0;self.notice_until=0
        self.last_ui=-1e9;self.events=[];self.submissions=0;self.full_copies=0
        self.next_fps=0;self.rates=(0.,0.);self._snapshot_ids=set()

    def message(self,notice,now):self.notice=notice;self.notice_until=now+3;self.last_ui=-1e9

    def poll(self,now):
        self.display.poll()
        if self.pending is not None:
            frame,info,patch,revision,submitted=self.pending
            if self.display.front is frame and self.display.pending is None:
                self.front=(frame,info,patch,revision);self.pending=None
                if info.kind=='video':
                    identity=(info.mode,info.identity if info.identity is not None else info.sequence)
                    if identity!=self.last_presented:
                        self.video_rate.add(now,identity);self.metrics.add('display_presented',identity,now)
                        self.last_presented=identity
            elif now-submitted>2:raise TimeoutError('DRM pageflip confirmation timed out')

    def clean_front(self):
        if self.front is None:return None
        frame,info,patch,_=self.front
        # Only the currently SCANNING frame is CPU-readable here; never a PL destination.
        image=frame.snapshot_displayed();self.full_copies+=1
        if patch is not None:
            y,x,original=patch;h,w=original.shape;image[y:y+h,x:x+w]=original
        return image

    def can_record(self):
        return (not self.page and self.front is not None and self.front[1].kind=='video'
            and self.front[1].page==0 and self.front[1].mode==self.mode
            and (self.mode==0 or (self.safe and (self.frame_epochs is None or self.front[1].identity is not None and self.front[1].identity[-2:]==self.frame_epochs))))

    def command(self,key,now):
        if 0xF1<=key<=0xF3:
            self.mode=key-0xF1;self.page=0;self.message(4,now)
        elif key in (0xF4,0xF5):
            self.page=(self.page+(-1 if key==0xF4 else 1))%(len(self.pages)+1);self.last_ui=-1e9
        elif key==0xF7:
            callback=getattr(self,'on_reset',None)
            if callback is not None:callback()
        elif key==0xF6:
            if not self.can_record():self.message(2,now);return
            if len(self.pages)>=32:self.message(3,now);return
            image=self.clean_front();image.flags.writeable=False;info=self.front[1]
            self.pages.append(Page(image,info.mode,info.sequence));self.message(1,now)
            self.events.append(dict(event='saved',page=len(self.pages),mode=info.mode,sequence=info.sequence))

    def save_snapshot(self,pixels,sequence,mode=2,reason='large_erase',now=None):
        """Archive a CPU-owned, UI-free pre-erase image without changing the view.

        The caller owns synchronization and selects the last intact board before
        erase. This is deliberately independent of front/pending pageflip and
        current history selection. Copy before the caller can reuse its buffer.
        """
        now=time.monotonic() if now is None else now
        identity=(str(reason),int(mode),int(sequence))
        if identity in self._snapshot_ids:return False
        if mode not in (0,1,2):raise ValueError('Snapshot mode must be 0, 1 or 2')
        image=np.asarray(pixels)
        if image.dtype!=np.uint16 or image.ndim!=2:
            raise ValueError('Snapshot must be a clean RGB565 image')
        if len(self.pages)>=32:
            self.message(3,now);return False
        image=np.array(image,copy=True,order='C');image.flags.writeable=False
        self.pages.append(Page(image,int(mode),int(sequence),str(reason)))
        self._snapshot_ids.add(identity)
        self.full_copies+=1;self.message(1,now)
        self.events.append(dict(event='saved',page=len(self.pages),mode=int(mode),
                                sequence=int(sequence),reason=str(reason)))
        return True

    def wanted(self,mode,now):
        return (not self.page and mode==self.mode and (mode==0 or self.safe)
            and self.pending is None and self.display.pending is None and now-self.last_submit>=self.interval)

    def reserve_deep(self,now):
        # Rendering into a free third buffer may overlap a pending pageflip.
        # Throttle presentation at completion, not allocation at stage launch.
        if self.page or self.mode!=2 or not self.safe:return None
        return self.display.try_newframe()

    def submit(self,frame,info,now,prepared=None):
        patch=frame.edit_rgb565(self.native.blend) if prepared is None else prepared[0]
        if not self.display.try_writeframe(frame):raise RuntimeError('Display submission ownership changed')
        if info.kind=='video' and (info.mode,info.identity if info.identity is not None else info.sequence)!=self.last_presented:
            self.metrics.add('display_submitted',(info.mode,info.identity if info.identity is not None else info.sequence),now)
        self.pending=(frame,info,patch,self.native.revision,now);self.last_submit=now;self.submissions+=1

    def offer(self,mode,sequence,source,now,context=None):
        """Source may be a completed ScanFrame, ring buffer, or CPU camera view."""
        direct=hasattr(source,'edit_rgb565')
        if not self.wanted(mode,now):
            if direct:self.display.discard(source)
            return False
        frame=source if direct else self.display.try_newframe()
        if frame is None:return False
        if not direct:
            if hasattr(source,'invalidate'):source.invalidate()
            def copy_blend(image):
                self.native.copy(image,np.asarray(source));return self.native.blend(image)
            patch=frame.edit_rgb565(copy_blend);self.full_copies+=1
        identity=None if context is None else context.identity
        self.submit(frame,FrameInfo(mode,int(sequence),identity=identity),now,None if direct else (patch,));return True

    def guidance(self,screen,sequence,now):
        if self.page or self.mode==0 or self.pending is not None or self.display.pending is not None:return
        if now-self.last_submit<self.interval:return
        frame=self.display.try_newframe()
        if frame is not None:
            frame.write_direct_rgb565(screen);self.full_copies+=1
            self.submit(frame,FrameInfo(self.mode,int(sequence),kind='guidance'),now)

    def tick(self,now):
        self.poll(now);self.native.tick(now)
        while True:
            key=self.native.lib.ps_take()
            if not key:break
            self.command(key,now)
        if now>=self.notice_until:self.notice=0
        if now>=self.next_fps:
            self.rates=(self.video_rate.value(now),self.processing_rate.value(now));self.next_fps=now+1;self._rates_due=True
        if now-self.last_ui>=.1:
            info=self.front[1] if self.front else FrameInfo(self.mode,0)
            # Do not show a selected mode/page until its pageflip is confirmed.
            rate=self.rates[1 if info.page else 0]
            state=(info.mode,info.page,len(self.pages),round(rate,1),self.can_record(),self.notice)
            if state!=self._last_state:
                self.native.lib.ps_state(*state);self._last_state=state;self._rates_due=True
            if getattr(self,'_rates_due',True):
                guiding=info.kind=='guidance' or (not self.safe and info.mode!=0)
                source=self.metrics.source(2 if info.page else 0 if guiding else info.mode,now)
                if hasattr(self.native.lib,'ps_rates'):
                    self.native.lib.ps_rates(info.mode,info.page,int(guiding),source,self.metrics.rates['display_presented'].value(now))
                if info.mode==1 and not info.page and not guiding and hasattr(self.native.lib,'ps_rectify_compute'):
                    core=self.metrics.rectify_compute.value(now)
                    self.native.lib.ps_rectify_compute(core or 0.,self.metrics.rectify_compute_state(now),
                        self.metrics.rates['display_presented'].value(now))
                self._rates_due=False
            self.native.render();self.last_ui=now
        if self.pending is not None or self.display.pending is not None:return
        if now-self.last_submit<self.interval:return
        if self.page:
            saved=self.pages[self.page-1];info=FrameInfo(saved.mode,saved.sequence,self.page,'history')
            if self.front and self.front[1]==info and self.front[3]==self.native.revision:return
            base=saved.pixels
        elif self.front and self.front[1].page==0 and self.front[3]!=self.native.revision and (self.safe or self.front[1].mode==0 or self.front[1].kind=='guidance'):
            # Repaint paused camera/guidance promptly; reusing the sequence never adds FPS.
            base=self.clean_front();info=self.front[1]
        else:return
        frame=self.display.try_newframe()
        if frame is not None:
            frame.write_direct_rgb565(base);self.full_copies+=1;self.submit(frame,info,now)

    def processed(self,sequence,now):self.processing_rate.add(now,sequence)
