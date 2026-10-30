# Garden distribution — design

Date: 2026-10-10 · Revised: 2026-10-15 (minimum: 1 skrzynka)  
Repo: `tank-level` (consumer: `tank-level-mains`)  
Related: [`2026-09-24-tank-level-mains-design.md`](2026-09-24-tank-level-mains-design.md)  
Schemat: [`../../schematics/garden-distribution-r1-r2.pl.md`](../../schematics/garden-distribution-r1-r2.pl.md)  
BOM (Excel): [`../../bom/garden-distribution-r1-r2.xlsx`](../../bom/garden-distribution-r1-r2.xlsx)

## Goal

Zasilenie czujnika szamba 230 V z **jednej** skrzynki ogrodowej (minimum); docelowo rozbudowa o pompy/gniazda / ewentualnie R2.

## Decisions

- **Teraz (minimum):** 1 skrzynka przy istniejącym dopływie (ogród przy domu). Kabel prosto do czujnika (~13 m trasy). Bez R2.
- Dopływ: istniejący **3×2,5** + PE z uziemieniem budynku.
- W skrzynce: **Q0 rozłącznik 2P** + **RCBO 30 mA** na czujnik (bez smart; always-on).
- Kabel do czujnika: **2×1,5** (L/N do HLK), ziemny/zewnętrzny; ~15 m z zapasem.
- Obudowa IP zewnętrzna z **zapasem** (~18–24 mod.) pod późniejsze RCBO/smart — bez drugiej skrzynki na start.
- **Docelowo (bez zmian intencji):** pompy + gniazda (RCBO → smart DIN → obciążenie); opcjonalnie druga skrzynka R2.
- 230 V zewnętrzne: montaż/odbiór wg przepisów (elektryk); ten spec ≠ projekt uprawniony.

## Scope / out of scope

- In: minimum 1 skrzynka + kabel do czujnika; lista zakupów; schemat; ścieżka rozbudowy
- Out: zakup R2 teraz; konkretny model smart; projekt uprawniony

## Acceptance criteria

- Jedna skrzynka zasila czujnik always-on przez osobny RCBO
- Q0 odcina całą skrzynkę
- Zapas miejsca pod ≥2–3 kolejne obwody bez wymiany obudowy
