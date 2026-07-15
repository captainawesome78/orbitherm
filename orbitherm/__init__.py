"""orbitherm -- thermal digital twin for orbital compute payloads.

In vacuum, heat leaves only by radiation. A space data center must radiate away
every watt it burns, so radiator area -- not power -- is the binding constraint.
orbitherm sizes that radiator and tells you whether a payload can shed its own
heat, from first-order radiative physics.

Quick start
-----------
    import orbitherm as ot

    twin = ot.ThermalTwin(
        power_w=100_000,                         # 100 kW compute payload
        radiator=ot.Radiator(area_m2=200, orientation="deep_space"),
        orbit=ot.Orbit(altitude_km=550),
    )
    r = twin.evaluate()
    print(r.verdict, r.radiator_temp_c, "C")     # -> viable 48 C
    print(r.message)

    # How big must a 1 MW radiator be to hold 50 C?
    print(ot.size_radiator(1_000_000))
"""

from .model import Radiator, Orbit, ThermalTwin, ThermalResult, size_radiator
from . import physics, constants

__all__ = [
    "Radiator", "Orbit", "ThermalTwin", "ThermalResult", "size_radiator",
    "physics", "constants",
]
__version__ = "0.1.0"
