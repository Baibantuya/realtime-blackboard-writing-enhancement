"""Continuous sensor normalization owns its IO process and cannot stop camera DMA."""
import multiprocessing as mp
import queue
import time
from .service import SampleMailbox,_latest


def _sensor_worker(runtime_path,mailbox,ready,version,stamp,corners,status,stop,target,deadband):
    import sys,os,types,subprocess
    import numpy as np
    import cv2
    sys.path.insert(0,runtime_path)
    import auto_exposure as module
    from rgb565 import SparseRgbView
    cv2.setNumThreads(1)
    if hasattr(os,'nice'):os.nice(8)
    real_run=subprocess.run
    def guarded_run(command,*args,**kwargs):
        if any(str(item).startswith('--set-ctrl') for item in command):
            ready.value=False;version.value+=1;stamp.value=time.monotonic()
        return real_run(command,*args,**kwargs)
    module.subprocess=types.SimpleNamespace(run=guarded_run)
    # Preserve the original 48-source-pixel patch footprint on a 1/6 lattice.
    try:ae=module.BlackboardAutoExposure(target=target,deadband=deadband,patch_size=8)
    except Exception as exc:
        ready.value=False;_latest(status,dict(error=type(exc).__name__+': '+str(exc)));return
    revision=0
    while not stop.value:
        item=mailbox.take(revision)
        if item is None:time.sleep(.005);continue
        revision,sample=item
        try:
            points=np.frombuffer(corners,np.float64).reshape(4,2).copy()
            if not np.any(points):points=None
            else:points*=np.array((sample.pixels.shape[1],sample.pixels.shape[0]))/sample.source_size
            result=ae.update(SparseRgbView(sample.pixels),corners=points,now=time.monotonic())
            ready.value=bool(ae.ready_for_pl);stamp.value=time.monotonic()
            _latest(status,result)
        except Exception as exc:
            ready.value=False;_latest(status,dict(error=type(exc).__name__+': '+str(exc)))


class SensorService:
    def __init__(self,runtime_path,shape=(180,320),source_size=(1920,1080),target=80,deadband=6,context=None):
        import numpy as np
        self.context=context or mp.get_context('spawn')
        self.mailbox=SampleMailbox(self.context,shape,source_size)
        self.ready=self.context.RawValue('b',False);self.version=self.context.RawValue('q',0)
        self.stamp=self.context.RawValue('d',0.);self.corners=self.context.RawArray('d',8)
        self.stop=self.context.RawValue('b',False);self.status=self.context.Queue(maxsize=1)
        self.last={};self.next_sample=0.;self.np=np
        self.process=self.context.Process(target=_sensor_worker,args=(str(runtime_path),self.mailbox,
            self.ready,self.version,self.stamp,self.corners,self.status,self.stop,target,deadband),daemon=True)
        self.process.start()

    def submit(self,sample,corners=None):
        if sample.sampled_at<self.next_sample:return False
        self.next_sample=sample.sampled_at+.25
        points=self.np.frombuffer(self.corners,self.np.float64)
        points[:]=0 if corners is None else self.np.asarray(corners).reshape(-1)
        return self.mailbox.publish(sample)

    def snapshot(self,now):
        before=self.version.value
        ready=bool(self.ready.value and self.process.is_alive() and 0<=now-self.stamp.value<2.)
        after=self.version.value
        return ready and before==after,after

    def poll(self):
        while True:
            try:self.last=self.status.get_nowait()
            except queue.Empty:break
        return self.last

    def close(self):
        self.stop.value=True;self.process.join(1.)
        if self.process.is_alive():self.process.terminate();self.process.join(1.)
        self.status.close();self.status.cancel_join_thread()
