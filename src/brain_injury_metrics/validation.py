from __future__ import annotations

import numpy as np


def as_xyz(values, *, name: str) -> np.ndarray:
    """Return a finite float array with shape (N, 3)."""
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 2 or arr.shape[1] != 3:
        raise ValueError(f"{name} must have shape (N, 3); got {arr.shape}.")
    if arr.shape[0] < 2:
        raise ValueError(f"{name} must contain at least two samples.")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} contains non-finite values.")
    return arr


def as_time(values, *, name: str = "time_s") -> np.ndarray:
    """Return strictly increasing finite time in seconds."""
    arr = np.asarray(values, dtype=float).squeeze()
    if arr.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional.")
    if arr.size < 2:
        raise ValueError(f"{name} must contain at least two samples.")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} contains non-finite values.")
    if np.any(np.diff(arr) <= 0):
        raise ValueError(f"{name} must be strictly increasing.")
    return arr


def uniform_dt(time_s: np.ndarray, *, rtol: float = 1e-4, atol: float = 1e-10) -> float:
    """Return sample interval for an approximately uniformly sampled trace."""
    time_s = as_time(time_s)
    dts = np.diff(time_s)
    dt = float(np.median(dts))
    if not np.allclose(dts, dt, rtol=rtol, atol=atol):
        raise ValueError(
            "Trace is not uniformly sampled. Resample explicitly before using metrics "
            "that assume a constant sample interval."
        )
    return dt
