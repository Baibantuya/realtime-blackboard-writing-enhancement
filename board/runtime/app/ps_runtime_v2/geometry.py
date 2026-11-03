"""Small-image camera motion, physical edges and presence are separate measurements."""
import time
import cv2
import numpy as np
from .contracts import BoardState,GeometryResult
from .policy import Evidence,PresencePolicy


def rgb565(pixels):
    p=pixels.astype(np.uint32)
    return np.stack((((p>>11)&31)*255//31,((p>>5)&63)*255//63,(p&31)*255//31),-1).astype(np.uint8)


def ordered_quad(points):
    p=np.asarray(points,np.float32).reshape(4,2)
    center=p.mean(0);p=p[np.argsort(np.arctan2(p[:,1]-center[1],p[:,0]-center[0]))]
    return np.roll(p,-int(np.argmin(p.sum(1))),axis=0)


def valid_quad(p,shape,inside=True):
    if p is None or p.shape!=(4,2) or not np.all(np.isfinite(p)):return False
    h,w=shape
    if inside and (np.any(p[:,0]<1) or np.any(p[:,0]>w-2) or np.any(p[:,1]<1) or np.any(p[:,1]>h-2)):return False
    return bool(cv2.isContourConvex(p.astype(np.float32)) and
                abs(cv2.contourArea(p.astype(np.float32)))>.06*w*h)


def board_mask(corners,shape,margin=0):
    mask=np.zeros(shape,np.uint8)
    if corners is not None:cv2.fillConvexPoly(mask,np.rint(corners).astype(np.int32),255)
    if margin:mask=cv2.dilate(mask,np.ones((margin*2+1,margin*2+1),np.uint8))
    return mask


def locate(gray,clean_connections=False):
    """Cold-start proposals require a closed, in-frame dark board quadrilateral."""
    h,w=gray.shape;threshold=float(np.clip(np.percentile(gray,75)*.72,50,155))
    mask=(gray<threshold).astype(np.uint8)*255
    mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    if clean_connections:
        # Retry only when a thin cable/shadow connects the board to furniture.
        mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    candidates=[]
    for contour in contours:
        if cv2.contourArea(contour)<.06*w*h:continue
        hull=cv2.convexHull(contour)
        p=cv2.approxPolyDP(hull,.018*cv2.arcLength(hull,True),True)
        if len(p)!=4:continue
        p=ordered_quad(p)
        if not valid_quad(p,gray.shape):continue
        inside=board_mask(p,gray.shape)
        inner=cv2.erode(inside,np.ones((5,5),np.uint8))>0
        outer=(cv2.dilate(inside,np.ones((7,7),np.uint8))>0)&(inside==0)
        if not inner.any() or not outer.any():continue
        contrast=float(np.median(gray[outer]))-float(np.median(gray[inner]))
        if contrast<12:continue
        candidates.append((cv2.contourArea(p)*min(contrast,80),p))
    if candidates:return max(candidates,key=lambda item:item[0])[1]
    return None if clean_connections else locate(gray,True)


def camera_motion(previous,current,corners):
    # Geometry samples are decimated sensor pixels; suppress sensor-grain
    # features before selecting/tracking exterior scene landmarks.
    previous=cv2.GaussianBlur(previous,(3,3),.8)
    current=cv2.GaussianBlur(current,(3,3),.8)
    mask=255-board_mask(corners,previous.shape,margin=2)
    points=cv2.goodFeaturesToTrack(previous,180,.012,4,mask=mask,blockSize=5)
    if points is None or len(points)<10:
        # Frame corners and static text may supplement a textureless wall;
        # geometric support tests still reject a local moving person.
        points=cv2.goodFeaturesToTrack(previous,180,.015,5,blockSize=5)
    if points is None or len(points)<10:return None,False
    moved,ok,_=cv2.calcOpticalFlowPyrLK(previous,current,points,None,winSize=(17,17),maxLevel=3)
    if moved is None:return None,False
    back,valid,_=cv2.calcOpticalFlowPyrLK(current,previous,moved,None,winSize=(17,17),maxLevel=3)
    if back is None:return None,False
    good=(ok[:,0]>0)&(valid[:,0]>0)&(np.linalg.norm(points[:,0]-back[:,0],axis=1)<1.)
    a=points[:,0][good];b=moved[:,0][good]
    if len(a)<10:return None,False
    transform,inliers=cv2.findHomography(a,b,cv2.RANSAC,1.5)
    if transform is None:return None,False
    good=inliers[:,0]>0
    if good.sum()<8 or good.mean()<.7:return None,False
    h,w=current.shape
    # Interior/person features can propose a transform, but cannot prove camera
    # motion. Require support outside the board or immediately on its frame.
    outside_frame=255-cv2.erode(board_mask(corners,previous.shape),np.ones((7,7),np.uint8))
    positions=np.rint(a[good]).astype(int)
    positions[:,0]=np.clip(positions[:,0],0,w-1);positions[:,1]=np.clip(positions[:,1],0,h-1)
    if np.count_nonzero(outside_frame[positions[:,1],positions[:,0]])<8:return None,False
    cells={(int(x>=w/2),int(y>=h/2)) for x,y in a[good]}
    area=cv2.contourArea(cv2.convexHull(a[good].astype(np.float32)))
    if len(cells)<3 or area<.04*w*h:return None,False
    # Prefer a translation or similarity when it explains the same distributed
    # tracks. A free homography overfits sensor noise and extrapolates it into
    # corner motion even when the actual camera is stationary.
    source=a[good];destination=b[good]
    shift=np.median(destination-source,axis=0)
    residual=np.linalg.norm(destination-source-shift,axis=1)
    if np.mean(residual<.35)>=.85:
        transform=np.array(((1.,0.,shift[0]),(0.,1.,shift[1]),(0.,0.,1.)))
    else:
        affine,ok=cv2.estimateAffinePartial2D(source,destination,method=cv2.RANSAC,
            ransacReprojThreshold=.5,maxIters=500,confidence=.99)
        if affine is not None:
            residual=np.linalg.norm(source@affine[:,:2].T+affine[:,2]-destination,axis=1)
            if np.median(residual)<.2 and np.percentile(residual,90)<.5:
                transform=np.vstack((affine,(0.,0.,1.)))
    return transform,True


def edge_lines(gray,predicted):
    """Fit the board-side edge of a frame, not its outside shadow.

    A narrow derivative resolves the frame's bright strip and dark shadow as
    separate transitions. Pick the innermost transition supported along most
    of the edge, then fit individual samples around that shared peak. This
    prevents a strong wall/shadow edge from winning independently at each point.
    All distances here are in the small geometry image (normally 1:6).
    """
    lines=[];support=[];center=predicted.mean(0);h,w=gray.shape
    for index in range(4):
        a=predicted[index];b=predicted[(index+1)%4];direction=b-a
        length=np.linalg.norm(direction)
        if length<8:lines.append(None);support.append(0.);continue
        normal=np.array((-direction[1],direction[0]))/length
        if np.dot(center-(a+b)/2,normal)<0:normal=-normal
        base=a[None,:]+np.linspace(.12,.88,20)[:,None]*direction
        offsets=np.arange(-6.,8.1,.5)
        positions=base[:,None,:]+offsets[None,:,None]*normal
        inner=positions+normal*.75;outer=positions-normal*.75
        good=(inner[...,0]>=0)&(inner[...,0]<w-1)&(inner[...,1]>=0)&(inner[...,1]<h-1)&(outer[...,0]>=0)&(outer[...,0]<w-1)&(outer[...,1]>=0)&(outer[...,1]<h-1)
        def sample(points):
            return cv2.remap(gray,points[...,0].astype(np.float32),points[...,1].astype(np.float32),cv2.INTER_LINEAR).astype(np.float32)
        score=sample(outer)-sample(inner);score[~good]=-1000
        # A local chalk stroke cannot nominate a frame edge: require at least
        # 55% of the separated probes to agree. Occluded probes remain free to
        # fail, so a monitor/person covering part of the edge does not move it.
        profile=np.median(score,axis=0)
        agreement=np.mean(score>=10,axis=0)
        peaks=[k for k in range(1,len(offsets)-1)
               if profile[k]>=10 and agreement[k]>=.55 and
               profile[k]>=profile[k-1] and profile[k]>=profile[k+1]]
        if not peaks:lines.append(None);support.append(0.);continue
        peak=peaks[-1]
        near=np.abs(offsets-offsets[peak])<=.75
        score[:,~near]=-1000
        best=np.argmax(score,axis=1);strength=score[np.arange(20),best]
        selected=positions[np.arange(20),best][strength>=10]
        support.append(len(selected)/20.)
        if len(selected)<9:lines.append(None);continue
        vx,vy,x,y=cv2.fitLine(selected.astype(np.float32),cv2.DIST_HUBER,0,.01,.01).ravel()
        residual=np.abs((selected[:,0]-x)*vy-(selected[:,1]-y)*vx)
        selected=selected[residual<1.4]
        if len(selected)<8:lines.append(None);continue
        vx,vy,x,y=cv2.fitLine(selected.astype(np.float32),cv2.DIST_L2,0,.01,.01).ravel()
        lines.append(np.array((vy,-vx,vx*y-vy*x),np.float64))
    return lines,tuple(support)


def refine_quad(predicted,lines):
    complete=[]
    for i,line in enumerate(lines):
        if line is None:
            a=np.r_[predicted[i],1.];b=np.r_[predicted[(i+1)%4],1.]
            line=np.cross(a,b)
        complete.append(line)
    points=[]
    for i in range(4):
        p=np.cross(complete[(i-1)%4],complete[i])
        if abs(p[2])<1e-8:return None
        points.append(p[:2]/p[2])
    return np.array(points)


class GeometryEngine:
    def __init__(self,movement_threshold=2.):
        # Threshold is in original camera pixels, independent of sample scale.
        # Accumulate against the last published matrix, not the previous sample.
        self.movement_threshold=movement_threshold
        self.policy=PresencePolicy();self.reset()

    def reset(self):
        self.policy.reset();self.corners=None;self.previous=None;self.capture_epoch=None
        self.pending=None;self.version=0;self.last_sequence=-1
        self.published=None;self.anchor_gray=None;self.anchor_corners=None

    def update(self,frame):
        start=time.monotonic()
        if frame.capture_epoch!=self.capture_epoch:
            self.reset();self.capture_epoch=frame.capture_epoch
        if frame.sequence<=self.last_sequence:raise ValueError('Reordered geometry sample')
        self.last_sequence=frame.sequence
        gray=cv2.cvtColor(rgb565(frame.pixels),cv2.COLOR_RGB2GRAY)
        scale=np.array(frame.source_size,dtype=float)/np.array((gray.shape[1],gray.shape[0]))
        anchor_ok=False;anchor_predicted=None;anchor_displacement=None
        if self.anchor_gray is not None and self.anchor_corners is not None:
            anchor_transform,anchor_ok=camera_motion(self.anchor_gray,gray,self.anchor_corners)
            if anchor_ok:
                anchor_predicted=cv2.perspectiveTransform(self.anchor_corners[None].astype(np.float32),anchor_transform)[0]
                anchor_displacement=float(np.max(np.linalg.norm((anchor_predicted-self.anchor_corners)*scale,axis=1)))
        reliable=False;predicted=self.corners;stationary=False;local=False;replaced=False
        if self.previous is not None and self.corners is not None:
            transform,reliable=camera_motion(self.previous,gray,self.corners)
            if reliable:predicted=cv2.perspectiveTransform(self.corners[None].astype(np.float32),transform)[0]
            outside=board_mask(self.corners,gray.shape,margin=2)==0
            diff=gray.astype(np.int16)-self.previous.astype(np.int16)
            if outside.any():
                offset=np.median(diff[outside]);change=np.abs(diff-offset)>18
                stationary=float(np.mean(change[outside]))<.12
                local=stationary and np.mean(change[~outside])>.08 if (~outside).any() else False
                replaced=np.mean(change[outside])>.65 and not reliable
        candidate=None;supports=(0.,)*4;visible=0;fraction=1.
        if self.corners is None:
            candidate=locate(gray)
            if candidate is not None:
                lines,supports=edge_lines(gray,candidate)
                if sum(line is not None for line in lines)>=3:
                    refined=refine_quad(candidate,lines)
                    if valid_quad(refined,gray.shape):candidate=refined
                if self.pending is not None and np.max(np.linalg.norm(candidate-self.pending,axis=1))>3:
                    self.policy.found=0
                self.pending=candidate.copy();visible=4
        else:
            lines,supports=edge_lines(gray,predicted);visible=sum(line is not None for line in lines)
            if visible>=3:candidate=refine_quad(predicted,lines)
            elif reliable and visible>=2:candidate=refine_quad(predicted,lines)
            if candidate is not None and not valid_quad(candidate,gray.shape):candidate=None
            area=abs(cv2.contourArea(predicted.astype(np.float32)))
            fraction=float(np.count_nonzero(board_mask(predicted,gray.shape)))/max(area,1)
            if visible<2 and not reliable and not local:
                found=locate(gray)
                if found is not None:candidate=found;visible=4
            # A static outside with temporarily missing physical edges is
            # occlusion evidence even if texture inside the board is unchanged.
            local=local or (stationary and visible<3)
        clipped=predicted is not None and (np.any(predicted[:,0]<1) or np.any(predicted[:,0]>gray.shape[1]-2)
            or np.any(predicted[:,1]<1) or np.any(predicted[:,1]>gray.shape[0]-2))
        self.debug=dict(predicted=None if predicted is None else predicted.tolist(),
            candidate=None if candidate is None else candidate.tolist(),visible_edges=visible,
            visible_fraction=fraction,frame_clipped=bool(clipped),stationary=bool(stationary),
            local_occlusion=bool(local),scene_replaced=bool(replaced))
        state=self.policy.update(Evidence(candidate is not None,visible,reliable,fraction,stationary,local,replaced,bool(clipped)))
        reason='measured'
        if state==BoardState.SEARCH:
            self.corners=None;self.published=None;self.pending=None;self.anchor_gray=None;self.anchor_corners=None;reason='search_board'
        elif state==BoardState.CONFIRM:
            reason='confirm_board'
        elif anchor_ok and self.published is not None:
            # A well-supported identity flow is evidence for holding geometry.
            # Anchor to the last publication: subpixel motion accumulates without
            # integrating per-frame edge noise or small incremental flow errors.
            if anchor_displacement>=self.movement_threshold:
                self.corners=anchor_predicted;reason='camera_anchor_motion'
            else:
                self.corners=self.published.copy();reason='camera_anchor_stationary'
        elif candidate is not None and state!=BoardState.OCCLUDED:
            if self.corners is None:new=candidate
            else:new=self.corners*.2+candidate*.8
            self.corners=new;reason='matrix_measurement'
        elif reliable:
            self.corners=predicted;reason='camera_prediction'
        elif state==BoardState.OCCLUDED and self.published is not None:
            self.corners=self.published.copy();reason='foreground_occlusion'
        else:reason='insufficient_observation'
        scale=np.array(frame.source_size,dtype=float)/np.array((gray.shape[1],gray.shape[0]))
        if self.corners is not None and (self.published is None or
            np.max(np.linalg.norm((self.corners-self.published)*scale,axis=1))>=self.movement_threshold):
            self.version+=1;self.published=self.corners.copy()
            self.anchor_gray=gray.copy();self.anchor_corners=self.published.copy()
        self.debug.update(anchor_motion_reliable=bool(anchor_ok),
            anchor_displacement_source_px=anchor_displacement,
            matrix_publish_threshold_source_px=self.movement_threshold,
            edge_selection='innermost_coherent_frame_transition')
        self.previous=gray.copy()
        points=None if self.published is None else self.published*scale
        return GeometryResult(frame.sequence,frame.capture_epoch,frame.sampled_at,state,
            points,self.version,reliable,supports,reason,(time.monotonic()-start)*1000)
