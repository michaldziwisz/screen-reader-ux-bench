# Pomiar 2: okno główne na Androidzie, iOS i macOS

Data opracowania: 31.10.2026. Przedmiotem jest przeglądanie rekordów, poruszanie się po obszarach, hierarchia, tabela, pole tylko do odczytu i komunikaty dynamiczne. To rozwinięcie pomiaru formularza, nie ponowne opracowanie jego wyników.

## Co mierzono i jak

Programy korzystają ze wspólnego `shared2/fixture.json`, odtwarzającego rekordy i tekst szczegółów aplikacji Windows. Wariant NAZWA ma kolejność Nazwa, Data, Rozmiar, Stan. Wariant STAN ma kolejność Stan, Rozmiar, Data, Nazwa. Zmieniana jest kolejność prezentacji, nie dane. Ekran zawiera Narzędzia, Foldery, Pliki, Szczegóły oraz komunikaty.

Porównanie nie zakłada jednakowych implementacji. W UIKit i androidowym RecyclerView aplikacja składa etykietę rekordu wraz z nazwami pól. AppKit używa rzeczywistych kolumn NSTableView. Androidowy TableLayout ma osobne fokusowalne komórki. Różnic między tymi kontrolkami nie należy przypisywać wyłącznie czytnikowi.

### Poziomy dowodu

**Mowa żywego czytnika.** Android: tekst faktycznie przekazany przez uruchomiony TalkBack do własnego TextToSpeechService. Kontrola bezpośredniego TTS jest odrębna od kontroli TalkBack odczytującego pole Szukaj. Silnik oddaje krótki bufor ciszy. To nie nagranie, czas słuchania ani dowód dokończenia wypowiedzi. macOS: tekst żywego VoiceOver, uzyskany przez Guidepup lub bezpośrednio przez AppleScript `content of last phrase`.

**Drzewo dostępności.** Android: AccessibilityNodeInfo i zdarzenia AccessibilityService. macOS: systemowe AX, odrębnie od dziennika zaznaczenia aplikacji. iOS: snapshoty XCUITest. Dodatkowy dziennik UIKit odczytuje właściwości działających widoków, ale nie zastępuje zewnętrznego drzewa ani mowy.

**Brak pomiaru.** Dotyczy mowy VoiceOver na iOS Simulatorze, nieudanych kontroli i zachowania poza badaną konfiguracją. Nie zamieniamy braku danych na zero wypowiedzi.

Każdy krok Androida ma znacznik logcat. Dla komunikatów liczone są unikalne numery plików obecne w tekście TTS w oknie danego kroku, nie liczba wywołań API. W macOS liczymy zaobserwowane zmiany ostatniej frazy podczas wysyłania komunikatów. To dolne ograniczenie: krótka fraza zastąpiona między próbkami może nie zostać zauważona. Kontrola z odrębnymi ogłoszeniami rozłożonymi w czasie sprawdza, czy kanał potrafi w ogóle odebrać komunikaty.

Słowo oznacza fragment oddzielony białym znakiem. Daty i liczby pozostają tokenami zapisu, a nie symulacją ich wymowy. Osobno pokazujemy główną wypowiedź rekordu i cały zarejestrowany krok, jeśli zawiera wskazówki czytnika. Pozycja nazwy jest liczona od początku głównej wypowiedzi.

Koszt przejścia dotyczy rzeczywistych zmian fokusu od wskazanego punktu początkowego. Powodzenie `dispatchGesture` lub wstrzyknięcia klawisza nie jest dowodem ruchu. Zaznaczenie rekordu, fokus klawiatury i kursor czytnika są rozdzielone.

## iOS: wyniki na poziomie drzewa dostępności

Źródło: [przebieg iOS][I], artefakt `ios2-measure`. XCUITest zakończył się powodzeniem i zapisał snapshoty obu wariantów. Surowe załączniki, dzienniki UIKit, log testu i wynik xcresult zostały pobrane. Nazwy oryginalnych plików i ich skróty znajdują się w `results2/manifest.json`.

Wersje z `versions.txt`, `simulators.json` i logu testu: host macOS 15.8.2, build 24H232; Xcode 16.4, build 16F6; iOS Simulator 18.5, build 22F77; iPad Pro 13-inch (M4). VoiceOver nie działa w tej konfiguracji Simulatora. Aplikacja zapisała `voiceOverRunning=false`. [I]

### 1. Rekord i kolejność pól

Komórka `row_1` ma pełną etykietę:

> Nazwa: Faktura marzec; Data: 02.10.2026; Rozmiar: 49 KB; Stan: zsynchronizowany

W wariancie STAN:

> Stan: zsynchronizowany; Rozmiar: 49 KB; Data: 02.10.2026; Nazwa: Faktura marzec

Obie etykiety mają po 10 tokenów. Nazwa zaczyna się odpowiednio na pozycji 2 i 9. To **liczby etykiety w drzewie, nie wypowiedzi VoiceOver**. Nie dodajemy etykiety dziecka do identycznej etykiety komórki, aby nie policzyć tego samego tekstu podwójnie. Źródło: `initial`, węzeł `row_1`, w obu końcowych załącznikach XCUITest. [I]

### 2. Obszary i nagłówki

Dziennik żywych widoków potwierdza cztery elementy z trait `header`: Narzędzia, Foldery, Pliki, Szczegóły. Kontenery mają semantykę `semanticGroup`. Zewnętrzny snapshot pokazuje etykiety tytułów i kontenerów, ale zastosowany serializer XCTest nie zawiera wszystkich traitów UIKit. Dlatego informacja o trait `header` pochodzi jawnie z dziennika UIKit, a nie z udawanego odczytu VoiceOver. [I]

