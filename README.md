# Multi-sport brain injury metrics

Python code for calculating brain injury metrics from instrumented-mouthguard head kinematics used in rugby union, amateur MMA, professional MMA and boxing.

The repository contains the metric calculations only. Kinematic filtering/preprocessing is performed upstream and is not repeated here.


## Metrics

| Metric | Definition | Implementation in this repository | Reference |
|---|---|---|---|
| **PLA** Peak Linear Acceleration | Maximum of the resultant linear-acceleration time history: `max √(ax² + ay² + az²)`. Units: g. | Calculated directly from `LinAccX`, `LinAccY` and `LinAccZ`. The exported resultant channel is used only for QC. | Conventional head-kinematic measure; Hernandez et al. (2015), DOI: [10.1007/s10439-014-1212-4](https://doi.org/10.1007/s10439-014-1212-4). |
| **PRA** Peak Rotational Acceleration | Maximum of the resultant rotational-acceleration time history: `max √(αx² + αy² + αz²)`. Units: rad/s². | Calculated directly from `RotAccX`, `RotAccY` and `RotAccZ`. | Conventional head-kinematic measure; Hernandez et al. (2015), DOI: [10.1007/s10439-014-1212-4](https://doi.org/10.1007/s10439-014-1212-4). |
| **PRV** Peak Rotational Velocity | Maximum of the resultant rotational-velocity time history: `max √(ωx² + ωy² + ωz²)`. Units: rad/s. | Calculated directly from `RotVelX`, `RotVelY` and `RotVelZ`. | Conventional head-kinematic measure; Hernandez et al. (2015), DOI: [10.1007/s10439-014-1212-4](https://doi.org/10.1007/s10439-014-1212-4). |
| **HIC15** Head Injury Criterion | Maximum HIC calculated from resultant linear acceleration over all candidate intervals with `t2 − t1 ≤ 15 ms`: `(t2−t1) × [mean acceleration over (t1,t2)]^2.5`. Acceleration is expressed in g. | Calculated using [`dynars==1.1.0`](https://docs.rs/dynars/latest/dynars/results/injury/index.html), which searches candidate windows up to 15 ms. | HIC15 is formally defined in NHTSA crashworthiness standards; it is also commonly used in head-impact biomechanics. See Hernandez et al. (2015), DOI: [10.1007/s10439-014-1212-4](https://doi.org/10.1007/s10439-014-1212-4). |
| **BrIC** Brain Injury Criterion | Direction-dependent combination of peak absolute angular velocities: `BrIC = √[(ωx/ωxc)² + (ωy/ωyc)² + (ωz/ωzc)²]`. | Calculated using [`dynars==1.1.0`](https://docs.rs/dynars/latest/dynars/results/injury/index.html), with the critical values CSDM-derived values `(66.2, 59.1, 44.2) rad/s`. The averaged CSDM/MPS values `(66.25, 56.45, 42.87) rad/s` are also retained in `constants.py` for selection. | Takhounts et al. (2013), DOI: [10.4271/2013-22-0010](https://doi.org/10.4271/2013-22-0010). The `(66.2, 59.1, 44.2)` set is also used by Hernandez et al. (2015), DOI: [10.1007/s10439-014-1212-4](https://doi.org/10.1007/s10439-014-1212-4). |
| **UBrIC** Universal Brain Injury Criterion | Combines direction-dependent rotational velocity and acceleration. For each axis, rotational velocity is defined as peak-to-peak, `ωp2p = max(ω) − min(ω)`, and rotational acceleration as `max \|α\|`. The MPS-calibrated critical values used here are `ωcr = (211, 171, 115) rad/s`, `αcr = (20.0, 10.3, 7.76) krad/s²`, with `r = 2`. | Implemented directly in this repository from the published Gabler et al. formulation.| Gabler, Crandall & Panzer (2018), *Development of a Metric for Predicting Brain Strain Responses Using Head Kinematics*, *Annals of Biomedical Engineering* 46:972–985, DOI: [10.1007/s10439-018-2015-9](https://doi.org/10.1007/s10439-018-2015-9). |
| **DAMAGE** Diffuse Axonal Multi-Axis General Evaluation | A coupled three-degree-of-freedom second-order system driven by the three rotational-acceleration time histories. DAMAGE is the scaled maximum resultant deformation of the system and was developed as a rapid estimator of maximum brain strain. | Calculated using the open-source [`Dynasaur==1.3.53`](https://gitlab.com/VSI-TUGraz/Dynasaur) `StandardFunction.DAMAGE` implementation. Published model parameters are passed explicitly from `damage.py`; no parameters are fitted or recalibrated to the present dataset. | Gabler, Crandall & Panzer (2019), *Development of a Second-Order System for Rapid Estimation of Maximum Brain Strain*, *Annals of Biomedical Engineering* 47:1971–1981, DOI: [10.1007/s10439-018-02179-9](https://doi.org/10.1007/s10439-018-02179-9). |
| **HARM** Head Acceleration Response Metric | Linear combination of translational- and rotational-motion criteria: `HARM = 0.0148 × HIC15 + 15.6 × DAMAGE`. | Calculated directly in this repository from the HIC15 and DAMAGE values above. | Bailey et al. (2020), *Development and Evaluation of a Test Method for Assessing the Performance of American Football Helmets*, *Annals of Biomedical Engineering* 48:2566–2579, DOI: [10.1007/s10439-020-02626-6](https://doi.org/10.1007/s10439-020-02626-6). |

## Input format

Each impact is stored in one `.xlsx` file with the following columns:

```text
LinAccX  LinAccY  LinAccZ  LinAccRes
RotVelX  RotVelY  RotVelZ  RotVelRes
RotAccX  RotAccY  RotAccZ  RotAccRes
t(ms)
```

Units:

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

## Tests

```bash
pytest
```

Tests cover input parsing, conventional resultant peaks, UBrIC, HARM and the open-source package adapters.

## Data availability

No instrumented-mouthguard data are included in this repository. The code can therefore be shared independently of access restrictions applying to the underlying impact datasets.

## References

1. Hernandez F, Wu LC, Yip MC, et al. Six Degree-of-Freedom Measurements of Human Mild Traumatic Brain Injury. *Annals of Biomedical Engineering*. 2015;43(8):1918–1934. doi: 10.1007/s10439-014-1212-4.

2. Takhounts EG, Craig MJ, Moorhouse K, McFadden J, Hasija V. Development of Brain Injury Criteria (BrIC). *Stapp Car Crash Journal*. 2013;57:243–266. doi: 10.4271/2013-22-0010.

3. Gabler LF, Crandall JR, Panzer MB. Development of a Metric for Predicting Brain Strain Responses Using Head Kinematics. *Annals of Biomedical Engineering*. 2018;46(7):972–985. doi: 10.1007/s10439-018-2015-9.

4. Gabler LF, Crandall JR, Panzer MB. Development of a Second-Order System for Rapid Estimation of Maximum Brain Strain. *Annals of Biomedical Engineering*. 2019;47(9):1971–1981. doi: 10.1007/s10439-018-02179-9.

5. Bailey AM, Sanchez EJ, Park G, et al. Development and Evaluation of a Test Method for Assessing the Performance of American Football Helmets. *Annals of Biomedical Engineering*. 2020;48(11):2566–2579. doi: 10.1007/s10439-020-02626-6.

### Software

- **dynars 1.1.0**: open-source injury-criterion implementation used here for HIC15 and BrIC.
- **Dynasaur 1.3.53**: open-source post-processing library developed by TU Graz; `StandardFunction.DAMAGE` is used here for DAMAGE.