import importlib.util
import numpy as np
import pytest

from brain_injury_metrics.damage import damage_dynasaur


pytestmark = pytest.mark.skipif(importlib.util.find_spec("dynasaur") is None, reason="Dynasaur not installed")


def test_dynasaur_zero_input_smoke():
    t = np.linspace(0.0, 0.05, 51)
    aa = np.zeros((len(t), 3))
    assert abs(damage_dynasaur(t, aa)) < 1e-12
