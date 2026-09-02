> [English](2026-09-02-ao3401a-migration-design.en.md) · **Polski**

# Migracja Q1: IRLZ44N → AO3401A + NPN

**Data:** 2026-09-02  
**Status:** Zatwierdzony do implementacji (etapowy)

**Powiązane dokumenty:**
- Połączenia AO3401A: [`docs/schematics/connections-ao3401a.pl.md`](../../schematics/connections-ao3401a.pl.md)
- Poprzedni wariant (IRLZ44N): [`docs/schematics/connections-devkit.pl.md`](../../schematics/connections-devkit.pl.md)
- Spec główna: [`2026-08-25-tank-level-sensor-design.pl.md`](2026-08-25-tank-level-sensor-design.pl.md)
- Firmware: [`esphome/tank-level-sensor.yaml`](../../../esphome/tank-level-sensor.yaml)

## Cel

Zastąpić IRLZ44N (N-MOS low-side na GND czujnika) tranzystorem **AO3401A** (P-MOS high-side na VCC czujnika) ze sterowaniem bramki przez **NPN (2N3904 lub BC547)**. Pełne odcięcie zasilania czujnika między pomiarami, wydłużenie deep sleep do **8 h**, montaż DevKit **bez expansion board**.

Ładowarka i panel solarny — **poza zakresem** tej migracji (kolejny krok po weryfikacji AO3401A).

## Kontekst i motywacja

| Obserwacja | Wniosek |
|------------|---------|
| Układ z IRLZ44N low-side działał **~3 dni** bez ładowania (18650, sleep 4 h) | MT3608 + częściowe zasilanie czujnika przez Echo dominują w poborze |
| IRLZ44N OFF: VCC czujnika nadal ~4,2 V (obejście sygnałów) | Low-side nie daje pełnego odcięcia |
| Expansion board odłączony | Mniejszy pobór jałowy; DevKit podłączony bezpośrednio |
| Brak logów USB w deep sleep | Etap 1 testów na USB z wyłączonym snem |

## Architektura hardware (docelowa)

```
OUT+ (5 V) ───────────── SOURCE (S) AO3401A
DRAIN (D) AO3401A ────── VCC czujnika (+ C2 do GND)
GND czujnika ─────────── GND (bezpośrednio)

GATE (G) ──┬── R1 10k ── OUT+ (5 V)
           └── kolektor NPN (2N3904 / BC547)
Emiter NPN ───────────── GND
Baza NPN ─── R2 10k ─── GPIO4
```

### Logika sterowania

| GPIO4 | NPN | P-MOS | VCC czujnika |
|-------|-----|-------|--------------|
| **HIGH** | ON | ON | **~4,8–5 V** |
| **LOW** | OFF | OFF | **~0 V** |

**Firmware:** `sensor_power` **bez** `inverted` — HIGH = czujnik ON (jak przy IRLZ44N).

### Dlaczego NPN zamiast GPIO → Gate

- Pull-up R1 trzyma Gate na ~5 V → pewne OFF (Vgs ≈ 0 V).
- GPIO HIGH ściąga Gate przez NPN → pewne ON.
- Brak `inverted` w YAML — mniejsze ryzyko pomyłki przy migracji.
- Bezpieczniejszy stan po resecie ESP (pull-up domyślnie wyłącza czujnik).

### AO3401A na adapterze SOT-23 → DIP

Patrząc na element od strony napisu, piny w dół (standardowy pinout AO3401A):

| Pin SOT-23 | Funkcja | Połączenie |
|------------|---------|------------|
| 1 | Gate | R1 + kolektor NPN |
| 2 | Source | OUT+ (5 V) |
| 3 | Drain | VCC czujnika |

**Sprawdź oznaczenia G / S / D na adapterze** — kolejność pinów DIP może różnić się od obudowy SOT-23.

### Elementy do usunięcia / zmiany względem IRLZ44N

| Element | Akcja |
|---------|--------|
| IRLZ44N | Odłączyć (nie używany) |
| R3 pulldown Gate→GND | Usunąć lub przerobić na **R1 pull-up Gate→5 V** |
| GND czujnika przez DRAIN | Przepiąć **prosto na GND** |
| VCC czujnika stałe z OUT+ | Przepiąć przez **DRAIN** AO3401A |
| Expansion board 38P | Nie używać |

### Odrzucone warianty (bez zmian)

- **IRLZ44N na IN− MT3608** — IN− = OUT−; moduł się grzeje.
- **IRLZ44N high-side na VCC** (OUT+ → DRAIN) — przy Gate 3,3 V VCC ≈ 0,94 V.
- **GPIO bezpośrednio na Gate AO3401A** — działa, ale gorsze OFF i wymaga `inverted: true`.

## Plan testów (etapowy)

### Etap 0 — bez ogniwa (lub ogniwo wyjęte)

