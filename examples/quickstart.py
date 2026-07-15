"""Run: python examples/quickstart.py"""
import orbitherm as ot

print("=== Case 1: 100 kW edge payload, deep-space radiator ===")
twin = ot.ThermalTwin(
    power_w=100_000,
    radiator=ot.Radiator(area_m2=200, orientation="deep_space"),
    orbit=ot.Orbit(altitude_km=550),
)
r = twin.evaluate()
print(f"verdict={r.verdict}  radiator={r.radiator_temp_c:.0f} C  "
      f"junction={r.junction_temp_c:.0f} C  mass={r.radiator_mass_kg:.0f} kg")
print(r.message)

print("\n=== Case 2: same payload, but radiator points at the Sun ===")
twin.radiator.orientation = "sun_facing"
print(twin.evaluate().message)

print("\n=== Case 3: size a 1 MW data center radiator to hold 50 C ===")
s = ot.size_radiator(1_000_000, target_temp_c=50)
print(f"area={s['area_m2']:.0f} m2  mass={s['mass_kg']:.0f} kg  "
      f"launch ${s['launch_cost_today_usd']/1e6:.1f}M today / "
      f"${s['launch_cost_target_usd']/1e6:.1f}M at target cost")

print("\n=== Transient over one orbit (Case 1) ===")
twin.radiator.orientation = "deep_space"
prof = twin.transient(steps=6)
for p in prof:
    print(f"t={p['t_s']/60:5.1f} min  T={p['temp_c']:5.1f} C  "
          f"{'sun' if p['sunlit'] else 'eclipse'}")
