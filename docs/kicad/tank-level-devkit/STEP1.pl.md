# KiCad — krok 1: ESP32 + AO3401A

Minimalny schemat — tylko sterowanie zasilaniem czujnika. Reszta (MT3608, JSN, dzielniki) w kolejnych krokach.

## Otwarcie

**File → Open Project** → `tank-level-devkit.kicad_pro`

Jeśli masz już własne zmiany na schemacie, zrób kopię albo otwórz wygenerowany plik od nowa:

```bash
python3 docs/kicad/tank-level-devkit/generate_schematic.py
```

KiCad zapyta o przeładowanie — **tak**, jeśli chcesz wersję „krok 1” z repo.

## Co jest na schemacie (rev 0.2-step1)

| Ref | Element |
|-----|---------|
| **U2** | ESP32 DevKit (GPIO4, 5V, GND) |
| **Q1** | AO3401A |
| **Q2** | 2N3904 |
| **R1** | 10k — Gate → +5V |
| **R2** | 10k — GPIO4 → baza Q2 |

Sieci: `+5V`, `GND`, `GPIO4`, `GATE`, `SENSOR_VCC`

## Ręczne dokończenie w KiCad (jeśli budujesz sam)

Masz już **AO3401A** na schemacie — dopnij tylko:

### 1. ESP32 (symbol lub tekst)

Użyj symbolu `tank-level:ESP32_DEVKIT` albo etykiet:

| Pin ESP | Sieć |
|---------|------|
| 5V/VIN | `+5V` |
| GND | `GND` |
| **GPIO4** | `GPIO4` |

### 2. AO3401A Q1

| Pin AO3401A | Sieć |
|-------------|------|
| **1 GATE** | `GATE` (węzeł: R1 + kolektor Q2) |
| **2 SOURCE** | `+5V` |
| **3 DRAIN** | `SENSOR_VCC` → później VCC czujnika |

### 3. NPN Q2 (2N3904)

| Pin | Sieć |
|-----|------|
| Baza | `GPIO4` przez **R2 10k** |
| Emiter | `GND` |
| Kolektor | `GATE` |

### 4. R1 10k

Między **`+5V`** i **`GATE`**.

### 5. Zasilanie +5V / GND

Na razie możesz użyć symboli zasilania `+5V` i `GND` — w kroku 2 podłączysz je do MT3608 OUT+.

## Logika (test multimetrem)

| GPIO4 | SENSOR_VCC |
|-------|------------|
| LOW (0 V) | **~0 V** |
| HIGH (3,3 V) | **~4,8–5 V** |

Firmware: **Sensor Power** / **Wake and Measure** w HA.

## Krok 2 (później)

- MT3608 + ogniwo → szyna `+5V` / `BAT+`
- JSN-SR04T na `SENSOR_VCC`
- Dzielniki GPIO26 / GPIO34

## Zoom w KiCad

- **Ctrl + scroll** — powiększenie  
- **A** — dopasuj widok do arkusza  
- Jeśli schemat pusty: **View → Show Symbol Fields** / sprawdź czy symbol AO3401A ma przypisaną bibliotekę `Transistor_FET`