Nie zmierzono rotora, Tab ani kosztu dojścia do Szukaj z czytnikiem. Samo istnienie nagłówka nie dowodzi skutecznego skrótu nawigacji.

### 3. Hierarchia

W stanie początkowym snapshot zawiera Dokumenty, Zdjęcia i Muzyka. Po rozwinięciu Dokumentów pojawiają się Umowy, Faktury i Raporty. Po rozwinięciu Umów dochodzą Najem i Praca. Snapshoty `initial`, `expanded_Dokumenty` i `expanded_Umowy` mają odpowiednio 3, 6 i 8 różnych identyfikatorów folderów. Wybór Najem daje `selected=true` na komórce. [I]

Jest to działająca lista outline, nie statyczny rysunek drzewa. Nie określono jednak, jak VoiceOver wypowiada poziom, rozwinięcie ani pozycję. Zastosowany format snapshotu nie udostępnia takiej wypowiedzi.

### 4. Lista a tabela

Dane są prezentowane jako UICollectionView z etykietą całego rekordu, nie tabela nawigowana po czterech komórkach. Po dotknięciu `row_1` komórka jest zaznaczona. Łączny zbiór identyfikatorów z `initial` i `files_scrolled` obejmuje wszystkie 20 rekordów w każdym wariancie. To kontrola zawartości i przewijania, nie pomiar liczby gestów VoiceOver. [I]

### 5. Komunikaty dynamiczne

Test wykonuje zmianę zwykłej etykiety, pojedyncze `UIAccessibility.post(.announcement)` oraz sześć serii po pięć komunikatów. Końcowy dziennik każdego wariantu zawiera 32 zdarzenia `emit`: zmianę zwykłą, pojedyncze ogłoszenie i 30 wywołań w seriach. Snapshot końcowy pokazuje aktualny tekst stanu. [I]

To dowód wykonania API i zmiany drzewa. **Nie znamy liczby komunikatów wypowiedzianych przez VoiceOver ani skutków ich kolejkowania.** Nie należy wpisywać zera do porównania z Androidem i macOS.

### 6. Szczegóły tylko do odczytu

UITextView ma `isEditable=false`, `isSelectable=true`; snapshot zawiera pełny tekst szczegółów jako wartość elementu `details`. Dziennik UIKit potwierdza właściwości kontrolki. Nie zmierzono sposobu odczytu przy wejściu ani nawigacji po wierszach VoiceOver. [I]

### 7. Gesty

XCUITest rzeczywiście dotyka folderów i rekordów oraz przewija listę. Nie są to jednak gesty obsługiwane przez VoiceOver. Wyniku nie wolno przenosić na fizyczny iPhone lub iPad z włączonym czytnikiem.

## Android: wyniki z żywym TalkBack

Źródło podstawowe: [pełny pomiar Androida][A], artefakt `android2-measure`, pliki `out/NAZWA-RECYCLER.json`, `out/STAN-RECYCLER.json` i `out/NAZWA-TABLE.json`. Dodatkowy [pomiar gestów][G] zapisuje `out/GESTY-EXTRA.json`. Kontrole własnego TTS oraz TalkBack przed i po pełnym pomiarze przeszły we wszystkich trzech konfiguracjach. [A]

Wersje: Android 15, API 35, obraz `google_apis_playstore` x86_64, build `AE3A.240806.036/12592187`; TalkBack `15.0.0.639625893`, versionCode `60138361`. Metadane czytnika są angielskie, treści aplikacji polskie. To istotne przy porównywaniu liczby słów z polskim NVDA. Źródła: `properties.txt`, `talkback-package.txt` i log workflow. [A]

### 1. Rekord i kolejność pól

Główna wypowiedź dla `row_1` w wariancie NAZWA:

> Nazwa: Faktura marzec; Data: 02.10.2026; Rozmiar: 49 KB; Stan: zsynchronizowany, 2 of 20

W wariancie STAN:

> Stan: zsynchronizowany; Rozmiar: 49 KB; Data: 02.10.2026; Nazwa: Faktura marzec, 2 of 20

Każda ma 13 tokenów. Nazwa zaczyna się jako token 2 albo 9. Po dodaniu oddzielnej wskazówki „Double-tap to activate” cały zarejestrowany krok ma 16 tokenów. Źródło: `focus:row_1` w obu plikach RecyclerView. [A]

Czytany jest cały rekord, lecz nazwy pól pochodzą z etykiety złożonej przez aplikację. Nie jest to automatyczne rozpoznanie czterech kolumn przez RecyclerView. Drzewo pokazuje kolekcję o 20 wierszach i jednej kolumnie. [A]

### 2. Obszary, nagłówki i koszt dojścia

`tree-initial` potwierdza cztery nagłówki oraz cztery tytuły paneli: Narzędzia, Foldery, Pliki, Szczegóły. W TableLayout dochodzą nagłówki kolumn. Sam tytuł panelu nie jest poleceniem skoku. [A]

Dojście od fokusu klawiatury w Szczegółach do Szukaj wymagało 7 Tabów w obu wariantach RecyclerView oraz w TableLayout. Po drodze przechodzi się przez przyciski Narzędzi. Źródło: `anchor-details-route`, kolejne `details-to-search:Tab` i `state.focusId`. [A]

Nawigacja po nagłówkach **zadziałała gestami TalkBack**. Gest góra, potem dół w jednym ruchu przełączał ustawienie czytania. Po usłyszeniu „Headings” gesty w dół dały kolejno „Foldery”, „Pliki”, „Szczegóły”, „No next heading”, następnie „Narzędzia”. Zmianie mowy towarzyszyły zdarzenia fokusu dostępności. Źródło: `reading-control:headings` i `reading-headings:down`. [G]

