# Tank Level Mains — always-on simplification plan

**Goal:** Align docs + firmware with always-on sensor (no MOSFET). Leave `.kicad_sch` alone until user asks.

**Approach:** Update spec/BOM/README; strip `sensor_power` from `tank-level-mains.yaml`. Shared symbols already in place.

## Files

| Path | Action |
|------|--------|
| `docs/superpowers/specs/2026-09-24-tank-level-mains-design.md` | Update (done with this change) |
| `esphome/tank-level-mains.yaml` | Remove GPIO4 / switch / stabilize |
| `esphome/README-mains.pl.md` | Always-on behaviour |
| `docs/kicad/tank-level-mains/README.pl.md` | BOM without Q1/Q2/R1/R2 |
| `docs/kicad/**/*.kicad_sch` | **Do not touch** |

## Tasks

1. Spec + README BOM match always-on parts table
2. Firmware: measure_cycle = update distance + fill only
3. Done when AC below hold; schematic untouched

## Done when

- [x] Spec / mains README list only: AC parts + ESP + JSN + R3/R4 + C2
- [x] YAML has no `sensor_power` / `pin_sensor_power` / `sensor_stabilize`
- [x] `git diff` shows no `.kicad_sch` changes
