from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .models import ImpactKinematics


@dataclass(frozen=True)
class ColumnMap:
    """Column names and units for one-impact-per-file kinematic data."""

    time_ms: str
    linear_acceleration_g: tuple[str, str, str]
    angular_velocity_rad_s: tuple[str, str, str]
    angular_acceleration_rad_s2: tuple[str, str, str]
    linear_acceleration_resultant_g: str | None = None
    angular_velocity_resultant_rad_s: str | None = None
    angular_acceleration_resultant_rad_s2: str | None = None

    @property
    def required_columns(self) -> list[str]:
        """Columns used in the actual metric calculations."""
        return [
            self.time_ms,
            *self.linear_acceleration_g,
            *self.angular_velocity_rad_s,
            *self.angular_acceleration_rad_s2,
        ]

    @property
    def resultant_columns(self) -> list[str]:
        """Optional exported resultants used only for quality-control checks."""
        return [
            c
            for c in (
                self.linear_acceleration_resultant_g,
                self.angular_velocity_resultant_rad_s,
                self.angular_acceleration_resultant_rad_s2,
            )
            if c is not None
        ]


# Default schema for the Protecht impact spreadsheets used in this study.
# One .xlsx file = one impact.
PROTECHT_COLUMN_MAP = ColumnMap(
    time_ms="t(ms)",
    linear_acceleration_g=("LinAccX", "LinAccY", "LinAccZ"),
    angular_velocity_rad_s=("RotVelX", "RotVelY", "RotVelZ"),
    angular_acceleration_rad_s2=("RotAccX", "RotAccY", "RotAccZ"),
    linear_acceleration_resultant_g="LinAccRes",
    angular_velocity_resultant_rad_s="RotVelRes",
    angular_acceleration_resultant_rad_s2="RotAccRes",
)


def _read_dataframe(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".xlsx":
        return pd.read_excel(path, sheet_name=0)
    if path.suffix.lower() == ".csv":
        # CSV support is retained for testing / future reuse; study data are .xlsx.
        return pd.read_csv(path, sep=None, engine="python")
    raise ValueError(f"Unsupported impact file extension: {path.suffix}")


def _numeric_required_data(df: pd.DataFrame, path: Path, column_map: ColumnMap) -> pd.DataFrame:
    missing = [c for c in column_map.required_columns if c not in df.columns]
    if missing:
        raise KeyError(
            f"{path.name} is missing required columns: {missing}. "
            f"Available columns: {list(df.columns)}"
        )

    numeric = df[column_map.required_columns].apply(pd.to_numeric, errors="coerce")
    numeric = numeric.dropna(subset=column_map.required_columns)
    if len(numeric) < 2:
        raise ValueError(f"{path.name} has fewer than two complete numeric samples.")

    numeric = numeric.sort_values(column_map.time_ms)
    numeric = numeric.drop_duplicates(subset=[column_map.time_ms], keep="first")
    return numeric


def read_impact(
    path: str | Path,
    column_map: ColumnMap = PROTECHT_COLUMN_MAP,
) -> ImpactKinematics:
    """Read one impact spreadsheet using explicit named component channels.

    The study data are expected to contain one impact per .xlsx file with the
    Protecht schema defined by :data:`PROTECHT_COLUMN_MAP`. Exported resultant
    columns (``*Res``) are deliberately not used as calculation inputs: all
    resultants are recalculated from the three component channels.

    No filtering is performed here. The input spreadsheet is treated as the
    kinematic trace supplied to the injury-metric calculation pipeline.
    """
    path = Path(path)
    df = _read_dataframe(path)
    numeric = _numeric_required_data(df, path, column_map)

    t_s = numeric[column_map.time_ms].to_numpy(float) / 1000.0
    # The absolute time origin is irrelevant to the metrics; normalising to zero
    # makes every impact internally consistent even when exported time starts at 1 ms.
    t_s = t_s - t_s[0]

    la = numeric[list(column_map.linear_acceleration_g)].to_numpy(float)
    w = numeric[list(column_map.angular_velocity_rad_s)].to_numpy(float)
    aa = numeric[list(column_map.angular_acceleration_rad_s2)].to_numpy(float)

    return ImpactKinematics(t_s, la, w, aa)


def validate_exported_resultants(
    path: str | Path,
    column_map: ColumnMap = PROTECHT_COLUMN_MAP,
    *,
    rtol: float = 1e-5,
    atol: float = 1e-6,
) -> dict[str, float | bool]:
    """Compare exported ``*Res`` columns with resultants recomputed from XYZ.

    This is a data-integrity check only. The exported resultant columns are not
    used to calculate injury metrics.
    """
    path = Path(path)
    df = _read_dataframe(path)

    missing_required = [c for c in column_map.required_columns if c not in df.columns]
    if missing_required:
        raise KeyError(f"{path.name} is missing required columns: {missing_required}")

    checks = [
        (
            "LinAccRes",
            column_map.linear_acceleration_g,
            column_map.linear_acceleration_resultant_g,
        ),
        (
            "RotVelRes",
            column_map.angular_velocity_rad_s,
            column_map.angular_velocity_resultant_rad_s,
        ),
        (
            "RotAccRes",
            column_map.angular_acceleration_rad_s2,
            column_map.angular_acceleration_resultant_rad_s2,
        ),
    ]

    result: dict[str, float | bool] = {}
    for label, components, resultant_col in checks:
        if resultant_col is None or resultant_col not in df.columns:
            result[f"{label}_present"] = False
            continue

        subset = df[[*components, resultant_col]].apply(pd.to_numeric, errors="coerce").dropna()
        xyz = subset[list(components)].to_numpy(float)
        exported = subset[resultant_col].to_numpy(float)
        recomputed = np.linalg.norm(xyz, axis=1)
        abs_diff = np.abs(exported - recomputed)
        denom = np.maximum(np.abs(recomputed), 1e-12)
        rel_diff = abs_diff / denom

        result[f"{label}_present"] = True
        result[f"{label}_allclose"] = bool(
            np.allclose(exported, recomputed, rtol=rtol, atol=atol)
        )
        result[f"{label}_max_abs_diff"] = float(abs_diff.max(initial=0.0))
        result[f"{label}_max_rel_diff"] = float(rel_diff.max(initial=0.0))

    return result
