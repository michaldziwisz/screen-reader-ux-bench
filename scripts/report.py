"""Składa raport z wyliczeń, bez zastępowania braków zerami."""
import json,re,datetime
from pathlib import Path
from analyze import load,save
ROOT=Path(__file__).resolve().parents[1]

def table(headers,rows):
 def cell(x):return str(x if x is not None else "brak wyniku").replace("|","\\|").replace("\n"," ")
 return "| "+" | ".join(headers)+" |\n| "+" | ".join("---" for _ in headers)+" |\n"+"\n".join("| "+" | ".join(cell(c) for c in row)+" |" for row in rows)+"\n"
def url(rid):return f"https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/{rid}"
def link(d):return f"[{d['source']['run']}]({d['source']['url']})"
def task(d):return d.get("summary",{}).get("task",{})
def yn(v):return "tak" if v else "nie"
def dataset(platform,variant):return next(d for d in DATA if d['platform']==platform and d['variant']==variant)
DATA=load(ROOT/'results/summary.json')
RUNS=load(ROOT/'wyniki/runs.json')
assert len(RUNS)<=25
assert len(DATA)==8
for d in DATA:assert next(r for r in RUNS if str(r['databaseId'])==d['source']['run'])['status']=='completed'
versions={}
for plat in ['macos','ios','android','catalyst']:
 d=dataset(plat,'GRUPY');rid=d['source']['run'];folder=ROOT/f'wyniki/{plat}/{rid}'
 log=(folder/'workflow.log').read_text()
 image=[l.split('Z ',1)[-1] for l in log.splitlines() if 'Image:'in l or re.search(r'Z Version:',l)]
 files={p.name:p.read_text() for name in ['versions.txt','runner.txt','voiceover-plist.txt'] for p in folder.rglob(name)}
 if plat=='android':
  package=next(folder.rglob('talkback-package.txt')).read_text();prop=next(folder.rglob('properties.txt')).read_text()
  files['talkback_version']='\n'.join(l.strip() for l in package.splitlines() if 'versionName='in l or 'versionCode='in l)
  files['android_properties']='\n'.join(l for l in prop.splitlines() if any('['+k+']'in l for k in ['ro.build.version.sdk','ro.build.version.release','ro.build.fingerprint','ro.product.model']))
 versions[plat]={'source':d['source'],'runner':image,'files':files}
save(ROOT/'results/versions.json',versions)
save(ROOT/'results/runs.json',RUNS)
A,B=dataset('macos','GRUPY'),dataset('macos','PLASKI')
parts=[f'''# Pomiar czytników ekranu: Android, iOS i macOS

Data: {datetime.date.today().strftime('%d.%m.%Y')}. Publiczne repozytorium: [screen-reader-ux-bench](https://github.com/michaldziwisz/screen-reader-ux-bench). Licencja własnego kodu: MIT.

## Wynik w skrócie

Na Androidzie uruchomiono prawdziwy TalkBack i przechwycono tekst przekazywany do TTS. Na macOS uruchomiono prawdziwy VoiceOver. Na iOS uzyskano drzewo UIKit przez XCUITest, nie mowę VoiceOver. Catalyst uruchamia VoiceOver macOS nad interfejsem UIKit i nie jest pomiarem iOS.

Na macOS dojście kolejno do sześciu celów wymagało {task(A)['steps']} naciśnięć Tab w wariancie GRUPY i {task(B)['steps']} w wariancie PLASKI. Zarejestrowano odpowiednio {task(A)['words']} i {task(B)['words']} słów w oknach tych kroków. Źródło: {link(A)}. To wynik konkretnej implementacji AppKit, nie norma dla całego systemu.

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
''']
for plat in ['android','ios','macos','catalyst']:
 v=versions[plat]
 parts.append(f"### {plat}\n\nŹródło: {link(dataset(plat,'GRUPY'))}.\n\n```text\n"+'\n'.join(v['runner'])+'\n'+'\n'.join(f'{k}:\n{x}' for k,x in v['files'].items())+'\n```\n')
