# Wspólna biblioteka symboli KiCad

Źródło prawdy: `tank-level.kicad_sym` (ten katalog).

Każdy projekt ma lokalny symlink:

- `tank-level-*/symbols/tank-level.kicad_sym` → `../../symbols/tank-level.kicad_sym`

`sym-lib-table` w projekcie wskazuje na `${KIPRJMOD}/symbols/tank-level.kicad_sym`
(ścieżka wewnątrz projektu — KiCad to lubi; treść jest wspólna).

W chooserze: biblioteka **`tank-level`** (np. `tank-level:JSN_SR04T`).

Po zmianie `sym-lib-table` **zamknij i otwórz ponownie** projekt (`.kicad_pro`).
