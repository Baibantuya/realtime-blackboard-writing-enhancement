"""Value-only messages. No camera lease or device object may cross a worker boundary."""
from dataclasses import dataclass
from enum import Enum
import math
import numpy as np


class BoardState(str, Enum):
    SEARCH = 'search'
    CONFIRM = 'confirm'
    TRACK = 'track'
    OCCLUDED = 'occluded'
    UNOBSERVABLE = 'unobservable'


@dataclass(frozen=True)
class FrameKey:
    capture_epoch: int
    sequence: int
    board_epoch: int
    history_epoch: int
    captured_at: float
    photometry_epoch: int = 0

    @property
    def identity(self):
        return self.capture_epoch,self.sequence,self.board_epoch,self.history_epoch,self.photometry_epoch


@dataclass(frozen=True)
class Sample:
    sequence: int
    capture_epoch: int
    sampled_at: float
    source_size: tuple
    pixels: np.ndarray

    def __post_init__(self):
        if (self.pixels.dtype != np.uint16 or self.pixels.ndim != 2 or
            self.pixels.size > 320*180 or not math.isfinite(self.sampled_at)):
            raise ValueError('Expected a bounded RGB565 sample')
        copy=np.array(self.pixels,copy=True,order='C');copy.flags.writeable=False
        object.__setattr__(self,'pixels',copy)


@dataclass(frozen=True)
class GeometryResult:
    sequence: int
    capture_epoch: int
    sampled_at: float
    state: BoardState
    corners: object
    transform_version: int
    motion_reliable: bool
    edge_support: tuple
    reason: str
    duration_ms: float = 0.

    def __post_init__(self):
        if self.corners is not None:
            p=np.array(self.corners,dtype=np.float64,copy=True)
            if p.shape!=(4,2) or not np.all(np.isfinite(p)):
                raise ValueError('Invalid corner result')
            p.flags.writeable=False;object.__setattr__(self,'corners',p)


@dataclass(frozen=True)
class Transform:
    """Camera transform version is independent of the persistent board epoch."""
    version: int
    board_epoch: int
    source_corners: np.ndarray
    target_rect: tuple
    source_size: tuple

    def __post_init__(self):
        p=np.array(self.source_corners,dtype=np.float64,copy=True)
        if p.shape!=(4,2) or not np.all(np.isfinite(p)):raise ValueError('Invalid transform')
        p.flags.writeable=False;object.__setattr__(self,'source_corners',p)

    def words(self):
        """Existing rectify ABI4. Homography maps local target pixels to camera pixels."""
        import cv2
        x,y,w,h=self.target_rect
        if min(w,h)<=1:raise ValueError('Empty target board')
        dst=np.array(((0,0),(w-1,0),(w-1,h-1),(0,h-1)),np.float32)
        matrix=cv2.getPerspectiveTransform(dst,self.source_corners.astype(np.float32))
        matrix/=matrix[2,2]
        values=matrix.ravel()[:8].astype(np.float32)
        if not np.all(np.isfinite(values)):raise ValueError('Singular homography')
        out=np.zeros(20,np.uint32)
        out[:8]=(0x57424734,self.version,*self.source_size,x,y,w,h)
        out[8:16]=values.view(np.uint32)
        corners=np.rint(self.source_corners)
        if np.any(corners<0) or np.any(corners>65535):raise ValueError('Unpackable corners')
        corners=corners.astype(np.uint32);out[16:20]=corners[:,0]|(corners[:,1]<<16)
        return out

    def restore_words(self):
        # Same-board camera updates preserve this epoch and history, as in V22.
        # F7 or explicit board-coordinate changes still drain and reset.
        out=self.words();out[1]=self.board_epoch
        return out
