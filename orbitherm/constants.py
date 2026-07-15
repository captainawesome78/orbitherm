"""Physical constants and default material/environment parameters.

All SI units unless noted. Values are first-order engineering figures suitable
for feasibility sizing, not detailed thermal CAD.
"""

# Fundamental
STEFAN_BOLTZMANN = 5.670374419e-8   # W / m^2 / K^4
MU_EARTH = 3.986004418e14           # gravitational parameter, m^3 / s^2
R_EARTH = 6.371e6                   # mean Earth radius, m
ABS_ZERO_C = -273.15                # 0 K in Celsius

# Space thermal environment (near-Earth)
SOLAR_CONSTANT = 1361.0            # W / m^2 at 1 AU
EARTH_ALBEDO = 0.30               # fraction of solar reflected by Earth
EARTH_IR = 237.0                  # W / m^2 outgoing longwave (orbit average)
DEEP_SPACE_TEMP = 2.7            # K (cosmic background; sink temperature)

# Radiator material defaults
DEFAULT_EMISSIVITY = 0.85          # white paint / optical solar reflector (OSR)
DEFAULT_SOLAR_ABSORPTANCE = 0.20   # OSR-class low-alpha coating
DEFAULT_AREAL_DENSITY = 4.0        # kg / m^2, deployable radiator panel
ALUMINUM_CP = 900.0                # J / kg / K, specific heat (thermal mass)

# Economics
LAUNCH_COST_TODAY = 1000.0         # USD / kg (order-of-magnitude, 2026)
LAUNCH_COST_TARGET = 200.0         # USD / kg (breakeven target for orbital compute)

# Hardware thermal limits
GPU_JUNCTION_LIMIT_C = 85.0            # typical throttle onset
RADIATOR_TO_JUNCTION_DELTA_C = 30.0   # assumed conduction/spreading rise
