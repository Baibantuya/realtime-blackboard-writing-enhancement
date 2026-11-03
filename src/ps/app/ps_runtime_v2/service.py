"""Latest-only shared samples and a separate CPU process; producer never waits."""
from dataclasses import dataclass
import multiprocessing as mp
import queue
import time
import numpy as np
from .contracts import Sample,BoardState


@dataclass(frozen=True)
class WorkerFault:
    sequence: int
    sampled_at: float
    error: str


class SampleMailbox:
    def __init__(self,context,shape=(180,320),source_size=(1920,1080)):
        self.shape=tuple(shape);self.source_size=tuple(source_size)
        self.storage=context.RawArray('H',2*int(np.prod(shape)))
        self.header=context.RawArray('d',5)
        self.revision=context.RawValue('q',0);self.lock=context.Lock()
        self.overwritten=0;self.busy_skips=0

    def publish(self,sample):
        if sample.pixels.shape!=self.shape or sample.source_size!=self.source_size:
            raise ValueError('Mailbox raster mismatch')
        if not self.lock.acquire(False):self.busy_skips+=1;return False
        try:
            slot=(self.revision.value+1)&1
            values=np.frombuffer(self.storage,np.uint16).reshape((2,)+self.shape)
            np.copyto(values[slot],sample.pixels)
            self.header[:]=(sample.sequence,sample.capture_epoch,sample.sampled_at,slot,0)
            self.revision.value+=1
        finally:self.lock.release()
        return True

    def take(self,after_revision):
        if not self.lock.acquire(False):return None
        try:
            revision=self.revision.value
            if revision==after_revision:return None
            sequence,epoch,stamp,slot,_=self.header[:]
            values=np.frombuffer(self.storage,np.uint16).reshape((2,)+self.shape)
            sample=Sample(int(sequence),int(epoch),stamp,self.source_size,values[int(slot)])
            return revision,sample
        finally:self.lock.release()


def _latest(queue_,value):
    try:queue_.put_nowait(value);return
    except queue.Full:pass
    try:queue_.get_nowait()
    except queue.Empty:pass
    try:queue_.put_nowait(value)
    except queue.Full:pass


def _geometry_worker(mailbox,results,stop,artificial_delay,diagnostic_dir):
    import os
    import cv2
    from .geometry import GeometryEngine
    cv2.setNumThreads(1)
    if hasattr(os,'nice'):os.nice(8)
    engine=GeometryEngine();revision=0;remaining=60
    if diagnostic_dir:
        from pathlib import Path
        import json
        evidence=Path(diagnostic_dir);evidence.mkdir(parents=True,exist_ok=True)
    while not stop.value:
        item=mailbox.take(revision)
        if item is None:time.sleep(.005);continue
        revision,sample=item
        try:
            if artificial_delay:
                end=time.monotonic()+artificial_delay
                while time.monotonic()<end and not stop.value:time.sleep(.005)
                if stop.value:break
            result=engine.update(sample)
            if diagnostic_dir:
                request=evidence/'capture.request'
                if request.exists():request.unlink();remaining=60
                if remaining:
                    name=evidence/('sample_%010d'%sample.sequence)
                    np.save(str(name)+'.npy',sample.pixels,allow_pickle=False)
                    data=dict(sequence=sample.sequence,source_size=sample.source_size,
                        corners=None if result.corners is None else result.corners.tolist(),
                        state=result.state.value,version=result.transform_version,reason=result.reason,
                        motion_reliable=result.motion_reliable,edge_support=result.edge_support,
                        duration_ms=result.duration_ms,measurements=engine.debug)
                    name.with_suffix('.json').write_text(json.dumps(data),encoding='utf-8');remaining-=1
        except Exception as exc:
            result=WorkerFault(sample.sequence,sample.sampled_at,type(exc).__name__+': '+str(exc))
        _latest(results,result)


class GeometryService:
    def __init__(self,shape=(180,320),source_size=(1920,1080),interval=.5,max_age=1.2,
                 context=None,artificial_delay=0.,diagnostic_dir=None,startup_interval=.15):
        if interval<=0 or max_age<=0:raise ValueError('Invalid geometry timing')
        self.context=context or mp.get_context('spawn')
        self.mailbox=SampleMailbox(self.context,shape,source_size)
        self.results=self.context.Queue(maxsize=1);self.stop=self.context.RawValue('b',False)
        self.process=self.context.Process(target=_geometry_worker,
            args=(self.mailbox,self.results,self.stop,artificial_delay,diagnostic_dir),daemon=True)
        self.interval=interval;self.max_age=max_age;self.next_sample=0.
        self.startup_interval=min(interval,max(.001,startup_interval));self.initializing=True
        self.last_sequence=-1;self.last_result=None;self.last_error=None
        self.offered=self.accepted=self.stale=self.reordered=0
        self.process.start()

    def due(self,now):return now>=self.next_sample

    def submit(self,sample):
        if not self.due(sample.sampled_at):return False
        period=self.startup_interval if self.initializing else self.interval
        self.offered+=1;self.next_sample=sample.sampled_at+period
        return self.mailbox.publish(sample)

    def poll(self,now,capture_epoch):
        newest=None
        while True:
            try:item=self.results.get_nowait()
            except queue.Empty:break
            if isinstance(item,WorkerFault):self.last_error=item;continue
            if item.capture_epoch!=capture_epoch or not 0<=now-item.sampled_at<=self.max_age:
                self.stale+=1;continue
            if item.sequence<=self.last_sequence:self.reordered+=1;continue
            self.last_sequence=item.sequence;newest=item
        if newest is not None:
            self.accepted+=1;self.last_result=newest;self.last_error=None
            if newest.state in (BoardState.TRACK,BoardState.OCCLUDED):self.initializing=False
        return newest

    def healthy(self,now):
        return bool(self.process.is_alive() and self.last_result is not None and
                    0<=now-self.last_result.sampled_at<=self.max_age)

    def close(self):
        self.stop.value=True;self.process.join(1.)
        if self.process.is_alive():self.process.terminate();self.process.join(1.)
        self.results.close();self.results.cancel_join_thread()
