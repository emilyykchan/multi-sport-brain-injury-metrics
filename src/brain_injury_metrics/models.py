from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .validation import as_time, as_xyz, uniform_dt


@dataclass(frozen=True)
class ImpactKinematics:
    """Kinematic time histories supplied to injury-metric calculations.

    Parameters are explicit about units to prevent silent unit-conversion errors.
    No filtering or signal derivation is performed by this class; filtering
    provenance is documented separately for each source dataset.
    """

    time_s: np.ndarray
    linear_acceleration_g: np.ndarray
    angular_velocity_rad_s: np.ndarray
    angular_acceleration_rad_s2: np.ndarray

    def __post_init__(self) -> None:
        time = as_time(self.time_s)
        la = as_xyz(self.linear_acceleration_g, name="linear_acceleration_g")
        w = as_xyz(self.angular_velocity_rad_s, name="angular_velocity_rad_s")
        aa = as_xyz(self.angular_acceleration_rad_s2, name="angular_acceleration_rad_s2")
        n = time.size
        if not (la.shape[0] == w.shape[0] == aa.shape[0] == n):
            raise ValueError("All kinematic arrays must have the same number of samples.")
        object.__setattr__(self, "time_s", time)
        object.__setattr__(self, "linear_acceleration_g", la)
        object.__setattr__(self, "angular_velocity_rad_s", w)
        object.__setattr__(self, "angular_acceleration_rad_s2", aa)

    @property
    def dt_s(self) -> float:
        return uniform_dt(self.time_s)
