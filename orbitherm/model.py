"""High-level thermal digital twin: assemble a payload + radiator + orbit and
get a sizing verdict, mass/cost, and a transient temperature profile."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from . import physics as P
from .constants import (
    DEFAULT_EMISSIVITY, DEFAULT_SOLAR_ABSORPTANCE, DEFAULT_AREAL_DENSITY,
    ALUMINUM_CP, LAUNCH_COST_TODAY, LAUNCH_COST_TARGET,
    GPU_JUNCTION_LIMIT_C, RADIATOR_TO_JUNCTION_DELTA_C,
)


@dataclass
class Radiator:
    area_m2: float
    emissivity: float = DEFAULT_EMISSIVITY
    solar_absorptance: float = DEFAULT_SOLAR_ABSORPTANCE
    areal_density: float = DEFAULT_AREAL_DENSITY   # kg/m^2
    orientation: str = "deep_space"

    @property
    def mass_kg(self) -> float:
        return self.area_m2 * self.areal_density

    def launch_cost_usd(self, cost_per_kg: float = LAUNCH_COST_TODAY) -> float:
        return self.mass_kg * cost_per_kg


@dataclass
class Orbit:
    altitude_km: float = 550.0

    @property
    def period_s(self) -> float:
        return P.orbit_period(self.altitude_km)

    @property
    def eclipse_fraction(self) -> float:
        return P.eclipse_fraction(self.altitude_km)


@dataclass
class ThermalResult:
    radiator_temp_c: float
    junction_temp_c: float
    flux_w_m2: float
    required_area_50c_m2: float
    radiator_mass_kg: float
    launch_cost_today_usd: float
    launch_cost_target_usd: float
    verdict: str          # "viable" | "marginal" | "infeasible"
    message: str


@dataclass
class ThermalTwin:
    """A compute payload (watts) attached to a Radiator, in an Orbit."""
    power_w: float
    radiator: Radiator
    orbit: Orbit = field(default_factory=Orbit)

    def _avg_env_flux(self) -> float:
        ecl = self.orbit.eclipse_fraction
        sun = P.environmental_flux(
            self.radiator.orientation, self.radiator.emissivity,
            self.radiator.solar_absorptance, sunlit=True)
        shade = P.environmental_flux(
            self.radiator.orientation, self.radiator.emissivity,
            self.radiator.solar_absorptance, sunlit=False)
        return sun * (1 - ecl) + shade * ecl

    def evaluate(self) -> ThermalResult:
        env = self._avg_env_flux()
        t_k = P.steady_state_temp(
            self.power_w, self.radiator.area_m2, self.radiator.emissivity, env)
        t_c = P.k_to_c(t_k)
        junction = t_c + RADIATOR_TO_JUNCTION_DELTA_C
        flux = P.radiative_flux(t_k, self.radiator.emissivity)
        req = P.required_area(self.power_w, 50.0, self.radiator.emissivity, env)
        mass = self.radiator.mass_kg
        if junction < GPU_JUNCTION_LIMIT_C:
            verdict = "viable"
            msg = (f"Radiator settles at {t_c:.0f} C (~{junction:.0f} C junction); "
                   f"the {self.radiator.area_m2:.0f} m2 panel sheds all "
                   f"{self.power_w/1000:.0f} kW. Mass to orbit: {mass:.0f} kg.")
        elif junction < 110:
            verdict = "marginal"
            msg = (f"Radiator runs hot at {t_c:.0f} C (~{junction:.0f} C junction) - "
                   f"hardware will throttle. Need ~{req:.0f} m2, not "
                   f"{self.radiator.area_m2:.0f} m2.")
        else:
            verdict = "infeasible"
            msg = (f"Cannot shed the heat: radiator would sit at {t_c:.0f} C. "
                   f"This power needs ~{req:.0f} m2 of radiator. "
                   f"Cooling, not power, is the wall.")
        return ThermalResult(
            radiator_temp_c=t_c,
            junction_temp_c=junction,
            flux_w_m2=flux,
            required_area_50c_m2=req,
            radiator_mass_kg=mass,
            launch_cost_today_usd=self.radiator.launch_cost_usd(LAUNCH_COST_TODAY),
            launch_cost_target_usd=self.radiator.launch_cost_usd(LAUNCH_COST_TARGET),
            verdict=verdict,
            message=msg,
        )

    def transient(self, steps: int = 240) -> List[dict]:
        """Temperature over one orbit including eclipse, using radiator thermal mass.

        Returns a list of ``{"t_s", "temp_c", "sunlit"}`` samples. Integrates
        dT/dt = (Q_in - Q_out) / (m * cp) with a simple forward-Euler step.
        """
        rad = self.radiator
        period = self.orbit.period_s
        ecl = self.orbit.eclipse_fraction
        cap = max(rad.mass_kg, 1.0) * ALUMINUM_CP        # J/K
        dt = period / steps
        ecl_start, ecl_end = 0.28, 0.28 + ecl
        # seed at the orbit-average steady temperature
        t_k = P.steady_state_temp(self.power_w, rad.area_m2, rad.emissivity,
                                  self._avg_env_flux())
        out = []
        for k in range(steps + 1):
            frac = k / steps
            sunlit = not (ecl_start <= frac < ecl_end)
            env = P.environmental_flux(rad.orientation, rad.emissivity,
                                       rad.solar_absorptance, sunlit=sunlit)
            q_in = self.power_w + env * rad.area_m2
            q_out = P.radiative_flux(t_k, rad.emissivity) * rad.area_m2
            t_k += (q_in - q_out) / cap * dt
            out.append({"t_s": frac * period, "temp_c": P.k_to_c(t_k),
                        "sunlit": sunlit})
        return out


def size_radiator(power_w: float, target_temp_c: float = 50.0,
                  orientation: str = "deep_space",
                  emissivity: float = DEFAULT_EMISSIVITY,
                  areal_density: float = DEFAULT_AREAL_DENSITY,
                  altitude_km: float = 550.0) -> dict:
    """Convenience: minimum radiator area/mass/cost to hold ``target_temp_c``."""
    orbit = Orbit(altitude_km)
    ecl = orbit.eclipse_fraction
    sun = P.environmental_flux(orientation, emissivity, sunlit=True)
    shade = P.environmental_flux(orientation, emissivity, sunlit=False)
    env = sun * (1 - ecl) + shade * ecl
    area = P.required_area(power_w, target_temp_c, emissivity, env)
    mass = area * areal_density
    return {
        "area_m2": area,
        "mass_kg": mass,
        "launch_cost_today_usd": mass * LAUNCH_COST_TODAY,
        "launch_cost_target_usd": mass * LAUNCH_COST_TARGET,
    }
