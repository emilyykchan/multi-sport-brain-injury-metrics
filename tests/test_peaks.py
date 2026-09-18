import numpy as np

from brain_injury_metrics.peaks import pla, pra, prv, resultant


def test_resultant_and_conventional_peaks():
    xyz = np.array([[3.0, 4.0, 0.0], [0.0, 0.0, 12.0]])
    np.testing.assert_allclose(resultant(xyz), [5.0, 12.0])
    assert pla(xyz) == 12.0
    assert prv(xyz) == 12.0
    assert pra(xyz) == 12.0