Próba klawiaturowa Alt+H przez `adb input keycombination` nie dała potwierdzonego skoku po nagłówkach. Występowała cisza albo komunikaty o klawiaturze ekranowej. Nie jest to dowód niesprawności fizycznego skrótu TalkBack; nie powiodła się konkretna droga wstrzyknięcia. [A]

### 3. Hierarchia

Dla Dokumentów TalkBack powiedział:

> collapsed, zwinięte, Dokumenty, 1 of 3, In list, 3 items

Po rozwinięciu Dokumentów pojawiło się „Umowy, 2 of 6”, a po rozwinięciu Umów „Najem, 3 of 8” i „Praca, 4 of 8”. Liczby odnoszą się do spłaszczonej listy widocznych elementów, nie do rodzeństwa danego węzła. `collection.hierarchical` ma wartość `false`; nie ma semantycznego poziomu drzewa. Wcięcie graficzne nie wystarczyło, żeby TalkBack zapowiedział poziom. [A]

Stan jest powtórzony: angielskie „collapsed/expanded” pochodzi z obsługiwanych akcji, a polskie „zwinięte/rozwinięte” ze `stateDescription`. To niepotrzebny narzut tej implementacji. Po przebudowie listy podczas rozwijania fokus potrafił przejść na inny węzeł, na przykład z Umów na Dokumenty. Ślad pokazuje tę zmianę. Nie przedstawiamy tego drzewa jako gotowej, dobrze zachowującej fokus kontrolki produkcyjnej. [A]

### 4. RecyclerView a TableLayout

Od pierwszego rekordu RecyclerView do przycisku Dalej było 20 Tabów w obu wariantach. Od pierwszej komórki TableLayout do Dalej było 80 Tabów. W TableLayout każde pole jest osobnym przystankiem klawiatury. [A]

Istotna korekta liczenia: w NAZWA polecenie kotwiczące pierwszy rekord nie przeniosło fokusu i pozostał on w Szukaj. Nie policzono więc wszystkich 27 kroków oznaczonych przez harness jako `table-exit:Tab`. Pierwszych 7 prowadziło dopiero do `row_0`; koszt wyjścia policzono od **zaobserwowanego** wejścia do tego rekordu. W STAN kotwica od razu wskazywała `row_0`. `results2/summary.json` jawnie zapisuje `anchor_valid=false` i `pre_anchor_steps_excluded=7` dla NAZWA. [A]

Przy fokusie komórki TableLayout czytnik podawał samą wartość, na przykład „01.10.2026” lub „12 KB”, oraz wskazówkę aktywacji. Nie podał nazwy odpowiedniej kolumny. W drzewie tej kontrolki nie było `CollectionInfo` opisującego tabelę. Widoczne nagłówki nie zapewniły relacji komórka–nagłówek. [A]

Odczyt przez `ACTION_ACCESSIBILITY_FOCUS` nie zmieniał `selectedRow`, które pozostawało `-1`. Ta aplikacja wybiera rekord po aktywacji, nie po samym czytaniu. Nie należy traktować fokusu czytnika jako potwierdzenia wyboru rekordu. [A]

### 5. Komunikaty dynamiczne

Pojedyncze komunikaty regionów polite i assertive, Toast oraz Snackbar były przekazywane do TTS. Zwykła zmiana etykiety nie dała odczytu jej nowej treści. Regionów live nie wolno opisywać jako całkowitego braku zdarzeń: framework może sam generować zdarzenia zmiany tekstu. Kontrola dotyczy braku jawnego ogłoszenia i wyłączonego live region. [A]

| Mechanizm | NAZWA, numery plików w kolejnych sześciu seriach | STAN, numery plików w kolejnych sześciu seriach |
| --- | --- | --- |
| Zwykła etykieta | brak; brak; brak; brak; brak; brak | brak; brak; brak; brak; brak; brak |
| Live polite | 5; 5; 5; 5; 5; 5 | 5; 5; 5; 5; 5; 5 |
| Live assertive | 5; 5; 5; 5; 5; 5 | 5; 5; 5; 5; 5; 5 |
| Snackbar | 5; 5; 5; 5; 5; 5 | 5; 5; 5; 5; 5; 5 |

Źródło każdej komórki: `burst:<mechanizm>:<powtórzenie>`, wywołania `emit` i `phrases` w obu plikach RecyclerView. Każda seria rzeczywiście wysyłała pięć tekstów. „5” oznacza **jeden komunikat: Plik 5**, a nie pięć dostarczonych komunikatów. W badanym scenariuszu assertive nie zwiększyło liczby dostarczonych tekstów względem polite. [A]

Pierwszy pomiar Toast odrzucono jako pomiar dostarczalności. Okno 9 sekund kończyło się przed opróżnieniem kolejki. W kolejnym oknie pojawiał się „Plik 5” poprzedniej serii; spóźniony Toast trafił nawet do kroku pojedynczego Snackbar. Tych wyników nie wolno nazywać stratą komunikatów. To błąd granicy obserwacji, widoczny w znacznikach czasu. Wyniki Toast są podane osobno poniżej, z wydłużonym oknem. [A]

#### Toast po poprawieniu okna obserwacji

W [oddzielnym przebiegu Toast][T] ustawiono okno 20 sekund. We wszystkich sześciu seriach NAZWA i wszystkich sześciu seriach STAN dotarły do TTS **wszystkie komunikaty 1, 2, 3, 4, 5**, we właściwej kolejności. Ostatni pojawiał się od 10,12 do 10,59 sekundy po znaczniku kroku. Zatem wcześniejsze okno 9 sekund rzeczywiście nie mogło objąć końca kolejki. Kontrole TTS i TalkBack przed oraz po serii przeszły w obu wariantach. [T]

