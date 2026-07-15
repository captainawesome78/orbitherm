# orbitherm

**Thermal digital twin for orbital compute — size the radiator, find the cooling wall.**

In vacuum, heat leaves only by radiation (`q = εσT⁴`). A space data center must
radiate away every watt it burns, plus what it absorbs from the Sun, Earth
albedo, and Earth IR. Radiative capacity grows only as T⁴, so **radiator area —
not power — is the binding constraint** on dense orbital compute. `orbitherm`
sizes that radiator and gives a go/no-go verdict from first-order physics, with
no heavy dependencies.

## Install

```bash
pip install orbitherm
```

## Quick start

```python
import orbitherm as ot

twin = ot.ThermalTwin(
    power_w=100_000,                                  # 100 kW compute payload
    radiator=ot.Radiator(area_m2=200, orientation="deep_space"),
    orbit=ot.Orbit(altitude_km=550),
)

r = twin.evaluate()
print(r.verdict, f"{r.radiator_temp_c:.0f} C")        # -> viable 48 C
print(r.message)

# How big must a 1 MW data-center radiator be to hold 50 C?
print(ot.size_radiator(1_000_000))
# -> {'area_m2': ~1940, 'mass_kg': ~7760, ...}
```

## What it models

- **Steady-state radiator temperature** — Stefan-Boltzmann rejection balanced
  against compute dissipation plus absorbed solar / albedo / Earth-IR loads.
- **Required radiator area** to hold a target temperature at a given power.
- **Mass and launch cost** (today's ~$1000/kg vs. a ~$200/kg breakeven target).
- **Transient temperature** over one orbit, including the eclipse swing, using
  radiator thermal mass.
- **Orbit geometry** — period and eclipse fraction from altitude.

Radiator orientation matters: `deep_space` (best), `nadir`, or `sun_facing`
(worst case) change the parasitic environmental load.

## API

| Object / function | Purpose |
|---|---|
| `Radiator(area_m2, emissivity, areal_density, orientation)` | Radiator panel |
| `Orbit(altitude_km)` | Circular orbit; `.period_s`, `.eclipse_fraction` |
| `ThermalTwin(power_w, radiator, orbit)` | `.evaluate()` and `.transient()` |
| `size_radiator(power_w, target_temp_c=50, ...)` | Minimum area/mass/cost |
| `orbitherm.physics` | Low-level functions (`steady_state_temp`, `required_area`, …) |

## Scope

First-order feasibility and sizing tool — good for go/no-go decisions,
architecture trade studies, and pitch analysis. It is **not** a substitute for
detailed CAD/finite-element thermal analysis. Assumes an isothermal radiator, a
fixed radiator→junction temperature rise, and worst-case (β=0) eclipse geometry.

## License

Apache-2.0
