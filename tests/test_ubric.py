import numpy as np

from brain_injury_metrics.constants import (
    UBRIC_ALPHA_CRITICAL_MPS_RAD_S2,
    UBRIC_OMEGA_CRITICAL_MPS_P2P_RAD_S,
)
from brain_injury_metrics.ubric import ubric_gabler_2018


def manual_ubric(w, aa):
    omega_p2p = np.ptp(w, axis=0)
    alpha_peak = np.max(np.abs(aa), axis=0)
    ws = omega_p2p / np.asarray(UBRIC_OMEGA_CRITICAL_MPS_P2P_RAD_S)
    aps = alpha_peak / np.asarray(UBRIC_ALPHA_CRITICAL_MPS_RAD_S2)
    terms = np.where(ws > 0, ws + (aps - ws) * np.exp(-aps / ws), 0.0)
    return float(np.sqrt(np.sum(terms**2)))


def test_ubric_matches_hand_calculation():
    w = np.array([[-10.0, -20.0, 0.0], [20.0, 10.0, 5.0], [5.0, 0.0, -2.0]])
    aa = np.array([[1000.0, -2500.0, 300.0], [-2000.0, 1000.0, -800.0], [500.0, 0.0, 100.0]])
    expected = manual_ubric(w, aa)
    actual = ubric_gabler_2018(w, aa)
    assert np.isclose(actual, expected, rtol=1e-12, atol=0.0)


def test_ubric_is_invariant_to_constant_angular_velocity_baseline():
    w = np.array([[-10.0, -20.0, 0.0], [20.0, 10.0, 5.0], [5.0, 0.0, -2.0]])
    aa = np.array([[1000.0, -2500.0, 300.0], [-2000.0, 1000.0, -800.0], [500.0, 0.0, 100.0]])
    offset = np.array([35.0, -12.0, 8.0])
    assert np.isclose(
        ubric_gabler_2018(w, aa),
        ubric_gabler_2018(w + offset, aa),
        rtol=1e-12,
    )


def test_ubric_zero_trace_is_zero():
    w = np.zeros((4, 3))
    aa = np.zeros((4, 3))
    assert ubric_gabler_2018(w, aa) == 0.0