Źródła: `out/NAZWA-TOAST.json`, `out/STAN-TOAST.json`, kroki `burst:toast:1` do `burst:toast:6`, znaczniki `UX_TTS`. Inny komunikat systemowy w jednym oknie nie został doliczony do numerów plików. Ten wynik nie oznacza, że seryjne Toasty są dobrym sposobem raportowania postępu: dostarczenie końca tej krótkiej serii trwało ponad dziesięć sekund. [T]

### 6. Szczegóły tylko do odczytu

Przy wejściu odczytano wszystkie wiersze szczegółów, ale czytnik używał roli „Edit box” i komunikatu „Editing”. Zastosowano EditText z `keyListener=null`, czyli blokadę wpisywania z klawiatury; sonda nadal raportowała `editable=true`. Nie jest to potwierdzenie poprawnej semantyki pola tylko do odczytu i nie testowano prób zmiany wartości przez akcję dostępności. Pojawiały się też wskazówki korekty pisowni. Wynik pokazuje ograniczenie tej implementacji, nie nieuchronne zachowanie wszystkich nieedytowalnych tekstów Androida. [A]

Strzałki w dół przesuwały kursor tekstowy. Pierwszy ruch zmienił pozycję na 12 bez uchwyconej mowy, następne dały „Utworzono: 01.10.2026”, „Rozmiar: 12 KB”, „Stan: zsynchronizowany”. Akcja przejścia do następnego wiersza dała „Udostępniono: nikomu, End of field”. Potwierdzają to `details:ArrowDown`, `details:ACTION_NEXT_LINE` i pozycje zaznaczenia w stanie aplikacji. [A]

Natomiast wybranie gestami ustawienia „Lines” nie dało w tej próbie czytania kolejnych wierszy pola: pierwszy gest wyszedł do „Gotowe”. Nie utożsamiamy skutecznych strzałek lub bezpośredniej akcji dostępności ze skutecznością tej nawigacji gestowej. [G]

#### Właściwy nieedytowalny TextView

Dlatego wykonano [osobny pomiar TextView][R], który jest już domyślną implementacją Szczegółów w końcowym kodzie. W obu wariantach sonda potwierdziła `role=android.widget.TextView` i `editable=false`. Próba `ACTION_SET_TEXT` z niepustą nową treścią została odrzucona (`ok=false`), a wartość pola pozostała identyczna z danymi źródłowymi przez wszystkie kroki. To mocniejszy dowód niż samo ustawienie `keyListener=null`. [R]

Przy wejściu TalkBack mówił tylko „Szczegóły”, bez treści. Przyczyną jest nadane w tej próbie `contentDescription`, które zastępuje zwykłą prezentację tekstu TextView. Treść nie znika z drzewa, ale nie jest automatycznie czytana przy wejściu. To osobna wada nazwania kontrolki, nie utrata danych. [R]

Nawigacja po wierszach działała: po początkowym ruchu bez mowy kolejne strzałki odczytały datę, rozmiar, stan i informację o udostępnieniu. Ctrl+Home przywróciło kursor na początek, a `ACTION_NEXT_AT_MOVEMENT_GRANULARITY` z poziomem wiersza odczytało „Umowa najmu” i przesunęło kursor do pozycji 12. Źródła: `out/NAZWA-READONLY.json`, `out/STAN-READONLY.json`, kroki `readonly:*`. Kontrole czytnika przed i po pomiarze przeszły. [R]

Nie przepisano tym wynikiem wcześniejszych pomiarów Tabów ani EditText. Każdy z nich pozostaje przypisany do swojego przebiegu i commitu. Końcowy kod i prototyp użyty w pełnym przebiegu nie są w tym miejscu identyczne.

### 7. Gesty w emulatorze i tryb telefonu

`dispatchGesture` z usługi dostępności rozwiązało problem znany z pomiaru formularza. Od Szukaj kolejne gesty w prawo przeniosły fokus do nagłówka Foldery, Dokumentów i Zdjęć. Każdy udany ruch ma jednocześnie tekst TalkBack i zdarzenie fokusu dostępności. To rzeczywisty ruch, nie tylko zaakceptowanie gestu przez API. [A]

Osobna próba `UiDevice.swipe` została wykonana po głównym pomiarze. Instrumentation potwierdza wstrzyknięcie, ale ponowne uruchomienie procesu celu odłącza obserwatora. W jej logu występuje `observer=false`; brak równorzędnego dowodu zmiany fokusu czytnika. Tego wariantu nie oznaczono jako skutecznej nawigacji. Źródła: `instrumentation.txt` i `instrumentation-logcat.txt`. [A]

Gotowy `android2/measure_device.py` **nie był uruchamiany na fizycznym telefonie**. Wymaga jawnego numeru urządzenia i zgody `--confirm-settings-change`. Instaluje tylko APK zawierający aplikację, własny TTS i obserwatora. Zachowuje wcześniejsze ustawienia w `saved-settings.json`, przywraca je w `finally`, obsługuje Ctrl+C i SIGTERM, a następnie porównuje odczyt z zapisanym stanem. Osobne `--restore` pozwala odtworzyć ustawienia po awarii. Instrukcja i ostrzeżenie o zastąpieniu mowy ciszą znajdują się w `android2/README.md`. Test lokalny sprawdza składnię i obecność ścieżki przywracania, nie udaje testu telefonu.

## macOS: wyniki z żywym VoiceOver