parts.append('''Guidepup 0.39.0, setup 0.29.3, XcodeGen 2.46.0. iOS: iPad Pro 13 cali (M4), runtime 18.5, potwierdzone `simulators.json` i logiem `xcodebuild`. Android: obraz Google Play x86_64, API 35, profil Pixel 2; ekran ustawiony przez skrypt na 1080 × 2400 i 160 dpi, aby cały formularz mieścił się bez dodatkowego przewijania. To nie jest typowy fizyczny Pixel 2. Gradle 8.11.1, AGP 8.9.2, Kotlin 2.1.20, JDK 17. Użyto TalkBack dostarczonego w obrazie; nie kopiowano jego binariów do repo.

VoiceOver: oficjalny pakiet startowy deklaruje wersję 10 i build 964.12.11. Guidepup zwraca dla procesu automatyzacji `0.0.1-VoiceOver4`. Nie są to zamienne identyfikatory. Identyfikacja wyniku wymaga także wersji macOS i obrazu runnera. Nie założono, że wcześniejszy błąd automatyzacji macOS 15 nadal blokuje pomiar: wybrany obraz rzeczywiście uruchomił mówienie i nawigację.

## Wyniki: koszt zadania i słowa
''')
rows=[]
for plat in ['android','macos','ios']:
 for var in ['GRUPY','PLASKI']:
  d=dataset(plat,var)
  if plat=='ios':c=d['bidirectional_model'];mode='model drzewa, oba kierunki';med=__import__('statistics').median(s['words'] for s in d['stops'])
  else:c=task(d);mode='mowa czytnika, Tab';med=d['cycle_words_median']
  rows.append([plat,var,mode,c.get('steps'),c.get('words'),med,link(d)])
parts.append(table(['Platforma','Wariant','Poziom i tryb','Kroki do 6 celów','Słowa na drodze','Mediana słów/przystanek','Actions'],rows))
parts.append('Mediana Androida i macOS obejmuje pierwszy pełny obieg Tab bez kotwicy startowej. Mediana iOS obejmuje wszystkie wybrane węzły. Wartości iOS opisują tekst drzewa i nie wolno porównywać ich jako kosztu słuchania z mową pozostałych systemów.\n')
for plat in ['android','macos','ios']:
 parts.append(f'### {plat}: odcinki drogi do sześciu celów\n')
 for var in ['GRUPY','PLASKI']:
  d=dataset(plat,var);c=d['bidirectional_model'] if plat=='ios' else task(d)
  parts.append(f"**{var}**, {link(d)}.\n")
  parts.append(table(['Następny cel','Kroki na odcinku','Słowa','Kierunek'],[[x['target'],x['steps'],x['words'],x.get('direction','Tab do przodu')] for x in c.get('legs',[])]))
  if not c.get('complete',True):parts.append(f"Zadanie nieukończone w zebranej sekwencji. Brakujący cel: `{c.get('missing')}`. Nie ekstrapolowano brakujących kroków.\n")
parts.append('''## Android: nawigacja TalkBack a zwykły Tab

`adb input swipe` nie zostało przyjęte jako poprawny gest „następny element” tylko dlatego, że polecenie kończyło się kodem zero. Sprawdzono zmianę fokusu dostępności. Niepowodzenie tej drogi oznacza brak pomiaru gestów dotykowych, nie brak działania TalkBack. Alternatywą był skrót Alt+Right czytnika, a osobno zwykły Tab aplikacji. Gdy frameworkowe `input keycombination` nie dawało ruchu, sprawdzano też zdarzenia klawiatury na wejściu emulatora (`adb emu event send`). Nazwa `hardware-Alt-Right` oznacza tę drugą drogę, nie fizyczne urządzenie użytkownika.
''')
for var in ['GRUPY','PLASKI']:
 d=dataset('android',var);s=d['reader_next_summary']
 parts.append(f"**{var}**, {link(d)}: swipe: {d['swipe_focus_events']} zdarzeń zmiany fokusu na {d['swipe_attempts']} prób. {d['reader_next_mode']}: {len(d['reader_next'])-1} prób, {sum(x.get('focus_event',False) for x in d['reader_next'][1:])} okien ze zdarzeniem fokusu. Koszt 6 celów w tej serii: {s['task'].get('steps')} kroków, {s['task'].get('words')} słów; `None` oznacza nieuzyskanie pełnej drogi, nie zero.\n")
