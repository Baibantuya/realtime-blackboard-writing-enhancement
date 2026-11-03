#!/usr/bin/env python3
"""Zero-Copy Contiguous Memory Buffer Pool for PYNQ DMA.

Eliminates memory fragmentation, prevents repeated CMA allocation overhead,
and guarantees physical address overlap detection.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Any, Generator, List, Tuple

logger = logging.getLogger("pynq_skill.dma_buffer_pool")


class DmaBufferPool:
    """Pre-allocated ring pool of contiguous physical CMA buffers."""

    def __init__(
        self,
        buffer_shape: Tuple[int, ...],
        dtype: str = "uint8",
        pool_size: int = 4,
        allocate_fn: Any = None,
    ) -> None:
        """Initialize buffer pool.

        Args:
            buffer_shape: Dimensions of each buffer (e.g. (1080, 1920, 3)).
            dtype: Data type string (e.g. 'uint8', 'uint16', 'uint32').
            pool_size: Number of contiguous buffers to pre-allocate.
            allocate_fn: Custom allocate function (defaults to pynq.allocate).
        """
        self.shape = buffer_shape
        self.dtype = dtype
        self.pool_size = pool_size
        self._buffers: List[Any] = []
        self._in_use: List[bool] = []
        self._allocate_fn = allocate_fn

        if self._allocate_fn is None:
            try:
                from pynq import allocate

                self._allocate_fn = allocate
            except ImportError:
                # Mock allocation for host testing
                import numpy as np

                def _mock_alloc(shape, dtype):
                    arr = np.zeros(shape, dtype=dtype)
                    # assign dummy physical address
                    arr.physical_address = id(arr) & 0xFFFFFFF0
                    arr.flush = lambda: None
                    arr.invalidate = lambda: None
                    arr.freebuffer = lambda: None
                    return arr

                self._allocate_fn = _mock_alloc

        self._allocate_all()

    def _allocate_all(self) -> None:
        """Pre-allocate all contiguous buffers at once during setup."""
        logger.info(
            "Pre-allocating %d CMA buffers of shape %s, dtype %s",
            self.pool_size,
            self.shape,
            self.dtype,
        )
        for i in range(self.pool_size):
            buf = self._allocate_fn(shape=self.shape, dtype=self.dtype)
            if not hasattr(buf, "physical_address"):
                raise TypeError(
                    "Allocated buffer is not a valid PYNQ CMA buffer (missing physical_address)"
                )
            self._buffers.append(buf)
            self._in_use.append(False)
            logger.debug(
                "Buffer #%d allocated at physical address 0x%08X",
                i,
                int(buf.physical_address),
            )

    @contextmanager
    def acquire(self) -> Generator[Any, None, None]:
        """Lease a free buffer from the pool and automatically return it on context exit."""
        chosen_idx = -1
        for i in range(self.pool_size):
            if not self._in_use[i]:
                self._in_use[i] = True
                chosen_idx = i
                break

        if chosen_idx == -1:
            raise BufferError(
                f"All {self.pool_size} buffers in DmaBufferPool are currently in use! "
                "Consider increasing pool_size."
            )

        buf = self._buffers[chosen_idx]
        try:
            yield buf
        finally:
            self._in_use[chosen_idx] = False

    @staticmethod
    def check_overlap(buf_a: Any, buf_b: Any) -> bool:
        """Verify that two CMA buffers do not overlap in physical DDR address space."""
        addr_a = int(buf_a.physical_address)
        size_a = buf_a.nbytes
        addr_b = int(buf_b.physical_address)
        size_b = buf_b.nbytes

        end_a = addr_a + size_a
        end_b = addr_b + size_b

        # Overlap occurs if A starts before B ends and B starts before A ends
        return (addr_a < end_b) and (addr_b < end_a)

    def close(self) -> None:
        """Safely release all physical memory allocations back to Linux CMA."""
        for i, buf in enumerate(self._buffers):
            try:
                buf.freebuffer()
            except Exception as e:
                logger.warning("Error freeing buffer #%d: %s", i, e)
        self._buffers.clear()
        self._in_use.clear()
        logger.info("DmaBufferPool released successfully.")
