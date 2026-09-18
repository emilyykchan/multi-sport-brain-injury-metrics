from pathlib import Path

import numpy as np
import pandas as pd

from brain_injury_metrics.io import PROTECHT_COLUMN_MAP, read_impact, validate_exported_resultants


def _protecht_frame() -> pd.DataFrame:
    la = np.array([[3.0, 4.0, 0.0], [0.0, 0.0, 2.0], [1.0, 2.0, 2.0]])
    w = np.array([[0.0, 0.0, 1.0], [1.0, 2.0, 2.0], [0.0, 3.0, 4.0]])
    aa = np.array([[6.0, 8.0, 0.0], [0.0, 0.0, 5.0], [2.0, 3.0, 6.0]])
    return pd.DataFrame(
        {
            "LinAccX": la[:, 0],
            "LinAccY": la[:, 1],
            "LinAccZ": la[:, 2],
            "LinAccRes": np.linalg.norm(la, axis=1),
            "RotVelX": w[:, 0],
            "RotVelY": w[:, 1],
            "RotVelZ": w[:, 2],
            "RotVelRes": np.linalg.norm(w, axis=1),
            "RotAccX": aa[:, 0],
            "RotAccY": aa[:, 1],
            "RotAccZ": aa[:, 2],
            "RotAccRes": np.linalg.norm(aa, axis=1),
            # Mirrors the study export: time does not need to start at 0.
            "t(ms)": [1.0, 2.0, 3.0],
        }
    )


def test_protecht_xlsx_schema_loads_without_custom_map(tmp_path: Path):
    path = tmp_path / "Rugby1478.xlsx"
    _protecht_frame().to_excel(path, index=False)

    kin = read_impact(path)
    assert kin.linear_acceleration_g.shape == (3, 3)
    assert kin.angular_velocity_rad_s.shape == (3, 3)
    assert kin.angular_acceleration_rad_s2.shape == (3, 3)
    np.testing.assert_allclose(kin.time_s, [0.0, 0.001, 0.002])
    assert kin.linear_acceleration_g[0, 0] == 3.0


def test_exported_resultants_are_qc_only_and_match_xyz(tmp_path: Path):
    path = tmp_path / "Rugby1478.xlsx"
    _protecht_frame().to_excel(path, index=False)

    qc = validate_exported_resultants(path)
    assert qc["LinAccRes_allclose"]
    assert qc["RotVelRes_allclose"]
    assert qc["RotAccRes_allclose"]


def test_metric_input_does_not_depend_on_exported_resultant(tmp_path: Path):
    path = tmp_path / "Rugby1478.xlsx"
    df = _protecht_frame()
    # Deliberately corrupt an exported resultant: the component input must remain unchanged.
    df["LinAccRes"] = 9999.0
    df.to_excel(path, index=False)

    kin = read_impact(path, PROTECHT_COLUMN_MAP)
    np.testing.assert_allclose(kin.linear_acceleration_g[0], [3.0, 4.0, 0.0])
    qc = validate_exported_resultants(path)
    assert not qc["LinAccRes_allclose"]
