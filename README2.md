# Pomiar 2: okno główne

Niezależne rozszerzenie pomiaru formularza. Nie zmienia katalogów, workflow ani wyników pomiaru 1.

## Wynik i dowody

[Raport po polsku](REPORT-2.pl.md) rozdziela mowę żywego czytnika, drzewo dostępności oraz brak pomiaru. Podaje wyniki, ograniczenia, nieudane przebiegi i porównanie z WinForms.

W `results2/manifest.json` są adresy przebiegów, ścieżki źródeł w artefaktach, SHA-256 oryginałów i SHA-256 publikowanych projekcji. Projekcja usuwa powtarzający się dziennik aplikacji i zachowuje nowe zdarzenia. Próbki macOS są zredukowane do zmian wartości i statystyki odstępów. Surowe próbki pozostają w artefaktach Actions. Słowa, pozycje nazw, serie i drogi fokusu można przeliczyć skryptem.

```sh
python3 scripts2/fetch.py
python3 scripts2/curate.py --verify
python3 scripts2/verify_results.py
python3 -m unittest discover -s scripts2 -p 'test_*.py' -v
python3 scripts2/publish_check.py
```

`fetch.py` używa `gh run download` i nie uruchamia pomiarów. `curate.py --verify` porównuje publikowane projekcje z pobranymi oryginałami. Wariant bez `--verify` odtwarza projekcje. `verify_results.py --write` odtwarza zestawienie; domyślny tryb tylko je sprawdza. Skan publikacji zawiera dodatnią kontrolę detekcji i porównanie chronionych plików z bazą pomiaru 1.

## Implementacje

| Katalog | Zakres |
| --- | --- |
| [android2](android2/README.md) | TalkBack, RecyclerView, TableLayout, nagłówki, gesty, komunikaty, przygotowany tryb telefonu |
| [ios2](ios2/README.md) | UIKit, UICollectionView outline, snapshoty XCUITest; bez VoiceOver w Simulatorze |
| [macos2](macos2/README.md) | AppKit, NSTableView, NSOutlineView, żywy VoiceOver, AX i AppleScript |
| shared2 | Wspólne rekordy i tekst szczegółów |

Środowiska CI są odizolowane od czytnika na komputerze użytkownika. Skrypt fizycznego Androida wymaga jawnej zgody na zmianę ustawień i ma tryb przywracania. Nie był uruchamiany na telefonie.

Nie należy utożsamiać wejścia tekstu do TTS, kolejki NVDA i ostatniej frazy VoiceOver z nagraniem tego samego rodzaju. Wyniki opisują konkretne konfiguracje i kontrolki, a nie ranking platform.
