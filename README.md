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

## Źródła

[Apple: testowanie dostępności](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)

[Guidepup](https://www.guidepup.dev/docs/api/class-voiceover)

[Zamknięty błąd obrazów macOS](https://github.com/actions/runner-images/issues/11257)

[Emulator Androida w Actions](https://github.com/ReactiveCircus/android-emulator-runner)

## Licencja

Własny kod: MIT. Czytniki i narzędzia zależne zachowują własne licencje. Nie są tu przechowywane ich binaria.