parts.append("**Wynik Androida jest pomiarem Tab z działającym TalkBack, nie pomiarem gestów dotykowych.** W tej kampanii ani swipe z adb, ani Alt+Right przez framework, ani Alt+Right przez konsolę emulatora nie dały zarejestrowanego przesunięcia fokusu czytnika. `accessibility.txt` potwierdza związane usługi TalkBack i obserwatora oraz `touchExplorationEnabled=true`. Nie rozstrzygnięto, czy przyczyną bezskutecznych poleceń jest droga wstrzykiwania, mapa skrótów czy inny element konfiguracji. Nie zastąpiono tego braku modelem udającym rzeczywisty gest.\n")
parts.append('''## Zachowania i skróty
''')
parts.append(table(['Platforma','Wariant','Tak/Nie zamknięte przez Esc/Back','Skrót zapisu dał potwierdzenie','Actions'],[[p,v,yn(dataset(p,v)['dialog_closed']),yn(dataset(p,v)['shortcut_saved']),link(dataset(p,v))] for p in ['android','macos','ios'] for v in ['GRUPY','PLASKI']]))
parts.append('''Android używa Back oraz Ctrl+S; iOS i macOS używają Escape oraz Command+S. Potwierdzenie zapisu na macOS to zmiana tytułu na `UXPomiar zapisano`, na iOS wartość dostępności `Zapisano zamówienie`, a na Androidzie przechwycona zapowiedź. To nie test utworzenia pliku. Same dźwięki wypowiadanych nazw skrótów nie były uznawane za wykonanie akcji. Przycisk zapisu jako plik jest obecny w każdym formularzu, ale systemowe okna plikowe nie były osobnym pełnym scenariuszem pomiarowym.

Na macOS zwykły Tab przechodzi osobno przez wszystkie trzy przyciski opcji. W tabeli występują dodatkowo edytowalna komórka i pionowy pasek przewijania. Nie jest to identyczny model jak RadioBox i ListBox z Windows. W szeregu VoiceOver nazwane grupy wymagają wejścia i wyjścia. Zapisano także próby ruchu na granicy grupy, które nie zmieniły elementu. Nie uznano ich za przystanki nowej kontrolki.

Przejście Tabem w AppKit zapowiada wejście i wyjście z grupy. W nawigacji VO+Right występują ponadto etykiety tekstowe, np. „Nazwisko”, oddzielnie od pola „Nazwisko edit text”. Samo ustawienie etykiety dostępności kontrolki nie gwarantuje usunięcia sąsiedniego tekstu z porządku czytania. Wariant PLASKI nie zmusza VoiceOver do grupowania, ale nadal ma wszystkie koszty wynikające z pomieszanej kolejności.

W AppKit pytanie NSAlert z przyciskami Tak i Nie pozostało po Escape. Tak samo zachowało się badane pytanie UIKit na symulatorze. Android Back zamknął pytanie. Wnioski opierają się na porównaniu drzew przed i po, nie na samym powodzeniu wysłania klawisza. Żaden z dialogów Apple nie miał przycisku z rolą Anuluj.

## iOS: audyt i granice modelu

Apple stwierdza, że VoiceOver nie jest dostępny w Simulatorze. Uruchomiono `performAccessibilityAudit`, lecz procedura zapisuje problemy i pozwala testowi przejść dalej. Zielony test **nie oznacza czystego audytu dostępności**. Zrzuty ekranów potwierdzają obecność formularza i listy; nie dowodzą kolejności czytania.
''')
for var in ['GRUPY','PLASKI']:
 d=dataset('ios',var)
 parts.append(f"**{var}**: {len(d['stops'])} węzły w modelu, grupy: {', '.join(d['tree_groups']) or 'brak'}. Ruch wyłącznie do przodu: "+(f"{d['forward_task']['steps']} kroków do wszystkich celów." if d['forward_task']['complete'] else f"Nie dociera do następnego celu `{d['forward_task'].get('missing')}` bez cofnięcia lub powrotu na początek. Nie założono cyklicznych gestów.")+f" Problemy audytu ({len(d['audit_issues'])}):\n")
 for issue in d['audit_issues']:parts.append('1. '+issue+'\n')
parts.append('''## Catalyst: próba przybliżenia, nie wynik iOS

Ta sama aplikacja UIKit została zbudowana dla Mac Catalyst i udostępniła realną mowę VoiceOver macOS. Nie przyjęto jej jednak jako wiarygodnego zastępstwa zachowania VoiceOver na iPadzie. UIKit pod Catalyst ma inne role, reguły klawiatury i śledzenie fokusu. Wykryto rozbieżności między aktualnym fokusem AX a tekstem przechwyconym w tym samym krótkim oknie.
''')
for var in ['GRUPY','PLASKI']:
 d=dataset('catalyst',var)
 parts.append(f"**{var}**, {link(d)}: {len(d['stops'])-1} naciśnięć Tab; identyfikatory fokusowanych kontrolek: `{', '.join(d['focused_ids'])}`. Pustych okien rejestru mowy: {d['empty_windows']} na {len(d['stops'])} okien razem z kotwicą. Kontrola obecności znanego tekstu: {yn(d['positive'])}. Nie wyliczono na tej podstawie kosztu mowy iOS.\n")
