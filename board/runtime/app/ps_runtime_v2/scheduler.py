"""Pure nonblocking ownership scheduler; tests need no FPGA or camera."""
from collections import deque
from dataclasses import dataclass
from enum import Enum


class Stage(str,Enum):
    RECTIFY='rectify'
    RESTORE='restore'
    CONTENT='content'
    QUANTIZE='quantize'
    READY='ready'


@dataclass
class Work:
    key: object
    transform: object
    camera: object
    a: object
    b: object
    state: Stage=Stage.RECTIFY
    metadata: object=None
    content_deadline: float=0.
    hold: bool=False


class VideoScheduler:
    """The adapter owns DMA. The scheduler never releases an active device lease."""
    def __init__(self,adapter,capacity=3,content_budget=.080):
        if capacity<2 or content_budget<=0:raise ValueError('Invalid video capacity/budget')
        self.io=adapter;self.capacity=capacity;self.content_budget=content_budget
        self.work=deque();self.active={};self.transforms=None
        self.accepting=True;self.reset_pending=False
        self.pending_transform=None;self.reset_reason=None
        self.resume_after_reset=True
        self.metrics=dict(admitted=0,completed=0,content_deadline_holds=0,
                          capacity_skips=0,camera_skips=0,transform_updates=0,
                          geometry_resets=0,manual_resets=0)

    def publish_transform(self,transform):
        # A late pre-F7 publication cannot roll the new board epoch backwards.
        if self.transforms is not None and transform.board_epoch<self.transforms.board_epoch:return
        current=self.pending_transform or self.transforms
        if (current is not None and transform.version==current.version and
            transform.board_epoch==current.board_epoch and transform.target_rect==current.target_rect and
            transform.source_size==current.source_size):return
        self.metrics['transform_updates']+=1
        if self.transforms is None and not self.reset_pending:
            self.transforms=transform;return
        # An explicit reset still coalesces newer geometry while old work drains.
        if self.reset_pending:
            self.pending_transform=transform;return
        current=self.transforms
        same_board=(transform.board_epoch==current.board_epoch and
                    transform.target_rect==current.target_rect and
                    transform.source_size==current.source_size)
        if same_board:
            # Accepted V22 contract: only future Rectify launches see this
            # version. In-flight work retains its immutable transform; fixed
            # board coordinates and the epoch keep Restore/PS/Canvas aligned.
            self.transforms=transform
        else:
            self.pending_transform=transform;self.request_reset('geometry')

    def request_reset(self,reason='manual'):
        if not self.reset_pending:self.resume_after_reset=self.accepting
        self.reset_pending=True;self.accepting=False;self.reset_reason=reason

    def _launch(self,stage,work,now):
        if stage in self.active:raise RuntimeError('Stage still owns a buffer')
        # Reserve ownership first: an exception after AP_START must never let
        # cleanup treat the device's source/destination as free.
        self.active[stage]=work;self.io.launch(stage,work,now)

    def tick(self,now):
        # A slow CPU worker is never invoked or joined on this path.
        for stage,work in list(self.active.items()):
            if not self.io.poll(stage,work,now):continue
            del self.active[stage]
            if stage==Stage.RECTIFY:
                self.io.release_camera(work.camera);work.camera=None;work.state=Stage.RESTORE
            elif stage==Stage.RESTORE:
                work.content_deadline=now+self.content_budget
                work.state=Stage.CONTENT;self.io.offer_content(work,now)
            elif stage==Stage.QUANTIZE:
                self.io.present(work,now);self.io.ack_content(work,not work.hold)
                self.io.release_pair(work.a,work.b)
                self.work.remove(work);self.metrics['completed']+=1

        # Preserve per-board content ordering. A late worker result cannot
        # block Q forever or authorize writing using an older frame's mask.
        ready=[w for w in self.work if w.state==Stage.CONTENT]
        if ready and Stage.QUANTIZE not in self.active:
            work=ready[0];result=self.io.poll_content(work,now)
            if result is not None:
                if result.key!=work.key:raise RuntimeError('Cross-frame content result')
                work.metadata=result;work.hold=result.hold or result.valid_until<now
                work.state=Stage.QUANTIZE
                self._launch(Stage.QUANTIZE,work,now)
            elif now>=work.content_deadline:
                work.hold=True;work.state=Stage.QUANTIZE
                self.metrics['content_deadline_holds']+=1
                self._launch(Stage.QUANTIZE,work,now)
        if Stage.RESTORE not in self.active:
            waiting=next((w for w in self.work if w.state==Stage.RESTORE),None)
            if waiting is not None:self._launch(Stage.RESTORE,waiting,now)
        if self.reset_pending and not self.work and not self.active:
            replacement=self.io.reset_content(self.pending_transform or self.transforms,self.reset_reason)
            if replacement is not None:self.transforms=replacement
            self.metrics[self.reset_reason+'_resets']+=1
            self.pending_transform=None;self.reset_reason=None
            self.reset_pending=False;self.accepting=self.resume_after_reset
        if (not self.accepting or self.transforms is None or
            len(self.work)>=self.capacity or Stage.RECTIFY in self.active):return
        pair=self.io.reserve_pair()
        if pair is None:self.metrics['capacity_skips']+=1;return
        camera=self.io.acquire_latest()
        if camera is None:self.io.cancel_pair(*pair);return
        key=self.io.frame_key(camera,self.transforms)
        work=Work(key,self.transforms,camera,*pair)
        self.work.append(work);self.metrics['admitted']+=1
        self._launch(Stage.RECTIFY,work,now)

    def close(self):
        if self.work or self.active:raise RuntimeError('Drain hardware before closing buffers')
