"""Published constants used by the injury-metric calculations."""

# BrIC critical angular velocities [rad/s].
# CSDM-derived calibration from Takhounts et al. (2013).
BRIC_CRITICAL_CSDM = (66.2, 59.1, 44.2)

# Average of the CSDM- and MPS-derived critical angular velocities from
# Takhounts et al. (2013).
BRIC_CRITICAL_AVERAGED = (66.25, 56.45, 42.87)

# UBrIC MPS-calibrated peak-to-peak angular-velocity constants.
# Gabler, Crandall & Panzer (2018), doi:10.1007/s10439-018-2015-9.
UBRIC_OMEGA_CRITICAL_MPS_P2P_RAD_S = (211.0, 171.0, 115.0)
UBRIC_ALPHA_CRITICAL_MPS_RAD_S2 = (20_000.0, 10_300.0, 7_760.0)
UBRIC_R = 2.0

# HARM weights.
HARM_HIC_WEIGHT = 0.0148
HARM_DAMAGE_WEIGHT = 15.6