parts.append('''## Opóźnienia

Na Androidzie zapisano różnicę między znacznikiem w logcat przed wywołaniem adb a wejściem do `onSynthesizeText`. Zawiera koszt transportu adb i wstrzyknięcia zdarzenia. Jest to diagnostyczny czas **znacznik → wejście TTS**, nie czyste opóźnienie od fizycznego gestu i nie początek dźwięku. Występowały również starsze rekordy; wartości ujemne wyłączono z poniższej statystyki.
''')
for var in ['GRUPY','PLASKI']:
 d=dataset('android',var)
 parts.append(f"{var}: mediana {d['marker_to_tts_median_ms']} ms dla {d['marker_to_tts_n']} nieujemnych wartości w serii Tab, {link(d)}.\n")
parts.append('''Pole `api_ms` na macOS obejmuje czas wykonania API Guidepup i oczekiwania biblioteki na początkową wypowiedź. Nie jest znacznikiem początku mowy. Nie podano z niego pozornie dokładnej latencji VoiceOver. Na iOS nie mierzono opóźnienia mowy, ponieważ czytnik nie działał. Czasy Windows z poniższej tabeli nie są bezpośrednio porównywalne z czasem znacznika adb.

## Porównanie z Windows

Źródło Windows: dostarczony `WZORZEC-pomiar-windows-RAPORT.md`, sekcja „Wyniki: czasy”. Nie odczytywano bieżącej maszyny Windows ani NVDA i nie publikowano prywatnych logów. Dane Windows są jedynymi liczbami tej tabeli, które nie pochodzą z Actions.
''')
rows=[['Windows, NVDA 2026.2, wx','GRUPY','mowa kolejki, Tab',8,73,9,'wzorzec'],['Windows, NVDA 2026.2, wx','PLASKI','mowa kolejki, Tab',30,208,'7,5','wzorzec']]
for p in ['android','macos','ios']:
 for v in ['GRUPY','PLASKI']:
  d=dataset(p,v);c=d['bidirectional_model'] if p=='ios' else task(d)
  rows.append([p,v,'drzewo, model obu kierunków' if p=='ios' else 'mowa czytnika, Tab',c.get('steps'),c.get('words'),'nieporównywalna' if p=='ios' else d['cycle_words_median'],link(d)])
