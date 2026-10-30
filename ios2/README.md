# iOS: drzewo dostępności okna głównego

UIKit i UICollectionView z listą outline. Kontenery są oznaczone jako semanticGroup, tytuły mają trait header. Lista rekordów prezentuje jawnie nazwy czterech pól. NSTextView nie jest tu używane: szczegóły są natywnym UITextView z `isEditable=false` i `isSelectable=true`.

```sh
gh workflow run ios2.yml
python3 scripts2/fetch.py
```

XCUITest zapisuje rzeczywiste snapshoty, stan po rozwinięciu Dokumenty i Umowy oraz po wyborze Najem i rekordu. Surowe właściwości UIKit, w tym trait header i typ kontenera, są osobnym dziennikiem aplikacji w `app-runtime`. Nie wolno nazywać tego drugiego źródła drzewem systemowego czytnika: opisuje właściwości ustawione i odczytane z żywych widoków. Zewnętrzny snapshot XCTest jest podstawowym dowodem drzewa dostępności.

**VoiceOver nie działa w iOS Simulatorze.** `UIAccessibility.post(.announcement)` rejestruje się jedynie jako fakt wykonania wywołania. Sześć serii po pięć ogłoszeń nie dostarcza liczby usłyszanych komunikatów. Zerowa wartość `voiceOverRunning` nie jest liczbą wypowiedzi.

Zielony workflow musi mieć uruchomiony test i załączniki. Brak testu lub pusty manifest artefaktów oznacza nieudany pomiar, nawet jeżeli sam potok shell zwrócił kod zero.
