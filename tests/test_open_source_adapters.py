import sys
import types
import numpy as np

from brain_injury_metrics.damage import damage_dynasaur
from brain_injury_metrics.dynars_metrics import bric_dynars, hic15_dynars


def test_dynars_wrapper_calls_public_api(monkeypatch):
    fake = types.ModuleType("dynars")
    calls = {}

    def resultant(x, y, z):
        calls["resultant"] = True
        return np.sqrt(np.asarray(x) ** 2 + np.asarray(y) ** 2 + np.asarray(z) ** 2)

    def hic15(a, dt):
        calls["hic15"] = (np.asarray(a), dt)
        return 123.0

    def bric(wx, wy, wz, cx, cy, cz):
        calls["bric"] = (cx, cy, cz)
        return 0.42

    fake.resultant = resultant
    fake.hic15 = hic15
    fake.bric = bric
    monkeypatch.setitem(sys.modules, "dynars", fake)

    la = np.array([[3.0, 4.0, 0.0], [0.0, 0.0, 5.0]])
    w = np.array([[1.0, 2.0, 3.0], [2.0, 3.0, 4.0]])
    assert hic15_dynars(la, 0.001) == 123.0
    assert bric_dynars(w, (66.2, 59.1, 44.2)) == 0.42
    assert calls["resultant"]
    np.testing.assert_allclose(calls["hic15"][0], [5.0, 5.0])
    assert calls["bric"] == (66.2, 59.1, 44.2)


def test_dynasaur_wrapper_maps_published_parameter_names(monkeypatch):
    root = types.ModuleType("dynasaur")
    calc = types.ModuleType("dynasaur.calc")
    standard = types.ModuleType("dynasaur.calc.standard_functions")
    seen = {}

    def DAMAGE(ra_x, ra_y, ra_z, time, mx, my, mz, kxx, kyy, kzz, kxy, kyz, kxz, a0, a1, beta):
        seen.update(locals())
        return 0.25

    standard.DAMAGE = DAMAGE
    monkeypatch.setitem(sys.modules, "dynasaur", root)
    monkeypatch.setitem(sys.modules, "dynasaur.calc", calc)
    monkeypatch.setitem(sys.modules, "dynasaur.calc.standard_functions", standard)

    t = np.array([0.0, 0.001, 0.002])
    aa = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
    assert damage_dynasaur(t, aa) == 0.25
    np.testing.assert_allclose(seen["ra_x"], aa[:, 0])
    np.testing.assert_allclose(seen["time"], t)
    assert seen["a1"] == 0.0059148
    assert seen["beta"] == 2.9903
