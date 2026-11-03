"""Exact-frame content work lives in a process, not the video polling loop."""
from dataclasses import dataclass
from collections import OrderedDict
import multiprocessing as mp
import queue
import time
import numpy as np


class PreEraseArchive:
    """Retain a complete, person-free Q page before a progressive large wipe.

    Sparse inspection is capped at 2 Hz. Full RGB565 copies occur only for a
    stable initial page or stable additions, never after erase has started.
    Coordinates and sensor epochs invalidate comparisons rather than save a
    camera/exposure transition as an erasure.
    """
    def __init__(self,interval=.5,loss_fraction=.30):
        self.interval=interval;self.loss_fraction=loss_fraction
        self.saved=0;self.reset()

    def reset(self):
        self.identity=None;self.pixels=None;self.ink=None;self.sequence=None
        self.next_sample=0.;self.stable=0;self.erase_confirmations=0;self.erase_recoveries=0
        self.last_mask=None;self.erase_started=False;self.last_loss=0.
        self.saved_erase=False;self.after_erase_mask=None;self.rearm_count=0
        self.partial_rewrite_count=0;self.partial_rewrite_mask=None

    def observe(self,pixels,sequence,identity,rect,metadata,now,save):
        import cv2
        coord_identity = identity[:2] if isinstance(identity, (tuple, list)) and len(identity) >= 2 else identity
        prior_coord = self.identity[:2] if isinstance(self.identity, (tuple, list)) and len(self.identity) >= 2 else self.identity
        if coord_identity != prior_coord:
            self.reset(); self.identity = identity
        else:
            self.identity = identity
        if now<self.next_sample:return False
        self.next_sample=now+self.interval
        # The metadata belongs to this exact committed Q frame. Never accept
        # a body, unobserved tile or bootstrap frame into the retained page.
        x,y,w,h=rect
        tiles=metadata[y//16:(y+h)//16,x//16:(x+w)//16]
        visible=(tiles&(1<<16))!=0
        blocked=(tiles&((1<<19)|(1<<20)))!=0
        initializing=(tiles&(1<<17))!=0
        if not tiles.size or np.mean(visible&~blocked)<.97 or np.any(initializing):
            self.stable=0;self.erase_confirmations=0
            self.partial_rewrite_count=0;self.partial_rewrite_mask=None;return False
        current=np.array(pixels[y:y+h:4,x:x+w:4]!=np.uint16(0xffff),copy=True)
        # Palette color changes do not constitute erasure. A one-sample halo
        # rejects quantization sparkle/one-pixel pen-edge movement as evidence.
        nearby=cv2.dilate(current.astype(np.uint8),np.ones((3,3),np.uint8))!=0
        if self.saved_erase:
            # One progressive wipe is one archive event. After saving at 30%
            # loss, never adopt its remaining half-page as a new full page.
            # Only stable new writing starts a new archive generation.
            old_near=cv2.dilate(self.after_erase_mask.astype(np.uint8),np.ones((3,3),np.uint8))!=0
            additions=np.count_nonzero(current&~old_near)
            if additions>=max(32,.10*np.count_nonzero(self.after_erase_mask)):
                self.rearm_count+=1
                if self.rearm_count<3:return False
                self.saved_erase=False;self.after_erase_mask=None
            else:
                self.rearm_count=0
                # Follow erasure only; never accumulate new text into this
                # baseline before it has passed the rearm observation test.
                self.after_erase_mask &= nearby
                return False
        if self.ink is not None:
            total=int(np.count_nonzero(self.ink))
            lost=self.ink&~nearby
            lost_count=int(np.count_nonzero(lost))
            self.last_loss=lost_count/max(total,1)
            if not .05<=self.last_loss<self.loss_fraction:
                self.partial_rewrite_count=0;self.partial_rewrite_mask=None
            if self.erase_started:
                if self.last_loss<.05:
                    self.erase_recoveries+=1
                    if self.erase_recoveries>=3:
                        # A wipe that returns to the intact page is canceled;
                        # replace the baseline only after three clean samples.
                        self.erase_started=False;self.erase_recoveries=0
                        self.erase_confirmations=0;self.stable=0
                        self.pixels=np.array(pixels,copy=True,order='C')
                        self.pixels.flags.writeable=False
                        self.ink=current.copy();self.sequence=sequence
                        self.last_mask=current.copy()
                        return False
                else:
                    self.erase_recoveries=0
            elif self.last_loss>=.05:
                self.erase_started=True;self.erase_recoveries=0
            if total>=64 and lost_count>=32 and self.last_loss>=self.loss_fraction:
                self.erase_confirmations+=1
                if self.erase_confirmations>=2:
                    if save(self.pixels,self.sequence,mode=2,reason='large_erase',now=now):
                        self.saved+=1;identity=self.identity;self.reset();self.identity=identity
                        self.saved_erase=True;self.after_erase_mask=current.copy()
                        self.next_sample=now+self.interval
                        return True
                return False
            self.erase_confirmations=0
            # A partial wipe followed by substantial, stable NEW writing is a
            # completed editing event. It must not pin the pre-edit page forever.
            # A mere pause or static hand is never a reset condition: progressive
            # wipes may take minutes and still need the original intact page.
            if self.erase_started and .05<=self.last_loss<self.loss_fraction:
                original_near=cv2.dilate(self.ink.astype(np.uint8),np.ones((3,3),np.uint8))!=0
                additions=int(np.count_nonzero(current&~original_near))
                consistent=False
                if self.partial_rewrite_mask is not None:
                    prior_near=cv2.dilate(self.partial_rewrite_mask.astype(np.uint8),np.ones((3,3),np.uint8))!=0
                    difference=np.count_nonzero(current&~prior_near)+np.count_nonzero(self.partial_rewrite_mask&~nearby)
                    consistent=difference<=max(4,.02*np.count_nonzero(current))
                if additions>=max(32,.10*total):
                    self.partial_rewrite_count=self.partial_rewrite_count+1 if consistent else 1
                    self.partial_rewrite_mask=current.copy()
                    if self.partial_rewrite_count>=3:
                        self.pixels=np.array(pixels,copy=True,order='C');self.pixels.flags.writeable=False
                        self.ink=current.copy();self.sequence=sequence;self.last_mask=current.copy()
                        self.erase_started=False;self.erase_recoveries=0;self.stable=0
                        self.partial_rewrite_count=0;self.partial_rewrite_mask=None
                        self.last_loss=0.
                        return False
                else:
                    self.partial_rewrite_count=0;self.partial_rewrite_mask=None
            # Once a wipe begins, keep the whole pre-wipe page even if it takes
            # several minutes to pass the large-erase threshold.
            if self.erase_started:return False
        if self.last_mask is None:
            stable=False
        else:
            old_near=cv2.dilate(self.last_mask.astype(np.uint8),np.ones((3,3),np.uint8))!=0
            differences=np.count_nonzero(current&~old_near)+np.count_nonzero(self.last_mask&~nearby)
            stable=differences<=max(4,.02*np.count_nonzero(current))
        self.stable=self.stable+1 if stable else 0
        self.last_mask=current
        if self.stable<2:return False
        # Do not recopy a full unchanged page at the sampling frequency.
        additions=0 if self.ink is None else np.count_nonzero(current&~cv2.dilate(self.ink.astype(np.uint8),np.ones((3,3),np.uint8)).astype(bool))
        if self.ink is None or additions>=max(8,.02*np.count_nonzero(self.ink)):
            self.pixels=np.array(pixels,copy=True,order='C');self.pixels.flags.writeable=False
            self.ink=current.copy();self.sequence=sequence
        return False


@dataclass(frozen=True)
class ContentJob:
    key: object
    a: np.ndarray
    b: np.ndarray
    kind: str = 'complete'


@dataclass(frozen=True)
class ContentResult:
    key: object
    metadata: np.ndarray
    hold: bool
    valid_until: float
    reason: str


class ResultSlots:
    """No pipe reads: a worker killed halfway through a result cannot block video."""
    def __init__(self,context,shape,count):
        self.shape=tuple(shape);self.count=count;self.size=int(np.prod(shape));self.cursor=0
        self.data=context.RawArray('I',self.size*count)
        self.headers=context.RawArray('d',count*9)
        self.reasons=context.RawArray('B',count*256)
        self.locks=[context.Lock() for _ in range(count)]
        self.produced=context.RawValue('q',0);self.last_duration=context.RawValue('d',0.)

    def put(self,result):
        for offset in range(self.count):
            slot=(self.cursor+offset)%self.count
            if not self.locks[slot].acquire(False):continue
            try:
                header=np.frombuffer(self.headers,np.float64).reshape(self.count,9)[slot]
                header[8]=0
                np.copyto(np.frombuffer(self.data,np.uint32).reshape(self.count,*self.shape)[slot],result.metadata)
                text=np.frombuffer(self.reasons,np.uint8).reshape(self.count,256)[slot]
                encoded=result.reason.encode('utf-8')[:255];text[:]=0;text[:len(encoded)]=np.frombuffer(encoded,np.uint8)
                key=result.key
                header[:]=(key.sequence,key.capture_epoch,key.board_epoch,key.history_epoch,
                           key.captured_at,key.photometry_epoch,result.valid_until,result.hold,1)
                self.cursor=(slot+1)%self.count;return True
            finally:self.locks[slot].release()
        return False

    def take(self,key):
        for slot,lock in enumerate(self.locks):
            if not lock.acquire(False):continue
            try:
                header=np.frombuffer(self.headers,np.float64).reshape(self.count,9)[slot]
                if not header[8]:continue
                if tuple(int(header[i]) for i in (1,0,2,3,5))!=key.identity:continue
                data=np.frombuffer(self.data,np.uint32).reshape(self.count,*self.shape)[slot].copy()
                text=np.frombuffer(self.reasons,np.uint8).reshape(self.count,256)[slot].tobytes().split(b'\0',1)[0].decode('utf-8','replace')
                result=ContentResult(key,data,bool(header[7]),header[6],text)
                header[8]=0;return result
            finally:lock.release()
        return None


def _worker(runtime_path,width,height,rect,jobs,acks,results,stop,delay):
    import sys,os,cv2
    sys.path.insert(0,runtime_path)
    from scene_tracking import SceneTracker,RGB565Lattice,FrameContext
    cv2.setNumThreads(1)
    if hasattr(os,'nice'):os.nice(8)
    tracker=None;epoch=None;pending=OrderedDict();provisional=OrderedDict()
    while not stop.value:
        while True:
            try:key,commit=acks.get_nowait()
            except queue.Empty:break
            packet=pending.pop(key.identity,None)
            if not commit:provisional.pop(key.identity,None)
            if packet is not None and commit and tracker is not None and key.board_epoch==epoch:
                try:tracker.committed(packet)
                except ValueError:pass  # A reset explicitly invalidates old acknowledgments.
        try:job=jobs.get(timeout=.01)
        except queue.Empty:continue
        if delay:
            end=time.monotonic()+delay
            while time.monotonic()<end and not stop.value:time.sleep(.005)
            if stop.value:break
        key=job.key
        started=time.monotonic()
        try:
            if epoch!=key.board_epoch:
                tracker=SceneTracker(width,height);epoch=key.board_epoch;pending.clear();provisional.clear()
                x,y,w,h=rect;xx=np.arange(tracker.gw)*16;yy=np.arange(tracker.gh)*16
                tracker.roi=((xx[None,:]>=x)&(xx[None,:]+16<=x+w)&
                             (yy[:,None]>=y)&(yy[:,None]+16<=y+h))
            context=FrameContext(key.capture_epoch,key.sequence,key.board_epoch,
                                 key.history_epoch*1048576+key.photometry_epoch,key.captured_at)
            if job.kind=='finish':
                packet=provisional.pop(key.identity,None)
                if packet is None:raise ValueError('Prepared frame was canceled or missed its deadline')
            else:
                a=RGB565Lattice(width,height,tracker.step,job.a)
                # Only a new coordinate epoch may establish the caller's
                # startup reference. A runtime observation failure is not trust.
                packet=tracker.prepare(a,context,trusted_bootstrap=(
                    tracker.needs_bootstrap and tracker.reference is None))
            if job.kind=='prepare':
                provisional[key.identity]=packet
                while len(provisional)>12:provisional.popitem(last=False)
                continue
            b=RGB565Lattice(width,height,tracker.step,job.b)
            packet=tracker.refine(packet,b,context)
            pending[key.identity]=packet
            while len(pending)>12:pending.popitem(last=False)
            result=ContentResult(key,packet.metadata,packet.hold,packet.valid_until,packet.reason)
        except Exception as exc:
            result=ContentResult(key,np.zeros(((height+15)//16,width//16),np.uint32),
                                 True,key.captured_at,'content_fault:'+type(exc).__name__+': '+str(exc))
        results.last_duration.value=(time.monotonic()-started)*1000
        if results.put(result):results.produced.value+=1
        else:pending.pop(key.identity,None)


class ContentService:
    def __init__(self,runtime_path,width,height,target_rect,capacity=3,context=None,delay=0.):
        self.context=context or mp.get_context('spawn')
        self.jobs=self.context.Queue(capacity*2);self.acks=self.context.Queue(capacity*2)
        self.results=ResultSlots(self.context,((height+15)//16,width//16),capacity*2)
        self.stop=self.context.RawValue('b',False)
        self.process=self.context.Process(target=_worker,args=(str(runtime_path),width,height,
            target_rect,self.jobs,self.acks,self.results,self.stop,delay),daemon=True)
        self.pending=set();self.ready={};self.capacity=capacity
        self.rejected=self.expired=self.faults=0
        self.offered=self.received=0;self.last_reason=None
        self.process.start()

    def offer(self,key,a,b):
        prepared=key.identity in self.pending
        if not prepared and len(self.pending)>=self.capacity:self.rejected+=1;return False
        job=ContentJob(key,None if prepared else np.array(a,copy=True,order='C'),
                       np.array(b,copy=True,order='C'),'finish' if prepared else 'complete')
        try:self.jobs.put_nowait(job)
        except queue.Full:self.rejected+=1;return False
        self.pending.add(key.identity);self.offered+=1;return True

    def prepare(self,key,a):
        if key.identity in self.pending or len(self.pending)>=self.capacity:return False
        job=ContentJob(key,np.array(a,copy=True,order='C'),None,'prepare')
        try:self.jobs.put_nowait(job)
        except queue.Full:self.rejected+=1;return False
        self.pending.add(key.identity);return True

    def poll(self,key,now):
        result=self.results.take(key)
        if result is not None:self.received+=1;self.last_reason=result.reason
        if result is not None and result.reason.startswith('content_fault:'):self.faults+=1
        if result is not None and (result.valid_until<now or result.hold):
            self.expired+=1
            return ContentResult(result.key,result.metadata,True,result.valid_until,result.reason)
        return result

    def acknowledge(self,key,commit):
        known=key.identity in self.pending
        self.pending.discard(key.identity);self.ready.pop(key.identity,None)
        if not known:return
        try:self.acks.put_nowait((key,commit))
        except queue.Full:self.faults+=1

    def close(self):
        self.stop.value=True;self.process.join(1.)
        if self.process.is_alive():self.process.terminate();self.process.join(1.)
        for q in (self.jobs,self.acks):q.close();q.cancel_join_thread()
