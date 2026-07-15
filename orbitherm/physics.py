"""Core radiative-thermal physics for orbital compute payloads.

The governing idea: in vacuum a body sheds heat only by radiation, following
the Stefan-Boltzmann law  q = eps * sigma * T^4  (W/m^2). A compute payload must
radiate away every watt it consumes, plus whatever it absorbs from the Sun,
Earth albedo, and Earth infrared. Radiative capacity grows only as T^4, so the
radiator area (and therefore mass and launch cost) needed for a given power is
the binding constraint on dense orbital compute -- not the power itself.
"""
from __future__ import annotations

import math

from .constants import (
    STEFAN_BOLTZMANN, MU_EARTH, R_EARTH, ABS_ZERO_C,
    SOLAR_CONSTANT, EARTH_ALBEDO, EARTH_IR,
    DEFAULT_EMISSIVITY, DEFAULT_SOLAR_ABSORPTANCE,
)

ORIENTATIONS = ("deep_space", "nadir", "sun_facing")


def c_to_k(celsius: float) -> float:
    return celsius - ABS_ZERO_C


def k_to_c(kelvin: float) -> float:
    return kelvin + ABS_ZERO_C


def radiative_flux(temp_k: float, emissivity: float = DEFAULT_EMISSIVITY) -> float:
    """Heat radiated per unit area (W/m^2) by a surface at ``temp_k``."""
    return emissivity * STEFAN_BOLTZMANN * temp_k ** 4


def environmental_flux(
    orientation: str = "deep_space",
    emissivity: float = DEFAULT_EMISSIVITY,
    solar_absorptance: float = DEFAULT_SOLAR_ABSORPTANCE,
    sunlit: bool = True,
) -> float:
    """Absorbed environmental heat load on the radiator (W/m^2).

    ``orientation`` selects how much of the Sun / albedo / Earth-IR the surface
    sees. ``sunlit=False`` models the eclipse portion of an orbit (no direct sun
    or albedo). This is the parasitic load that eats into rejection capacity.
    """
    if orientation not in ORIENTATIONS:
        raise ValueError(f"orientation must be one of {ORIENTATIONS}")
    solar = 0.0
    albedo = 0.0
    earth_ir = 0.0
    if orientation == "deep_space":
        earth_ir = emissivity * EARTH_IR * 0.05           # small residual view of Earth
    elif orientation == "nadir":
        earth_ir = emissivity * EARTH_IR * 0.86
        albedo = solar_absorptance * EARTH_ALBEDO * SOLAR_CONSTANT * 0.30
    elif orientation == "sun_facing":
        solar = solar_absorptance * SOLAR_CONSTANT
        albedo = solar_absorptance * EARTH_ALBEDO * SOLAR_CONSTANT * 0.30
        earth_ir = emissivity * EARTH_IR * 0.30
    if not sunlit:
        solar = 0.0
        albedo = 0.0
    return solar + albedo + earth_ir


def steady_state_temp(
    power_w: float,
    area_m2: float,
    emissivity: float = DEFAULT_EMISSIVITY,
    env_flux: float = 0.0,
) -> float:
    """Equilibrium radiator temperature (K).

    Solves  eps*sigma*T^4 = power/area + env_flux.
    """
    if area_m2 <= 0:
        raise ValueError("area_m2 must be positive")
    q = power_w / area_m2 + env_flux
    return (q / (emissivity * STEFAN_BOLTZMANN)) ** 0.25


def required_area(
    power_w: float,
    target_temp_c: float,
    emissivity: float = DEFAULT_EMISSIVITY,
    env_flux: float = 0.0,
) -> float:
    """Radiator area (m^2) needed to hold ``target_temp_c`` while rejecting ``power_w``.

    Returns ``inf`` if the environment alone exceeds what the surface can radiate
    at the target temperature (i.e. no area can hold that temperature).
    """
    t_k = c_to_k(target_temp_c)
    denom = emissivity * STEFAN_BOLTZMANN * t_k ** 4 - env_flux
    if denom <= 0:
        return math.inf
    return power_w / denom


def orbit_period(altitude_km: float) -> float:
    """Circular orbital period (s) at ``altitude_km`` above Earth's surface."""
    a = R_EARTH + altitude_km * 1000.0
    return 2 * math.pi * math.sqrt(a ** 3 / MU_EARTH)


def eclipse_fraction(altitude_km: float) -> float:
    """Fraction of a circular orbit spent in Earth's shadow (beta=0 worst case)."""
    a = R_EARTH + altitude_km * 1000.0
    rho = math.asin(R_EARTH / a)
    return (2 * rho) / (2 * math.pi)
