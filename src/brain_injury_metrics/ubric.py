from __future__ import annotations

import numpy as np

from .constants import (
    UBRIC_ALPHA_CRITICAL_MPS_RAD_S2,
    UBRIC_OMEGA_CRITICAL_MPS_P2P_RAD_S,
    UBRIC_R,
)
from .validation import as_xyz


def ubric_gabler_2018(
    angular_velocity_rad_s: np.ndarray,
    angular_acceleration_rad_s2: np.ndarray,
    *,
    omega_critical_rad_s: tuple[float, float, float] = UBRIC_OMEGA_CRITICAL_MPS_P2P_RAD_S,
    alpha_critical_rad_s2: tuple[float, float, float] = UBRIC_ALPHA_CRITICAL_MPS_RAD_S2,
    r: float = UBRIC_R,
) -> float:
    """Universal Brain Injury Criterion following Gabler et al. (2018).

    This implementation uses the peak-to-peak angular-velocity form described by
    Gabler et al. (2018):

        omega_p2p_i = max(omega_i) - min(omega_i)
        alpha_peak_i = max(abs(alpha_i))

        term_i = w_i + (a_i - w_i) * exp(-a_i / w_i)
        UBrIC = (sum(term_i ** r)) ** (1 / r)

    with w_i = omega_p2p_i / omega_critical_i and
    a_i = alpha_peak_i / alpha_critical_i.

    Reference
    ---------
    Gabler LF, Crandall JR, Panzer MB. Development of a Metric for Predicting Brain
    Strain Responses Using Head Kinematics. Ann Biomed Eng. 2018;46:972-985.
    doi:10.1007/s10439-018-2015-9
    """
    w = as_xyz(angular_velocity_rad_s, name="angular_velocity_rad_s")
    aa = as_xyz(angular_acceleration_rad_s2, name="angular_acceleration_rad_s2")
    if w.shape != aa.shape:
        raise ValueError("angular velocity and acceleration must have identical shapes.")

    omega_crit = np.asarray(omega_critical_rad_s, dtype=float)
    alpha_crit = np.asarray(alpha_critical_rad_s2, dtype=float)
    if omega_crit.shape != (3,) or alpha_crit.shape != (3,):
        raise ValueError("Critical values must each contain exactly three axes.")
    if np.any(omega_crit <= 0) or np.any(alpha_crit <= 0):
        raise ValueError("Critical values must be positive.")
    if r <= 0:
        raise ValueError("r must be positive.")

    omega_p2p = np.ptp(w, axis=0)
    alpha_peak = np.max(np.abs(aa), axis=0)

    w_star = omega_p2p / omega_crit
    a_star = alpha_peak / alpha_crit

    terms = np.zeros(3, dtype=float)
    positive = w_star > 0
    wp = w_star[positive]
    ap = a_star[positive]
    terms[positive] = wp + (ap - wp) * np.exp(-ap / wp)

    return float(np.sum(terms**r) ** (1.0 / r))
