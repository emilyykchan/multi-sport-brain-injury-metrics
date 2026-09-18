from __future__ import annotations

from dataclasses import dataclass
import importlib
import inspect
import numpy as np

from .validation import as_time, as_xyz, uniform_dt


@dataclass(frozen=True)
class DAMAGEParams:
    """Published DAMAGE model parameters used by Dynasaur / published specifications."""

    mx: float = 1.0
    my: float = 1.0
    mz: float = 1.0
    kxx: float = 32142.0
    kyy: float = 23493.0
    kzz: float = 16935.0
    kxy: float = 0.0
    kyz: float = 0.0
    kxz: float = 1636.3
    a0: float = 0.0
    a1: float = 0.0059148
    beta: float = 2.9903


def _normalise_name(name: str) -> str:
    return name.lower().replace("_", "").replace("-", "")


def _dynasaur_damage_function():
    """Locate Dynasaur's public DAMAGE standard function without vendoring its GPL code."""
    candidates = [
        "dynasaur.calc.standard_functions",
        "dynasaur.standard_functions",
    ]
    errors = []
    for module_name in candidates:
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:  # pragma: no cover - external package/version dependent
            errors.append(f"{module_name}: {exc}")
            continue
        for attr in ("DAMAGE", "damage"):
            fn = getattr(module, attr, None)
            if callable(fn):
                return fn
    raise ImportError(
        "Could not locate Dynasaur's DAMAGE standard function. Install `dynasaur==1.3.53` "
        "in a compatible Python environment. Attempts: " + "; ".join(errors)
    )


def damage_dynasaur(
    time_s: np.ndarray,
    angular_acceleration_rad_s2: np.ndarray,
    *,
    params: DAMAGEParams = DAMAGEParams(),
) -> float:
    """Calculate DAMAGE by calling the open-source Dynasaur implementation.

    No filtering is performed here. Supply the angular-acceleration traces after the
    chosen preprocessing/filtering pipeline.

    Dynasaur has used the parameter names `ra_x`, `ra_y`, `ra_z`, `time`, `mx`, ...,
    `a1`, `beta` in its published definition-file examples. This adapter inspects the
    installed function signature and maps those names explicitly.
    """
    t = as_time(time_s)
    aa = as_xyz(angular_acceleration_rad_s2, name="angular_acceleration_rad_s2")
    if len(t) != len(aa):
        raise ValueError("time_s and angular_acceleration_rad_s2 length mismatch.")

    fn = _dynasaur_damage_function()
    values = {
        "time": t,
        "t": t,
        "rax": aa[:, 0],
        "ray": aa[:, 1],
        "raz": aa[:, 2],
        "alphax": aa[:, 0],
        "alphay": aa[:, 1],
        "alphaz": aa[:, 2],
        "mx": params.mx,
        "my": params.my,
        "mz": params.mz,
        "kxx": params.kxx,
        "kyy": params.kyy,
        "kzz": params.kzz,
        "kxy": params.kxy,
        "kyz": params.kyz,
        "kxz": params.kxz,
        "a0": params.a0,
        "a1": params.a1,
        "beta": params.beta,
    }

    sig = inspect.signature(fn)
    kwargs = {}
    unsupported = []
    for name, p in sig.parameters.items():
        if p.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue
        key = _normalise_name(name)
        if key in values:
            kwargs[name] = values[key]
        elif p.default is inspect.Parameter.empty:
            unsupported.append(name)

    if unsupported:
        raise RuntimeError(
            "Installed Dynasaur exposes an unexpected DAMAGE signature. Unmapped required "
            f"arguments: {unsupported}. Signature: {sig}. Please record the installed "
            "Dynasaur version before adapting this wrapper."
        )

    result = fn(**kwargs)
    if hasattr(result, "magnitude"):
        result = result.magnitude
    arr = np.asarray(result, dtype=float).squeeze()
    if arr.size != 1:
        raise RuntimeError(f"Dynasaur DAMAGE returned a non-scalar result with shape {arr.shape}.")
    return float(arr)
