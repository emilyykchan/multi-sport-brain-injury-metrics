import importlib.util
import numpy as np
import pytest

from brain_injury_metrics.dynars_metrics import bric_dynars, hic15_dynars


pytestmark = pytest.mark.skipif(importlib.util.find_spec("dynars") is None, reason="dynars not installed")


def test_dynars_hic_and_bric_smoke():
    t = np.arange(0.0, 0.0201, 0.001)
    la = np.zeros((len(t), 3))
    la[5:9, 0] = 50.0
    w = np.zeros((len(t), 3))
    w[:, 0] = np.linspace(0, 20, len(t))
    assert hic15_dynars(la, 0.001) >= 0.0
    assert bric_dynars(w) >= 0.0
