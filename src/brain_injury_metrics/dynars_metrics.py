from __future__ import annotations

from importlib import metadata

import numpy as np

from .constants import BRIC_CRITICAL_CSDM
from .validation import as_xyz


def _dynars_injury():
    """Return the dynars injury-criteria module."""
    try:
        import dynars
    except ImportError as exc:  # pragma: no cover - optional runtime dependency
        raise ImportError(
            "dynars is required for HIC15 and BrIC. "
            "Install it with `pip install dynars==1.1.0`."
        ) from exc

    if not hasattr(dynars, "injury"):
        raise ImportError(
            "The installed dynars package does not expose the `injury` module. "
            "This project expects dynars==1.1.0."
        )

    return dynars.injury


def dynars_version() -> str:
    """Return the installed dynars version."""
    try:
        return metadata.version("dynars")
    except metadata.PackageNotFoundError:
        return "not installed"


def hic15_dynars(
    linear_acceleration_g: np.ndarray,
    dt_s: float,
) -> float:
    """Calculate HIC15 using the open-source dynars implementation.

    Parameters
    ----------
    linear_acceleration_g
        Linear acceleration components with shape (n_samples, 3), in g.
    dt_s
        Uniform sampling interval in seconds.

    Returns
    -------
    float
        HIC15.

    Notes
    -----
    The resultant acceleration and HIC15 are both calculated using
    ``dynars.injury``. dynars evaluates candidate intervals up to 15 ms
    according to the HIC15 definition.
    """
    if not np.isfinite(dt_s) or dt_s <= 0:
        raise ValueError("dt_s must be a positive finite number.")

    xyz = as_xyz(
        linear_acceleration_g,
        name="linear_acceleration_g",
    )

    injury = _dynars_injury()

    # Convert to numpy arrays for dynars
    ax = np.asarray(xyz[:, 0], dtype=float)
    ay = np.asarray(xyz[:, 1], dtype=float)
    az = np.asarray(xyz[:, 2], dtype=float)

    a_resultant = injury.resultant(ax, ay, az)

    return float(
        injury.hic15(
            a_resultant,
            float(dt_s),
        )
    )


def bric_dynars(
    angular_velocity_rad_s: np.ndarray,
    critical_rad_s: tuple[float, float, float] = BRIC_CRITICAL_CSDM,
) -> float:
    """Calculate BrIC using the open-source dynars implementation.

    Parameters
    ----------
    angular_velocity_rad_s
        Angular velocity components with shape (n_samples, 3), in rad/s.
    critical_rad_s
        Direction-specific BrIC critical angular velocities in rad/s.

    Returns
    -------
    float
        BrIC.
    """
    xyz = as_xyz(
        angular_velocity_rad_s,
        name="angular_velocity_rad_s",
    )

    critical = tuple(float(value) for value in critical_rad_s)

    if len(critical) != 3 or any(
        not np.isfinite(value) or value <= 0
        for value in critical
    ):
        raise ValueError(
            "critical_rad_s must contain three positive finite values."
        )

    injury = _dynars_injury()

    wx = np.asarray(xyz[:, 0], dtype=float)
    wy = np.asarray(xyz[:, 1], dtype=float)
    wz = np.asarray(xyz[:, 2], dtype=float)

    return float(
        injury.bric(
            wx,
            wy,
            wz,
            critical[0],
            critical[1],
            critical[2],
        )
    )