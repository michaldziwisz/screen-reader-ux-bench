# Android: okno główne, pomiar 2

Aplikacja wykorzystuje RecyclerView z rekordem jako jednym węzłem oraz porównawczy TableLayout z osobnymi fokusowalnymi komórkami. Oba warianty mają te same dane z `shared2/fixture.json`. `NAZWA` to Nazwa, Data, Rozmiar, Stan; `STAN` to Stan, Rozmiar, Data, Nazwa.

Drzewo jest implementacją w RecyclerView. Wcięcie wizualne nie staje się automatycznie poziomem dostępności. Węzły mają stan rozwinięcia i akcje expand/collapse, ale nie dopisano słowa „poziom” do etykiety. Wynik trzeba odczytać z TalkBack, nie wywnioskować z kodu. Nagłówki używają `accessibilityHeading`, kontenery `accessibilityPaneTitle`.

## Emulator CI

```sh
gh workflow run android2.yml
python3 scripts2/fetch.py
```

Sonda wymaga `CI=true` oraz emulatora, nie dotyka Windows ani czytnika na hoście. Próbuje `dispatchGesture`, skrótu nawigacji nagłówkowej oraz UiDevice.swipe z Instrumentation. Ta ostatnia próba jest na końcu, ponieważ Instrumentation może ponownie uruchomić proces pakietu. Kod powodzenia gestu jest tylko informacją o wstrzyknięciu. Dowodem nawigacji jest zmiana fokusu dostępności i mowa. `ACTION_ACCESSIBILITY_FOCUS` stanowi kontrolę, nie zastępuje gestu użytkownika.

Każdy krok ma znacznik w logcat. Liczone są wyłącznie wpisy po znaczniku. Mowa to tekst na wejściu własnego `TextToSpeechService`, po którym silnik oddaje krótki bufor ciszy. Nie jest to nagranie, czas słuchania ani dowód dokończenia wypowiedzi.

Każdy mechanizm komunikatu ma pojedynczą próbę oraz serię wysyłaną w jednej pętli głównego wątku, powtórzoną sześciokrotnie. Okno serii trwa dziewięć sekund. Zwykła etykieta nie ma regionu live ani jawnego zdarzenia ogłoszenia; system nadal może sam wysłać zdarzenie zmiany tekstu. Nie wolno utożsamiać braku jawnego wywołania aplikacji z brakiem jakichkolwiek zdarzeń frameworka. Toast i Snackbar mają własne reguły kolejkowania oraz zastępowania, odmienne od regionów live.

## Telefon fizyczny: przygotowane, nieuruchomione

Skrypt `measure_device.py` nie został uruchomiony na fizycznym urządzeniu. Michał podłączy telefon później. Potrzebne są adb w WSL, autoryzowane debugowanie USB, Android API 30 lub nowszy, zainstalowany TalkBack i APK z artefaktu `android2-measure`. APK zawiera aplikację, własny silnik TTS i obserwatora. Skrypt nie instaluje innych pakietów, nie instaluje TalkBack ani test APK.

**Uwaga: podczas pomiaru dotychczasowa mowa telefonu zostanie zastąpiona ciszą testowego silnika.** Należy mieć dostęp do terminala WSL i zachować plik przywracania. To celowa zmiana po jawnej zgodzie. Nie należy uruchamiać pomiaru podczas pracy z prywatnymi dokumentami lub wiadomościami. Logi telefonu pozostają lokalnie i nie należy ich publikować bez przeglądu.

1. Sprawdź identyfikator przez `adb devices`.
2. Pobierz APK z zakończonego workflow. Wstaw rzeczywisty numer przebiegu oraz identyfikator telefonu w poniższe komendy.
3. Odblokuj ekran telefonu. Uruchom skrypt, podając jawnie `--confirm-settings-change`.
4. Po automatycznej części wykonaj fizyczne gesty według komunikatów w terminalu. Enter kończy okno próby już po wykonaniu gestu na telefonie.

```sh
gh run download NUMER_PRZEBIEGU -R michaldziwisz/screen-reader-ux-bench -n android2-measure -D wyniki/telefon-apk
python3 android2/measure_device.py --serial IDENTYFIKATOR --apk wyniki/telefon-apk/android2/app/build/outputs/apk/debug/app-debug.apk --output wyniki/telefon-pomiar-2 --confirm-settings-change
```

Należy sprawdzić faktyczne położenie `app-debug.apk` w pobranym artefakcie. Skrypt przed zmianami zapisuje `saved-settings.json`, nie nadpisuje poprzedniej kopii i w `finally` przywraca silnik TTS, ustawienie języka, listę usług i flagę dostępności. Po przywróceniu porównuje wartości z oryginałem w `restoration.json`. Krótkie ponowne związanie TalkBack jest częścią przywracania starego TTS. Inne usługi dostępności pozostają zachowane. Ctrl+C i SIGTERM także przechodzą przez przywracanie; odłączenie telefonu, zabicie procesu bez obsługi i utrata zasilania mogą je przerwać.

Po takiej awarii, po ponownym podłączeniu tego samego telefonu:

```sh
python3 android2/measure_device.py --serial IDENTYFIKATOR --output wyniki/telefon-pomiar-2 --restore wyniki/telefon-pomiar-2/saved-settings.json
```

Ostateczną kontrolą jest też powrót słyszalnej mowy poprzedniego silnika. Można następnie samodzielnie odinstalować `org.uxbench2`. Nie należy usuwać APK przed przywróceniem ustawień. Wyniki fizyczne nie zostały domieszane do raportu CI.
