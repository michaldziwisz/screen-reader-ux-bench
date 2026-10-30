# Koszt nawigacji czytnikiem ekranu

Laboratorium porównujące formularz uporządkowany w nazwanych grupach z identycznym formularzem w kolejności chaotycznej. Pomiar obejmuje Androida, iOS i macOS. Kod i dane testowe są syntetyczne. Nie są pobierane dane z urządzeń użytkowników.

## Poziomy dowodu

1. Mowa żywego czytnika: treść przekazana do silnika TTS albo zarejestrowana przez VoiceOver.
2. Drzewo dostępności: etykieta, rola, wartość i stan. To nie jest zapis mowy ani dowód kolejności gestów VoiceOver.
3. Brak pomiaru: błąd wykonania lub brak pozytywnej kontroli kanału pomiarowego.

Na iOS używany jest drugi poziom. Apple wyraźnie wyklucza VoiceOver w symulatorze.

## Metoda

Cele zadania: Imię, Nazwisko, Kraj, Liczba sztuk, Wystaw fakturę, Zapisz zamówienie. Mierzona jest nawigacja, nie czas pisania ani decyzji człowieka. Kierunek podstawowy: następny element. Przejście przez koniec formularza musi być osobno odnotowane, nie domyślnie uznane za gest cykliczny.

Android wykorzystuje natywne widoki Kotlin, iOS UIKit, macOS AppKit. Ułatwia to rozróżnienie zachowania systemowych kontrolek od semantyki dodatkowego frameworka.

Workflow uruchamia się wyłącznie ręcznie. Każdy job ma limit czasu. Nie są używane płatne większe runnery. Wyniki surowe są artefaktami Actions, lokalny katalog `wyniki` jest wyłączony z Git.

## Odtworzenie

```sh
git clone https://github.com/michaldziwisz/screen-reader-ux-bench.git
cd screen-reader-ux-bench
gh workflow run android.yml
gh workflow run ios.yml
gh workflow run macos.yml
# Opcjonalnie: eksperyment, NIE pomiar VoiceOver na iOS.
gh workflow run catalyst.yml
python3 scripts/fetch_runs.py
python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

Wymagane są uprawnienia do uruchamiania Actions. W obcym koncie należy użyć własnego forka. Skrypt pobierający wyniki odmawia zaakceptowania historii przekraczającej budżet tej kampanii. Nie uruchamia się kolejnych workflow automatycznie.

Android: Ubuntu 24.04, API 35, obraz Google Play x86_64, profil Pixel 2, Gradle 8.11.1, JDK 17. Testowy silnik TTS zapisuje tekst, po czym zwraca krótką ciszę. Usługa obserwatora czyta drzewo, ale nie wytwarza wypowiedzi TalkBack. Zmiana rozmiaru ekranu emulatora jest zapisana w skrypcie. Skrypt wymaga `CI` i emulatora, nie jest przeznaczony do urządzeń osobistych.

Apple: runner `macos-15`, Xcode 16.4. Dla iOS wybrano iPad Pro 13 cali (M4), iOS 18.5. Etykieta runnera nie jest niezmiennym obrazem dysku: dokładna wersja obrazu i systemu jest zapisana w artefaktach. Guidepup 0.39.0, setup 0.29.3 i XcodeGen 2.46.0 są przypięte.

Warianty noszą nazwy `GRUPY` i `PLASKI`. Zmieniają jednocześnie grupowanie i kolejność, więc pomiar nie izoluje samego wpływu nazw grup. Każda platforma wykorzystuje własne kontrolki. Na przykład UIKit nie ma natywnego przycisku opcji i używa przycisków z cechą zaznaczenia. Wyniki nie służą do rankingu systemów operacyjnych.

`results/` zawiera wybrany wynik końcowy i materiał źródłowy z publicznych runnerów. `WYNIK.md` opisuje liczby i ograniczenia. Cała historia prób oraz zrzuty ekranów pozostają w artefaktach Actions, a po pobraniu w ignorowanym katalogu `wyniki/`. Zielony workflow oznacza wykonanie skryptu, nie brak błędów dostępności. Audyt XCTest zapisuje wykryte problemy zamiast celowo przerywać pomiar.

## Bezpieczeństwo publikacji

Przed publikacją wykonywany jest `python3 scripts/scan_public.py`. Skaner szuka form kluczy, sekretów i prywatnej ścieżki, nie wypisuje wartości dopasowania. Pozytywna próba skanera została przeprowadzona przed utworzeniem repo, w pliku poza repo. W repo nie ma binariów czytników ani wyników mowy z urządzeń użytkownika. Regexowy skan nie jest gwarancją wykrycia każdego możliwego sekretu.

## Źródła

[Apple: testowanie dostępności](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)

[Guidepup](https://www.guidepup.dev/docs/api/class-voiceover)

[Zamknięty błąd obrazów macOS](https://github.com/actions/runner-images/issues/11257)

[Emulator Androida w Actions](https://github.com/ReactiveCircus/android-emulator-runner)

## Licencja

Własny kod: MIT. Czytniki i narzędzia zależne zachowują własne licencje. Nie są tu przechowywane ich binaria.
