#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

# Allows running directly from a source checkout without installation.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from brain_injury_metrics.io import (  # noqa: E402
    PROTECHT_COLUMN_MAP,
    read_impact,
    validate_exported_resultants,
)
from brain_injury_metrics.pipeline import compute_metrics  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Calculate injury metrics for one-impact-per-XLSX Protecht data."
    )
    p.add_argument("--input-dir", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument(
        "--pattern",
        default="*.xlsx",
        help="Input filename glob. Default: *.xlsx",
    )
    p.add_argument(
        "--damage-backend",
        choices=["dynasaur", "none"],
        default="dynasaur",
        help="Use Dynasaur for DAMAGE/HARM, or 'none' to omit them.",
    )
    p.add_argument(
        "--skip-resultant-qc",
        action="store_true",
        help="Do not compare exported *Res channels with recomputed XYZ resultants.",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cmap = PROTECHT_COLUMN_MAP
    backend = None if args.damage_backend == "none" else args.damage_backend

    files = sorted(p for p in args.input_dir.glob(args.pattern) if p.is_file())
    if not files:
        raise SystemExit(f"No files matching {args.pattern!r} found in {args.input_dir}")

    rows: list[dict] = []
    qc_rows: list[dict] = []
    errors: list[dict] = []

    for path in files:
        try:
            kin = read_impact(path, cmap)
            result = compute_metrics(kin, damage_backend=backend)
            rows.append({"impact": path.stem, **result})

            if not args.skip_resultant_qc:
                qc = validate_exported_resultants(path, cmap)
                qc_rows.append({"impact": path.stem, **qc})
        except Exception as exc:
            errors.append({"impact": path.stem, "file": path.name, "error": repr(exc)})

    out = pd.DataFrame(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    if args.output.suffix.lower() == ".xlsx":
        with pd.ExcelWriter(args.output) as writer:
            out.to_excel(writer, sheet_name="metrics", index=False)
            if qc_rows:
                pd.DataFrame(qc_rows).to_excel(writer, sheet_name="resultant_qc", index=False)
            if errors:
                pd.DataFrame(errors).to_excel(writer, sheet_name="errors", index=False)
    else:
        out.to_csv(args.output, index=False)
        if qc_rows:
            qc_path = args.output.with_name(args.output.stem + "_resultant_qc.csv")
            pd.DataFrame(qc_rows).to_csv(qc_path, index=False)
        if errors:
            err_path = args.output.with_name(args.output.stem + "_errors.csv")
            pd.DataFrame(errors).to_csv(err_path, index=False)

    print(f"Processed {len(rows)} impacts; {len(errors)} errors. Output: {args.output}")


if __name__ == "__main__":
    main()
