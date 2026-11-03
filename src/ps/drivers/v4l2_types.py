#!/usr/bin/env python3
"""Native Linux V4L2 multiplanar ctypes ABI; shared capture uses DMA-BUF."""
import ctypes
import os
import select

import numpy as np

V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE = 9
V4L2_MEMORY_MMAP = 1
V4L2_PIX_FMT_RGB24 = 0x33424752
V4L2_PIX_FMT_YUYV = 0x56595559
VIDEO_MAX_PLANES = 8

_libc = ctypes.CDLL("libc.so.6", use_errno=True)
_libc.mmap.restype = ctypes.c_void_p
_libc.mmap.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int,
                       ctypes.c_int, ctypes.c_int, ctypes.c_long]
_libc.munmap.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
_libc.munmap.restype = ctypes.c_int


def _iowr(nr, size):
    return 0xC0000000 | (size << 16) | (0x56 << 8) | nr


def _iow(nr, size):
    return 0x40000000 | (size << 16) | (0x56 << 8) | nr


class _PlanePixFmt(ctypes.Structure):
    _fields_ = [("sizeimage", ctypes.c_uint32), ("bytesperline", ctypes.c_uint32),
                ("reserved", ctypes.c_uint16 * 6)]


class _PixFmtMP(ctypes.Structure):
    _fields_ = [("width", ctypes.c_uint32), ("height", ctypes.c_uint32),
                ("pixelformat", ctypes.c_uint32), ("field", ctypes.c_uint32),
                ("colorspace", ctypes.c_uint32),
                ("plane_fmt", _PlanePixFmt * VIDEO_MAX_PLANES),
                ("num_planes", ctypes.c_uint8), ("flags", ctypes.c_uint8),
                ("ycbcr_enc", ctypes.c_uint8), ("quantization", ctypes.c_uint8),
                ("xfer_func", ctypes.c_uint8), ("reserved", ctypes.c_uint8 * 7)]


class _FmtU(ctypes.Union):
    _fields_ = [("pix_mp", _PixFmtMP), ("raw", ctypes.c_char * 200),
                ("_al", ctypes.c_void_p)]


class _V4L2Format(ctypes.Structure):
    _fields_ = [("type", ctypes.c_uint32), ("fmt", _FmtU)]


class _Timeval(ctypes.Structure):
    _fields_ = [("tv_sec", ctypes.c_long), ("tv_usec", ctypes.c_long)]


class _Timecode(ctypes.Structure):
    _fields_ = [("type", ctypes.c_uint32), ("flags", ctypes.c_uint32),
                ("frames", ctypes.c_uint8), ("seconds", ctypes.c_uint8),
                ("minutes", ctypes.c_uint8), ("hours", ctypes.c_uint8),
                ("userbits", ctypes.c_uint8 * 4)]


class _PlaneM(ctypes.Union):
    _fields_ = [("mem_offset", ctypes.c_uint32), ("userptr", ctypes.c_ulong),
                ("fd", ctypes.c_int32)]


class _Plane(ctypes.Structure):
    _fields_ = [("bytesused", ctypes.c_uint32), ("length", ctypes.c_uint32),
                ("m", _PlaneM), ("data_offset", ctypes.c_uint32),
                ("reserved", ctypes.c_uint32 * 11)]


class _MBuf(ctypes.Union):
    _fields_ = [("offset", ctypes.c_uint32), ("userptr", ctypes.c_ulong),
                ("planes", ctypes.POINTER(_Plane)), ("fd", ctypes.c_int32)]


class _V4L2Buffer(ctypes.Structure):
    _fields_ = [("index", ctypes.c_uint32), ("type", ctypes.c_uint32),
                ("bytesused", ctypes.c_uint32), ("flags", ctypes.c_uint32),
                ("field", ctypes.c_uint32), ("timestamp", _Timeval),
                ("timecode", _Timecode), ("sequence", ctypes.c_uint32),
                ("memory", ctypes.c_uint32), ("m", _MBuf),
                ("length", ctypes.c_uint32), ("reserved2", ctypes.c_uint32),
                ("reserved", ctypes.c_uint32)]


class _ReqBufs(ctypes.Structure):
    _fields_ = [("count", ctypes.c_uint32), ("type", ctypes.c_uint32),
                ("memory", ctypes.c_uint32), ("capabilities", ctypes.c_uint32),
                ("reserved", ctypes.c_uint32)]


_VIDIOC_S_FMT = _iowr(5, ctypes.sizeof(_V4L2Format))
_VIDIOC_REQBUFS = _iowr(8, ctypes.sizeof(_ReqBufs))
_VIDIOC_QUERYBUF = _iowr(9, ctypes.sizeof(_V4L2Buffer))
_VIDIOC_QBUF = _iowr(15, ctypes.sizeof(_V4L2Buffer))
_VIDIOC_DQBUF = _iowr(17, ctypes.sizeof(_V4L2Buffer))
_VIDIOC_STREAMON = _iow(18, 4)
_VIDIOC_STREAMOFF = _iow(19, 4)
_PROT_RW = 1 | 2
_MAP_SHARED = 1


def _ioctl(fd, req, obj):
    if _libc.ioctl(fd, req, ctypes.byref(obj)) < 0:
        e = ctypes.get_errno()
        raise OSError(e, "ioctl %#x: %s" % (req, os.strerror(e)))


def _new_buf(index=None):
    planes = (_Plane * 1)()
    b = _V4L2Buffer(type=V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE,
                    memory=V4L2_MEMORY_MMAP, length=1,
                    m=_MBuf(planes=ctypes.cast(planes, ctypes.POINTER(_Plane))))
    if index is not None:
        b.index = index
    return b, planes



