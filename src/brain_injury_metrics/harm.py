from __future__ import annotations

from .constants import HARM_DAMAGE_WEIGHT, HARM_HIC_WEIGHT


def harm(
    hic15: float,
    damage: float,
    *,
    hic_weight: float = HARM_HIC_WEIGHT,
    damage_weight: float = HARM_DAMAGE_WEIGHT,
) -> float:
    """Head Acceleration Response Metric (HARM)."""
    return float(hic_weight * float(hic15) + damage_weight * float(damage))
