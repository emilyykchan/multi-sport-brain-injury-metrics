from __future__ import annotations

import numpy as np

from .validation import as_xyz


def resultant(xyz: np.ndarray) -> np.ndarray:
    """Element-wise Euclidean resultant of three orthogonal components."""
    arr = as_xyz(xyz, name="xyz")
    return np.linalg.norm(arr, axis=1)


def _peak_resultant(xyz: np.ndarray) -> float:
    return float(np.max(resultant(xyz)))


def pla(linear_acceleration_g: np.ndarray) -> float:
    """Conventional peak resultant linear acceleration [g]."""
    return _peak_resultant(linear_acceleration_g)


def prv(angular_velocity_rad_s: np.ndarray) -> float:
    """Conventional peak resultant rotational velocity [rad/s].

    This is an absolute resultant peak, not a change in rotational velocity (delta-omega).
    """
    return _peak_resultant(angular_velocity_rad_s)


def pra(angular_acceleration_rad_s2: np.ndarray) -> float:
    """Conventional peak resultant rotational acceleration [rad/s^2]."""
    return _peak_resultant(angular_acceleration_rad_s2)
