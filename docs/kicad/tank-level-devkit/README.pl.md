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
| U3 | TP4056 (moduł ładowania — symbol własny) |
| J2 | Panel solarny USB 5 V (`SOLAR_USB`) |

### Symbole własne (`symbols/tank-level.kicad_sym`)

KiCad nie ma gotowego modułu breadboard — dodane w repo:

| Symbol | Opis | Piny |
|--------|------|------|
| `tank-level:TP4056` | Moduł z ochroną DW01 (6 padów) | IN+, IN−, B+, B−, OUT+, OUT− |
| `tank-level:TP4056_4P` | Goły moduł bez ochrony (4 pady) | IN+, IN−, B+, B− |
| `tank-level:SOLAR_USB` | Panel solarny, gniazdo **USB-A żeńskie** | +5V, GND |

**Dodanie na schemat:** Place → Symbol → biblioteka `tank-level` → `TP4056` (6 pinów) + `SOLAR_USB`.

**Panel + kabel (fizycznie):**

```
J2 Panel [USB-A F]  ←wtyk  Kabel USB-A → USB-C  →  U3 port USB-C
     (symbol J2: +5V/GND = VBUS/GND gniazda panelu)
```

Na schemacie połącz **J2 +5V/GND → U3 IN+/IN−** (logicznie to samo co port USB-C na module — nie lutuj jednocześnie kabla i padów IN+).

**Połączenia lutowane (moduł 6-pin):**

```
U3 B+  ──► BT1 (+)
U3 B−  ──► BT1 (−)
U3 OUT+ ──► szyna BAT+ (MT3608 IN+, C1, R5)
U3 OUT− ──► GND
```

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

## ERC / power flagi

KiCad: **PWR_FLAG** ma typ `Power output` — **nie** łącz go z pinem modułu już oznaczonym jako `power_out` (OUT+ TP4056 / MT3608).

| Źródło zasilania | Co wystarczy dla ERC |
|------------------|----------------------|
| **U3 OUT+** → BAT+ | pin `power_out` na TP4056 — **bez PWR_FLAG** |
| **U2 OUT+** → +5V | pin `power_out` na MT3608 — **bez PWR_FLAG** |
| **GND** | symbol **`GND`** na szynie masy — **bez PWR_FLAG** |
| **J2 +5V** → U3 IN+ | pin `power_out` panelu → `power_in` IN+ |
| **BT1** B+/B− | piny **`passive`** (ogniwo, nie źródło ERC) |

Po edycji schematu uruchom **Inspect → Electrical Rules Checker**.

- Symbol ESP32 to **uproszczenie** (tylko używane piny) — nie footprint DevKit.
- Schemat **nie zawiera PCB** — tylko dokumentacja montażu.

## Kolejne kroki (opcjonalnie)

- [ ] Wariant `tank-level-relay` (moduł przekaźnika 5V, `inverted: true`)
- [ ] Eksport PDF obok `connections-ao3401a.pl.md`
- [ ] Footprinty pod płytkę uniwersalną