Źródło: [końcowy pomiar macOS][M], artefakt `macos2-measure`, pliki `NAZWA.json`, `STAN.json`, `voiceover-settings.json`, `versions.txt` i `voiceover-plist.txt`. Kontrola czytnika, kontrola bezpośredniego podsłuchu oraz kontrola rozłożonych w czasie ogłoszeń przeszły w obu wariantach. [M]

Wersje: macOS 15.8.2, build 24H232; Xcode 16.4, build 16F6; VoiceOver 10, build 964.12.11; Guidepup 0.39.0. Włączona jest pełna nawigacja klawiaturowa `AppleKeyboardUIMode=3`. Głos i metadane VoiceOver są angielskie. Ustawienia czytnika zapisano, zamiast zakładać jego konfigurację. [M]

### 1. Rekord i kolejność pól

Przy zwykłej strzałce w dół NSTableView czyta cały wiersz bez nazw kolumn:

> Faktura marzec 02.10.2026 49 KB zsynchronizowany

Po przestawieniu kolumn:

> zsynchronizowany 49 KB 02.10.2026 Faktura marzec

Obie wypowiedzi mają po 6 tokenów. Nazwa zaczyna się jako token 1 albo 5. Źródło: pierwszy `table:ArrowDown` w obu wariantach. To nie ta sama wypowiedź co odczyt pojedynczej komórki po rozpoczęciu interakcji VoiceOver z tabelą. [M]

### 2. Obszary i klawisze nawigacji

Od Szczegółów do Szukaj było 7 Tabów w obu wariantach. Domyślne F6, Ctrl+F6 i Shift+F6 nie przeniosły fokusu z pola Szczegóły do innego obszaru. Każdą kombinację powtórzono trzykrotnie w każdym wariancie. Wniosek dotyczy badanego okna AppKit, nie wszystkich aplikacji macOS. [M]

Nazwane grupy są użyteczne dla VoiceOver. Ślad `areas:*` zawiera między innymi „Out of Narzędzia group”, „Foldery i pliki split group”, „Foldery group” i „Pliki group”. Nawigacja wymaga jednak odpowiedniego wejścia do grupy i wyjścia z niej; same VO+strzałki w obrębie tabeli kontynuują ruch po komórkach. Interakcja z separatorem NSSplitView zmieniała jego położenie, a nie obszar. [M]

Rotor otworzył kategorie „Window Spots” i „Content Chooser”. Nie uzyskano potwierdzonego skoku z rotora do Szukaj lub Szczegółów. Samo nadanie nazw grupom nie utworzyło sprawdzonego odpowiednika ręcznie zaprogramowanego cyklu F6 z Windows. [M]

### 3. Hierarchia NSOutlineView

Strzałka w prawo dała „row 1 expanded”; kolejne ruchy dały „Umowy”, „row 2 expanded”, „Najem” i „Praca”. Strzałka w lewo z dziecka wracała do Umów, a następna zwijała węzeł. Początkowe zapowiedzi zawierały stan rozwinięcia i w niektórych krokach numer wiersza, nie pełną formułę „poziom, n z m” znaną z Windows. [M]

Sonda AX potwierdza natywne wiersze `AXOutlineRow`, `AXDisclosing` oraz poziomy `AXDisclosureLevel` 0, 1 i 2. To dowód dostępnej semantyki drzewa. Nie twierdzimy, że VoiceOver nigdy nie wypowie poziomu: standardowy zapis nawigacji zbiera początkową wypowiedź, a nie wszystkie możliwe opóźnione wskazówki i ustawienia szczegółowości. [M]

### 4. NSTableView, nagłówki i zaznaczenie

Po rozpoczęciu interakcji z tabelą VoiceOver czyta komórki z nagłówkami, na przykład „Data 05.10.2026” i „Rozmiar 160 KB”. Ruch w dół w tej samej kolumnie może odczytać samą nową wartość. Zatem ta sama tabela daje zwięzły odczyt wiersza zwykłą strzałką i bardziej szczegółową nawigację komórkową VO+strzałkami. [M]

**W tej konfiguracji ruch pionowy VoiceOver zmieniał także zaznaczony rekord.** W dzienniku `table:VO-ArrowDown`, `table:VO-ArrowDown`, `table:VO-ArrowUp` indeks `tableSelected` zmienił się z 4 na 5, potem 6 i z powrotem 5. Są to indeksy aplikacji liczone od zera. To inne zachowanie niż zmiana samego punktu czytania NVDA w badanym ListView WinForms. Nie jest to obietnica dla wszystkich ustawień śledzenia kursora VoiceOver. [M]

Od tabeli do pola Szczegóły były 2 Taby w obu wariantach, a nie przejście przez wszystkie komórki. Źródło: `reset-table-tab`, `table-exit:Tab` i `after.focus.AXIdentifier`. [M]

### 5. Komunikaty dynamiczne i priorytety

Poprawna implementacja kieruje `NSAccessibility.announcementRequested` do głównego okna i przekazuje `priority.rawValue`. Wcześniejsze kierowanie ogłoszenia do etykiety stanu nie dało odczytu nawet pojedynczej kontroli. Dopiero po zmianie adresata zadziałała kontrola ogłoszeń. Nie wyciągamy wniosków o kolejce VoiceOver z tamtych nieudanych prób.

Pojedyncze komunikaty low, medium i high zostały zaobserwowane. Zmiana zwykłej etykiety nie spowodowała odczytu nowej treści; występujący w tym kroku tekst był wskazówką dotyczącą pola Szukaj, a nie ogłoszeniem etykiety. [M]