| Krok | Pomiar | OK |
|------|--------|-----|
| 0.1 | BAT+ ↔ GND | brak zwarcia |
| 0.2 | SOURCE ↔ OUT+ | ~0 Ω |
| 0.3 | DRAIN ↔ pin VCC czujnika | ~0 Ω |
| 0.4 | GND czujnika ↔ GND | ~0 Ω |
| 0.5 | Emiter NPN ↔ GND; Gate ↔ kolektor NPN | OK |
| 0.6 | OUT+ **nie** podłączony bezpośrednio na DRAIN bez SOURCE | — |

### Etap 1 — USB, deep sleep OFF

**Firmware tymczasowo:**
- `enable_deep_sleep: false`
- `sleep_duration: 8h` (zapisane, nieaktywne do etapu 2)

| Krok | Akcja | OK |
|------|-------|-----|
| 1.1 | ESP z USB; MT3608 zasilony (BAT+ lub tymczasowo testowo) | OUT+ ≈ 5 V |
| 1.2 | GPIO4 LOW | VCC czujnika ≈ **0 V** |
| 1.3 | GPIO4 HIGH | VCC czujnika ≈ **4,8–5 V** |
| 1.4 | Flash + `esphome logs esphome/tank-level-sensor.yaml` | `measure_cycle`, odczyt OK |
| 1.5 | 5–10 pomiarów | stabilne wartości w logach / HA |

**Kryterium przejścia:** skok VCC 0 V ↔ 5 V; pomiar ultrasoniczny działa.

### Etap 2 — bateria + deep sleep 8 h

| Krok | Akcja | OK |
|------|-------|-----|
| 2.1 | Ogniwo włożone, USB odłączony | — |
| 2.2 | `enable_deep_sleep: true` | — |
| 2.3 | Jeden pełny cykl ~8 h | nowy pomiar w HA |
| 2.4 | Battery Voltage vs miernik | zgodność w granicy błędu ADC |

## Zmiany firmware

| Parametr | Poprzednio | Docelowo |
|----------|------------|----------|
| `sleep_duration` | `4h` | **`8h`** |
| `enable_deep_sleep` | `true` | etap 1: `false`, etap 2: `true` |
| `sensor_power` inverted | brak | **brak** |
| `pin_sensor_power` | GPIO4 | GPIO4 (bez zmian) |
| Trig / Echo / bateria | — | bez zmian |

## Dokumentacja do aktualizacji (implementacja)

| Plik | Akcja |
|------|--------|
| `docs/schematics/connections-ao3401a.pl.md` (+ EN) | **Nowy** — utworzony |
| `docs/schematics/connections-devkit.pl.md` | Oznaczyć jako wariant historyczny IRLZ44N |
| `docs/superpowers/specs/2026-08-25-tank-level-sensor-design.pl.md` | Aktywny Q1, sleep 8h, wyniki baterii |
| `docs/superpowers/plans/2026-08-25-tank-level-sensor.pl.md` | Taski migracji AO3401A |
| `docs/README.md` | Link do connections-ao3401a |
| `esphome/README.pl.md` | sleep 8h, AO3401A |

## Ograniczenia i wyniki terenowe

| Konfiguracja | Czas pracy bez ładowania | Uwagi |
|--------------|--------------------------|-------|
| DevKit + expansion board + IRLZ44N + sleep **4 h** | **~3 dni** | Potwierdzone w terenie (18650) |
| DevKit bez expansion board + AO3401A + NPN + sleep **8 h** | **do weryfikacji** | Szacunek: +30–50% vs poprzedni wariant |
| MT3608 cały czas ON | — | ~2–5 mA jałowego; główny limit autonomii bez odcięcia boostera |
| Pełna autonomia tygodniowa | — | Wymaga panelu + ładowarki lub P-MOS na IN+ MT3608 |

### Szacunek zużycia (orientacyjny)

| Konfiguracja | Średni pobór (szac.) | 2500 mAh |
|--------------|----------------------|----------|
| IRLZ44N low-side + sleep 4h | ~25–35 mA (zmierzone ~3 dni) | ~3 dni |
| AO3401A + sleep 8h (bez expansion board) | ~20–28 mA (szacunek) | ~4–5 dni |
| + panel + ładowanie (plan) | doładowanie | cel ciągła praca |

## Mapa GPIO (bez zmian)

| GPIO | Funkcja |
|------|---------|
| GPIO4 | `sensor_power` → baza NPN |
| GPIO25 | TRIG |
| GPIO26 | ECHO (dzielnik 10k/20k) |
| GPIO33 | Wake (wyłączony w YAML) |
| GPIO34 | ADC baterii |

## Następny krok po tej migracji

1. Obserwacja **Battery Voltage** w HA przez kilka dni (nowy wariant).
2. Panel solarny + moduł ładowania (TP4056 lub dedykowany moduł) — osobna specyfikacja.
3. Opcjonalnie: P-MOS na IN+ MT3608 dla dalszej oszczędności energii.
