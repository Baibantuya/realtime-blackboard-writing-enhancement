"""Fuse independently measured camera, frame and occlusion evidence."""
from dataclasses import dataclass
from .contracts import BoardState


@dataclass(frozen=True)
class Evidence:
    candidate_valid: bool
    visible_edges: int
    motion_reliable: bool
    predicted_visible_fraction: float
    background_stationary: bool
    local_occlusion: bool
    scene_replaced: bool
    frame_clipped: bool = False


class PresencePolicy:
    def __init__(self,confirmations=3,exit_confirmations=2):
        self.confirmations=confirmations;self.exit_confirmations=exit_confirmations
        self.reset()

    def reset(self):
        self.state=BoardState.SEARCH;self.found=0;self.exit_count=0

    def update(self,evidence):
        e=evidence
        if self.state in (BoardState.SEARCH,BoardState.CONFIRM):
            self.found=self.found+1 if e.candidate_valid else 0
            self.state=(BoardState.TRACK if self.found>=self.confirmations else
                        BoardState.CONFIRM if self.found else BoardState.SEARCH)
            return self.state
        # A reliable camera transform carrying the board out of the image is
        # positive exit evidence. Partial or complete foreground occlusion is not.
        outside=e.motion_reliable and (e.frame_clipped or e.predicted_visible_fraction<.98)
        replaced=e.scene_replaced and not e.candidate_valid and not e.local_occlusion
        self.exit_count=self.exit_count+1 if outside or replaced else 0
        if self.exit_count>=self.exit_confirmations:
            self.reset();return self.state
        if e.candidate_valid or (e.motion_reliable and e.visible_edges>=2):
            self.state=BoardState.TRACK
        elif e.local_occlusion and e.background_stationary:
            self.state=BoardState.OCCLUDED
        else:
            # With no background or frame evidence, exit and total occlusion
            # are not distinguishable. Do not invent a new matrix or background.
            self.state=BoardState.UNOBSERVABLE
        return self.state
