> English · [Polski](2026-09-02-ao3401a-migration-design.pl.md)

# Q1 migration: IRLZ44N → AO3401A + NPN

**Date:** 2026-09-02  
**Status:** Approved for implementation (staged)

**Related documents:**
- AO3401A connections: [`docs/schematics/connections-ao3401a.en.md`](../../schematics/connections-ao3401a.en.md)
- Previous variant (IRLZ44N): [`docs/schematics/connections-devkit.en.md`](../../schematics/connections-devkit.en.md)
- Main spec: [`2026-08-25-tank-level-sensor-design.en.md`](2026-08-25-tank-level-sensor-design.en.md)
- Firmware: [`esphome/tank-level-sensor.yaml`](../../../esphome/tank-level-sensor.yaml)

## Goal

Replace IRLZ44N (N-MOS low-side on sensor GND) with **AO3401A** (P-MOS high-side on sensor VCC) and **NPN gate driver (2N3904 or BC547)**. Full sensor power cut-off between measurements, extend deep sleep to **8 h**, DevKit mounted **without expansion board**.

Charger and solar panel are **out of scope** for this migration (next step after AO3401A verification).

## Context and motivation

| Observation | Conclusion |
|-------------|------------|
| IRLZ44N low-side setup ran **~3 days** without charging (18650, 4 h sleep) | MT3608 + partial sensor power via Echo dominate consumption |
| IRLZ44N OFF: sensor VCC still ~4.2 V (signal bleed) | Low-side does not fully cut power |
| Expansion board removed | Lower idle draw; DevKit wired directly |
| No USB logs during deep sleep | Stage 1 tests on USB with sleep disabled |

## Target hardware architecture

```
OUT+ (5 V) ───────────── SOURCE (S) AO3401A
DRAIN (D) AO3401A ────── sensor VCC (+ C2 to GND)
sensor GND ───────────── GND (direct)

GATE (G) ──┬── R1 10k ── OUT+ (5 V)
           └── NPN collector (2N3904 / BC547)
NPN emitter ──────────── GND
NPN base ─── R2 10k ─── GPIO4
```

### Control logic

| GPIO4 | NPN | P-MOS | sensor VCC |
|-------|-----|-------|------------|
| **HIGH** | ON | ON | **~4.8–5 V** |
| **LOW** | OFF | OFF | **~0 V** |

**Firmware:** `sensor_power` **without** `inverted` — HIGH = sensor ON (same as IRLZ44N).

### Why NPN instead of GPIO → Gate

- Pull-up R1 holds Gate at ~5 V → reliable OFF (Vgs ≈ 0 V).
- GPIO HIGH pulls Gate low via NPN → reliable ON.
- No `inverted` in YAML — lower migration risk.
- Safer state after ESP reset (pull-up defaults to sensor off).

### AO3401A on SOT-23 → DIP adapter

Component marking facing you, pins down (standard AO3401A pinout):

| SOT-23 pin | Function | Connection |
|------------|----------|------------|
| 1 | Gate | R1 + NPN collector |
| 2 | Source | OUT+ (5 V) |
| 3 | Drain | sensor VCC |

**Verify G / S / D labels on the adapter** — DIP pin order may differ from the SOT-23 package.

### Changes vs IRLZ44N

| Item | Action |
|------|--------|
| IRLZ44N | Disconnect (not used) |
| R3 pulldown Gate→GND | Remove or repurpose as **R1 pull-up Gate→5 V** |
| Sensor GND via DRAIN | Rewire **directly to GND** |
| Sensor VCC from OUT+ | Rewire through **AO3401A DRAIN** |
| 38P expansion board | Do not use |

### Rejected variants (unchanged)

- **IRLZ44N on MT3608 IN−** — IN− = OUT−; module overheats.
- **IRLZ44N high-side on VCC** (OUT+ → DRAIN) — at Gate 3.3 V, VCC ≈ 0.94 V.
- **GPIO directly on AO3401A Gate** — works but weaker OFF and requires `inverted: true`.

## Staged test plan

### Stage 0 — no cell (or cell removed)

