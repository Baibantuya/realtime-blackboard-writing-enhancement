#!/usr/bin/env python3
"""Golden Reference Comparator for Hardware Verification.

Compares hardware acceleration output against software golden model
with exact matching, tolerance thresholds, and metrics (PSNR, MAE, MaxErr).
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional
import numpy as np


@dataclass
class ComparisonResult:
    """Structured result of golden reference comparison."""

    is_match: bool
    total_elements: int
    mismatch_count: int
    mismatch_ratio: float
    max_abs_error: float
    mean_abs_error: float
    psnr_db: float
    error_summary: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class GoldenComparator:
    """Compares array outputs between hardware and software reference."""

    def __init__(self, tolerance: float = 0.0, max_dynamic_range: float = 255.0) -> None:
        """Initialize comparator.

        Args:
            tolerance: Maximum allowable absolute error per element. 0 = exact match.
            max_dynamic_range: Dynamic range for PSNR calculation (e.g. 255 for 8-bit, 65535 for 16-bit).
        """
        self.tolerance = tolerance
        self.dynamic_range = max_dynamic_range

    def compare(
        self,
        actual: np.ndarray,
        expected: np.ndarray,
        mask: Optional[np.ndarray] = None,
    ) -> ComparisonResult:
        """Compare actual hardware output with golden expected array.

        Args:
            actual: Hardware acceleration output array.
            expected: Software reference golden array.
            mask: Optional boolean mask specifying valid regions to compare.
        """
        act = np.asarray(actual)
        exp = np.asarray(expected)

        if act.shape != exp.shape:
            raise ValueError(
                f"Shape mismatch: actual shape {act.shape} != expected shape {exp.shape}"
            )

        diff = np.abs(act.astype(np.float64) - exp.astype(np.float64))

        if mask is not None:
            m = np.asarray(mask, dtype=bool)
            diff = diff[m]
            total_elements = int(np.sum(m))
        else:
            total_elements = diff.size

        if total_elements == 0:
            return ComparisonResult(
                is_match=True,
                total_elements=0,
                mismatch_count=0,
                mismatch_ratio=0.0,
                max_abs_error=0.0,
                mean_abs_error=0.0,
                psnr_db=float("inf"),
                error_summary="Empty evaluation set.",
            )

        mismatches = diff > self.tolerance
        mismatch_count = int(np.sum(mismatches))
        mismatch_ratio = float(mismatch_count) / float(total_elements)

        max_err = float(np.max(diff))
        mean_err = float(np.mean(diff))
        mse = float(np.mean(diff ** 2))

        if mse == 0.0:
            psnr = float("inf")
        else:
            psnr = 20.0 * math.log10(self.dynamic_range) - 10.0 * math.log10(mse)

        is_match = mismatch_count == 0

        summary = (
            f"Comparison {'PASSED' if is_match else 'FAILED'}: "
            f"mismatches={mismatch_count}/{total_elements} ({mismatch_ratio:.2%}), "
            f"max_err={max_err:.2f}, mean_err={mean_err:.4f}, PSNR={psnr:.2f}dB (tol={self.tolerance})"
        )

        return ComparisonResult(
            is_match=is_match,
            total_elements=total_elements,
            mismatch_count=mismatch_count,
            mismatch_ratio=mismatch_ratio,
            max_abs_error=max_err,
            mean_abs_error=mean_err,
            psnr_db=round(psnr, 2),
            error_summary=summary,
        )