parts.append(table(['Platforma','Wariant','Dowód i metoda','Kroki','Słowa','Mediana słów/przystanek','Źródło'],rows))
parts.append(f'''Windows: mediana opóźnienia do kolejki 32,8 ms, p90 62,4 ms, 278 pomiarów. Wzrost kosztu kroków po wymieszaniu kolejności: Windows 3,75 raza; AppKit {task(B)['steps']/task(A)['steps']:.2f} raza. Wzrost kosztu słów w AppKit: {task(B)['words']/task(A)['words']:.2f} raza. Nie przeliczono angielskich wypowiedzi ról macOS i Androida na polskie czasy syntezatorów z wzorca.

## Kontrola jakości, publikacja i historia prób

Kod jest publiczny, z licencją MIT i polskim README. Kontrola skanera przed pierwszą publikacją: sztuczny sekret w pliku poza repo został wykryty kodem 1, a skan początkowego drzewa siedmiu plików zwrócił kod 0. Wartość kontrolną usunięto przed pierwszym push. Bieżące potwierdzenie skanu i powtórzonej kontroli jest zapisane w `results/security.json`. Regexowy skan nie zastępuje przeglądu treści.

Uruchomiono {len(RUNS)} workflow, przy limicie kampanii około 25. Każdy ma timeout. Artefakty pobrano pod `wyniki/<platforma>/<id>/`; pliki `workflow.log` i `run.json` przechowują pełną historię. Wybrane wyniki końcowe zachowano w `results/`, aby nie znikły po wygaśnięciu artefaktów Actions. Sumy SHA-256 w `summary.json` odnoszą się do plików pobranych z artefaktów. Kopie JSON w `results/` mogą mieć inne formatowanie, ale są sprawdzane pod względem równości danych.

Pierwsza kontrola mowy nie wystarczała: odrzucono także zielony przebieg, w którym klawisze Tab nie zmieniały fokusu aplikacji. Brak ruchu nie został opublikowany jako tani formularz. Nieudane próby uruchomienia, błędy sterownika i rzeczywiste zachowania kontrolek są oddzielone.
''')
notes={'41116654791':'Rozpoznanie obrazów, obecności TalkBack i uruchomienia VoiceOver.','41116964774':'Bramka PID przerwała po przejściu procesu VoiceOver na pierwszy plan.','41117041338':'Ujemna kontrola TTS; usługi przerwane przez force-stop, brak DEFAULT w filtrze TTS. Wynik odrzucony.','41117258635':'Końcowy pomiar drzewa iOS; zgłoszenia audytu zapisane, nie zamaskowane werdyktem czystego audytu.','41117361067':'Zielony technicznie, lecz Tab nie przesuwał fokusu aplikacji. Odrzucony.','41117442426':'Nieudana aktywacja Catalyst przez identyfikator aplikacji w Guidepup.','41117642301':'Błąd sondy: nieobsługiwana opcja adb --activity-new-task.','41117848919':'Nieudana aktywacja AppKit przez nazwę aplikacji w Guidepup.','41117853216':'Nieudana aktywacja Catalyst przez nazwę aplikacji w Guidepup.','41118208720':'TalkBack i Tab działały. Gesty adb nie zmieniały fokusu. Seria Tab zbyt krótka do całego zadania PLASKI.','41118242572':'Prawdziwa mowa i ruch Tab; za krótka seria dla całej drogi PLASKI.','41118246911':'Catalyst bez poprawnej aktywacji nie przeszedł kontroli.','41118572905':'Końcowy pomiar AppKit.','41118577430':'Catalyst: realna mowa macOS, ale nieodpowiedni zamiennik iOS.','41119543530':'Ujemna kontrola czytnika: obserwator niegotowy, dialog zgody na powiadomienia Android Accessibility Suite zasłonił formularz.', '41120203817':'Nieuzyskana gotowość obserwatora przed pierwszym uruchomieniem świeżo zainstalowanego pakietu.', '41120875415':'Start aplikacji przed włączeniem obserwatora; kontrola kanału i nawigacja klawiaturowa.'}
parts.append(table(['Przebieg','Wynik Actions','Interpretacja'],[[f"[{r['databaseId']}]({r['url']})",r['conclusion'] or r['status'],notes.get(str(r['databaseId']),'Patrz artefakty')] for r in reversed(RUNS)]))
parts.append('''## Czego pomiar nie rozstrzyga

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
''')
for p in ['android','macos','ios']:
 for v in ['GRUPY','PLASKI']:
  d=dataset(p,v);parts.append(f"### {p} {v}\n\nŹródło: {link(d)}, plik `{d['source']['path']}`.\n")
  parts.append(table(['Indeks','id','Rola','Treść','Słowa'],[[i,s['id'],s['role'],s['text'] or '[brak wypowiedzi w oknie]',s['words']] for i,s in enumerate(d['stops'])]))
  if p=='ios':
   parts.append(table(['id','Etykieta','Wartość','enabled','selected','Odległość od Imienia w modelu'],[[s['id'],s['label'],s['value'],s['enabled'],s['selected'],d['distance_from_name'][s['id']]] for s in d['stops']]))
  else:parts.append(table(['Cel','Pierwsze dojście od Imienia'],d['summary']['first_steps'].items()))
parts.append('## Załącznik B: ruchy kursora czytnika\n\nKażda pozycja to wysłane polecenie, także próba na końcu grupy. Puste okno nie dowodzi braku zdolności do mówienia.\n')
for p in ['android','macos']:
 for v in ['GRUPY','PLASKI']:
  d=dataset(p,v);parts.append(f'### {p} {v}: {link(d)}\n')
  seq=d['reader_next'] if p=='android' else d['vo']
  parts.append(table(['Numer','Polecenie','Element/fokus','Treść','Słowa'],[[i,s.get('action',''),s.get('item',s.get('id','')),s['text'] or '[brak wypowiedzi w oknie]',s['words']] for i,s in enumerate(seq)]))
text='\n'.join(parts)
assert '/home/' not in text
(ROOT/'WYNIK.md').write_text(text)
(ROOT.parent/'RAPORT.md').write_text(text)
print(json.dumps({'report_characters':len(text),'datasets':len(DATA),'runs':len(RUNS)},ensure_ascii=False))
