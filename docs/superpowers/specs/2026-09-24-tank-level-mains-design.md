# Tank Level Mains — design

Date: 2026-09-24 · Revised: 2026-09-25 (always-on sensor)  
Repo: `~/Projects/SiteProjects/ESP32/tank-level`

## Goal

Tank level like battery `tank-level-devkit`, powered from mains (HLK 5 V). ESP and JSN always on; no deep sleep; no sensor power switch.

## Decisions

- Two proto boards: **AC** (mains → fuse → MOV → HLK → 5 V) and **NODE** (SELV only)
- Link boards with screw-terminal cable `+5V` / `GND`
- Sensor VCC tied to +5 V; **C2 100 nF** at sensor VCC; keep Echo divider **10k/20k**
- Drop AO3401A, 2N3904, R1, R2, GPIO4 sensor power
- Shared KiCad symbols: `docs/kicad/symbols/tank-level.kicad_sym` (symlink into each project)
- USB program only with HLK disconnected; never parallel USB 5 V and HLK 5 V
- Schematic wiring: user in KiCad; agent must not edit `.kicad_sch` until user says so

## Parts

| Zone | Ref | Part |
|------|-----|------|
| AC | J1 | Screw terminal L/N |
| AC | F1 | Fuse ~1 A |
| AC | RV1 | MOV L–N |
| AC | U1 | HLK-2M05 (5 V / 0.6 A / 3 W) |
| AC | J2 | Screw terminal +5V / GND OUT |
| NODE | J3 | Screw terminal +5V / GND IN |
| NODE | U2 | ESP32 DevKit V1 |
| NODE | J4 | JSN-SR04T |
| NODE | R3 | 10k Echo divider |
| NODE | R4 | 20k Echo divider |
| NODE | C2 | 100 nF on sensor VCC |

## Behaviour

- ESP always powered from HLK +5 V; JSN always powered
- Trig GPIO25, Echo (via divider) GPIO26
- Hourly measure + “Measure Now”; no `sensor_power` switch

## Scope / out of scope

- In: design, shared symbols, ESPHome mains YAML, docs/BOM
- Out until asked: `.kicad_sch` edits, PCB, enclosure

## Acceptance criteria

- Spec and README parts match the table above (no MOSFET switch)
- `esphome/tank-level-mains.yaml` has no GPIO4 / `sensor_power`
- Shared lib `tank-level:JSN_SR04T` loads in both KiCad projects
- Schematic file unchanged until user requests wiring/placement