| Mechanizm | NAZWA, numery plików w sześciu seriach | STAN, numery plików w sześciu seriach |
| --- | --- | --- |
| Zwykła etykieta | brak; brak; brak; brak; brak; brak | brak; brak; brak; brak; brak; brak |
| Ogłoszenie low | 5; 5; 5; 5; 5; 5 | 5; 5; 5; 5; 5; 5 |
| Ogłoszenie medium | 5; 5; 5; 5; 5; 5 | 5; 5; 5; 5; 5; 5 |
| Ogłoszenie high | 5; 5; 5; 5; 5; 5 | 5; 5; 5; 5; 5; 5 |

Każda seria wysłała pięć ogłoszeń. Tabela pokazuje **zaobserwowany tekst Plik 5**, nie pięć wypowiedzi. Źródło: `burst:*`, surowe `captureResult.samples` oraz dziennik aplikacji; kontrola `positive-paced-announcements` uchwyciła wszystkie pięć różnych tekstów rozłożonych w czasie. [M]

Priorytet nie zmienił zaobserwowanego wyniku tej serii. Nie dowiedziono jednak, że VoiceOver nigdy nie zaczął żadnej wcześniejszej wypowiedzi. Odpytywany jest ostatni tekst, nie pełna kolejka mowy. Największy odstęp próbek w seriach wyniósł po zaokrągleniu 292 ms dla NAZWA i 433 ms dla STAN; krótsze zdarzenie mogło znaleźć się pomiędzy próbkami. Nie należy porównywać tych liczb jeden do jednego z podsłuchem kolejki NVDA. [M]

### 6. Szczegóły tylko do odczytu

Przy wejściu pojawiała się zapowiedź „Szczegóły text Umowa najmu”. W badanej sekwencji kursor tekstowy był już na końcu, z zaznaczeniem `[92, 0]`. Strzałka w dół dawała „end of text Udostępniono: nikomu”, zamiast przejścia do drugiego wiersza. Command+strzałka w górę ustawiło `[0, 0]`; następna strzałka w dół dała „Utworzono: 01.10.2026” i pozycję `[12, 0]`. [M]

Pole jest dostępne do czytania i ma nawigowalny kursor mimo braku edycji. Nie wolno jednak zakładać, że przy wejściu kursor jest na początku. Tu nie stwierdzono zaznaczenia całej treści jak w początkowym zachowaniu WinForms: długość zaznaczenia wynosiła zero. To podobny problem użytkowy z innym stanem kontrolki.

### 7. Gesty

Nie mierzono gestów gładzika VoiceOver. Wyniki macOS dotyczą klawiatury, poleceń VoiceOver i systemowego drzewa AX. Nie przenosimy na macOS rezultatu androidowego `dispatchGesture`.

## Porównanie z pomiarem Windows

Kolumna Windows pochodzi z dostarczonego raportu `pomiar-nvda-widoki-2026-10-30/RAPORT.md`, z części WinForms: NVDA 2026.2, Windows 11 25H2, .NET Framework 4.8.1. To lokalny pomiar kolejki NVDA, bez przebiegu GitHub Actions. Nie dopisano mu fikcyjnego adresu CI i nie wykonywano go ponownie. Pozostałe kolumny mają źródła w [A], [G], [M], [I], [T] i [R]. Koszty Tabów Androida odnoszą się do pełnego przebiegu [A], a dodatkowy wynik nieedytowalnego tekstu do [R].

| Temat | Windows, WinForms i NVDA | Android i TalkBack | macOS i VoiceOver | iOS Simulator |
| --- | --- | --- | --- | --- |
| Rekord „Faktura marzec” | 12 słów; wszystkie pola; pierwsza kolumna bez nazwy | 13 tokenów głównej wypowiedzi, 16 ze wskazówką; etykieta z nazwami pól jest składana przez aplikację | 6 tokenów przy zwykłej strzałce; cały wiersz bez nazw kolumn | 10 tokenów etykiety; brak pomiaru mowy |
| Początek identyfikatora, NAZWA / STAN | token 1 / 8 | token 2 / 9 | token 1 / 5 | token 2 / 9 w etykiecie |
| Szczegóły → Szukaj, Tab | 7 | 7 | 7 | brak pomiaru |
| Szybka nawigacja obszarów | F6 działa dopiero po zaprogramowaniu; wtedy 1 krok | działające gesty po nagłówkach; sam pane title nie jest skrótem | nazwane grupy działają, F6 bez skoku, rotor bez potwierdzonej drogi | nagłówki i kontenery w strukturze, bez testu VoiceOver |
| Wyjście z dużej siatki | DataGridView: 80 Tabów; z StandardTab: 1 | TableLayout: 80; RecyclerView: 20 od pierwszego rekordu | NSTableView: 2 do Szczegółów | brak pomiaru |
| Czytany rekord a zaznaczenie | Polecenia tabelowe NVDA przesuwają sam punkt czytania | Sam fokus dostępności nie wybiera rekordu | Pionowy ruch VO w tabeli zmieniał zaznaczenie w badanych ustawieniach | Zaznaczenie po dotknięciu potwierdzone; brak czytnika |
| Hierarchia | Poziom, rozwinięcie i pozycja w zapowiedzi | Stan i pozycja spłaszczonej listy; brak semantycznego poziomu | Stan w mowie; poziom w AX; brak pełnej formuły w początkowym odczycie | Rozwijanie i dzieci w snapshotach |
| Seria pięciu komunikatów | Do kolejki docierały 3 albo 4, bez numeru 3 | Live polite i assertive: tylko numer 5 na wejściu TTS | W ostatniej frazie zaobserwowano tylko numer 5; dolne ograniczenie | Tylko fakt wywołania API |
| Szczegóły tylko do odczytu | Pierwsze zaznaczenie całej treści i skok na koniec | EditText: rola edycji; TextView: sama nazwa przy wejściu; wiersze dostępne dalszą nawigacją | Początkowa zapowiedź nie gwarantuje pozycji kursora; w sekwencji był na końcu | Wartość i właściwości pola, bez mowy |

