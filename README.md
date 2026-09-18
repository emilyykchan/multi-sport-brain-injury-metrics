# Multi-sport brain injury metrics

Python code for calculating brain injury metrics from instrumented-mouthguard head kinematics used in rugby union, amateur MMA, professional MMA and boxing.

The repository contains the metric calculations only. Kinematic filtering/preprocessing is performed upstream and is not repeated here.


## Metrics

| Metric | Implementation |
|---|---|
| PLA | Peak resultant linear acceleration calculated from the three linear-acceleration components |
| PRA | Peak resultant rotational acceleration calculated from the three rotational-acceleration components |
| PRV | Peak resultant rotational velocity calculated from the three rotational-velocity components |
| HIC15 | Open-source [`dynars`](https://pypi.org/project/dynars/) implementation |
| BrIC | Open-source `dynars` implementation with explicitly specified critical angular velocities |
| UBrIC | Gabler et al. (2018) peak-to-peak angular-velocity formulation implemented in this repository |
| DAMAGE | Open-source [`Dynasaur`](https://gitlab.com/VSI-TUGraz/Dynasaur) implementation using published model parameters |
| HARM | Published linear combination of HIC15 and DAMAGE |

The XGB-based metric used in the associated study will be added using the original trained model artefact and its exact feature-extraction pipeline; it is not reconstructed from manuscript text.

## Input format

Each impact is stored in one `.xlsx` file with the following columns:

```text
LinAccX  LinAccY  LinAccZ  LinAccRes
RotVelX  RotVelY  RotVelZ  RotVelRes
RotAccX  RotAccY  RotAccZ  RotAccRes
t(ms)
```

Units are:

- linear acceleration: g
- rotational velocity: rad/s
- rotational acceleration: rad/s²
- time: ms

Metric calculations use the XYZ component channels. The exported `*Res` columns are not used as calculation inputs; they are compared with resultants recomputed from XYZ as a quality-control check.

## Installation

Python 3.10–3.12 is supported. Python 3.11 is recommended when using Dynasaur.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e '.[dev]'
pip install dynasaur==1.3.53
```

`dynars==1.1.0` is installed as a package dependency.

## Batch calculation

For a folder containing one `.xlsx` file per impact:

```bash
python scripts/calculate_metrics.py \
  --input-dir test_impacts \
  --output results/test_impacts_metrics.xlsx \
  --damage-backend dynasaur
```

The output workbook contains:

- `metrics`: one row per impact;
- `resultant_qc`: comparison of exported and recomputed resultant traces;
- `errors`: files that could not be processed, if any.

## Metric definitions

### PLA, PRA and PRV

For a three-component kinematic signal \(q=(q_x,q_y,q_z)\), the resultant is

\[
q_r(t)=\sqrt{q_x(t)^2+q_y(t)^2+q_z(t)^2}.
\]

PLA, PRA and PRV are the maxima of the corresponding resultant time histories.

### HIC15

HIC15 is calculated with `dynars.hic15`, which maximises HIC over candidate time windows no longer than 15 ms.

### BrIC

BrIC is calculated with `dynars.bric`. The critical angular velocities are passed explicitly in `constants.py` so that the selected calibration is transparent.

The default values are the CSDM-derived critical velocities from Takhounts et al. (2013):

```text
(66.2, 59.1, 44.2) rad/s
```

The averaged CSDM/MPS values are also provided in `constants.py` for explicit selection when required.

### UBrIC

UBrIC follows Gabler, Crandall & Panzer (2018), using peak-to-peak angular velocity for each axis:

\[
\omega_{p2p,i}=\max(\omega_i)-\min(\omega_i)
\]

and peak absolute angular acceleration. The MPS-calibrated critical values used are:

```text
omega_critical = (211, 171, 115) rad/s
alpha_critical = (20000, 10300, 7760) rad/s²
r = 2
```

### DAMAGE

DAMAGE is calculated by calling the public Dynasaur implementation with the published model parameters defined in `damage.py`. No DAMAGE model is refitted to the input dataset.

### HARM

HARM is calculated as

\[
HARM = 0.0148\,HIC15 + 15.6\,DAMAGE.
\]

## Tests

```bash
pytest
```

Tests cover input parsing, conventional resultant peaks, UBrIC, HARM and the open-source package adapters.

## Data availability

No instrumented-mouthguard data are included in this repository. The code can therefore be shared independently of access restrictions applying to the underlying impact datasets.

## References

- Gabler LF, Crandall JR, Panzer MB. Development of a Metric for Predicting Brain Strain Responses Using Head Kinematics. *Annals of Biomedical Engineering*. 2018;46:972–985. doi:10.1007/s10439-018-2015-9.
- Takhounts EG, et al. Development of Brain Injury Criteria (BrIC). *Stapp Car Crash Journal*. 2013.
- Dynasaur, Vehicle Safety Institute, Graz University of Technology: https://gitlab.com/VSI-TUGraz/Dynasaur
- dynars: https://pypi.org/project/dynars/
