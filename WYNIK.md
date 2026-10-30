# Pomiar czytników ekranu: Android, iOS i macOS

Data: 30.10.2026. Publiczne repozytorium: [screen-reader-ux-bench](https://github.com/michaldziwisz/screen-reader-ux-bench). Licencja własnego kodu: MIT.

## Wynik w skrócie

Na Androidzie uruchomiono prawdziwy TalkBack i przechwycono tekst przekazywany do TTS. Na macOS uruchomiono prawdziwy VoiceOver. Na iOS uzyskano drzewo UIKit przez XCUITest, nie mowę VoiceOver. Catalyst uruchamia VoiceOver macOS nad interfejsem UIKit i nie jest pomiarem iOS.

Na macOS dojście kolejno do sześciu celów wymagało 12 naciśnięć Tab w wariancie GRUPY i 40 w wariancie PLASKI. Zarejestrowano odpowiednio 75 i 175 słów w oknach tych kroków. Źródło: [41118572905](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41118572905). To wynik konkretnej implementacji AppKit, nie norma dla całego systemu.

## Metoda

Formularz zawiera Imię, Nazwisko, trzy sposoby dostawy, Kraj, Liczbę sztuk, Wystaw fakturę, Newsletter, listę ośmiu zamówień oraz cztery przyciski. GRUPY ma sekcje Dane odbiorcy, Dostawa i Opcje. PLASKI ma kolejność: Zapisz, lista, Nazwisko, Newsletter, Liczba sztuk, komunikat, Imię, dostawa, Anuluj, Kraj, faktura, plik. Warianty zmieniają jednocześnie kolejność i grupy. Nie izolują wpływu samych nazw grup.

Wybrano Kotlin z systemowymi widokami Androida, UIKit i AppKit. Pozwala to badać podstawowe kontrolki bez dodatkowej warstwy Compose lub SwiftUI. Nie wykonano drugiej implementacji w tych frameworkach. Kontrolki nie są identyczne między systemami: m.in. UIKit reprezentuje wybór sposobu dostawy przez przyciski z cechą zaznaczenia, a AppKit udostępnia dodatkowe przystanki wewnątrz tabeli. Liczba przystanków nie została z góry zrównana z liczbą kontrolek Windows.

Sześć celów to **Imię → Nazwisko → Kraj → Liczba sztuk → Wystaw fakturę → Zapisz zamówienie**. Start na Imieniu kosztuje zero. Sumowane są ruchy pomiędzy celami i słowa z tych ruchów; wypowiedź początkowa nie wchodzi w koszt zadania. To pomiar nawigacji, nie wykonanie wprowadzania danych, zmiany wszystkich wartości ani test poprawności zapisu zamówienia. Tak samo interpretowany jest koszt ze wzorca Windows.

Słowo oznacza fragment po podziale tekstu białymi znakami (`str.split`). Nie tłumaczono angielskich ról systemowych ani wskazówek, nie usuwano powtórzeń. Surowa treść jest zachowana w załącznikach poniżej. Na iOS liczone są wyłącznie słowa etykiety i wartości; nie są nazywane słowami wypowiedzianymi.

**Poziomy dowodu:** mowa żywego czytnika, drzewo dostępności, brak pomiaru. Tekst na wejściu TTS i rejestr VoiceOver nie są nagraniem dźwięku. Wyniku ujemnej kontroli nie uznaje się za ciszę czytnika.

Android używa własnego `TextToSpeechService`. Kontrola „Kontrola kanału mowy” sprawdza silnik, osobna zapowiedź „Imię” sprawdza TalkBack. Obserwator dostępności zapisuje fokus oraz role i stany; sam nie generuje wypowiedzi czytnika. TTS po zapisaniu tekstu oddaje krótki bufor ciszy, więc nie mierzono czasu słuchania. W projekcji wynikowej pomijane są rekordy starsze od znacznika początku danego kroku; pozostają w materiale źródłowym.

VoiceOver sterowany jest przez Guidepup i rzeczywiste klawisze w izolowanym runnerze. Przechwytywany jest tryb `initial`, czyli początkowa odpowiedź, nie wszystkie późniejsze wskazówki. Sprawdzany jest PID aplikacji i odczytywany fokus AX. Polecenia VoiceOver wysyłane są jako Control+Option z odpowiednią strzałką. Tab oraz nawigacja kursorem VoiceOver są osobnymi seriami.

XCUITest zapisuje etykietę, typ elementu, wartość, enabled, selected oraz dzieci. Do modelu iOS wybrano pierwszy węzeł o każdym identyfikatorze kontrolki, w kolejności pre-order; tekst komórki listy pobrano z jej potomka, jeśli sama komórka nie ma etykiety. Nie policzono dwukrotnie komórki i jej tekstu. Kontener listy jest osobnym kandydatem. Nazwane grupy są pokazane osobno. **Jest to jawny model po drzewie, nie dowód rzeczywistej kolejności gestów VoiceOver.**

## Środowiska i wersje

### android

Źródło: [41120875415](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41120875415).

```text
Version: 20261021.618
Image: ubuntu-24.04
Version: 20261025.353.1
runner.txt:
ubuntu24
20261026.354.1

talkback_version:
versionCode=60138361 minSdk=26 targetSdk=35
versionName=15.0.0.639625893
android_properties:
[ro.build.fingerprint]: [google/sdk_gphone64_x86_64/emu64xa:15/AE3A.240806.036/12592187:user/release-keys]
[ro.build.version.release]: [15]
[ro.build.version.sdk]: [35]
[ro.product.model]: [sdk_gphone64_x86_64]
```

### ios

Źródło: [41117258635](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41117258635).

```text
Version: 20261021.618
Image: macos-15-arm64
Version: 20261028.0489.1
versions.txt:
ProductName:		macOS
ProductVersion:		15.8.2
BuildVersion:		24H232
Xcode 16.4
Build version 16F6

```

### macos

Źródło: [41118572905](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41118572905).

```text
Version: 20261021.618
Image: macos-15-arm64
Version: 20261028.0489.1
versions.txt:
ProductName:		macOS
ProductVersion:		15.8.2
BuildVersion:		24H232
Xcode 16.4
Build version 16F6
macos15

voiceover-plist.txt:
{
  "CFBundleAllowMixedLocalizations" => 1
  "CFBundleDevelopmentRegion" => "English"
  "CFBundleDisplayName" => "VoiceOver"
  "CFBundleExecutable" => "VoiceOverStarter"
  "CFBundleIconFile" => "VoiceOver"
  "CFBundleIdentifier" => "com.apple.VoiceOver"
  "CFBundleInfoDictionaryVersion" => "6.0"
  "CFBundleName" => "VoiceOver"
  "CFBundlePackageType" => "APPL"
  "CFBundleShortVersionString" => "10"
  "CFBundleSignature" => "????"
  "CFBundleVersion" => "964.12.11"
  "LSBackgroundOnly" => 1
  "LSLaunchDLabel" => "com.apple.VoiceOver"
  "LSMinimumSystemVersion" => "10.7.0"
  "LSUIElement" => "1"
  "NSAppleScriptEnabled" => 1
  "NSBluetoothAlwaysUsageDescription" => "Used for portable preference"
  "NSHighResolutionCapable" => 1
  "NSHumanReadableCopyright" => "Copyright © 2004-2024 Apple Inc. All Rights Reserved."
  "NSSupportsSuddenTermination" => "YES"
  "OSAScriptingDefinition" => "VoiceOver.sdef"
  "POSIXSpawnType" => "Interactive"
}

```

### catalyst

Źródło: [41118577430](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41118577430).

```text
Version: 20261021.618
Image: macos-15-arm64
Version: 20261028.0489.1
versions.txt:
ProductName:		macOS
ProductVersion:		15.8.2
BuildVersion:		24H232
Xcode 16.4
Build version 16F6

```

Guidepup 0.39.0, setup 0.29.3, XcodeGen 2.46.0. iOS: iPad Pro 13 cali (M4), runtime 18.5, potwierdzone `simulators.json` i logiem `xcodebuild`. Android: obraz Google Play x86_64, API 35, profil Pixel 2; ekran ustawiony przez skrypt na 1080 × 2400 i 160 dpi, aby cały formularz mieścił się bez dodatkowego przewijania. To nie jest typowy fizyczny Pixel 2. Gradle 8.11.1, AGP 8.9.2, Kotlin 2.1.20, JDK 17. Użyto TalkBack dostarczonego w obrazie; nie kopiowano jego binariów do repo.

VoiceOver: oficjalny pakiet startowy deklaruje wersję 10 i build 964.12.11. Guidepup zwraca dla procesu automatyzacji `0.0.1-VoiceOver4`. Nie są to zamienne identyfikatory. Identyfikacja wyniku wymaga także wersji macOS i obrazu runnera. Nie założono, że wcześniejszy błąd automatyzacji macOS 15 nadal blokuje pomiar: wybrany obraz rzeczywiście uruchomił mówienie i nawigację.

## Wyniki: koszt zadania i słowa

| Platforma | Wariant | Poziom i tryb | Kroki do 6 celów | Słowa na drodze | Mediana słów/przystanek | Actions |
| --- | --- | --- | --- | --- | --- | --- |
| android | GRUPY | mowa czytnika, Tab | 17 | 202 | 10 | [41120875415](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41120875415) |
| android | PLASKI | mowa czytnika, Tab | 50 | 582 | 11 | [41120875415](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41120875415) |
| macos | GRUPY | mowa czytnika, Tab | 12 | 75 | 5.0 | [41118572905](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41118572905) |
| macos | PLASKI | mowa czytnika, Tab | 40 | 175 | 4.0 | [41118572905](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41118572905) |
| ios | GRUPY | model drzewa, oba kierunki | 18 | 37 | 2.0 | [41117258635](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41117258635) |
| ios | PLASKI | model drzewa, oba kierunki | 48 | 89 | 2.0 | [41117258635](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41117258635) |

Mediana Androida i macOS obejmuje pierwszy pełny obieg Tab bez kotwicy startowej. Mediana iOS obejmuje wszystkie wybrane węzły. Wartości iOS opisują tekst drzewa i nie wolno porównywać ich jako kosztu słuchania z mową pozostałych systemów.

### android: odcinki drogi do sześciu celów

**GRUPY**, [41120875415](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41120875415).

| Następny cel | Kroki na odcinku | Słowa | Kierunek |
| --- | --- | --- | --- |
| nazw | 1 | 7 | Tab do przodu |
| kraj | 4 | 57 | Tab do przodu |
| szt | 1 | 17 | Tab do przodu |
| faktura | 1 | 14 | Tab do przodu |
| zapisz | 10 | 107 | Tab do przodu |

**PLASKI**, [41120875415](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41120875415).

| Następny cel | Kroki na odcinku | Słowa | Kierunek |
| --- | --- | --- | --- |
| nazw | 17 | 185 | Tab do przodu |
| kraj | 9 | 122 | Tab do przodu |
| szt | 14 | 158 | Tab do przodu |
| faktura | 8 | 97 | Tab do przodu |
| zapisz | 2 | 20 | Tab do przodu |

### macos: odcinki drogi do sześciu celów

**GRUPY**, [41118572905](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41118572905).

| Następny cel | Kroki na odcinku | Słowa | Kierunek |
| --- | --- | --- | --- |
| nazw | 1 | 3 | Tab do przodu |
| kraj | 4 | 22 | Tab do przodu |
| szt | 1 | 7 | Tab do przodu |
| faktura | 1 | 9 | Tab do przodu |
| zapisz | 5 | 34 | Tab do przodu |

**PLASKI**, [41118572905](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41118572905).

| Następny cel | Kroki na odcinku | Słowa | Kierunek |
| --- | --- | --- | --- |
| nazw | 12 | 52 | Tab do przodu |
| kraj | 9 | 36 | Tab do przodu |
| szt | 9 | 52 | Tab do przodu |
| faktura | 8 | 28 | Tab do przodu |
| zapisz | 2 | 7 | Tab do przodu |

### ios: odcinki drogi do sześciu celów

**GRUPY**, [41117258635](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41117258635).

| Następny cel | Kroki na odcinku | Słowa | Kierunek |
| --- | --- | --- | --- |
| nazw | 1 | 1 | next |
| kraj | 4 | 6 | next |
| szt | 1 | 3 | next |
| faktura | 1 | 3 | next |
| zapisz | 11 | 24 | next |

**PLASKI**, [41117258635](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41117258635).

| Następny cel | Kroki na odcinku | Słowa | Kierunek |
| --- | --- | --- | --- |
| nazw | 4 | 10 | previous |
| kraj | 9 | 17 | next |
| szt | 7 | 11 | previous |
| faktura | 8 | 13 | next |
| zapisz | 20 | 38 | previous |

## Android: nawigacja TalkBack a zwykły Tab

`adb input swipe` nie zostało przyjęte jako poprawny gest „następny element” tylko dlatego, że polecenie kończyło się kodem zero. Sprawdzono zmianę fokusu dostępności. Niepowodzenie tej drogi oznacza brak pomiaru gestów dotykowych, nie brak działania TalkBack. Alternatywą był skrót Alt+Right czytnika, a osobno zwykły Tab aplikacji. Gdy frameworkowe `input keycombination` nie dawało ruchu, sprawdzano też zdarzenia klawiatury na wejściu emulatora (`adb emu event send`). Nazwa `hardware-Alt-Right` oznacza tę drugą drogę, nie fizyczne urządzenie użytkownika.

**GRUPY**, [41120875415](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41120875415): swipe: 0 zdarzeń zmiany fokusu na 3 prób. hardware-Alt-Right: 3 prób, 0 okien ze zdarzeniem fokusu. Koszt 6 celów w tej serii: None kroków, None słów; `None` oznacza nieuzyskanie pełnej drogi, nie zero.

**PLASKI**, [41120875415](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41120875415): swipe: 0 zdarzeń zmiany fokusu na 3 prób. hardware-Alt-Right: 3 prób, 0 okien ze zdarzeniem fokusu. Koszt 6 celów w tej serii: None kroków, None słów; `None` oznacza nieuzyskanie pełnej drogi, nie zero.

**Wynik Androida jest pomiarem Tab z działającym TalkBack, nie pomiarem gestów dotykowych.** W tej kampanii ani swipe z adb, ani Alt+Right przez framework, ani Alt+Right przez konsolę emulatora nie dały zarejestrowanego przesunięcia fokusu czytnika. `accessibility.txt` potwierdza związane usługi TalkBack i obserwatora oraz `touchExplorationEnabled=true`. Nie rozstrzygnięto, czy przyczyną bezskutecznych poleceń jest droga wstrzykiwania, mapa skrótów czy inny element konfiguracji. Nie zastąpiono tego braku modelem udającym rzeczywisty gest.

## Zachowania i skróty

| Platforma | Wariant | Tak/Nie zamknięte przez Esc/Back | Skrót zapisu dał potwierdzenie | Actions |
| --- | --- | --- | --- | --- |
| android | GRUPY | tak | tak | [41120875415](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41120875415) |
| android | PLASKI | tak | tak | [41120875415](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41120875415) |
| macos | GRUPY | nie | tak | [41118572905](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41118572905) |
| macos | PLASKI | nie | tak | [41118572905](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41118572905) |
| ios | GRUPY | nie | tak | [41117258635](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41117258635) |
| ios | PLASKI | nie | tak | [41117258635](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41117258635) |

Android używa Back oraz Ctrl+S; iOS i macOS używają Escape oraz Command+S. Potwierdzenie zapisu na macOS to zmiana tytułu na `UXPomiar zapisano`, na iOS wartość dostępności `Zapisano zamówienie`, a na Androidzie przechwycona zapowiedź. To nie test utworzenia pliku. Same dźwięki wypowiadanych nazw skrótów nie były uznawane za wykonanie akcji. Przycisk zapisu jako plik jest obecny w każdym formularzu, ale systemowe okna plikowe nie były osobnym pełnym scenariuszem pomiarowym.

Na macOS zwykły Tab przechodzi osobno przez wszystkie trzy przyciski opcji. W tabeli występują dodatkowo edytowalna komórka i pionowy pasek przewijania. Nie jest to identyczny model jak RadioBox i ListBox z Windows. W szeregu VoiceOver nazwane grupy wymagają wejścia i wyjścia. Zapisano także próby ruchu na granicy grupy, które nie zmieniły elementu. Nie uznano ich za przystanki nowej kontrolki.

Przejście Tabem w AppKit zapowiada wejście i wyjście z grupy. W nawigacji VO+Right występują ponadto etykiety tekstowe, np. „Nazwisko”, oddzielnie od pola „Nazwisko edit text”. Samo ustawienie etykiety dostępności kontrolki nie gwarantuje usunięcia sąsiedniego tekstu z porządku czytania. Wariant PLASKI nie zmusza VoiceOver do grupowania, ale nadal ma wszystkie koszty wynikające z pomieszanej kolejności.

W AppKit pytanie NSAlert z przyciskami Tak i Nie pozostało po Escape. Tak samo zachowało się badane pytanie UIKit na symulatorze. Android Back zamknął pytanie. Wnioski opierają się na porównaniu drzew przed i po, nie na samym powodzeniu wysłania klawisza. Żaden z dialogów Apple nie miał przycisku z rolą Anuluj.

## iOS: audyt i granice modelu

Apple stwierdza, że VoiceOver nie jest dostępny w Simulatorze. Uruchomiono `performAccessibilityAudit`, lecz procedura zapisuje problemy i pozwala testowi przejść dalej. Zielony test **nie oznacza czystego audytu dostępności**. Zrzuty ekranów potwierdzają obecność formularza i listy; nie dowodzą kolejności czytania.

**GRUPY**: 22 węzły w modelu, grupy: Dane odbiorcy, Dostawa, Sposób dostawy, Opcje, Vertical scroll bar, 1 page, Horizontal scroll bar, 1 page, Vertical scroll bar, 1 page, Horizontal scroll bar, 1 page, Vertical scroll bar, 1 page, Horizontal scroll bar, 1 page. Ruch wyłącznie do przodu: 18 kroków do wszystkich celów. Problemy audytu (26):

1. <XCUIAccessibilityAuditIssue: 0x600000ca02a0>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"Pokaż komunikat" StaticText

1. <XCUIAccessibilityAuditIssue: 0x600000ca00c0>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"Paczkomat" StaticText

1. <XCUIAccessibilityAuditIssue: 0x600000ca02d0>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"Dostawa" StaticText

1. <XCUIAccessibilityAuditIssue: 0x600000ca0300>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"Zapisz zamówienie" StaticText

1. <XCUIAccessibilityAuditIssue: 0x600000ca0330>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"Kraj: Polska" StaticText

1. <XCUIAccessibilityAuditIssue: 0x600000ca0390>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:(null)

1. <XCUIAccessibilityAuditIssue: 0x600000ca03c0>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"Wystaw fakturę" StaticText

1. <XCUIAccessibilityAuditIssue: 0x600000ca0360>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"Odbiór osobisty" StaticText

1. <XCUIAccessibilityAuditIssue: 0x600000ca03f0>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"imie" TextField

1. <XCUIAccessibilityAuditIssue: 0x600000ca0180>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"Anuluj" StaticText

1. <XCUIAccessibilityAuditIssue: 0x600000ca0420>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:(null)

1. <XCUIAccessibilityAuditIssue: 0x600000ca0450>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"Kurier" StaticText

1. <XCUIAccessibilityAuditIssue: 0x600000ca0480>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"szt" TextField

1. <XCUIAccessibilityAuditIssue: 0x600000ca04b0>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"Opcje" StaticText

1. <XCUIAccessibilityAuditIssue: 0x600000ca04e0>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"Zapisz jako plik" StaticText

1. <XCUIAccessibilityAuditIssue: 0x600000ca0510>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"Dane odbiorcy" StaticText

1. <XCUIAccessibilityAuditIssue: 0x600000ca0540>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"Zapisz na newsletter" StaticText

1. <XCUIAccessibilityAuditIssue: 0x600000ca0570>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"nazw" TextField

1. <XCUIAccessibilityAuditIssue: 0x600000ca05a0>AuditType:"131072" CompactDescription:"Text clipped" DetailedDescription:"Text of this element may be clipped at larger Dynamic Type sizes." Element:(null)

1. <XCUIAccessibilityAuditIssue: 0x600000ca05d0>AuditType:"131072" CompactDescription:"Text clipped" DetailedDescription:"Text of this element may be clipped at larger Dynamic Type sizes." Element:(null)

1. <XCUIAccessibilityAuditIssue: 0x600000ca0600>AuditType:"131072" CompactDescription:"Text clipped" DetailedDescription:"Text of this element may be clipped at larger Dynamic Type sizes." Element:(null)

1. <XCUIAccessibilityAuditIssue: 0x600000ca0630>AuditType:"131072" CompactDescription:"Text clipped" DetailedDescription:"Text of this element may be clipped at larger Dynamic Type sizes." Element:(null)

1. <XCUIAccessibilityAuditIssue: 0x600000ca0660>AuditType:"131072" CompactDescription:"Text clipped" DetailedDescription:"Text of this element may be clipped at larger Dynamic Type sizes." Element:(null)

1. <XCUIAccessibilityAuditIssue: 0x600000ca0690>AuditType:"131072" CompactDescription:"Text clipped" DetailedDescription:"Text of this element may be clipped at larger Dynamic Type sizes." Element:(null)

1. <XCUIAccessibilityAuditIssue: 0x600000ca06c0>AuditType:"131072" CompactDescription:"Text clipped" DetailedDescription:"Text of this element may be clipped at larger Dynamic Type sizes." Element:(null)

1. <XCUIAccessibilityAuditIssue: 0x600000ca0240>AuditType:"131072" CompactDescription:"Text clipped" DetailedDescription:"Text of this element may be clipped at larger Dynamic Type sizes." Element:(null)

**PLASKI**: 22 węzły w modelu, grupy: Vertical scroll bar, 1 page, Horizontal scroll bar, 1 page, Sposób dostawy, Vertical scroll bar, 1 page, Horizontal scroll bar, 1 page, Vertical scroll bar, 1 page, Horizontal scroll bar, 1 page. Ruch wyłącznie do przodu: Nie dociera do następnego celu `nazw` bez cofnięcia lub powrotu na początek. Nie założono cyklicznych gestów. Problemy audytu (23):

1. <XCUIAccessibilityAuditIssue: 0x600000cc77e0>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:(null)

1. <XCUIAccessibilityAuditIssue: 0x600000cc7960>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"nazw" TextField

1. <XCUIAccessibilityAuditIssue: 0x600000cc4000>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"Paczkomat" StaticText

1. <XCUIAccessibilityAuditIssue: 0x600000cc6850>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"Anuluj" StaticText

1. <XCUIAccessibilityAuditIssue: 0x600000cc49c0>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"imie" TextField

1. <XCUIAccessibilityAuditIssue: 0x600000cc6370>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"szt" TextField

1. <XCUIAccessibilityAuditIssue: 0x600000cc73c0>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:(null)

1. <XCUIAccessibilityAuditIssue: 0x600000cc41e0>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"Odbiór osobisty" StaticText

1. <XCUIAccessibilityAuditIssue: 0x600000cc7480>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"Wystaw fakturę" StaticText

1. <XCUIAccessibilityAuditIssue: 0x600000cc7240>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"Zapisz zamówienie" StaticText

1. <XCUIAccessibilityAuditIssue: 0x600000cc7120>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"Zapisz na newsletter" StaticText

1. <XCUIAccessibilityAuditIssue: 0x600000cc7180>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"Kurier" StaticText

1. <XCUIAccessibilityAuditIssue: 0x600000cc6f10>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"Zapisz jako plik" StaticText

1. <XCUIAccessibilityAuditIssue: 0x600000cc7060>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"Kraj: Polska" StaticText

1. <XCUIAccessibilityAuditIssue: 0x600000cc7360>AuditType:"65536" CompactDescription:"Dynamic Type font sizes are unsupported" DetailedDescription:"User will not be able to change the font size of this element" Element:"Pokaż komunikat" StaticText

1. <XCUIAccessibilityAuditIssue: 0x600000cc71e0>AuditType:"131072" CompactDescription:"Text clipped" DetailedDescription:"Text of this element may be clipped at larger Dynamic Type sizes." Element:(null)

1. <XCUIAccessibilityAuditIssue: 0x600000cc72a0>AuditType:"131072" CompactDescription:"Text clipped" DetailedDescription:"Text of this element may be clipped at larger Dynamic Type sizes." Element:(null)

1. <XCUIAccessibilityAuditIssue: 0x600000cc7090>AuditType:"131072" CompactDescription:"Text clipped" DetailedDescription:"Text of this element may be clipped at larger Dynamic Type sizes." Element:(null)

1. <XCUIAccessibilityAuditIssue: 0x600000cc7030>AuditType:"131072" CompactDescription:"Text clipped" DetailedDescription:"Text of this element may be clipped at larger Dynamic Type sizes." Element:(null)

1. <XCUIAccessibilityAuditIssue: 0x600000cc6ee0>AuditType:"131072" CompactDescription:"Text clipped" DetailedDescription:"Text of this element may be clipped at larger Dynamic Type sizes." Element:(null)

1. <XCUIAccessibilityAuditIssue: 0x600000cc6f70>AuditType:"131072" CompactDescription:"Text clipped" DetailedDescription:"Text of this element may be clipped at larger Dynamic Type sizes." Element:(null)

1. <XCUIAccessibilityAuditIssue: 0x600000cc41b0>AuditType:"131072" CompactDescription:"Text clipped" DetailedDescription:"Text of this element may be clipped at larger Dynamic Type sizes." Element:(null)

1. <XCUIAccessibilityAuditIssue: 0x600000cc69d0>AuditType:"131072" CompactDescription:"Text clipped" DetailedDescription:"Text of this element may be clipped at larger Dynamic Type sizes." Element:(null)

## Catalyst: próba przybliżenia, nie wynik iOS

Ta sama aplikacja UIKit została zbudowana dla Mac Catalyst i udostępniła realną mowę VoiceOver macOS. Nie przyjęto jej jednak jako wiarygodnego zastępstwa zachowania VoiceOver na iPadzie. UIKit pod Catalyst ma inne role, reguły klawiatury i śledzenie fokusu. Wykryto rozbieżności między aktualnym fokusem AX a tekstem przechwyconym w tym samym krótkim oknie.

**GRUPY**, [41118577430](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41118577430): 25 naciśnięć Tab; identyfikatory fokusowanych kontrolek: `imie, nazw`. Pustych okien rejestru mowy: 9 na 26 okien razem z kotwicą. Kontrola obecności znanego tekstu: tak. Nie wyliczono na tej podstawie kosztu mowy iOS.

**PLASKI**, [41118577430](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41118577430): 25 naciśnięć Tab; identyfikatory fokusowanych kontrolek: `anuluj, faktura, imie, komunikat, kraj, nazw, news, order_1, plik, sposob_0, sposob_1, sposob_2, szt, zapisz`. Pustych okien rejestru mowy: 5 na 26 okien razem z kotwicą. Kontrola obecności znanego tekstu: tak. Nie wyliczono na tej podstawie kosztu mowy iOS.

## Opóźnienia

Na Androidzie zapisano różnicę między znacznikiem w logcat przed wywołaniem adb a wejściem do `onSynthesizeText`. Zawiera koszt transportu adb i wstrzyknięcia zdarzenia. Jest to diagnostyczny czas **znacznik → wejście TTS**, nie czyste opóźnienie od fizycznego gestu i nie początek dźwięku. Występowały również starsze rekordy; wartości ujemne wyłączono z poniższej statystyki.

GRUPY: mediana 126.0 ms dla 65 nieujemnych wartości w serii Tab, [41120875415](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41120875415).

PLASKI: mediana 77.0 ms dla 65 nieujemnych wartości w serii Tab, [41120875415](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41120875415).

Pole `api_ms` na macOS obejmuje czas wykonania API Guidepup i oczekiwania biblioteki na początkową wypowiedź. Nie jest znacznikiem początku mowy. Nie podano z niego pozornie dokładnej latencji VoiceOver. Na iOS nie mierzono opóźnienia mowy, ponieważ czytnik nie działał. Czasy Windows z poniższej tabeli nie są bezpośrednio porównywalne z czasem znacznika adb.

## Porównanie z Windows

Źródło Windows: dostarczony `WZORZEC-pomiar-windows-RAPORT.md`, sekcja „Wyniki: czasy”. Nie odczytywano bieżącej maszyny Windows ani NVDA i nie publikowano prywatnych logów. Dane Windows są jedynymi liczbami tej tabeli, które nie pochodzą z Actions.

| Platforma | Wariant | Dowód i metoda | Kroki | Słowa | Mediana słów/przystanek | Źródło |
| --- | --- | --- | --- | --- | --- | --- |
| Windows, NVDA 2026.2, wx | GRUPY | mowa kolejki, Tab | 8 | 73 | 9 | wzorzec |
| Windows, NVDA 2026.2, wx | PLASKI | mowa kolejki, Tab | 30 | 208 | 7,5 | wzorzec |
| android | GRUPY | mowa czytnika, Tab | 17 | 202 | 10 | [41120875415](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41120875415) |
| android | PLASKI | mowa czytnika, Tab | 50 | 582 | 11 | [41120875415](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41120875415) |
| macos | GRUPY | mowa czytnika, Tab | 12 | 75 | 5.0 | [41118572905](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41118572905) |
| macos | PLASKI | mowa czytnika, Tab | 40 | 175 | 4.0 | [41118572905](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41118572905) |
| ios | GRUPY | drzewo, model obu kierunków | 18 | 37 | nieporównywalna | [41117258635](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41117258635) |
| ios | PLASKI | drzewo, model obu kierunków | 48 | 89 | nieporównywalna | [41117258635](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41117258635) |

Windows: mediana opóźnienia do kolejki 32,8 ms, p90 62,4 ms, 278 pomiarów. Wzrost kosztu kroków po wymieszaniu kolejności: Windows 3,75 raza; AppKit 3.33 raza. Wzrost kosztu słów w AppKit: 2.33 raza. Nie przeliczono angielskich wypowiedzi ról macOS i Androida na polskie czasy syntezatorów z wzorca.

## Kontrola jakości, publikacja i historia prób

Kod jest publiczny, z licencją MIT i polskim README. Kontrola skanera przed pierwszą publikacją: sztuczny sekret w pliku poza repo został wykryty kodem 1, a skan początkowego drzewa siedmiu plików zwrócił kod 0. Wartość kontrolną usunięto przed pierwszym push. Bieżące potwierdzenie skanu i powtórzonej kontroli jest zapisane w `results/security.json`. Regexowy skan nie zastępuje przeglądu treści.

Uruchomiono 17 workflow, przy limicie kampanii około 25. Każdy ma timeout. Artefakty pobrano pod `wyniki/<platforma>/<id>/`; pliki `workflow.log` i `run.json` przechowują pełną historię. Wybrane wyniki końcowe zachowano w `results/`, aby nie znikły po wygaśnięciu artefaktów Actions. Sumy SHA-256 w `summary.json` odnoszą się do plików pobranych z artefaktów. Kopie JSON w `results/` mogą mieć inne formatowanie, ale są sprawdzane pod względem równości danych.

Pierwsza kontrola mowy nie wystarczała: odrzucono także zielony przebieg, w którym klawisze Tab nie zmieniały fokusu aplikacji. Brak ruchu nie został opublikowany jako tani formularz. Nieudane próby uruchomienia, błędy sterownika i rzeczywiste zachowania kontrolek są oddzielone.

| Przebieg | Wynik Actions | Interpretacja |
| --- | --- | --- |
| [41116654791](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41116654791) | success | Rozpoznanie obrazów, obecności TalkBack i uruchomienia VoiceOver. |
| [41116964774](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41116964774) | failure | Bramka PID przerwała po przejściu procesu VoiceOver na pierwszy plan. |
| [41117041338](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41117041338) | failure | Ujemna kontrola TTS; usługi przerwane przez force-stop, brak DEFAULT w filtrze TTS. Wynik odrzucony. |
| [41117258635](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41117258635) | success | Końcowy pomiar drzewa iOS; zgłoszenia audytu zapisane, nie zamaskowane werdyktem czystego audytu. |
| [41117361067](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41117361067) | success | Zielony technicznie, lecz Tab nie przesuwał fokusu aplikacji. Odrzucony. |
| [41117442426](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41117442426) | failure | Nieudana aktywacja Catalyst przez identyfikator aplikacji w Guidepup. |
| [41117642301](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41117642301) | failure | Błąd sondy: nieobsługiwana opcja adb --activity-new-task. |
| [41117848919](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41117848919) | failure | Nieudana aktywacja AppKit przez nazwę aplikacji w Guidepup. |
| [41117853216](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41117853216) | failure | Nieudana aktywacja Catalyst przez nazwę aplikacji w Guidepup. |
| [41118208720](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41118208720) | success | TalkBack i Tab działały. Gesty adb nie zmieniały fokusu. Seria Tab zbyt krótka do całego zadania PLASKI. |
| [41118242572](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41118242572) | success | Prawdziwa mowa i ruch Tab; za krótka seria dla całej drogi PLASKI. |
| [41118246911](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41118246911) | failure | Catalyst bez poprawnej aktywacji nie przeszedł kontroli. |
| [41118572905](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41118572905) | success | Końcowy pomiar AppKit. |
| [41118577430](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41118577430) | success | Catalyst: realna mowa macOS, ale nieodpowiedni zamiennik iOS. |
| [41119543530](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41119543530) | failure | Ujemna kontrola czytnika: obserwator niegotowy, dialog zgody na powiadomienia Android Accessibility Suite zasłonił formularz. |
| [41120203817](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41120203817) | failure | Nieuzyskana gotowość obserwatora przed pierwszym uruchomieniem świeżo zainstalowanego pakietu. |
| [41120875415](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41120875415) | success | Start aplikacji przed włączeniem obserwatora; kontrola kanału i nawigacja klawiaturowa. |

## Czego pomiar nie rozstrzyga

1. Nie mierzy intuicyjności u ludzi, czasu decyzji, uczenia się ani obciążenia pamięci. Krótsza droga klawiszowa jest wskaźnikiem kosztu, nie dowodem lepszej użyteczności dla każdego użytkownika.
2. Nie izoluje grupowania od kolejności. Nie obejmuje Compose, SwiftUI, innych wersji czytników, brajla ani niestandardowych konfiguracji użytkowników.
3. iOS pozostaje poziomem drzewa. Nie dowodzi liczby gestów, treści mowy, zachowania rotora ani interakcji palcem. Model następny/poprzedni jest obliczeniem, nie zasymulowanym nagraniem VoiceOver.
4. Skróty i zamknięcie dialogu są wynikami tej aplikacji i tych wersji. Nie są gwarancją zachowania dowolnego dialogu systemowego.
5. Nie mierzono fizycznego dźwięku. Wskazówki, interpunkcja i opóźnione komunikaty mogą zmieniać liczbę słów między kolejnymi obiegami. Nie zamieniono jednego przebiegu w próbę populacyjną.
6. Brak reakcji na wstrzyknięty gest adb nie dowodzi braku reakcji na gest prawdziwego użytkownika. Dla tej ścieżki wynik brzmi „brak pomiaru gestów”, mimo działającego TalkBack.
7. Nie wykonywano zmian na Windows, nie uruchamiano ani nie zatrzymywano NVDA, nie korzystano z osobistych telefonów. Wszystkie nowe serie pochodzą z publicznych runnerów.

## Źródła dokumentacji

[Apple: ograniczenia Simulatora i testowanie dostępności](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)

[Guidepup: VoiceOver](https://www.guidepup.dev/docs/api/class-voiceover)

[Zgłoszenie dotyczące automatyzacji na macOS](https://github.com/actions/runner-images/issues/11257)

[TalkBack: domyślny model skrótów](https://github.com/google/talkback/blob/master/talkback/src/main/java/com/google/android/accessibility/talkback/keyboard/DefaultKeyComboModel.java)

[Android: rejestracja silników TTS](https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/core/java/android/speech/tts/TtsEngines.java)

## Załącznik A: przystanki i treści

Poniżej są pełne serie użyte do wyliczeń. Indeks 0 to kotwica. Kolumna „słowa” jest policzona z dosłownego tekstu. Dla iOS indeks oznacza pozycję w drzewie, nie rzeczywisty gest. `id` służy jednoznacznemu powiązaniu z kodem i plikiem JSON.

### android GRUPY

Źródło: [41120875415](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41120875415), plik `wyniki/android/41120875415/android-measure/GRUPY.json`.

| Indeks | id | Rola | Treść | Słowa |
| --- | --- | --- | --- | --- |
| 0 | imie | android.widget.EditText | keyboard hidden | 2 |
| 1 | nazw | android.widget.EditText | Nazwisko Editing, Nazwisko, Edit box Showing Gboard | 7 |
| 2 | sposob_0 | android.widget.RadioButton | Kurier selected, Kurier, Radio button, 1 of 3, In list Sposób dostawy, 3 items Showing split keyboard Showing Physical keyboard | 20 |
| 3 | sposob_1 | android.widget.RadioButton | Paczkomat not selected, Paczkomat, Radio button, 2 of 3 Double-tap to select | 12 |
| 4 | sposob_2 | android.widget.RadioButton | not selected, Odbiór osobisty, Radio button, 3 of 3 Double-tap to select | 12 |
| 5 | kraj | android.widget.Spinner | Kraj Kraj, Drop down list, Out of list Sposób dostawy Double-tap to change | 13 |
| 6 | szt | android.widget.EditText | Liczba sztuk Editing, 1, Edit box, Liczba sztuk Showing split keyboard Double-tap and hold to long press | 17 |
| 7 | faktura | android.widget.CheckBox | Wystaw fakturę not checked, Wystaw fakturę, Check box Showing split keyboard Double-tap to toggle | 14 |
| 8 | news | android.widget.CheckBox | Wystaw fakturę Zapisz na newsletter not checked, Zapisz na newsletter, Check box Double-tap to toggle | 15 |
| 9 | lista | android.widget.ListView | Zapisz na newsletter Ostatnie zamówienia | 5 |
| 10 | order_2 | android.widget.CheckedTextView | Zamówienie 2 Ostatnie zamówienia selected, Zamówienie 2, In list Ostatnie zamówienia Double-tap to select | 14 |
| 11 | order_3 | android.widget.CheckedTextView | Zamówienie 3 Ostatnie zamówienia selected, Zamówienie 3 Double-tap to select | 10 |
| 12 | order_4 | android.widget.CheckedTextView | Zamówienie 4 Ostatnie zamówienia selected, Zamówienie 4 Double-tap to select | 10 |
| 13 | order_5 | android.widget.CheckedTextView | Zamówienie 5 Ostatnie zamówienia selected, Zamówienie 5 Double-tap to select | 10 |
| 14 | order_6 | android.widget.CheckedTextView | Zamówienie 6 Ostatnie zamówienia selected, Zamówienie 6 Double-tap to select | 10 |
| 15 | order_7 | android.widget.CheckedTextView | Zamówienie 7 Ostatnie zamówienia selected, Zamówienie 7 Double-tap to select | 10 |
| 16 | order_8 | android.widget.CheckedTextView | Zamówienie 8 Ostatnie zamówienia selected, Zamówienie 8 Double-tap to select | 10 |
| 17 | zapisz | android.widget.Button | Zapisz zamówienie Zapisz zamówienie, Button, Out of list Ostatnie zamówienia Double-tap to activate | 13 |
| 18 | anuluj | android.widget.Button | Anuluj Anuluj, Button Double-tap to activate | 6 |
| 19 | komunikat | android.widget.Button | Pokaż komunikat Pokaż komunikat, Button Double-tap to activate | 8 |
| 20 | plik | android.widget.Button | Zapisz jako plik Zapisz jako plik, Button Double-tap to activate | 10 |
| 21 | imie | android.widget.EditText | Imię Editing, Imię, Edit box Showing split keyboard Showing Gboard | 10 |
| 22 | nazw | android.widget.EditText | Nazwisko Editing, Nazwisko, Edit box Showing split keyboard Double-tap and hold to long press, Proofreading is available. 1 misspelled words. Swipe down with 3 fingers and use "Proofread" to view | 30 |
| 23 | sposob_0 | android.widget.RadioButton | Kurier Showing split keyboard selected, Kurier, Radio button, 1 of 3, In list Sposób dostawy, 3 items Showing Physical keyboard | 20 |
| 24 | sposob_1 | android.widget.RadioButton | Paczkomat not selected, Paczkomat, Radio button, 2 of 3 Double-tap to select | 12 |
| 25 | sposob_2 | android.widget.RadioButton | Odbiór osobisty not selected, Odbiór osobisty, Radio button, 3 of 3 Double-tap to select | 14 |
| 26 | kraj | android.widget.Spinner | Kraj Kraj, Drop down list, Out of list Sposób dostawy Double-tap to change | 13 |
| 27 | szt | android.widget.EditText | Liczba sztuk Showing split keyboard Editing, 1, Edit box, Liczba sztuk Double-tap and hold to long press | 17 |
| 28 | faktura | android.widget.CheckBox | Wystaw fakturę Showing split keyboard not checked, Wystaw fakturę, Check box Double-tap to toggle | 14 |
| 29 | news | android.widget.CheckBox | Wystaw fakturę Zapisz na newsletter not checked, Zapisz na newsletter, Check box Double-tap to toggle | 15 |
| 30 | lista | android.widget.ListView | Zapisz na newsletter Ostatnie zamówienia | 5 |
| 31 | order_2 | android.widget.CheckedTextView | Zamówienie 2 Ostatnie zamówienia selected, Zamówienie 2, In list Ostatnie zamówienia Double-tap to select | 14 |
| 32 | order_3 | android.widget.CheckedTextView | Zamówienie 3 Ostatnie zamówienia selected, Zamówienie 3 Double-tap to select | 10 |
| 33 | order_4 | android.widget.CheckedTextView | Zamówienie 4 Ostatnie zamówienia selected, Zamówienie 4 Double-tap to select | 10 |
| 34 | order_5 | android.widget.CheckedTextView | Zamówienie 5 Ostatnie zamówienia selected, Zamówienie 5 Double-tap to select | 10 |
| 35 | order_6 | android.widget.CheckedTextView | Zamówienie 6 Ostatnie zamówienia selected, Zamówienie 6 Double-tap to select | 10 |
| 36 | order_7 | android.widget.CheckedTextView | Zamówienie 7 Ostatnie zamówienia selected, Zamówienie 7 Double-tap to select | 10 |
| 37 | order_8 | android.widget.CheckedTextView | Zamówienie 8 Ostatnie zamówienia selected, Zamówienie 8 Double-tap to select | 10 |
| 38 | zapisz | android.widget.Button | Zapisz zamówienie Zapisz zamówienie, Button, Out of list Ostatnie zamówienia Double-tap to activate | 13 |
| 39 | anuluj | android.widget.Button | Anuluj Anuluj, Button Double-tap to activate | 6 |
| 40 | komunikat | android.widget.Button | Pokaż komunikat Pokaż komunikat, Button Double-tap to activate keyboard hidden | 10 |
| 41 | plik | android.widget.Button | Zapisz jako plik Zapisz jako plik, Button Double-tap to activate Showing split keyboard | 13 |
| 42 | imie | android.widget.EditText | Imię Editing, Imię, Edit box Double-tap and hold to long press | 11 |
| 43 | nazw | android.widget.EditText | Nazwisko Editing, Nazwisko, Edit box Showing split keyboard Showing Gboard | 10 |
| 44 | sposob_0 | android.widget.RadioButton | Kurier selected, Kurier, Radio button, 1 of 3, In list Sposób dostawy, 3 items Showing split keyboard Showing Physical keyboard | 20 |
| 45 | sposob_1 | android.widget.RadioButton | Paczkomat not selected, Paczkomat, Radio button, 2 of 3 Double-tap to select | 12 |
| 46 | sposob_2 | android.widget.RadioButton | Odbiór osobisty not selected, Odbiór osobisty, Radio button, 3 of 3 Double-tap to select | 14 |
| 47 | kraj | android.widget.Spinner | Kraj Kraj, Drop down list, Out of list Sposób dostawy Double-tap to change | 13 |
| 48 | szt | android.widget.EditText | Liczba sztuk Editing, 1, Edit box, Liczba sztuk Showing split keyboard Double-tap and hold to long press | 17 |
| 49 | faktura | android.widget.CheckBox | Wystaw fakturę not checked, Wystaw fakturę, Check box Showing split keyboard Double-tap to toggle | 14 |
| 50 | news | android.widget.CheckBox | Wystaw fakturę Zapisz na newsletter not checked, Zapisz na newsletter, Check box Double-tap to toggle | 15 |
| 51 | lista | android.widget.ListView | Zapisz na newsletter Ostatnie zamówienia | 5 |
| 52 | order_2 | android.widget.CheckedTextView | Zamówienie 2 Ostatnie zamówienia selected, Zamówienie 2, In list Ostatnie zamówienia Double-tap to select | 14 |
| 53 | order_3 | android.widget.CheckedTextView | Zamówienie 3 Ostatnie zamówienia selected, Zamówienie 3 Double-tap to select | 10 |
| 54 | order_4 | android.widget.CheckedTextView | Zamówienie 4 Ostatnie zamówienia selected, Zamówienie 4 Double-tap to select | 10 |
| 55 | order_5 | android.widget.CheckedTextView | Zamówienie 5 Ostatnie zamówienia selected, Zamówienie 5 Double-tap to select | 10 |
| 56 | order_6 | android.widget.CheckedTextView | Zamówienie 6 Ostatnie zamówienia selected, Zamówienie 6 Double-tap to select | 10 |
| 57 | order_7 | android.widget.CheckedTextView | Zamówienie 7 Ostatnie zamówienia selected, Zamówienie 7 Double-tap to select | 10 |
| 58 | order_8 | android.widget.CheckedTextView | Zamówienie 8 Ostatnie zamówienia selected, Zamówienie 8 Double-tap to select | 10 |
| 59 | zapisz | android.widget.Button | Zapisz zamówienie Zapisz zamówienie, Button, Out of list Ostatnie zamówienia Double-tap to activate | 13 |
| 60 | anuluj | android.widget.Button | Anuluj Anuluj, Button Double-tap to activate | 6 |
| 61 | komunikat | android.widget.Button | Pokaż komunikat Pokaż komunikat, Button Double-tap to activate | 8 |
| 62 | plik | android.widget.Button | Zapisz jako plik Zapisz jako plik, Button Double-tap to activate | 10 |
| 63 | imie | android.widget.EditText | Imię Editing, Imię, Edit box Showing split keyboard Showing Gboard | 10 |
| 64 | nazw | android.widget.EditText | Nazwisko Editing, Nazwisko, Edit box Showing split keyboard Double-tap and hold to long press, Proofreading is available. 1 misspelled words. Swipe down with 3 fingers and use "Proofread" to view | 30 |
| 65 | sposob_0 | android.widget.RadioButton | Kurier selected, Kurier, Radio button, 1 of 3, In list Sposób dostawy, 3 items Showing split keyboard Showing Physical keyboard | 20 |

| Cel | Pierwsze dojście od Imienia |
| --- | --- |
| imie | 0 |
| nazw | 1 |
| sposob_0 | 2 |
| sposob_1 | 3 |
| sposob_2 | 4 |
| kraj | 5 |
| szt | 6 |
| faktura | 7 |
| news | 8 |
| lista | 9 |
| order_2 | 10 |
| order_3 | 11 |
| order_4 | 12 |
| order_5 | 13 |
| order_6 | 14 |
| order_7 | 15 |
| order_8 | 16 |
| zapisz | 17 |
| anuluj | 18 |
| komunikat | 19 |
| plik | 20 |

### android PLASKI

Źródło: [41120875415](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41120875415), plik `wyniki/android/41120875415/android-measure/PLASKI.json`.

| Indeks | id | Rola | Treść | Słowa |
| --- | --- | --- | --- | --- |
| 0 | imie | android.widget.EditText | keyboard hidden | 2 |
| 1 | sposob_0 | android.widget.RadioButton | Kurier Showing split keyboard selected, Kurier, Radio button, 1 of 3, In list Sposób dostawy, 3 items Showing Physical keyboard | 20 |
| 2 | sposob_1 | android.widget.RadioButton | Paczkomat not selected, Paczkomat, Radio button, 2 of 3 Double-tap to select | 12 |
| 3 | sposob_2 | android.widget.RadioButton | Odbiór osobisty not selected, Odbiór osobisty, Radio button, 3 of 3 Double-tap to select | 14 |
| 4 | anuluj | android.widget.Button | Anuluj Anuluj, Button, Out of list Sposób dostawy Double-tap to activate | 11 |
| 5 | kraj | android.widget.Spinner | Kraj Kraj, Drop down list Double-tap to change | 8 |
| 6 | faktura | android.widget.CheckBox | Wystaw fakturę not checked, Wystaw fakturę, Check box Double-tap to toggle | 11 |
| 7 | plik | android.widget.Button | Wystaw fakturę Zapisz jako plik Zapisz jako plik, Button Double-tap to activate | 12 |
| 8 | zapisz | android.widget.Button | Zapisz zamówienie Zapisz zamówienie, Button Double-tap to activate | 8 |
| 9 | lista | android.widget.ListView | Ostatnie zamówienia | 2 |
| 10 | order_2 | android.widget.CheckedTextView | Zamówienie 2 Ostatnie zamówienia selected, Zamówienie 2, In list Ostatnie zamówienia Double-tap to select | 14 |
| 11 | order_3 | android.widget.CheckedTextView | Zamówienie 3 Ostatnie zamówienia selected, Zamówienie 3 Double-tap to select | 10 |
| 12 | order_4 | android.widget.CheckedTextView | Zamówienie 4 Ostatnie zamówienia selected, Zamówienie 4 Double-tap to select | 10 |
| 13 | order_5 | android.widget.CheckedTextView | Zamówienie 5 Ostatnie zamówienia selected, Zamówienie 5 Double-tap to select | 10 |
| 14 | order_6 | android.widget.CheckedTextView | Ostatnie zamówienia selected, Zamówienie 6 Double-tap to select | 8 |
| 15 | order_7 | android.widget.CheckedTextView | Zamówienie 7 Ostatnie zamówienia selected, Zamówienie 7 Double-tap to select | 10 |
| 16 | order_8 | android.widget.CheckedTextView | Zamówienie 8 Ostatnie zamówienia selected, Zamówienie 8 Double-tap to select | 10 |
| 17 | nazw | android.widget.EditText | Nazwisko Editing, Nazwisko, Edit box, Out of list Ostatnie zamówienia Showing split keyboard Showing Gboard | 15 |
| 18 | news | android.widget.CheckBox | Zapisz na newsletter not checked, Zapisz na newsletter, Check box Showing split keyboard Showing Physical keyboard | 16 |
| 19 | szt | android.widget.EditText | Zapisz na newsletter Liczba sztuk Showing split keyboard Editing, 1, Edit box, Liczba sztuk Double-tap and hold to long press | 20 |
| 20 | komunikat | android.widget.Button | Pokaż komunikat Pokaż komunikat, Button Showing split keyboard Double-tap to activate | 11 |
| 21 | imie | android.widget.EditText | Imię Showing split keyboard Editing, Imię, Edit box Showing Gboard | 10 |
| 22 | sposob_0 | android.widget.RadioButton | Kurier selected, Kurier, Radio button, 1 of 3, In list Sposób dostawy, 3 items Showing split keyboard Showing Physical keyboard | 20 |
| 23 | sposob_1 | android.widget.RadioButton | Paczkomat not selected, Paczkomat, Radio button, 2 of 3 Double-tap to select | 12 |
| 24 | sposob_2 | android.widget.RadioButton | Odbiór osobisty not selected, Odbiór osobisty, Radio button, 3 of 3 Double-tap to select | 14 |
| 25 | anuluj | android.widget.Button | Anuluj Anuluj, Button, Out of list Sposób dostawy Double-tap to activate | 11 |
| 26 | kraj | android.widget.Spinner | Kraj Kraj, Drop down list Double-tap to change | 8 |
| 27 | faktura | android.widget.CheckBox | Wystaw fakturę not checked, Wystaw fakturę, Check box Double-tap to toggle | 11 |
| 28 | plik | android.widget.Button | Wystaw fakturę Zapisz jako plik Zapisz jako plik, Button Double-tap to activate | 12 |
| 29 | zapisz | android.widget.Button | Zapisz zamówienie Zapisz zamówienie, Button Double-tap to activate | 8 |
| 30 | lista | android.widget.ListView | Ostatnie zamówienia | 2 |
| 31 | order_2 | android.widget.CheckedTextView | Zamówienie 2 Ostatnie zamówienia selected, Zamówienie 2, In list Ostatnie zamówienia Double-tap to select | 14 |
| 32 | order_3 | android.widget.CheckedTextView | Zamówienie 3 Ostatnie zamówienia selected, Zamówienie 3 Double-tap to select | 10 |
| 33 | order_4 | android.widget.CheckedTextView | Zamówienie 4 Ostatnie zamówienia selected, Zamówienie 4 Double-tap to select | 10 |
| 34 | order_5 | android.widget.CheckedTextView | Zamówienie 5 Ostatnie zamówienia selected, Zamówienie 5 Double-tap to select | 10 |
| 35 | order_6 | android.widget.CheckedTextView | Zamówienie 6 Ostatnie zamówienia selected, Zamówienie 6 Double-tap to select | 10 |
| 36 | order_7 | android.widget.CheckedTextView | Zamówienie 7 Ostatnie zamówienia selected, Zamówienie 7 Double-tap to select | 10 |
| 37 | order_8 | android.widget.CheckedTextView | Zamówienie 8 Ostatnie zamówienia selected, Zamówienie 8 Double-tap to select | 10 |
| 38 | nazw | android.widget.EditText | Nazwisko Showing split keyboard Editing, Nazwisko, Edit box, Out of list Ostatnie zamówienia Showing Gboard | 15 |
| 39 | news | android.widget.CheckBox | Zapisz na newsletter not checked, Zapisz na newsletter, Check box Showing split keyboard Showing Physical keyboard | 16 |
| 40 | szt | android.widget.EditText | Zapisz na newsletter Liczba sztuk Showing split keyboard Editing, 1, Edit box, Liczba sztuk Double-tap and hold to long press | 20 |
| 41 | komunikat | android.widget.Button | Pokaż komunikat Showing split keyboard Pokaż komunikat, Button Double-tap to activate | 11 |
| 42 | imie | android.widget.EditText | Imię Editing, Imię, Edit box Showing split keyboard Showing Gboard | 10 |
| 43 | sposob_0 | android.widget.RadioButton | Kurier selected, Kurier, Radio button, 1 of 3, In list Sposób dostawy, 3 items Showing split keyboard Showing Physical keyboard | 20 |
| 44 | sposob_1 | android.widget.RadioButton | Paczkomat not selected, Paczkomat, Radio button, 2 of 3 Double-tap to select | 12 |
| 45 | sposob_2 | android.widget.RadioButton | Odbiór osobisty not selected, Odbiór osobisty, Radio button, 3 of 3 Double-tap to select | 14 |
| 46 | anuluj | android.widget.Button | Anuluj Anuluj, Button, Out of list Sposób dostawy Double-tap to activate | 11 |
| 47 | kraj | android.widget.Spinner | Kraj Kraj, Drop down list Double-tap to change | 8 |
| 48 | faktura | android.widget.CheckBox | Wystaw fakturę not checked, Wystaw fakturę, Check box Double-tap to toggle | 11 |
| 49 | plik | android.widget.Button | Wystaw fakturę Zapisz jako plik Zapisz jako plik, Button Double-tap to activate | 12 |
| 50 | zapisz | android.widget.Button | Zapisz zamówienie Zapisz zamówienie, Button Double-tap to activate | 8 |
| 51 | lista | android.widget.ListView | Ostatnie zamówienia | 2 |
| 52 | order_2 | android.widget.CheckedTextView | Zamówienie 2 Ostatnie zamówienia selected, Zamówienie 2, In list Ostatnie zamówienia Double-tap to select | 14 |
| 53 | order_3 | android.widget.CheckedTextView | Zamówienie 3 Ostatnie zamówienia selected, Zamówienie 3 Double-tap to select | 10 |
| 54 | order_4 | android.widget.CheckedTextView | Zamówienie 4 Ostatnie zamówienia selected, Zamówienie 4 Double-tap to select | 10 |
| 55 | order_5 | android.widget.CheckedTextView | Zamówienie 5 Ostatnie zamówienia selected, Zamówienie 5 Double-tap to select | 10 |
| 56 | order_6 | android.widget.CheckedTextView | Zamówienie 6 Ostatnie zamówienia selected, Zamówienie 6 Double-tap to select | 10 |
| 57 | order_7 | android.widget.CheckedTextView | Zamówienie 7 Ostatnie zamówienia selected, Zamówienie 7 Double-tap to select | 10 |
| 58 | order_8 | android.widget.CheckedTextView | Zamówienie 8 Ostatnie zamówienia selected, Zamówienie 8 Double-tap to select | 10 |
| 59 | nazw | android.widget.EditText | Nazwisko Editing, Nazwisko, Edit box, Out of list Ostatnie zamówienia Showing split keyboard Showing Gboard | 15 |
| 60 | news | android.widget.CheckBox | Zapisz na newsletter not checked, Zapisz na newsletter, Check box Showing split keyboard Showing Physical keyboard | 16 |
| 61 | szt | android.widget.EditText | Zapisz na newsletter Liczba sztuk Showing split keyboard Editing, 1, Edit box, Liczba sztuk Double-tap and hold to long press | 20 |
| 62 | komunikat | android.widget.Button | Pokaż komunikat Showing split keyboard Pokaż komunikat, Button Double-tap to activate | 11 |
| 63 | imie | android.widget.EditText | Imię Showing split keyboard Editing, Imię, Edit box Showing Gboard | 10 |
| 64 | sposob_0 | android.widget.RadioButton | Kurier selected, Kurier, Radio button, 1 of 3, In list Sposób dostawy, 3 items Showing split keyboard Showing Physical keyboard | 20 |
| 65 | sposob_1 | android.widget.RadioButton | Paczkomat not selected, Paczkomat, Radio button, 2 of 3 Double-tap to select | 12 |

| Cel | Pierwsze dojście od Imienia |
| --- | --- |
| imie | 0 |
| sposob_0 | 1 |
| sposob_1 | 2 |
| sposob_2 | 3 |
| anuluj | 4 |
| kraj | 5 |
| faktura | 6 |
| plik | 7 |
| zapisz | 8 |
| lista | 9 |
| order_2 | 10 |
| order_3 | 11 |
| order_4 | 12 |
| order_5 | 13 |
| order_6 | 14 |
| order_7 | 15 |
| order_8 | 16 |
| nazw | 17 |
| news | 18 |
| szt | 19 |
| komunikat | 20 |

### macos GRUPY

Źródło: [41118572905](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41118572905), plik `wyniki/macos/41118572905/macos-measure/GRUPY.json`.

| Indeks | id | Rola | Treść | Słowa |
| --- | --- | --- | --- | --- |
| 0 | imie | AXTextField | Imię edit text is in the VoiceOver cursor | 8 |
| 1 | nazw | AXTextField | Nazwisko edit text | 3 |
| 2 | sposob_0 | AXRadioButton | Leaving Dane odbiorcy. Entering Dostawa group. Kurier selected radio button | 10 |
| 3 | sposob_1 | AXRadioButton | Paczkomat radio button | 3 |
| 4 | sposob_2 | AXRadioButton | Odbiór osobisty radio button | 4 |
| 5 | kraj | AXPopUpButton | Polska Kraj pop up button | 5 |
| 6 | szt | AXTextField | 1 contents selected Liczba sztuk edit text | 7 |
| 7 | faktura | AXCheckBox | Leaving Dostawa. Entering Opcje group. Wystaw fakturę unchecked checkbox | 9 |
| 8 | news | AXCheckBox | Zapisz na newsletter unchecked checkbox | 5 |
| 9 | lista | AXTable | Entering Ostatnie zamówienia table. Ostatnie zamówienia table Row 1 of 8 Zamówienie 1 selected | 14 |
| 10 |  | AXTextField | Zamówienie 1 contents selected edit text | 6 |
| 11 |  | AXScrollBar | vertical scroll bar | 3 |
| 12 | zapisz | AXButton | Leaving Ostatnie zamówienia. Zapisz zamówienie button | 6 |
| 13 | anuluj | AXButton | Anuluj button | 2 |
| 14 | komunikat | AXButton | Pokaż komunikat button | 3 |
| 15 | plik | AXButton | Zapisz jako plik button | 4 |
| 16 | imie | AXTextField | Entering Dane odbiorcy group. Imię edit text | 7 |
| 17 | nazw | AXTextField | Nazwisko edit text | 3 |
| 18 | sposob_0 | AXRadioButton | Leaving Dane odbiorcy. Entering Dostawa group. Kurier selected radio button | 10 |
| 19 | sposob_1 | AXRadioButton | Paczkomat radio button | 3 |
| 20 | sposob_2 | AXRadioButton | Odbiór osobisty radio button | 4 |
| 21 | kraj | AXPopUpButton | Polska Kraj pop up button | 5 |
| 22 | szt | AXTextField | 1 contents selected Liczba sztuk edit text | 7 |
| 23 | faktura | AXCheckBox | Leaving Dostawa. Entering Opcje group. Wystaw fakturę unchecked checkbox | 9 |
| 24 | news | AXCheckBox | Zapisz na newsletter unchecked checkbox | 5 |
| 25 | lista | AXTable | Entering Ostatnie zamówienia table. Ostatnie zamówienia table Row 1 of 8 Zamówienie 1 selected | 14 |
| 26 |  | AXTextField | Zamówienie 1 contents selected edit text | 6 |
| 27 |  | AXScrollBar | vertical scroll bar | 3 |
| 28 | zapisz | AXButton | Leaving Ostatnie zamówienia. Zapisz zamówienie button | 6 |
| 29 | anuluj | AXButton | Anuluj button | 2 |
| 30 | komunikat | AXButton | Pokaż komunikat button | 3 |
| 31 | plik | AXButton | Zapisz jako plik button | 4 |
| 32 | imie | AXTextField | Entering Dane odbiorcy group. Imię edit text | 7 |
| 33 | nazw | AXTextField | Nazwisko edit text | 3 |
| 34 | sposob_0 | AXRadioButton | Leaving Dane odbiorcy. Entering Dostawa group. Kurier selected radio button | 10 |
| 35 | sposob_1 | AXRadioButton | Paczkomat radio button | 3 |
| 36 | sposob_2 | AXRadioButton | Odbiór osobisty radio button | 4 |
| 37 | kraj | AXPopUpButton | Polska Kraj pop up button | 5 |
| 38 | szt | AXTextField | 1 contents selected Liczba sztuk edit text | 7 |
| 39 | faktura | AXCheckBox | Leaving Dostawa. Entering Opcje group. Wystaw fakturę unchecked checkbox | 9 |
| 40 | news | AXCheckBox | Zapisz na newsletter unchecked checkbox | 5 |
| 41 | lista | AXTable | Entering Ostatnie zamówienia table. Ostatnie zamówienia table Row 1 of 8 Zamówienie 1 selected | 14 |
| 42 |  | AXTextField | Zamówienie 1 contents selected edit text | 6 |
| 43 |  | AXScrollBar | vertical scroll bar | 3 |
| 44 | zapisz | AXButton | Leaving Ostatnie zamówienia. Zapisz zamówienie button | 6 |
| 45 | anuluj | AXButton | Anuluj button | 2 |
| 46 | komunikat | AXButton | Pokaż komunikat button | 3 |
| 47 | plik | AXButton | Zapisz jako plik button | 4 |
| 48 | imie | AXTextField | Entering Dane odbiorcy group. Imię edit text | 7 |

| Cel | Pierwsze dojście od Imienia |
| --- | --- |
| imie | 0 |
| nazw | 1 |
| sposob_0 | 2 |
| sposob_1 | 3 |
| sposob_2 | 4 |
| kraj | 5 |
| szt | 6 |
| faktura | 7 |
| news | 8 |
| lista | 9 |
| zapisz | 12 |
| anuluj | 13 |
| komunikat | 14 |
| plik | 15 |

### macos PLASKI

Źródło: [41118572905](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41118572905), plik `wyniki/macos/41118572905/macos-measure/PLASKI.json`.

| Indeks | id | Rola | Treść | Słowa |
| --- | --- | --- | --- | --- |
| 0 | imie | AXTextField | Imię edit text is in the VoiceOver cursor | 8 |
| 1 | sposob_0 | AXRadioButton | Kurier selected radio button | 4 |
| 2 | sposob_1 | AXRadioButton | Paczkomat radio button | 3 |
| 3 | sposob_2 | AXRadioButton | Odbiór osobisty radio button | 4 |
| 4 | anuluj | AXButton | Anuluj button | 2 |
| 5 | kraj | AXPopUpButton | Polska Kraj pop up button | 5 |
| 6 | faktura | AXCheckBox | Wystaw fakturę unchecked checkbox | 4 |
| 7 | plik | AXButton | Zapisz jako plik button | 4 |
| 8 | zapisz | AXButton | Zapisz zamówienie button | 3 |
| 9 | lista | AXTable | Entering Ostatnie zamówienia table. Ostatnie zamówienia table Row 1 of 8 Zamówienie 1 selected | 14 |
| 10 |  | AXTextField | [brak wypowiedzi w oknie] | 0 |
| 11 |  | AXScrollBar | vertical scroll bar | 3 |
| 12 | nazw | AXTextField | Leaving Ostatnie zamówienia. Nazwisko edit text | 6 |
| 13 | news | AXCheckBox | Zapisz na newsletter unchecked checkbox | 5 |
| 14 | szt | AXTextField | 1 contents selected Liczba sztuk edit text | 7 |
| 15 | komunikat | AXButton | Pokaż komunikat button | 3 |
| 16 | imie | AXTextField | Imię edit text | 3 |
| 17 | sposob_0 | AXRadioButton | Kurier selected radio button | 4 |
| 18 | sposob_1 | AXRadioButton | Paczkomat radio button | 3 |
| 19 | sposob_2 | AXRadioButton | Odbiór osobisty radio button | 4 |
| 20 | anuluj | AXButton | Anuluj button | 2 |
| 21 | kraj | AXPopUpButton | Polska Kraj pop up button | 5 |
| 22 | faktura | AXCheckBox | Wystaw fakturę unchecked checkbox | 4 |
| 23 | plik | AXButton | Zapisz jako plik button | 4 |
| 24 | zapisz | AXButton | Zapisz zamówienie button | 3 |
| 25 | lista | AXTable | Entering Ostatnie zamówienia table. Ostatnie zamówienia table Row 1 of 8 Zamówienie 1 selected | 14 |
| 26 |  | AXTextField | Zamówienie 1 contents selected edit text | 6 |
| 27 |  | AXScrollBar | vertical scroll bar | 3 |
| 28 | nazw | AXTextField | Leaving Ostatnie zamówienia. Nazwisko edit text | 6 |
| 29 | news | AXCheckBox | Zapisz na newsletter unchecked checkbox | 5 |
| 30 | szt | AXTextField | 1 contents selected Liczba sztuk edit text | 7 |
| 31 | komunikat | AXButton | Pokaż komunikat button | 3 |
| 32 | imie | AXTextField | Imię edit text | 3 |
| 33 | sposob_0 | AXRadioButton | Kurier selected radio button | 4 |
| 34 | sposob_1 | AXRadioButton | Paczkomat radio button | 3 |
| 35 | sposob_2 | AXRadioButton | Odbiór osobisty radio button | 4 |
| 36 | anuluj | AXButton | Anuluj button | 2 |
| 37 | kraj | AXPopUpButton | Polska Kraj pop up button | 5 |
| 38 | faktura | AXCheckBox | Wystaw fakturę unchecked checkbox | 4 |
| 39 | plik | AXButton | Zapisz jako plik button | 4 |
| 40 | zapisz | AXButton | Zapisz zamówienie button | 3 |
| 41 | lista | AXTable | Entering Ostatnie zamówienia table. Ostatnie zamówienia table Row 1 of 8 Zamówienie 1 selected | 14 |
| 42 |  | AXTextField | Zamówienie 1 contents selected edit text | 6 |
| 43 |  | AXScrollBar | vertical scroll bar | 3 |
| 44 | nazw | AXTextField | Leaving Ostatnie zamówienia. Nazwisko edit text | 6 |
| 45 | news | AXCheckBox | Zapisz na newsletter unchecked checkbox | 5 |
| 46 | szt | AXTextField | 1 contents selected Liczba sztuk edit text | 7 |
| 47 | komunikat | AXButton | Pokaż komunikat button | 3 |
| 48 | imie | AXTextField | Imię edit text | 3 |

| Cel | Pierwsze dojście od Imienia |
| --- | --- |
| imie | 0 |
| sposob_0 | 1 |
| sposob_1 | 2 |
| sposob_2 | 3 |
| anuluj | 4 |
| kraj | 5 |
| faktura | 6 |
| plik | 7 |
| zapisz | 8 |
| lista | 9 |
| nazw | 12 |
| news | 13 |
| szt | 14 |
| komunikat | 15 |

### ios GRUPY

Źródło: [41117258635](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41117258635), plik `wyniki/ios/41117258635/ios-measure/attachments/F88524EB-0777-4643-AAF1-6696C3128E06.json`.

| Indeks | id | Rola | Treść | Słowa |
| --- | --- | --- | --- | --- |
| 0 | imie | textField | Imię | 1 |
| 1 | nazw | textField | Nazwisko | 1 |
| 2 | sposob_0 | button | Kurier | 1 |
| 3 | sposob_1 | button | Paczkomat | 1 |
| 4 | sposob_2 | button | Odbiór osobisty | 2 |
| 5 | kraj | button | Kraj Polska | 2 |
| 6 | szt | textField | Liczba sztuk 1 | 3 |
| 7 | faktura | cell | Wystaw fakturę 0 | 3 |
| 8 | news | cell | Zapisz na newsletter 0 | 4 |
| 9 | lista | table | Ostatnie zamówienia | 2 |
| 10 | order_1 | switch | Zamówienie 1 | 2 |
| 11 | order_2 | switch | Zamówienie 2 | 2 |
| 12 | order_3 | switch | Zamówienie 3 | 2 |
| 13 | order_4 | switch | Zamówienie 4 | 2 |
| 14 | order_5 | switch | Zamówienie 5 | 2 |
| 15 | order_6 | switch | Zamówienie 6 | 2 |
| 16 | order_7 | switch | Zamówienie 7 | 2 |
| 17 | order_8 | switch | Zamówienie 8 | 2 |
| 18 | zapisz | button | Zapisz zamówienie | 2 |
| 19 | anuluj | button | Anuluj | 1 |
| 20 | komunikat | button | Pokaż komunikat | 2 |
| 21 | plik | button | Zapisz jako plik | 3 |

| id | Etykieta | Wartość | enabled | selected | Odległość od Imienia w modelu |
| --- | --- | --- | --- | --- | --- |
| imie | Imię |  | True | False | 0 |
| nazw | Nazwisko |  | True | False | 1 |
| sposob_0 | Kurier |  | True | True | 2 |
| sposob_1 | Paczkomat |  | True | False | 3 |
| sposob_2 | Odbiór osobisty |  | True | False | 4 |
| kraj | Kraj | Polska | True | False | 5 |
| szt | Liczba sztuk | 1 | True | False | 6 |
| faktura | Wystaw fakturę | 0 | True | False | 7 |
| news | Zapisz na newsletter | 0 | True | False | 8 |
| lista | Ostatnie zamówienia |  | True | False | 9 |
| order_1 | Zamówienie 1 |  | True | False | 10 |
| order_2 | Zamówienie 2 |  | True | False | 11 |
| order_3 | Zamówienie 3 |  | True | False | 12 |
| order_4 | Zamówienie 4 |  | True | False | 13 |
| order_5 | Zamówienie 5 |  | True | False | 14 |
| order_6 | Zamówienie 6 |  | True | False | 15 |
| order_7 | Zamówienie 7 |  | True | False | 16 |
| order_8 | Zamówienie 8 |  | True | False | 17 |
| zapisz | Zapisz zamówienie |  | True | False | 18 |
| anuluj | Anuluj |  | True | False | 19 |
| komunikat | Pokaż komunikat |  | True | False | 20 |
| plik | Zapisz jako plik |  | True | False | 21 |

### ios PLASKI

Źródło: [41117258635](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41117258635), plik `wyniki/ios/41117258635/ios-measure/attachments/006D2080-C881-426B-8BEE-091EBB804023.json`.

| Indeks | id | Rola | Treść | Słowa |
| --- | --- | --- | --- | --- |
| 0 | zapisz | button | Zapisz zamówienie | 2 |
| 1 | lista | table | Ostatnie zamówienia | 2 |
| 2 | order_1 | switch | Zamówienie 1 | 2 |
| 3 | order_2 | switch | Zamówienie 2 | 2 |
| 4 | order_3 | switch | Zamówienie 3 | 2 |
| 5 | order_4 | switch | Zamówienie 4 | 2 |
| 6 | order_5 | switch | Zamówienie 5 | 2 |
| 7 | order_6 | switch | Zamówienie 6 | 2 |
| 8 | order_7 | switch | Zamówienie 7 | 2 |
| 9 | order_8 | switch | Zamówienie 8 | 2 |
| 10 | nazw | textField | Nazwisko | 1 |
| 11 | news | cell | Zapisz na newsletter 0 | 4 |
| 12 | szt | textField | Liczba sztuk 1 | 3 |
| 13 | komunikat | button | Pokaż komunikat | 2 |
| 14 | imie | textField | Imię | 1 |
| 15 | sposob_0 | button | Kurier | 1 |
| 16 | sposob_1 | button | Paczkomat | 1 |
| 17 | sposob_2 | button | Odbiór osobisty | 2 |
| 18 | anuluj | button | Anuluj | 1 |
| 19 | kraj | button | Kraj Polska | 2 |
| 20 | faktura | cell | Wystaw fakturę 0 | 3 |
| 21 | plik | button | Zapisz jako plik | 3 |

| id | Etykieta | Wartość | enabled | selected | Odległość od Imienia w modelu |
| --- | --- | --- | --- | --- | --- |
| zapisz | Zapisz zamówienie |  | True | False | 14 |
| lista | Ostatnie zamówienia |  | True | False | 13 |
| order_1 | Zamówienie 1 |  | True | False | 12 |
| order_2 | Zamówienie 2 |  | True | False | 11 |
| order_3 | Zamówienie 3 |  | True | False | 10 |
| order_4 | Zamówienie 4 |  | True | False | 9 |
| order_5 | Zamówienie 5 |  | True | False | 8 |
| order_6 | Zamówienie 6 |  | True | False | 7 |
| order_7 | Zamówienie 7 |  | True | False | 6 |
| order_8 | Zamówienie 8 |  | True | False | 5 |
| nazw | Nazwisko |  | True | False | 4 |
| news | Zapisz na newsletter | 0 | True | False | 3 |
| szt | Liczba sztuk | 1 | True | False | 2 |
| komunikat | Pokaż komunikat |  | True | False | 1 |
| imie | Imię |  | True | False | 0 |
| sposob_0 | Kurier |  | True | True | 1 |
| sposob_1 | Paczkomat |  | True | False | 2 |
| sposob_2 | Odbiór osobisty |  | True | False | 3 |
| anuluj | Anuluj |  | True | False | 4 |
| kraj | Kraj | Polska | True | False | 5 |
| faktura | Wystaw fakturę | 0 | True | False | 6 |
| plik | Zapisz jako plik |  | True | False | 7 |

## Załącznik B: ruchy kursora czytnika

Każda pozycja to wysłane polecenie, także próba na końcu grupy. Puste okno nie dowodzi braku zdolności do mówienia.

### android GRUPY: [41120875415](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41120875415)

| Numer | Polecenie | Element/fokus | Treść | Słowa |
| --- | --- | --- | --- | --- |
| 0 | anchor-hardware | imie | Editing, Imię, Edit box Double-tap and hold to long press, Proofreading is available. 1 misspelled words. Swipe down with 3 fingers and use "Proofread" to view | 26 |
| 1 | hardware-Alt-Right | imie | [brak wypowiedzi w oknie] | 0 |
| 2 | hardware-Alt-Right | imie | [brak wypowiedzi w oknie] | 0 |
| 3 | hardware-Alt-Right | imie | [brak wypowiedzi w oknie] | 0 |

### android PLASKI: [41120875415](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41120875415)

| Numer | Polecenie | Element/fokus | Treść | Słowa |
| --- | --- | --- | --- | --- |
| 0 | anchor-hardware | imie | Editing, Imię, Edit box Double-tap and hold to long press, Proofreading is available. 1 misspelled words. Swipe down with 3 fingers and use "Proofread" to view | 26 |
| 1 | hardware-Alt-Right | imie | [brak wypowiedzi w oknie] | 0 |
| 2 | hardware-Alt-Right | imie | [brak wypowiedzi w oknie] | 0 |
| 3 | hardware-Alt-Right | imie | [brak wypowiedzi w oknie] | 0 |

### macos GRUPY: [41118572905](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41118572905)

| Numer | Polecenie | Element/fokus | Treść | Słowa |
| --- | --- | --- | --- | --- |
| 0 | VO+Right | Nazwisko | Nazwisko | 1 |
| 1 | VO+Right | Nazwisko edit text | Nazwisko edit text | 3 |
| 2 | VO+Right | Nazwisko edit text | [brak wypowiedzi w oknie] | 0 |
| 3 | VO+Shift+Up | Dane odbiorcy group | Out of Dane odbiorcy group | 5 |
| 4 | VO+Right | Dostawa group | Dostawa group | 2 |
| 5 | VO+Shift+Down | Dostawa | In Dostawa group 7 items Dostawa | 6 |
| 6 | VO+Right | Kurier selected radio button | Kurier selected radio button | 4 |
| 7 | VO+Right | Paczkomat radio button | Paczkomat radio button | 3 |
| 8 | VO+Right | Odbiór osobisty radio button | Odbiór osobisty radio button | 4 |
| 9 | VO+Right | Polska Kraj pop up button | Polska Kraj pop up button | 5 |
| 10 | VO+Right | Liczba sztuk | Liczba sztuk | 2 |
| 11 | VO+Right | 1 Liczba sztuk edit text | 1 contents selected Liczba sztuk edit text | 7 |
| 12 | VO+Right | 1 Liczba sztuk edit text | [brak wypowiedzi w oknie] | 0 |
| 13 | VO+Shift+Up | Dostawa group | Out of Dostawa group | 4 |
| 14 | VO+Right | Opcje group | Opcje group | 2 |
| 15 | VO+Shift+Down | Opcje | In Opcje group 4 items Opcje | 6 |
| 16 | VO+Right | Wystaw fakturę unchecked checkbox | Wystaw fakturę unchecked checkbox | 4 |
| 17 | VO+Right | Zapisz na newsletter unchecked checkbox | Zapisz na newsletter unchecked checkbox | 5 |
| 18 | VO+Right | scroll area | Ostatnie zamówienia table Row 1 of 8 Zamówienie 1 selected | 10 |
| 19 | VO+Shift+Down | Zamówienie 1 edit text | In Ostatnie zamówienia table Row 1 of 8 Zamówienie 1 selected Zamówienie 1 | 13 |
| 20 | VO+Right | Zamówienie 2 edit text | Zamówienie 2 | 2 |
| 21 | VO+Right | Zamówienie 3 edit text | Zamówienie 3 | 2 |
| 22 | VO+Right | Zamówienie 4 edit text | Zamówienie 4 | 2 |
| 23 | VO+Right | Zamówienie 5 edit text | Zamówienie 5 | 2 |
| 24 | VO+Right | Zamówienie 6 edit text | Zamówienie 6 | 2 |
| 25 | VO+Right | Zamówienie 7 edit text | Zamówienie 7 | 2 |
| 26 | VO+Right | Zamówienie 8 edit text | Zamówienie 8 | 2 |
| 27 | VO+Right | Zamówienie 8 edit text | [brak wypowiedzi w oknie] | 0 |
| 28 | VO+Shift+Up | Ostatnie zamówienia table | Out of Ostatnie zamówienia table | 5 |
| 29 | VO+Right | Ostatnie zamówienia table | Ostatnie zamówienia table Row 8 of 8 Zamówienie 8 selected | 10 |
| 30 | VO+Shift+Down | Zamówienie 8 edit text | In Ostatnie zamówienia table Row 8 of 8 Zamówienie 8 selected Zamówienie 8 | 13 |
| 31 | VO+Right | Zamówienie 8 edit text | Zamówienie 8 | 2 |
| 32 | VO+Right | Zamówienie 8 edit text | [brak wypowiedzi w oknie] | 0 |
| 33 | VO+Shift+Up | Ostatnie zamówienia table | Out of Ostatnie zamówienia table | 5 |
| 34 | VO+Right | Ostatnie zamówienia table | Ostatnie zamówienia table Row 8 of 8 Zamówienie 8 selected | 10 |
| 35 | VO+Right | Ostatnie zamówienia table | [brak wypowiedzi w oknie] | 0 |
| 36 | VO+Shift+Up | Opcje group | Out of Opcje group | 4 |
| 37 | VO+Right | Zapisz zamówienie button | Zapisz zamówienie button | 3 |
| 38 | VO+Right | Anuluj button | Anuluj button | 2 |
| 39 | VO+Right | Pokaż komunikat button | Pokaż komunikat button | 3 |
| 40 | VO+Right | Zapisz jako plik button | Zapisz jako plik button | 4 |
| 41 | VO-top | Dane odbiorcy group | Dane odbiorcy group | 3 |
| 42 | VO-top:next | Dostawa group | Dostawa group | 2 |
| 43 | VO-top:in | Dostawa | In Dostawa group 7 items Dostawa | 6 |
| 44 | VO-top:next | Kurier selected radio button | Kurier selected radio button | 4 |
| 45 | VO-top:next | Paczkomat radio button | Paczkomat radio button | 3 |
| 46 | VO-top:next | Odbiór osobisty radio button | Odbiór osobisty radio button | 4 |
| 47 | VO-top:next | Polska Kraj pop up button | Polska Kraj pop up button | 5 |
| 48 | VO-top:next | Liczba sztuk | Liczba sztuk | 2 |
| 49 | VO-top:next | 1 Liczba sztuk edit text | 1 contents selected Liczba sztuk edit text | 7 |
| 50 | VO-top:next | 1 Liczba sztuk edit text | [brak wypowiedzi w oknie] | 0 |
| 51 | VO-top:out | Dostawa group | Out of Dostawa group | 4 |
| 52 | VO-top:next | Opcje group | Opcje group | 2 |
| 53 | VO-top:in | Opcje | In Opcje group 4 items Opcje | 6 |
| 54 | VO-top:next | Wystaw fakturę unchecked checkbox | Wystaw fakturę unchecked checkbox | 4 |
| 55 | VO-top:next | Zapisz na newsletter unchecked checkbox | Zapisz na newsletter unchecked checkbox | 5 |
| 56 | VO-top:next | Ostatnie zamówienia table | Ostatnie zamówienia table Row 8 of 8 Zamówienie 8 selected | 10 |
| 57 | VO-top:in | Zamówienie 8 edit text | In Ostatnie zamówienia table Row 8 of 8 Zamówienie 8 selected Zamówienie 8 | 13 |
| 58 | VO-top:next | Zamówienie 8 edit text | Zamówienie 8 | 2 |
| 59 | VO-top:next | Zamówienie 8 edit text | [brak wypowiedzi w oknie] | 0 |
| 60 | VO-top:out | Ostatnie zamówienia table | Out of Ostatnie zamówienia table | 5 |
| 61 | VO-top:next | Ostatnie zamówienia table | Ostatnie zamówienia table Row 8 of 8 Zamówienie 8 selected | 10 |
| 62 | VO-top:next | Ostatnie zamówienia table | [brak wypowiedzi w oknie] | 0 |
| 63 | VO-top:out | Opcje group | Out of Opcje group | 4 |
| 64 | VO-top:next | Zapisz zamówienie button | Zapisz zamówienie button | 3 |
| 65 | VO-top:next | Anuluj button | Anuluj button | 2 |
| 66 | VO-top:next | Pokaż komunikat button | Pokaż komunikat button | 3 |
| 67 | VO-top:next | Zapisz jako plik button | Zapisz jako plik button | 4 |

### macos PLASKI: [41118572905](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41118572905)

| Numer | Polecenie | Element/fokus | Treść | Słowa |
| --- | --- | --- | --- | --- |
| 0 | VO+Right | Kurier selected radio button | Kurier selected radio button | 4 |
| 1 | VO+Right | Paczkomat radio button | Paczkomat radio button | 3 |
| 2 | VO+Right | Odbiór osobisty radio button | Odbiór osobisty radio button | 4 |
| 3 | VO+Right | Anuluj button | Anuluj button | 2 |
| 4 | VO+Right | Polska Kraj pop up button | Polska Kraj pop up button | 5 |
| 5 | VO+Right | Wystaw fakturę unchecked checkbox | Wystaw fakturę unchecked checkbox | 4 |
| 6 | VO+Right | Zapisz jako plik button | Zapisz jako plik button | 4 |
| 7 | VO-top | Zapisz zamówienie button | Zapisz zamówienie button | 3 |
| 8 | VO-top:next | scroll area | Ostatnie zamówienia table Row 1 of 8 Zamówienie 1 selected | 10 |
| 9 | VO-top:in | Zamówienie 1 edit text | In Ostatnie zamówienia table Row 1 of 8 Zamówienie 1 selected Zamówienie 1 | 13 |
| 10 | VO-top:next | Zamówienie 2 edit text | Zamówienie 2 | 2 |
| 11 | VO-top:next | Zamówienie 3 edit text | Zamówienie 3 | 2 |
| 12 | VO-top:next | Zamówienie 4 edit text | Zamówienie 4 | 2 |
| 13 | VO-top:next | Zamówienie 5 edit text | Zamówienie 5 | 2 |
| 14 | VO-top:next | Zamówienie 6 edit text | Zamówienie 6 | 2 |
| 15 | VO-top:next | Zamówienie 7 edit text | Zamówienie 7 | 2 |
| 16 | VO-top:next | Zamówienie 8 edit text | Zamówienie 8 | 2 |
| 17 | VO-top:next | Zamówienie 8 edit text | [brak wypowiedzi w oknie] | 0 |
| 18 | VO-top:out | Ostatnie zamówienia table | Out of Ostatnie zamówienia table | 5 |
| 19 | VO-top:next | Nazwisko | Nazwisko | 1 |
| 20 | VO-top:next | Nazwisko edit text | Nazwisko edit text | 3 |
| 21 | VO-top:next | Zapisz na newsletter unchecked checkbox | Zapisz na newsletter unchecked checkbox | 5 |
| 22 | VO-top:next | Liczba sztuk | Liczba sztuk | 2 |
| 23 | VO-top:next | 1 Liczba sztuk edit text | 1 contents selected Liczba sztuk edit text | 7 |
| 24 | VO-top:next | Pokaż komunikat button | Pokaż komunikat button | 3 |
| 25 | VO-top:next | Imię | Imię | 1 |
| 26 | VO-top:next | Imię edit text | Imię edit text | 3 |
| 27 | VO-top:next | Kurier selected radio button | Kurier selected radio button | 4 |
| 28 | VO-top:next | Paczkomat radio button | Paczkomat radio button | 3 |
| 29 | VO-top:next | Odbiór osobisty radio button | Odbiór osobisty radio button | 4 |
| 30 | VO-top:next | Anuluj button | Anuluj button | 2 |
| 31 | VO-top:next | Polska Kraj pop up button | Polska Kraj pop up button | 5 |
| 32 | VO-top:next | Wystaw fakturę unchecked checkbox | Wystaw fakturę unchecked checkbox | 4 |
| 33 | VO-top:next | Zapisz jako plik button | Zapisz jako plik button | 4 |
