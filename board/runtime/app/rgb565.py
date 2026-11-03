"""Standard RGB565 storage and sparse RGB access; no full-frame live expansion."""
import numpy as np

def expand(pixels):
    p=np.asarray(pixels,dtype=np.uint16)
    r=(p>>11)&31;g=(p>>5)&63;b=p&31
    return np.stack(((r<<3)|(r>>2),(g<<2)|(g>>4),(b<<3)|(b>>2)),axis=-1).astype(np.uint8)

def pack(rgb):
    p=np.asarray(rgb,dtype=np.uint16)
    return ((p[...,0]>>3)<<11)|((p[...,1]>>2)<<5)|(p[...,2]>>3)

class SparseRgbView:
    """Expand only requested detector profiles and AE patches from a held frame."""
    dtype=np.dtype('uint8')
    ndim=3
    def __init__(self,pixels):
        self.pixels=pixels;self.shape=(*pixels.shape,3)
    def __getitem__(self,key):
        if not isinstance(key,tuple):key=(key,)
        return expand(self.pixels[key[:2]])[(...,)+key[2:]]
