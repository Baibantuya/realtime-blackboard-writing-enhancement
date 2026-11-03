"""Hardware adapter. Reuses sealed device drivers, never the legacy event loop."""
from collections import deque
from pathlib import Path
import json
import sys
import time
import numpy as np
from . import __version__
from .contracts import BoardState,FrameKey,Sample,Transform
from .scheduler import Stage
from .content import ContentService,PreEraseArchive
from .service import GeometryService
from .sensor import SensorService
from runtime_paths import DATA


class PairPool:
    def __init__(self,allocate,count,width,height):
        self.pairs=[];self.owned=set()
        try:
            for _ in range(count):
                a=allocate(shape=(height,width),dtype='uint16')
                try:b=allocate(shape=(height,width),dtype='uint16')
                except BaseException:a.freebuffer();raise
                a.flush();b.flush();self.pairs.append((a,b))
        except BaseException:self.close();raise

    def reserve(self):
        for index,pair in enumerate(self.pairs):
            if index not in self.owned:self.owned.add(index);return pair
        return None

    def release(self,a,b):
        index=next(i for i,p in enumerate(self.pairs) if p[0] is a and p[1] is b)
        if index not in self.owned:raise RuntimeError('Double pair release')
        self.owned.remove(index)

    def close(self):
        if self.owned:raise RuntimeError('DMA still owns pair pool')
        for a,b in self.pairs:a.freebuffer();b.freebuffer()
        self.pairs.clear()


