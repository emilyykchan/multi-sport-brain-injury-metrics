from __future__ import annotations

from importlib import metadata
import numpy as np

from .constants import BRIC_CRITICAL_CSDM
from .validation import as_xyz


def _dynars():
    try:
        import dynars
    except ImportError as exc:  # pragma: no cover - depends on optional runtime package
        raise ImportError(
            "dynars is required for HIC15 and BrIC. Install the pinned dependency "
            "with `pip install dynars==1.1.0`."
        ) from exc
    return dynars


def dynars_version() -> str:
    try:
        return metadata.version("dynars")
    except metadata.PackageNotFoundError:
        return "not installed"


def hic15_dynars(linear_acceleration_g: np.ndarray, dt_s: float) -> float:
    """HIC15 using the open-source dynars implementation.

    dynars evaluates all candidate sub-windows with duration <= 15 ms.
    Input acceleration is in g and dt in seconds.
    """
    if not np.isfinite(dt_s) or dt_s <= 0:
        raise ValueError("dt_s must be a positive finite number.")
    xyz = as_xyz(linear_acceleration_g, name="linear_acceleration_g")
    d = _dynars()
    a_res = d.resultant(xyz[:, 0], xyz[:, 1], xyz[:, 2])
    return float(d.hic15(a_res, float(dt_s)))


def bric_dynars(
    angular_velocity_rad_s: np.ndarray,
    critical_rad_s: tuple[float, float, float] = BRIC_CRITICAL_CSDM,
) -> float:
    """BrIC using the open-source dynars implementation.

    Critical angular velocities are passed explicitly so the chosen calibration is visible.
    """
    w = as_xyz(angular_velocity_rad_s, name="angular_velocity_rad_s")
    crit = tuple(float(x) for x in critical_rad_s)
    if len(crit) != 3 or any(x <= 0 for x in crit):
        raise ValueError("critical_rad_s must contain three positive values.")
    d = _dynars()
    return float(d.bric(w[:, 0], w[:, 1], w[:, 2], *crit))