| Step | Measurement | OK |
|------|-------------|-----|
| 0.1 | BAT+ ↔ GND | no short |
| 0.2 | SOURCE ↔ OUT+ | ~0 Ω |
| 0.3 | DRAIN ↔ sensor VCC pin | ~0 Ω |
| 0.4 | sensor GND ↔ GND | ~0 Ω |
| 0.5 | NPN emitter ↔ GND; Gate ↔ NPN collector | OK |
| 0.6 | OUT+ **not** wired directly to DRAIN without SOURCE | — |

### Stage 1 — USB, deep sleep OFF

**Temporary firmware:**
- `enable_deep_sleep: false`
- `sleep_duration: 8h` (saved, inactive until stage 2)

| Step | Action | OK |
|------|--------|-----|
| 1.1 | ESP on USB; MT3608 powered | OUT+ ≈ 5 V |
| 1.2 | GPIO4 LOW | sensor VCC ≈ **0 V** |
| 1.3 | GPIO4 HIGH | sensor VCC ≈ **4.8–5 V** |
| 1.4 | Flash + `esphome logs esphome/tank-level-sensor.yaml` | `measure_cycle`, valid reading |
| 1.5 | 5–10 measurements | stable values in logs / HA |

**Pass criteria:** VCC toggles 0 V ↔ 5 V; ultrasonic measurement works.

### Stage 2 — battery + 8 h deep sleep

| Step | Action | OK |
|------|--------|-----|
| 2.1 | Cell inserted, USB disconnected | — |
| 2.2 | `enable_deep_sleep: true` | — |
| 2.3 | One full ~8 h cycle | new reading in HA |
| 2.4 | Battery Voltage vs multimeter | within ADC error |

## Firmware changes

| Parameter | Before | Target |
|-----------|--------|--------|
| `sleep_duration` | `4h` | **`8h`** |
| `enable_deep_sleep` | `true` | stage 1: `false`, stage 2: `true` |
| `sensor_power` inverted | none | **none** |
| `pin_sensor_power` | GPIO4 | GPIO4 (unchanged) |
| Trig / Echo / battery | — | unchanged |

## Documentation to update (implementation)

| File | Action |
|------|--------|
| `docs/schematics/connections-ao3401a.pl.md` (+ EN) | **New** — created |
| `docs/schematics/connections-devkit.pl.md` | Mark as historical IRLZ44N variant |
| `docs/superpowers/specs/2026-08-25-tank-level-sensor-design.pl.md` | Active Q1, 8 h sleep, battery results |
| `docs/superpowers/plans/2026-08-25-tank-level-sensor.pl.md` | AO3401A migration tasks |
| `docs/README.md` | Link to connections-ao3401a |
| `esphome/README.pl.md` | 8 h sleep, AO3401A |

## Limitations and field results

| Configuration | Runtime without charging | Notes |
|---------------|--------------------------|-------|
| DevKit + expansion board + IRLZ44N + **4 h** sleep | **~3 days** | Confirmed in field (18650) |
| DevKit without expansion board + AO3401A + NPN + **8 h** sleep | **TBD** | Estimate: +30–50% vs previous |
| MT3608 always ON | — | ~2–5 mA idle; main autonomy limit without cutting booster |
| Multi-week autonomy | — | Requires solar panel + charger or P-MOS on MT3608 IN+ |

### Power estimate (indicative)

| Configuration | Avg draw (est.) | 2500 mAh |
|---------------|-----------------|----------|
| IRLZ44N low-side + 4 h sleep | ~25–35 mA (measured ~3 days) | ~3 days |
| AO3401A + 8 h sleep (no expansion board) | ~20–28 mA (estimate) | ~4–5 days |
| + solar + charger (planned) | recharge | goal continuous operation |

## GPIO map (unchanged)

| GPIO | Function |
|------|----------|
| GPIO4 | `sensor_power` → NPN base |
| GPIO25 | TRIG |
| GPIO26 | ECHO (10k/20k divider) |
| GPIO33 | Wake (disabled in YAML) |
| GPIO34 | Battery ADC |

## Next step after this migration

1. Monitor **Battery Voltage** in HA for several days (new variant).
2. Solar panel + charging module — separate specification.
3. Optional: P-MOS on MT3608 IN+ for further power savings.