def initial_rect(corners,width,height):
    p=np.asarray(corners)
    bw=(np.linalg.norm(p[1]-p[0])+np.linalg.norm(p[2]-p[3]))/2
    bh=(np.linalg.norm(p[3]-p[0])+np.linalg.norm(p[2]-p[1]))/2
    if bw/bh>width/height:w=width;h=max(32,round(width*bh/bw))
    else:h=height;w=max(32,round(height*bw/bh))
    # Tile-aligned fixed board coordinates simplify the ROI contract.
    w=max(32,min(width,int(w)//16*16));h=max(32,min(height,int(h)//16*16))
    return ((width-w)//32*16,(height-h)//32*16,w,h)


def inset_corners(corners,margin=6.):
    """Intersect inward-offset edge lines, in original camera pixels."""
    p=np.asarray(corners,dtype=float);center=p.mean(axis=0);normals=[];offsets=[]
    for a,b in zip(p,np.roll(p,-1,axis=0)):
        edge=b-a;normal=np.array((-edge[1],edge[0]));length=np.linalg.norm(normal)
        if length<2*margin:raise ValueError('Board too narrow for inner crop')
        normal/=length
        if np.dot(center-a,normal)<0:normal=-normal
        normals.append(normal);offsets.append(np.dot(normal,a)+margin)
    out=np.array([np.linalg.solve(np.array((normals[i-1],normals[i])),
                 np.array((offsets[i-1],offsets[i]))) for i in range(4)])
    if not np.all(np.isfinite(out)):raise ValueError('Invalid inward board crop')
    return out


class BoardIO:
    def __init__(self,runtime,width=1920,height=1080,capacity=3,display=True,timeout=2.):
        self.runtime=Path(runtime).resolve();sys.path.insert(0,str(self.runtime))
        from verify_manifest import verify_package
        from scene_registers import from_hwh
        from scene_stage import SceneQuantizeStage
        from pynq import allocate,MMIO
        from baseline_stages import RectifierStage,RestoreStage
        from v4l2_rgb565 import V4l2Rgb565Stream
        from isp_white_balance import IspWhiteBalance
        from pipeline_metrics import PipelineMetrics
        from scene_tracking import FrameContext
        from types import SimpleNamespace
        self.manifest=verify_package(self.runtime)
        self.config=json.loads((self.runtime/'config/deployment.json').read_text())
        self.hwh=self.runtime/self.config['hwh'];mapping=from_hwh(self.hwh)
        self.width=width;self.height=height;self.capacity=capacity
        self.FrameContext=FrameContext
        self.pool=PairPool(allocate,capacity,width,height)
        self.rectifier=RectifierStage(timeout)
        # COR1 is optional on existing R3 hardware. Never derive compute time
        # by subtracting overlapping AXI wait counters from wall-clock time.
        self.coordinate_counter=self.rectifier.ip.read(0x68)==0x434f5231
        self.coordinate_sequence=None
        from pynq import Clocks
        self.coordinate_clock_hz=float(Clocks.fclk0_mhz)*1e6
        borrowed=SimpleNamespace(slots=[SimpleNamespace(buffer=self.pool.pairs[0][1])])
        self.restore=RestoreStage(borrowed,timeout,True,8,180)
        self.quantizer=SceneQuantizeStage(MMIO(mapping['base'],mapping['length']),mapping['registers'],
            allocate,width,height,mapping['abi'],mapping['vlnv'],timeout)
        self.output=allocate(shape=(height,width),dtype='uint16');self.output.flush()
        self.quantizer.set_thresholds(ink_delta=26,erase_delta=16,color_margin=24)
        self.display=None;self.native=None;self.ui=None;self.inputs=None;self.frontend=None
        self.metrics=PipelineMetrics()
        self.metrics.coordinate_counter_available=self.coordinate_counter
        if display:
            from shared_scanout import SharedScanout
            from archive_ui import NativeUI,Presentation
            from scene_input import LinuxInput
            from osd_frontend import BoardFrontend
            self.display=SharedScanout(width,height,3)
            self.native=NativeUI(self.runtime/'ui/libboard_ps_ui.so')
            self.ui=Presentation(self.display,self.native,30.,metrics=self.metrics)
            self.inputs=LinuxInput()
            self.frontend=BoardFrontend(asset_dir=self.runtime/'ui/assets')
        self.camera=V4l2Rgb565Stream('/dev/video0',width,height,4)
        self.camera.metrics=self.metrics
        self.awb=IspWhiteBalance(self.hwh)
        self.geometry=GeometryService(source_size=(width,height),diagnostic_dir=str(DATA/'geometry'))
        self.sensor=SensorService(self.runtime,source_size=(width,height))
        self.content=None;self.target_rect=None;self.board_epoch=1;self.latest=None
        self.last_transform=None
        self.crop_source_pixels=6.;self.erase_archive=PreEraseArchive(loss_fraction=.15)
        self.applied_transform=None;self.completed_transform=None;self.pl_geometry_echo=None
        self.state=BoardState.SEARCH;self.observation=None;self.initialized=False
        # A bright wall must not drive exposure away from an already usable
        # board before the first quad arrives. Bounded fallback still permits
        # coarse AE to help discovery in an initially extreme lighting scene.
        self.initial_metering_deadline=time.monotonic()+3.
        self.stages={Stage.RECTIFY:self.rectifier,Stage.RESTORE:self.restore,Stage.QUANTIZE:self.quantizer}
        self.last_display_preview=0.;self.guidance_interval=.1
        self.counts=dict(capture_latest_replacements=0,content_updates=0,content_holds=0,
                         preview_presented=0,manual_resets=0,geometry_resets=0,auto_saved_pages=0)
        self.timings={};self.arrivals=deque(maxlen=512)

    def sensor_sample_allowed(self,now):
        return ((self.observation is not None and self.observation.corners is not None)
                or now>=self.initial_metering_deadline)

    def pump_camera(self,now):
        # The stable camera driver permits one consumer lease. Its own drain
        # thread already keeps the newest pending buffer while Rectify owns it.
        if self.latest is not None or self.camera.consumer is not None:return
        try:lease=self.camera.acquire(.001)
        except TimeoutError:return
        if self.latest is not None:
            self.latest.release();self.counts['capture_latest_replacements']+=1
        self.latest=lease
        sensor_allowed=self.sensor_sample_allowed(now)
        sample_due=self.geometry.due(now) or (sensor_allowed and now>=self.sensor.next_sample)
        preview=(self.ui is not None and self.state in (BoardState.SEARCH,BoardState.CONFIRM,BoardState.UNOBSERVABLE)
                 and now-self.last_display_preview>=self.guidance_interval)
        raw_mode=self.ui is not None and self.ui.mode==0
        if sample_due or preview or raw_mode:
            lease.begin_cpu()
            try:
                if sample_due:
                    sample=Sample(lease.sequence,getattr(lease,'capture_epoch',0),now,
                                  (self.width,self.height),lease.frame[::6,::6])
                    self.geometry.submit(sample)
                    corners=None if self.observation is None else self.observation.corners
                    if sensor_allowed:self.sensor.submit(sample,corners)
                if raw_mode:self.ui.offer(0,lease.sequence,lease.frame,now)
                elif preview:
                    from osd_frontend import GuidanceSpec
                    spec=GuidanceSpec('search' if self.state==BoardState.SEARCH else 'confirming',self.state.value)
                    self.ui.guidance(self.frontend.render_guidance(lease.frame,spec),lease.sequence,now)
                    self.last_display_preview=now;self.counts['preview_presented']+=1
            finally:lease.end_cpu()

    def update_geometry(self,now,capture_epoch):
        result=self.geometry.poll(now,capture_epoch)
        if result is None:
            if self.observation is not None and not self.geometry.healthy(now):self.state=BoardState.UNOBSERVABLE
            return None
        self.observation=result;self.state=result.state
        if result.state not in (BoardState.TRACK,BoardState.OCCLUDED) or result.corners is None:return None
        p=inset_corners(result.corners,self.crop_source_pixels)
        if np.any(p<0) or np.any(p[:,0]>=self.width) or np.any(p[:,1]>=self.height):return None
        if self.target_rect is None:
            self.target_rect=initial_rect(p,self.width,self.height)
            self.content=ContentService(self.runtime,self.width,self.height,self.target_rect,self.capacity)
        self.last_transform=Transform(max(1,result.transform_version),self.board_epoch,p,self.target_rect,(self.width,self.height))
        return self.last_transform

    def ui_tick(self,now,reset):
        if self.ui is None:return
        self.ui.safe=self.state in (BoardState.TRACK,BoardState.OCCLUDED)
        self.ui.frame_epochs=None;self.ui.on_reset=reset
        self.inputs.poll(self.native);self.ui.tick(now)

    def reserve_pair(self):return self.pool.reserve()
    def cancel_pair(self,a,b):self.pool.release(a,b)
    def release_pair(self,a,b):self.pool.release(a,b)
    def release_camera(self,lease):lease.release()

    def acquire_latest(self):
        lease=self.latest;self.latest=None
        return lease

    def discard_unused_camera(self):
        if self.latest is not None:
            self.latest.release();self.latest=None
            self.counts['capture_latest_replacements']+=1

    def frame_key(self,lease,transform):
        _,photometry=self.sensor.snapshot(time.monotonic())
        return FrameKey(getattr(lease,'capture_epoch',0),lease.sequence,transform.board_epoch,0,lease.timestamp,photometry)

    def context(self,key):
        return self.FrameContext(key.capture_epoch,key.sequence,key.board_epoch,
                                 key.history_epoch*1048576+key.photometry_epoch,key.captured_at)

    def launch(self,stage,work,now):
        self.timings[(stage,work.key.identity)]=now
        if stage==Stage.RECTIFY:
            if self.rectifier.generation!=work.transform.version:self.rectifier.set_geometry(work.transform.words())
            self.applied_transform=work.transform
            self.rectifier.launch(work.camera,work.a)
        elif stage==Stage.RESTORE:
            self.restore.launch(work.a,work.b,work.transform.restore_words(),clear_eligible=False)
            ready,version=self.sensor.snapshot(time.monotonic())
            if ready and version==work.key.photometry_epoch:
                work.a.invalidate();self.content.prepare(work.key,work.a[::6,::6])
        else:
            from scene_tracking import ScenePacket
            context=self.context(work.key);packet=None
            if work.metadata is not None and not work.hold:
                shape=((self.height+15)//16,self.width//16)
                packet=ScenePacket(context,work.metadata.metadata,np.zeros(shape,np.uint8),
                    np.zeros(shape,np.int32),False,work.metadata.valid_until,work.metadata.reason)
            target=None if self.ui is None else self.ui.reserve_deep(now)
            self.quantizer.launch(work.a,self.output if target is None else target,context,packet)
            # The driver rechecks the deadline at AP_START. A packet that
            # expired between scheduling and launch never commits PS state.
            work.hold=bool(self.quantizer.hold)

    def poll(self,stage,work,now):
        done=self.stages[stage].poll()
        if done:
            elapsed=now-self.timings.pop((stage,work.key.identity))
            name=stage.value+'_completed'
            self.metrics.add(name,work.key.identity,now)
            self.timings[stage.value+'_last_ms']=elapsed*1000
            if stage==Stage.RECTIFY:
                if self.coordinate_counter:
                    sequence=self.rectifier.ip.read(0x70)
                    cycles=self.rectifier.ip.read(0x6c)
                    if sequence==self.rectifier.ip.read(0x70) and sequence!=self.coordinate_sequence and cycles:
                        self.metrics.record_rectify_compute(work.key.identity,cycles,self.coordinate_clock_hz,now)
                        self.coordinate_sequence=sequence
                self.completed_transform=work.transform
                self.rectifier.corners.invalidate()
                self.pl_geometry_echo=[(int(v)&65535,int(v)>>16) for v in self.rectifier.corners]
                if self.ui is not None:self.ui.offer(1,work.key.sequence,work.a,now,self.context(work.key))
        return done

    def offer_content(self,work,now):
        ready,version=self.sensor.snapshot(now)
        if not ready or version!=work.key.photometry_epoch:return False
        work.a.invalidate();work.b.invalidate()
        return self.content.offer(work.key,work.a[::6,::6],work.b[::6,::6])

    def poll_content(self,work,now):
        ready,version=self.sensor.snapshot(now)
        result=self.content.poll(work.key,now)
        if result is not None and (not ready or version!=work.key.photometry_epoch):
            from .content import ContentResult
            return ContentResult(result.key,result.metadata,True,result.valid_until,'sensor_transition')
        return result

    def ack_content(self,work,commit):self.content.acknowledge(work.key,commit)

    def present(self,work,now):
        if not work.hold:self.initialized=True;self.counts['content_updates']+=1
        else:self.counts['content_holds']+=1
        if self.ui is not None:
            self.ui.processed(work.key.identity,now)
            destination=self.quantizer.destination
            ready,version=self.sensor.snapshot(now)
            if (not work.hold and self.state in (BoardState.TRACK,BoardState.OCCLUDED) and ready and
                    work.metadata is not None and now>=self.erase_archive.next_sample):
                def archive(pixels):
                    identity=(work.key.capture_epoch,work.key.board_epoch,work.key.photometry_epoch)
                    saved=self.erase_archive.observe(pixels,work.key.sequence,identity,
                        work.transform.target_rect,work.metadata.metadata,now,self.ui.save_snapshot)
                    if saved:self.counts['auto_saved_pages']+=1
                # The just-completed Q destination is still owned and has no
                # UI painted yet. Scanout's DMA-BUF callback synchronizes the
                # CPU view without making a full frame copy each sample.
                if hasattr(destination,'edit_rgb565'):destination.edit_rgb565(archive)
                else:archive(destination)
            self.ui.offer(2,work.key.sequence,destination,now,self.context(work.key))
        self.arrivals.append(now)

    def reset_content(self,transform=None,reason='manual'):
        if self.rectifier.in_flight or self.restore.running or self.quantizer.running or self.pool.owned:
            raise RuntimeError('Reset requires all DMA and pair leases to drain')
        self.quantizer.reset_canvas();self.quantizer.last_context=None
        self.board_epoch+=1;self.initialized=False;self.counts[reason+'_resets']+=1
        self.erase_archive.reset()
        # The next Restore launch asserts initialize using the new board epoch
        # and new crop. ContentService recreates its tracker for that same epoch.
        self.restore.generation=0
        if transform is not None or self.last_transform is not None:
            t=transform or self.last_transform
            self.last_transform=Transform(t.version,self.board_epoch,t.source_corners,t.target_rect,t.source_size)
        return self.last_transform

    def report(self,now):
        frame_intervals=np.diff(self.arrivals)
        rates={k:v.value(now) for k,v in self.metrics.rates.items()}
        return dict(runtime='ps_runtime_v2',runtime_version=__version__,board_state=self.state.value,board_epoch=self.board_epoch,
            rectify_coordinate_counter_available=self.coordinate_counter,
            rectify_coordinate_equivalent_fps=self.metrics.rectify_compute.value(now),
            rectify_coordinate_clock_hz=self.coordinate_clock_hz,
            rectify_coordinate_status=self.metrics.snapshot(now)['rectify_coordinate_status'],
            input_devices=[] if self.inputs is None else sorted(self.inputs.device_paths.values()),
            input_errors={} if self.inputs is None else dict(self.inputs.errors),
            input_hotplug={} if self.inputs is None else dict(self.inputs.counters),
            board_inner_margin_source_px=self.crop_source_pixels,
            archive_reference_sequence=self.erase_archive.sequence,
            archive_loss_fraction=self.erase_archive.last_loss,
            archive_erase_started=self.erase_archive.erase_started,
            archive_partial_rewrite_count=self.erase_archive.partial_rewrite_count,
            transform_version=None if self.observation is None else self.observation.transform_version,
            geometry_reason=None if self.observation is None else self.observation.reason,
            measured_corners=None if self.observation is None or self.observation.corners is None else self.observation.corners.tolist(),
            edge_support=None if self.observation is None else self.observation.edge_support,
            camera_motion_reliable=None if self.observation is None else self.observation.motion_reliable,
            applied_transform_version=None if self.applied_transform is None else self.applied_transform.version,
            applied_corners=None if self.applied_transform is None else self.applied_transform.source_corners.tolist(),
            completed_transform_version=None if self.completed_transform is None else self.completed_transform.version,
            completed_corners=None if self.completed_transform is None else self.completed_transform.source_corners.tolist(),
            pl_geometry_echo=self.pl_geometry_echo,
            geometry_duration_ms=None if self.observation is None else self.observation.duration_ms,
            geometry_worker_alive=self.geometry.process.is_alive(),geometry_stale=self.geometry.stale,
            geometry_fault=None if self.geometry.last_error is None else self.geometry.last_error.error,
            content_worker_alive=self.content is not None and self.content.process.is_alive(),
            content_faults=0 if self.content is None else self.content.faults,
            content_offered=0 if self.content is None else self.content.offered,
            content_produced=0 if self.content is None else self.content.results.produced.value,
            content_received=0 if self.content is None else self.content.received,
            content_expired=0 if self.content is None else self.content.expired,
            content_duration_ms=0 if self.content is None else self.content.results.last_duration.value,
            content_reason=None if self.content is None else self.content.last_reason,
            photometry=self.sensor.snapshot(now),
            camera_dropped_before_acquire=self.camera.dropped,bad_frames=self.camera.bad_frames,
            **self.counts,throughput=rates,
            completion_interval_p95_ms=None if not len(frame_intervals) else float(np.percentile(frame_intervals,95)*1000),
            sensor=self.sensor.poll(),timings={k:v for k,v in self.timings.items() if isinstance(k,str)})

    def close(self):
        if self.latest is not None:self.latest.release();self.latest=None
        self.geometry.close();self.sensor.close()
        if self.content is not None:self.content.close()
        self.camera.close();self.quantizer.close();self.rectifier.close();self.restore.close()
        self.output.freebuffer();self.pool.close()
        if self.inputs is not None:self.inputs.close()
        if self.native is not None:self.native.close()
        if self.display is not None:self.display.close()
