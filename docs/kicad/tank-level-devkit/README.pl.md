# KiCad — Tank Level Sensor (DevKit + AO3401A)

Schemat ideowy prototypu na breadboardzie. Odpowiednik dokumentacji:
[`connections-ao3401a.pl.md`](../../schematics/connections-ao3401a.pl.md).

**Zacznij od kroku 1:** [`STEP1.pl.md`](STEP1.pl.md) — tylko ESP32 + AO3401A + NPN.

## Otwarcie projektu

1. Zainstaluj **KiCad 8** lub **9** (darmowy: [kicad.org](https://www.kicad.org/)).
2. **File → Open Project** → wybierz:
   ```
   docs/kicad/tank-level-devkit/tank-level-devkit.kicad_pro
   ```
3. Otwórz **Schematic Editor** (ikona Eeschema).

KiCad przy pierwszym otwarciu może zapytać o aktualizację bibliotek — zaakceptuj (standardowe symbole `Device`, `power`, `Transistor_FET`).

## Zawartość schematu (rev 0.1)

| Ref | Element |
|-----|---------|
| BT1 | 18650 + holder |
| U1 | MT3608 |
| C1 | 1000 µF (BAT+) |
| U2 | ESP32 DevKit V1 (uproszczony symbol pinów) |
| Q1 | AO3401A (P-MOS high-side) |
| Q2 | 2N3904 (NPN, sterowanie Gate) |
| R1 | 10k — pull-up Gate → +5V |
| R2 | 10k — GPIO4 → baza Q2 |
| R3, R4 | 10k / 20k — dzielnik Echo → GPIO26 |
| R5, R6 | 100k / 100k — dzielnik baterii → GPIO34 |
| C2 | 100nF — VCC czujnika |
| J1 | JSN-SR04T |

### Sieci globalne (etykiety)

| Sieć | Znaczenie |
|------|-----------|
| `BAT+` | Plus ogniwa (3–4,2 V) |
| `+5V` | OUT+ MT3608 |
| `GND` | Masa wspólna |
| `GPIO4` | sensor_power |
| `GPIO25` / `GPIO26` | Trig / Echo |
| `GPIO34` | ADC baterii |
| `SENSOR_VCC` | VCC czujnika (tylko przez Q1 DRAIN) |
| `GATE` | węzeł Gate AO3401A + kolektor NPN |

## Regeneracja schematu

Po edycji układu w `generate_schematic.py`:

```bash
python3 docs/kicad/tank-level-devkit/generate_schematic.py
```

Następnie ponownie otwórz projekt w KiCad.

## Współpraca z agentem (Cursor)

1. Opisz zmianę (np. „dodaj wariant przekaźnika”, „popraw R3/R4”).
2. Agent edytuje pliki w `docs/kicad/tank-level-devkit/`.
3. Ty otwierasz projekt w KiCad i weryfikujesz ERC.
4. Opcjonalnie: **File → Plot** → PDF do `docs/schematics/`.

**Nie ma** bezpośredniego połączenia z GUI KiCad — pracujemy przez pliki w repozytorium.

## ERC / uwagi

- Symbol ESP32 to **uproszczenie** (tylko używane piny) — nie footprint DevKit.
- MT3608 jako moduł 4-pin — bez footprint PCB.
- Po otwarciu uruchom **Inspect → Electrical Rules Checker**.
- Schemat **nie zawiera PCB** — tylko dokumentacja montażu.

## Kolejne kroki (opcjonalnie)

- [ ] Wariant `tank-level-relay` (moduł przekaźnika 5V, `inverted: true`)
- [ ] Eksport PDF obok `connections-ao3401a.pl.md`
- [ ] Footprinty pod płytkę uniwersalną