Raport Windows ma również odrębną część WPF. Nie utożsamiamy jej z powyższą kolumną WinForms: WPF czytał przy zwykłej strzałce tylko tekst rekordu, wymagał `IsReadOnlyCaretVisible=true` do czytania wierszy szczegółów, a do kolejki jego powiadomień trafiały najczęściej inne fragmenty serii. To dodatkowy argument, żeby porównywać konkretne kontrolki i konfiguracje, nie samą nazwę systemu.

Nie jest to ranking szybkości platform. Inne są kontrolki, język metadanych, ustawienia czytnika oraz punkt obserwacji mowy. Porównanie wskazuje za to, których założeń nie wolno przenosić między frameworkami.

## Co się nie udało i dlaczego

**Pozornie zielony iOS.** [41141871978](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41141871978) zawiera w `test.log` błąd kompilacji konfliktującej właściwości `children`, mimo zielonego statusu. Potok z `tee` nie propagował błędu. Naprawiono nazwę i ustawiono shell bash z pipefail w nowych workflow. Za dowód uznano dopiero rzeczywiście wykonany test [I], nie kolor poprzedniego przebiegu.

**Bramka okna Androida.** [41141735151](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41141735151) przerwał się komunikatem `Foreground gate: []`. Użyty wariant `dumpsys window windows` nie dostarczył oczekiwanej sekcji. Zmieniono go na pełne `dumpsys window`. Próby do miejsca błędu pozostały w artefakcie, ale nie udają pełnego pomiaru.

**Start obserwatora Androida.** [41142646520](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41142646520) zakończył się `RuntimeError: Observer not ready`. Dodano oczekiwanie na zimny start Activity i ograniczoną próbę ponownego związania usługi na emulatorze.

**Awaria sondy po dojściu do przycisku.** W [41143137886](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41143137886) po Tabie do Nowy zniknął poprawny stan aplikacji, a log zawiera „UXPomiar2 keeps stopping”. Kod sondy wywoływał `getResourceEntryName` również dla widoków bez ID. Zabezpieczono odczyt i nadano identyfikatory przyciskom. Dawny filtr nie zachował pełnego stosu AndroidRuntime, więc diagnoza opiera się na stanie, kodzie i skutecznym przebiegu po poprawce, a nie na nieistniejącym zrzucie stosu. Później rozszerzono też zapis błędów runtime.

**Pozorne zero w podsłuchu VoiceOver.** [41141515040](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41141515040) anulowano po wykryciu, że odpytywanie po zakończeniu callbacku nie obejmuje serii. [41142176613](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41142176613) był zielony, ale publiczne `lastSpokenPhrase()` Guidepup odczytywało własną pamięć, nie aktualny stan VoiceOver. Puste próbki odrzucono. Finalny kod korzysta bezpośrednio z AppleScript i ma kontrolę tego kanału.

**Niewłaściwy adresat ogłoszenia AppKit.** W [41143778670](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41143778670) i [41143989501](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41143989501) bezpośredni kanał widział mowę nawigacji, ale ogłoszenia kierowane do etykiety stanu nie były obserwowane, także w kontroli. Zmiana adresata na główne okno dała poprawny wynik [M]. Dane wcześniejszych serii nie są podstawą twierdzenia, że VoiceOver gubi wszystkie ogłoszenia.

**Rozmiar okna i stan po nawigacji.** Kontrola zrzutów macOS ujawniła, że wcześniejsze okno wychodziło poza ekran runnera. Zmniejszono je przed końcowym pomiarem. Końcowy zrzut nadal nie jest wzorcem wyglądu produkcyjnego: panel napisów VoiceOver zasłania fragment szczegółów, a interakcja z separatorem zmienia szerokości. Wnioski o pełnej treści opierają się na mowie i AX, nie na domyśleniu tekstu z obrazu.

**Za krótka obserwacja Toast.** W [A] komunikaty przechodziły do następnych okien pomiaru. Tę część wyłączono z zestawienia w `sources.json`. Oddzielny pomiar Toast zastępuje tylko tę część, nie przepisywał pozostałych wyników.

## Czego pomiar nie rozstrzyga

Nie mierzy komfortu długiej pracy, czasu namysłu, znajomości skrótów ani zachowania innych wersji czytników. Nie mierzy dokończenia odtwarzania mowy. Nie daje wyników VoiceOver na fizycznym urządzeniu iOS ani TalkBack na telefonie Michała.

Nie ustala ogólnej polityki wszystkich priorytetów w każdej sytuacji. Serie wysyłano z badanego okna, bez osobnego scenariusza intensywnej mowy użytkownika w tle. Wynik ostatniej frazy VoiceOver pozostaje dolnym ograniczeniem, mimo dodatnich kontroli.

Androidowe drzewo jest świadomie prostą implementacją RecyclerView, bez poprawnej semantyki głębokości i bez stabilnego zachowania fokusu przy przebudowie. TableLayout ma jawnie fokusowalne komórki. Te wyniki pokazują koszt takich decyzji, nie nieuchronną właściwość każdej aplikacji Androida.

Na iOS nie dowiedziono, że sam trait header lub semanticGroup zapewni intuicyjną nawigację VoiceOver. Na macOS nie sprawdzono alternatywnych ustawień śledzenia kursora. Na żadnej platformie zrzut drzewa nie został przedstawiony jako równoważnik testu żywego czytnika.

## Wnioski praktyczne

