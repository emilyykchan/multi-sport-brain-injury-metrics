from __future__ import annotations

from .constants import BRIC_CRITICAL_CSDM
from .damage import damage_dynasaur
from .dynars_metrics import bric_dynars, hic15_dynars
from .harm import harm
from .models import ImpactKinematics
from .peaks import pla, pra, prv
from .ubric import ubric_gabler_2018


def compute_metrics(
    kin: ImpactKinematics,
    *,
    bric_critical_rad_s: tuple[float, float, float] = BRIC_CRITICAL_CSDM,
    damage_backend: str | None = "dynasaur",
) -> dict[str, float]:
    """Compute the non-XGB metrics for one impact.

    Parameters
    ----------
    damage_backend:
        "dynasaur" to calculate DAMAGE with the open-source Dynasaur implementation;
        None to omit DAMAGE and HARM.
    """
    results = {
        "PLA_g": pla(kin.linear_acceleration_g),
        "PRA_rad_s2": pra(kin.angular_acceleration_rad_s2),
        "PRV_rad_s": prv(kin.angular_velocity_rad_s),
        "HIC15": hic15_dynars(kin.linear_acceleration_g, kin.dt_s),
        "BrIC": bric_dynars(kin.angular_velocity_rad_s, bric_critical_rad_s),
        "UBrIC": ubric_gabler_2018(
            kin.angular_velocity_rad_s,
            kin.angular_acceleration_rad_s2,
        ),
    }

    if damage_backend is None:
        return results
    if damage_backend == "dynasaur":
        dmg = damage_dynasaur(kin.time_s, kin.angular_acceleration_rad_s2)
    else:
        raise ValueError("damage_backend must be 'dynasaur' or None.")

    results["DAMAGE"] = dmg
    results["HARM"] = harm(results["HIC15"], dmg)
    return results
