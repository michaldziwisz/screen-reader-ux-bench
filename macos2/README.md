# macOS: okno główne, pomiar 2

AppKit: NSSplitView, nazwane grupy, NSOutlineView, NSTableView z nagłówkami, NSTextView tylko do odczytu i etykieta stanu. Dane pochodzą ze wspólnego `shared2/fixture.json`. Program nie implementuje F6. Badane klawisze trafiają do domyślnej obsługi AppKit lub systemu.

```sh
gh workflow run macos2.yml
python3 scripts2/fetch.py
```

Runner i Xcode są przypięte w workflow, dokładne wersje zapisują się w artefakcie. Guidepup uruchamia żywy VoiceOver wyłącznie na izolowanym runnerze. Sonda AX pilnuje procesu pierwszego planu. Dziennik aplikacji zapisuje zaznaczenie NSTableView niezależnie od kursora czytania.

## Dwa kanały obserwacji

Nawigacja używa `capture: initial` Guidepup, jak pomiar 1. To początkowa wypowiedź, nie wszystkie opóźnione wskazówki. Rozszerzone próby odczytują równolegle `content of last phrase` VoiceOver. Każda surowa próbka ma czas, a raport podaje zauważone zmiany tekstu. Obserwacja ostatniej frazy jest **dolnym ograniczeniem** liczby wypowiedzi. Szybko zastąpiona fraza może zniknąć pomiędzy próbkami; ten kanał nie jest podsłuchem całej kolejki.

Nie wolno dodawać oczekiwania na koniec serii do callbacku `voiceOver.capture` i uważać tego za ciągły podsłuch. Guidepup 0.39.0 odpytuje po callbacku. W pomiarze 2 jest osobna pętla `sampleDuring`, która odpytuje już w trakcie wysyłania. Surowe odstępy między próbkami umożliwiają ocenę ograniczenia.

Każdy priorytet low, medium, high oraz kontrola zwykłej etykiety ma sześć serii. Przed serią odczyt fokusu zapewnia frazę inną niż ostatni komunikat poprzedniej serii. Dodatkowa kontrola wysyła pięć odrębnych ogłoszeń rozłożonych w czasie. Mowa żywego czytnika nie oznacza nagrania audio ani potwierdzenia dokończenia odtwarzania.

Archiwalny pierwszy przebieg z sondą odpytującą po serii nie jest podstawą liczby dostarczonych ogłoszeń.
