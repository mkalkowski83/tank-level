# Tank Level Mains — schemat

Otwórz w KiCad:

`docs/kicad/tank-level-mains/tank-level-230V.kicad_pro`

(otwieraj **`.kicad_pro`**, nie sam `.kicad_sch`).

Własne symbole: wspólna lib `docs/kicad/symbols/tank-level.kicad_sym`
(symlink w `symbols/`; chooser: **`tank-level`**, np. `JSN_SR04T`).
Szczegóły: [`../symbols/README.pl.md`](../symbols/README.pl.md).

Dwie płytki: **AC** (sieć + HLK) oraz **NODE** (SELV 5 V). Czujnik **zawsze zasilany** — bez MOSFET.

Spec: [`../../superpowers/specs/2026-09-24-tank-level-mains-design.md`](../../superpowers/specs/2026-09-24-tank-level-mains-design.md).

## Referencje (docelowy BOM)

| Strefa | Ref | Element / wartość |
|---|---|---|
| AC | J1 | Zacisk śrubowy 2P — L / N |
| AC | F1 | Bezpiecznik ok. 1 A |
| AC | RV1 | Warystor MOV między L i N |
| AC | U1 | HLK-2M05, 5 V / 0,6 A / 3 W |
| AC | J2 | Zacisk śrubowy 2P — +5V / GND OUT |
| NODE | J3 | Zacisk śrubowy 2P — +5V / GND IN |
| NODE | U2 | ESP32 DevKit V1 |
| NODE | J4 | JSN-SR04T (`tank-level:JSN_SR04T`) |
| NODE | R3 | 10k — dzielnik Echo |
| NODE | R4 | 20k — dzielnik Echo |
| NODE | C2 | 100 nF — VCC czujnika |

**Nie używamy:** AO3401A, 2N3904, R1/R2 (sterowanie zasilaniem czujnika).

## Bezpieczeństwo

- Odstępy sieciowe tylko na płytce AC; na NODE tylko `+5V` / `GND`.
- **Nie łącz równolegle 5 V z USB i 5 V z HLK.**
- Programuj USB dopiero po odłączeniu HLK od NODE.