1. Identyfikator rekordu warto umieścić na początku. Liczba słów może się nie zmienić, a nazwa i tak pojawi się dużo później.
2. Nazwa grupy, nagłówek i skrót przejścia między obszarami to odrębne mechanizmy. Trzeba mierzyć rzeczywistą drogę, zamiast zakładać, że jeden zastępuje pozostałe.
3. Widoczna tabela nie musi mieć relacji nagłówków i komórek w dostępności. Osobny fokus każdej komórki może stworzyć długą drogę Tabem.
4. Fokus czytnika nie jest uniwersalnym odpowiednikiem zaznaczenia rekordu. Trzeba mierzyć oba stany w danym frameworku i konfiguracji.
5. Serii komunikatów nie należy traktować jak niezawodnego dziennika. Przy raportowaniu postępu bezpieczniejszy jest aktualny stan i komunikat zbiorczy, a szczegóły powinny pozostać dostępne do ponownego odczytu.
6. Pole tylko do odczytu nadal wymaga sensownej roli, pozycji kursora i sprawdzonej nawigacji tekstowej. Wyłączenie edycji nie wystarcza.
7. Nieudany `adb swipe` nie dowodzi braku możliwości automatycznego testu gestów TalkBack. Tutaj zadziałała inna droga wstrzyknięcia z niezależnym dowodem fokusu i mowy.

## Przebiegi, artefakty i kontrola odbioru

Łącznie uruchomiono 15 przebiegów, poniżej limitu około 30. GitHub podaje 10 zakończeń `success`, 3 `failure` i 2 `cancelled`. Kolor nie jest kryterium ważności pomiaru: pozornie zielony iOS oraz nieskuteczne kontrole ogłoszeń macOS zostały odrzucone. Metadane całej kampanii są zapisane w `results2/campaign.json`, a logi i artefakty pobrano poleceniem `gh run download` przez `scripts2/fetch.py`.

| Przebieg | Workflow | Stan GitHub | Zastosowanie |
| --- | --- | --- | --- |
| [41145131192](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41145131192) | macos2.yml | success | macOS: końcowa nawigacja i ogłoszenia |
| [41143989501](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41143989501) | macos2.yml | success | Nie jest źródłem końcowych liczb |
| [41143778670](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41143778670) | macos2.yml | success | Nie jest źródłem końcowych liczb |
| [41142176613](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41142176613) | macos2.yml | success | Nie jest źródłem końcowych liczb |
| [41141515040](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41141515040) | macos2.yml | cancelled | Nie jest źródłem końcowych liczb |
| [41147107630](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41147107630) | android2.yml | success | Android: nieedytowalny TextView |
| [41147056109](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41147056109) | android2.yml | cancelled | Nie jest źródłem końcowych liczb |
| [41146425924](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41146425924) | android2.yml | success | Android: izolowane serie Toast |
| [41144225222](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41144225222) | android2.yml | success | Android: pełny pomiar, bez serii Toast |
| [41143137886](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41143137886) | android2.yml | failure | Nie jest źródłem końcowych liczb |
| [41142719171](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41142719171) | android2.yml | success | Android: gesty i nagłówki |
| [41142646520](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41142646520) | android2.yml | failure | Nie jest źródłem końcowych liczb |
| [41141735151](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41141735151) | android2.yml | failure | Nie jest źródłem końcowych liczb |
| [41142135669](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41142135669) | ios2.yml | success | iOS: drzewo i dziennik UIKit |
| [41141871978](https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41141871978) | ios2.yml | success | Nie jest źródłem końcowych liczb |

Przebieg `41147056109` anulowano przed uzyskaniem wyników po wykryciu lokalnym kontroli kodu błędnych wywołań pomocniczych sondy readonly. Poprawiony przebieg [R] zakończył rzeczywisty pomiar. Ten błąd nie stał się rzekomym wynikiem dostępności; dodano test wywołań sterownika.

Do końcowych obliczeń służy 14 projekcji źródłowych z 6 przyjętych przebiegów. `results2/manifest.json` zawiera URL przebiegu, commit, ścieżkę oryginału, SHA-256 oryginału i SHA-256 projekcji. `results2/summary.json` jest przeliczanym zestawieniem. Projekcje usuwają powtarzany dziennik macOS, zachowują zmiany próbek i statystyki odstępów. W Androidzie zachowano też zdarzenia TTS ze znacznikami czasu. Pełne, nieprzetworzone pliki są w artefaktach Actions oraz lokalnym `repo/wyniki/campaign2/`.

Kontrola lokalna obejmuje zgodność projekcji z oryginałami, kompletność sześciu powtórzeń i pięciu emisji w serii, dodatnie kontrole czytników, liczby słów, drogi fokusu i flagę braku VoiceOver na iOS. Testy obejmują również odrzucenie zmienionego hasha, brakującego powtórzenia i brakującej emisji nawet po przeliczeniu hasha. Analiza skryptu telefonu nie uruchamia go.

```sh
python3 scripts2/fetch.py
python3 scripts2/curate.py --verify
python3 scripts2/verify_results.py
python3 -m unittest discover -s scripts2 -p 'test_*.py' -v
node --check macos2/measure.mjs
python3 scripts2/publish_check.py
```

Skan przed publikacją ma dodatnią kontrolę wykrywania sekretu. Porównanie z bazą `d7b8429` obejmuje 52 chronione pliki pomiaru 1, bez zmian. Oddzielne katalogi aplikacji i workflow nie zmieniają pomiaru formularza. Nie uruchamiano skryptu na fizycznym telefonie, nie sterowano Windows Garfielda ani NVDA.

[A]: https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41144225222
[G]: https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41142719171
[M]: https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41145131192
[T]: https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41146425924
[R]: https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41147107630
[I]: https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/41142135669
