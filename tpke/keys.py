"""
Keys

Hardcoding is bad. Use these constants instead.
"""

IMPLICIT_NAMES = ("implicit euler", "implicit", "backward euler", "backward")
EXPLICIT_NAMES = ("explicit euler", "explicit", "forward euler", "forward")
METH = "method"

# Reactivity functions
REAC = "reactivity"
REAC_TYPE = "type"
RHO = "rho"
STEP = "step"
RAMP = "ramp"
RAMP_SLOPE = "slope"
SINE = "sine"
SINE_OMEGA = "frequency"

# Time options
TIME = "time"
TIME_TOTAL = "total"
TIME_DELTA = "dt"

# Plot options
PLOT = "plots"
PLOT_SHOW = "show"
PLOT_SPY = "spy"
PLOT_PR = "power_reactivity"

# PKRE data inputs
DATA = "data"
DATA_B = "delay_fractions"
DATA_L = "decay_constants"
DATA_BIG_L = "Lambda"

# Plot names
EXT = ".pdf"  # consider making this user-configurable
FNAME_SPY = "spy" + EXT
FNAME_PR = "power_reactivity" + EXT

# Text names
FNAME_CFG = "config.yml"
FNAME_RHO = "reactivities.txt"
FNAME_P = "powers.txt"
FNAME_C = "concentrations.txt"
FNAME_MATRIX_A = "A.txt"
FNAME_MATRIX_B = "B.txt"
