from __future__ import annotations

import numpy as np
import pint

from .validation import as_xyz


# Published DAMAGE parameters
# Gabler et al., Annals of Biomedical Engineering (2019)
DAMAGE_MX = 1.0
DAMAGE_MY = 1.0
DAMAGE_MZ = 1.0

DAMAGE_KXX = 32142.0
DAMAGE_KYY = 23493.0
DAMAGE_KZZ = 16935.0

DAMAGE_KXY = 0.0
DAMAGE_KYZ = 0.0
DAMAGE_KXZ = 1636.3

DAMAGE_A0 = 0.0
DAMAGE_A1 = 0.0059148  # s
DAMAGE_BETA = 2.9903


def _dynasaur_damage():
    """Return Dynasaur's public DAMAGE implementation."""
    try:
        from dynasaur.calc.standard_functions import StandardFunction
    except ImportError as exc:
        raise ImportError(
            "Dynasaur is required for DAMAGE calculation. "
            "Install dynasaur==1.3.53 with a compatible SciPy version."
        ) from exc

    if not hasattr(StandardFunction, "DAMAGE"):
        raise ImportError(
            "The installed Dynasaur version does not expose "
            "StandardFunction.DAMAGE."
        )

    return StandardFunction.DAMAGE


def damage_dynasaur(
    time_s: np.ndarray,
    rotational_acceleration_rad_s2: np.ndarray,
) -> float:
    """Calculate DAMAGE using the Dynasaur implementation.

    Parameters
    ----------
    time_s
        One-dimensional time vector in seconds.

    rotational_acceleration_rad_s2
        Rotational acceleration components with shape
        ``(n_samples, 3)`` in rad/s².

    Returns
    -------
    float
        DAMAGE value.

    Notes
    -----
    DAMAGE is evaluated using ``StandardFunction.DAMAGE`` from
    Dynasaur 1.3.53 with the published model parameters of
    Gabler et al.

    No model parameters are fitted or recalibrated using the
    present dataset.
    """
    time = np.asarray(time_s, dtype=float).reshape(-1)

    aa = as_xyz(
        rotational_acceleration_rad_s2,
        name="rotational_acceleration_rad_s2",
    )

    if len(time) != len(aa):
        raise ValueError(
            "time_s and rotational_acceleration_rad_s2 "
            "must contain the same number of samples."
        )

    if len(time) < 2:
        raise ValueError(
            "At least two time samples are required for DAMAGE."
        )

    if not np.all(np.isfinite(time)):
        raise ValueError("time_s contains non-finite values.")

    if not np.all(np.isfinite(aa)):
        raise ValueError(
            "rotational_acceleration_rad_s2 contains non-finite values."
        )

    if np.any(np.diff(time) <= 0):
        raise ValueError(
            "time_s must be strictly increasing."
        )

    # Dynasaur's DAMAGE implementation expects Pint quantities and
    # converts them internally to base SI units.
    ureg = pint.UnitRegistry()

    time_q = time * ureg.second

    aa_x_q = aa[:, 0] * ureg.radian / ureg.second**2
    aa_y_q = aa[:, 1] * ureg.radian / ureg.second**2
    aa_z_q = aa[:, 2] * ureg.radian / ureg.second**2

    fn = _dynasaur_damage()

    value = fn(
        time_q,
        aa_x_q,
        aa_y_q,
        aa_z_q,
        DAMAGE_MX,
        DAMAGE_MY,
        DAMAGE_MZ,
        DAMAGE_KXX,
        DAMAGE_KYY,
        DAMAGE_KZZ,
        DAMAGE_KXY,
        DAMAGE_KYZ,
        DAMAGE_KXZ,
        DAMAGE_A0,
        DAMAGE_A1,
        DAMAGE_BETA,
    )

    return float(value)