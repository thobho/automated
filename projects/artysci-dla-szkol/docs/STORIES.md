# Approved stories: Artyści dla szkół

> Recovered on 2026-11-17 from the owner's planning session of 2026-11-11. Each section below is the
> text the owner approved, verbatim and in Polish, including acceptance criteria ("Kryteria
> akceptacji", Given/When/Then style) and the decisions taken with it.
>
> How to use it:
> - Find a story by its id (e.g. `US-2.5`). The roadmap may split a large story into parts
>   (`US-2.5a`, `US-2.5b`); each part takes the matching subset of that story's criteria.
> - [DECISIONS.md](DECISIONS.md) wins over this file when they differ. In particular: hosting is
>   undecided (D91), so ignore AWS/EC2-specific details in E0, E3 and E7 until E0b; pirx runs in
>   light mode (D87); AI goes through OpenRouter (D46, D59, D60).
> - Done already (M0, tasks T01-T09, issues #63-#71): US-0.1, US-0.2, US-0.3, US-0.6, US-0.7, US-0.10,
>   US-0.11, US-0.12, US-10.1, US-10.2, US-10.6 and the security baseline from step 5.


---

## E1 Konta i placówki


Zapisałem zatwierdzone epiki w planie roboczym. Poniżej historie dla E1 w formacie, który później zamienimy na zadania dla agentów. Każde kryterium jest sprawdzalne testem.

**Najpierw ustalenie z weryfikacji:** publiczne API rejestru szkół RSPO nie odpowiada z mojej sieci, więc go nie zakładam. Publiczna wyszukiwarka [rspo.gov.pl](https://rspo.gov.pl/) działa i według [kuratorium w Warszawie](https://www.kuratorium.waw.pl/pl/rodzice-i-uczniowie/rejestr-szkol-i-placowe/14386,Rejestr-szkol-i-placowek-oswiatowych.pdf) pozwala pobrać wyniki jako CSV z numerem RSPO, REGON i typem placówki. Weryfikację oprę na imporcie tego pliku i na administratorze.

### Trzy decyzje do zatwierdzenia
| # | Decyzja | Rekomendacja | Dlaczego |
|---|---|---|---|
| D1 | Jak się logować | **link w e-mailu plus 6-cyfrowy kod**, bez haseł | brak przechowywania haseł to mniej zabezpieczeń do zrobienia; kod pomaga, gdy szkolna poczta przetrzymuje linki |
| D2 | Ile profili artysty na konto | **jedno konto = jeden profil artysty**; spektakle i pokazy jako repertuar w tym profilu | prostsze; agencje z wieloma artystami dopiero po pilocie |
| D3 | Kiedy placówka musi być zweryfikowana | **zapytanie bez weryfikacji (z limitem), ogłoszenie tylko po weryfikacji** | zapytanie trafia do jednego artysty, a ogłoszenie do wielu, więc spam w ogłoszeniach jest groźniejszy |

### Historie

**US-1.1 Rejestracja artysty.** Jako artysta chcę założyć konto, żeby stworzyć swój profil.
- Zakładając, że podam e-mail, nazwę (osoba, zespół lub firma) i zaakceptuję regulamin, gdy wyślę formularz, wtedy dostanę e-mail z linkiem i kodem, a konto ma status „niepotwierdzone”.
- Gdy kliknę link lub wpiszę kod w ciągu 15 minut, wtedy konto jest potwierdzone, a ja trafiam do kreatora profilu (E2).
- Gdy e-mail jest już zarejestrowany, wtedy widzę ten sam komunikat co przy nowym koncie (bez ujawniania, czy konto istnieje), a właściciel dostaje link do logowania.
- Zgoda na regulamin i politykę prywatności jest zapisywana z datą i wersją dokumentu.

**US-1.2 Rejestracja placówki.** Jako dyrektor, nauczyciel lub pedagog chcę założyć konto placówki, żeby szukać artystów i wysyłać zapytania.
- Zakładając, że wybiorę typ (szkoła podstawowa, przedszkole, szkoła ponadpodstawowa, dom kultury, inne), podam nazwę, miejscowość, województwo, moją funkcję i e-mail, gdy potwierdzę e-mail, wtedy mam konto placówki ze statusem „niezweryfikowana”.
- Podczas rejestracji system podpowiada placówki z zaimportowanego RSPO po nazwie i miejscowości. Wybór z listy przypisuje numer RSPO.
- Gdy wybrana placówka ma już konto, wtedy nowe konto jest z nią powiązane, a administrator dostaje informację do sprawdzenia (bez automatycznego dostępu do zapytań innej osoby).

**US-1.3 Logowanie i sesje.**
- Gdy podam e-mail, wtedy dostaję link i kod ważne 15 minut i jednorazowe.
- Po 5 nieudanych kodach dla jednego e-maila logowanie jest blokowane na 15 minut.
- Sesja wygasa po 30 dniach bezczynności, a wylogowanie unieważnia ją na serwerze.
- Wysyłka linków jest ograniczona (np. 5 na godzinę na e-mail i 20 na adres IP).

**US-1.4 Weryfikacja placówki.**
- Administrator importuje plik CSV z RSPO, a system aktualizuje bazę placówek bez duplikatów (klucz: numer RSPO).
- Placówka jest „zweryfikowana”, gdy domena e-maila odpowiada domenie z RSPO albo gdy administrator zatwierdzi ją ręcznie. Ten pierwszy warunek zależy od tego, czy CSV zawiera adresy e-mail, co trzeba sprawdzić w pliku.
- Zweryfikowana placówka ma oznaczenie widoczne dla artystów w zapytaniach i ogłoszeniach.

**US-1.5 Role i uprawnienia.**
- Artysta nie może tworzyć zapytań ani ogłoszeń, a placówka nie może tworzyć profilu artysty.
- Konto administratora powstaje tylko z konfiguracji serwera, nie z formularza.
- Każde naruszenie uprawnień zwraca błąd 403 i jest zapisywane w dzienniku zdarzeń.

**US-1.6 Ustawienia konta.**
- Użytkownik może zmienić nazwę i dane kontaktowe. Zmiana e-maila wymaga potwierdzenia na nowym adresie.
- Usunięcie konta i eksport danych należą do E8 i tu tylko je linkujemy.

**Zdarzenia do analityki (E10):** konto utworzone, konto potwierdzone, placówka zweryfikowana.

### Co dalej
Po zatwierdzeniu E1 przejdę do E2 (generator profilu), który jest najbardziej rozbudowany i najlepiej przetestowany. Wykorzystam w nim wnioski z testu: instrukcję agenta v0.2, walidator, zakaz stockowych zdjęć w roli głównej i pętlę naprawy.


---

## E2 Generator profilu artysty


E1 jest zatwierdzony i zapisany w planie roboczym. Poniżej E2, oparty na wynikach testu na pięciu artystach.

### Trzy decyzje do zatwierdzenia
| # | Decyzja | Rekomendacja | Dlaczego |
|---|---|---|---|
| D4 | Import z cudzej strony | **tylko z własnej strony artysty, po oświadczeniu o prawach do treści i zdjęć**; zdjęcia kopiujemy do własnego magazynu | linkowanie zdjęć z cudzych serwerów jest zawodne, a bez oświadczenia ryzykujemy prawa autorskie |
| D5 | Kiedy działa AI | **w tle, automatycznie po imporcie lub wypełnieniu kwestionariusza**; limit 20 generacji dziennie na konto | artysta nie czeka przy ekranie; limit chroni przed nadużyciami, bo sam koszt to grosze |
| D6 | Minimum do publikacji | **nazwa, region działania, opis, co najmniej 1 oferta i oświadczenie o stosowaniu standardów ochrony małoletnich** (to ostatnie już w M1) | szkoła nie powinna oglądać profilu bez tego oświadczenia; pełny pakiet zgodności (OC, weryfikacja) zostaje w E8 |

### Historie

**US-2.1 Dane podstawowe.** Jako artysta chcę podać podstawowe informacje, żeby system wiedział, co generować.
- Wybieram rodzaj (teatr, iluzja, muzyka, pokaz naukowy, pokaz ze zwierzętami, warsztaty, inne), nazwę, miasto, województwa działania i odbiorców (przedszkola, klasy 0–3, 4–6, 7–8, szkoły ponadpodstawowe, rodziny).
- Bez tych pól nie mogę przejść dalej. Pozostałe kroki mogę pominąć i wrócić do nich później.

**US-2.2 Import z własnej strony.** Jako artysta chcę wkleić adres swojej strony, żeby nie przepisywać wszystkiego.
- Muszę zaznaczyć oświadczenie, że strona jest moja i mam prawa do treści i zdjęć.
- System pobiera najwyżej 10 podstron z tej samej domeny i zbiera tekst, zdjęcia, linki YouTube oraz ogólne dane kontaktowe. Nie przekracza 30 sekund na stronę i 20 MB łącznie.
- Numery kont, PESEL i podobne dane są usuwane przed przekazaniem do AI. W teście strona Edenu zawierała numery kont.
- Pobieranie odbywa się tylko pod publicznymi adresami. Adresy wewnętrzne i lokalne są blokowane (ochrona przed atakami SSRF).
- Jeśli import się nie powiedzie, dostaję czytelny komunikat i mogę uzupełnić dane ręcznie.

**US-2.3 Materiały i kwestionariusz.** Jako artysta chcę wgrać zdjęcia i odpowiedzieć na pytania szkoły, żeby profil był konkretny.
- Wgrywanie: JPG, PNG lub WebP do 15 MB. Usuwamy metadane z lokalizacją (EXIF GPS).
- Filmy: link YouTube sprawdzony przez publiczne oEmbed.
- Kwestionariusz dla szkół: wiek widzów, czas trwania, maksymalna liczba widzów, wymagania techniczne (sala, prąd, nagłośnienie), cena od–do lub „na zapytanie”, forma rozliczenia (faktura, rachunek).

**US-2.4 Kontrola zasobów.**
- Dla każdego zdjęcia zapisujemy wymiary, orientację i flagi: niska rozdzielczość (poniżej 1200 px), mocna kompresja, duplikat, zdjęcie stockowe, zrzut ekranu lub obraz AI, plakat.
- Zdjęcie z flagą stockową, zrzutu ekranu lub plakatu nie może być zdjęciem głównym.
- Artysta widzi flagi przy każdym zdjęciu z krótką wskazówką, co poprawić.

**US-2.5 Generowanie przez AI.**
- Zadanie w tle, ze statusem widocznym dla artysty. Typowy czas poniżej 2 minut (próg do potwierdzenia w testach).
- AI zwraca JSON według schematu z instrukcji v0.2: hero, fakty, opis, sekcja dla szkół, oferty, galeria, opinie, FAQ, motyw, SEO, braki, audyt twierdzeń.
- **Walidator twardych reguł:**
  - liczby i ceny tylko ze źródła;
  - opinie dosłownie;
  - zdjęcia i filmy tylko z materiałów artysty;
  - bez języka procesu („w materiałach”) i bez dodanych obietnic;
  - fakty do 22 znaków i bez nawiasów;
  - limity długości.
- Przy naruszeniu twardej reguły system automatycznie zleca naprawę, najwyżej 2 rundy. Jeśli nadal są błędy, profil czeka na ręczny przegląd administratora. To ta sama pętla, która w teście naprawiła profile Edenu i Magicznej Sceny.
- Reguły miękkie (np. ostrzeżenie o mało konkretnym opisie) trafiają tylko do raportu.

**US-2.6 Podgląd, edycja i wersje.**
- Podgląd strony w szablonie premium (E3) przed publikacją.
- Edycja każdego pola. Pole edytowane ręcznie dostaje blokadę, więc ponowne generowanie go nie nadpisze.
- Mogę wygenerować ponownie tylko jedną sekcję (np. opis).
- Ostatnie 10 wersji z możliwością powrotu.

**US-2.7 Lista braków.**
- Braki z generatora pokazują się jako lista zadań z przyciskiem do uzupełnienia, np. „Dodaj zdjęcie ze sceny” albo „Podaj maksymalną liczbę widzów”.
- Wskaźnik kompletności w procentach. Uzupełnienie braku odświeża odpowiednią sekcję.

**US-2.8 Publikacja.**
- Publikacja tylko po kliknięciu przez artystę i po spełnieniu minimum z D6.
- Profil dostaje stały adres (np. `/artysci/<nazwa>`). Artysta może go wycofać w każdej chwili, a wycofany profil znika z katalogu i wyszukiwarek.

**US-2.9 Oferty i repertuar.**
- Dodawanie, edycja i usuwanie ofert: tytuł, opis, wiek widzów, czas trwania, cena lub „na zapytanie”, plakat.
- Repertuar teatru z wieloma spektaklami (jak Eden z 20 tytułami) to oferty w jednym profilu, zgodnie z D2.

**Zdarzenia do analityki:** import rozpoczęty i zakończony, generowanie zakończone (z liczbą ostrzeżeń i rund naprawy), profil opublikowany, profil wycofany, kompletność przy publikacji.

**Co celowo zostaje poza E2:** wybór modelu AI i jego koszty (krok 4, stos), import z Facebooka, polecenia do agenta zwykłym językiem (po pilocie).


---

## E2 zmiana: własne zasoby artysty (US-2.3, D7, D8)

Rozszerzyłem E2: artysta może wgrywać własne zasoby niezależnie od tego, czy ma stronę. Zmiana jest zapisana w planie.

### Nowa wersja US-2.3 „Materiały artysty”
Jako artysta chcę wgrać własne zdjęcia, nagrania i dokumenty, żeby profil powstał także bez strony WWW albo był lepszy niż moja strona.

| Rodzaj | Formaty | Limit (propozycja D8) | Co system z tym robi |
|---|---|---|---|
| Zdjęcia | JPG, PNG, WebP, HEIC | do 15 MB, najwyżej 40 | kontrola jakości (US-2.4), usunięcie metadanych z lokalizacją, wersje w kilku rozmiarach |
| Wideo | MP4, MOV, WebM | do 500 MB i 10 minut, najwyżej 5 | konwersja do formatu dla przeglądarek, miniatura, odtwarzanie na stronie profilu |
| Audio | MP3, M4A, WAV | do 50 MB, najwyżej 10 | odtwarzacz na stronie (przydatne dla muzyków) |
| Dokumenty | PDF | do 20 MB, najwyżej 10 | tekst z PDF jest źródłem dla AI (oferta, scenariusz, wymagania techniczne); plakaty z PDF można użyć jako plakaty ofert |
| Linki | YouTube, Vimeo | bez limitu ilości | sprawdzenie przez publiczne oEmbed |

**Kryteria akceptacji:**
- Mogę wgrać zasoby przed importem strony, po nim albo zamiast niego. Profil da się wygenerować z samych wgranych materiałów i kwestionariusza.
- Przy przekroczeniu limitu albo złym formacie widzę komunikat przed wysyłką, a nie po niej.
- Wgrywanie dużych plików da się wznowić po przerwaniu połączenia.
- Treść PDF jest dodawana do materiałów źródłowych. Walidator traktuje ją jak tekst ze strony, więc agent może z niej brać ceny, czasy i opisy.
- Każdy plik jest skanowany pod kątem złośliwego oprogramowania i sprawdzany po zawartości, nie tylko po rozszerzeniu.
- Mogę usunąć każdy plik, a usunięty znika z profilu i z magazynu.

**Zmiany w innych historiach:**
- **US-2.4 Kontrola zasobów:** dla wideo dochodzą flagi „za krótkie” (poniżej 15 s), „pionowe” i „niska rozdzielczość” (poniżej 720p). Z wideo system wycina kilka kadrów jako kandydatów na zdjęcie główne, co pomaga artystom bez dobrych zdjęć (problem Edenu z testu).
- **US-2.5 Generowanie:** agent dostaje tekst z PDF, opisy filmów i kadry z wideo jako dodatkowe materiały.

### Dwie nowe decyzje
| # | Decyzja | Rekomendacja | Dlaczego |
|---|---|---|---|
| D7 | Wizerunek osób na zdjęciach i nagraniach | przy wgrywaniu artysta oświadcza, że ma zgody osób rozpoznawalnych, a **dla dzieci osobno potwierdza zgody rodziców lub szkoły**; materiały z rozpoznawalnymi dziećmi bez tej zgody nie są publikowane | nagrania z występów w szkołach prawie zawsze pokazują dzieci, a za publikację wizerunku bez zgody odpowiada też serwis. To moja ocena, nie porada prawna, i warto ją potwierdzić z prawnikiem |
| D8 | Limity plików | jak w tabeli wyżej | wideo kosztuje: przechowywanie i transmisja to realne koszty (np. 5 USD za 1000 minut przechowywania i 1 USD za 1000 minut obejrzanych w Cloudflare Stream, według cennika z wcześniejszego wyszukiwania) |

**Do kroku 4 (stos):** zdecydujemy, czy wideo obsługuje zewnętrzna usługa (np. Cloudflare Stream lub Mux), czy własna konwersja. Ma to wpływ na koszt i na pracę dla agentów.


---

## E3 Publiczna strona artysty


E2 jest zatwierdzony i zapisany. E3 przenosi do produktu szablon premium z testu, razem z poprawkami, które tam wyszły.

### Trzy decyzje do zatwierdzenia
| # | Decyzja | Rekomendacja | Dlaczego |
|---|---|---|---|
| D9 | Czy telefon i e-mail artysty są publiczne | **nie; strona ma tylko przycisk „Sprawdź termin”, a kontakt artysty widzi placówka po wysłaniu zapytania** | chroni artystę przed spamem, ogranicza omijanie platformy i pozwala mierzyć zapytania, od których zależą progi pilota |
| D10 | Opinie na stronie | **w MVP bez opinii importowanych ze stron artystów**; opinie wyłącznie od placówek po potwierdzonym występie, dopiero po pilocie | w teście opinie ze stron były słabe (komentarze uczniów, nie o ofercie); opinia z platformy jest wiarygodna dla dyrektora |
| D11 | Czcionki i zewnętrzne zasoby | **hostowane u nas**, bez Google Fonts ładowanych z serwerów Google | pobieranie czcionek z Google przekazuje adres IP odwiedzającego, co bywa kwestionowane na gruncie RODO; własny hosting jest też szybszy |

### Historie

**US-3.1 Szablon i sekcje.** Jako dyrektor chcę zobaczyć na jednej stronie wszystko, czego potrzebuję do decyzji.
- Sekcje w stałej kolejności: początek (nagłówek, zdjęcie główne, przycisk), pasek faktów, o nas, pas „Dla szkół i przedszkoli”, oferta, nagrania, zdjęcia, pytania, zapytanie o termin.
- Sekcja bez danych nie pokazuje się. Galeria pojawia się dopiero przy co najmniej 4 dobrych zdjęciach.
- Oferta pokazuje 6 pozycji, a resztę zwija pod przyciskiem „Pokaż pozostałe”. Jedna uwaga o cenach zamiast „Cena na zapytanie” przy każdej pozycji, a tagi nie pokazują się, gdy są wszędzie takie same.
- Bez zdjęcia głównego strona ma typograficzny początek z inicjałem w ramce.
- Wideo wgrane przez artystę odtwarza się na stronie, a link YouTube ma miniaturę z przyciskiem.

**US-3.2 Motywy.**
- Cztery motywy z testu (jasny burgund, kremowa zieleń, granat ze złotem, ciemny koral). AI proponuje motyw na podstawie opisu stylu, a artysta może go zmienić w podglądzie.
- Każdy motyw spełnia kontrast WCAG AA dla tekstu i przycisków, sprawdzany testem automatycznym.

**US-3.3 Telefon i wydajność.**
- Układ działa od szerokości 360 px bez przewijania w poziomie, z przypiętym przyciskiem „Sprawdź termin” na telefonie.
- Zdjęcia w kilku rozmiarach i ładowane leniwie. Główna treść ładuje się w 2,5 s na wolnym połączeniu mobilnym (cel do potwierdzenia testem Lighthouse).

**US-3.4 Widoczność w wyszukiwarkach.**
- Strona renderowana na serwerze, z tytułem, opisem, podglądem przy udostępnianiu (Open Graph) i danymi strukturalnymi schema.org.
- Opublikowany profil trafia do mapy strony. Wycofany ma znacznik „noindex” i znika z katalogu.

**US-3.5 Zapytanie o termin.**
- Przycisk otwiera formularz zapytania z E5, z wypełnionym artystą i typami oferty.
- Niezalogowana placówka może wypełnić formularz, a potwierdza go linkiem w e-mailu (E1). Zapytanie wysyła się dopiero po potwierdzeniu, więc nie tracimy wpisanych danych.

**US-3.6 Dostępność.**
- Opisy alternatywne dla wszystkich zdjęć, obsługa klawiaturą (galeria, wideo, rozwijane sekcje), widoczny fokus i wyłączenie animacji dla osób, które tego potrzebują.
- Automatyczny test dostępności bez błędów krytycznych.

**US-3.7 Podgląd i udostępnianie.**
- Przed publikacją artysta może wysłać komuś prywatny link do podglądu, ważny 7 dni i niewidoczny dla wyszukiwarek.
- Po publikacji przycisk „Kopiuj link” i dobry podgląd przy udostępnianiu w komunikatorach i mediach społecznościowych.

**Zdarzenia do analityki:** wyświetlenie profilu (bez danych osobowych), kliknięcie „Sprawdź termin”, rozpoczęcie i wysłanie formularza.

**Co zostaje poza E3:** własne domeny artystów, edytor wyglądu poza motywami, opinie (D10).


---

## E3 US-3.8 standard jakości i E11 Laboratorium jakości generatora


### US-3.8 „Standard jakości strony” (dodane do E3)
Strona może zostać zaproponowana artyście do publikacji tylko wtedy, gdy spełnia wszystkie progi. Inaczej wraca do naprawy albo czeka na przegląd administratora.

| Wymiar | Próg (propozycja) | Jak mierzony |
|---|---|---|
| Fakty i bezpieczeństwo treści | 100% twardych reguł spełnionych | walidator: liczby, ceny, opinie, zdjęcia, brak języka procesu i obietnic |
| Wierność, kompletność, przydatność, język, ton, uczciwość wobec braków | co najmniej 4 z 5 w każdym wymiarze | recenzent AI z rubryką, tą samą, której użyłem w teście |
| Dostępność | brak błędów krytycznych | automatyczny test dostępności |
| Wydajność na telefonie | Lighthouse co najmniej 85 | pomiar wyrenderowanej strony |
| Zdjęcia | brak stocku, zrzutu ekranu i plakatu w zdjęciu głównym; galeria tylko z co najmniej 4 dobrymi zdjęciami | flagi z kontroli zasobów |
| Wygląd | brak pustych miejsc i ucięć na 360 px i 1440 px | zrzuty ekranu oceniane automatycznie, jak w teście |

### Nowy epik E11 „Laboratorium jakości generatora”
Cel: każda zmiana w generatorze (instrukcja agenta, model, szablon, walidator) jest mierzona na tych samych danych, zanim trafi do artystów. Każdy nowy błąd zamienia się w regułę i test, żeby nie wrócił.

**US-11.1 Wersjonowanie i rejestr generacji.** Każda generacja zapisuje wersje instrukcji, schematu, walidatora, szablonu i modelu, odcisk materiałów wejściowych, wynik, ostrzeżenia, liczbę rund naprawy, czas i koszt. Mogę odtworzyć dowolną stronę z danej wersji.

**US-11.2 Zbiór testowy.** Około 30–50 pakietów materiałów w trzech poziomach jakości (słabe, średnie, bogate) i dla różnych rodzajów artystów, wzorem testu na Doxie, Joylandzie, Franku, Edenie i Magicznej Scenie. Do każdego pakietu można dopisać oczekiwania (np. „cena nie może się pojawić”, „hero musi być puste”).

**US-11.3 Automatyczna ocena.** Uruchomienie zestawu daje raport dla każdego pakietu:
- wynik walidatora;
- oceny recenzenta AI w 6 wymiarach z cytatami problemów;
- metryki strony (dostępność, Lighthouse);
- ocenę zrzutów ekranu przez model z obrazem.

Recenzent działa niezależnie od generatora, czyli innym wywołaniem i bez wglądu w jego rozumowanie.

**US-11.4 Porównanie wersji i bramka jakości.** Nowa wersja generatora jest uruchamiana na całym zbiorze testowym i porównywana z aktualną: różnice ocen w każdym wymiarze, nowe i naprawione błędy oraz strony obok siebie. Wdrożenie tylko po przejściu bramki (D13).

**US-11.5 Sygnały z produkcji.** Mierzymy, które pola artyści najczęściej poprawiają i jak mocno, ile stron publikują bez zmian, ile sekcji generują ponownie, czas do publikacji, a później też, ile profili dostaje zapytania. Raport tygodniowy w panelu administratora.

**US-11.6 Ocena ludzka.** Administrator ocenia strony w skali 1–5 i oznacza typy błędów z listy. Porównanie dwóch wersji strony na ślepo („która lepsza?”) dla trudnych przypadków.

**US-11.7 Katalog błędów i testy regresji.** Każdy znaleziony błąd dostaje typ (np. „język procesu”, „fakt z nawiasem”, „opinia ucznia”, „szacunek jako fakt”), regułę walidatora albo przykład w instrukcji i przypadek testowy w zbiorze. W teście dodaliśmy już kilka takich reguł ręcznie, a tu ma to być proces.

**US-11.8 Agent-ulepszacz (po pilocie).** Agent czyta raporty, edycje artystów i katalog błędów, proponuje zmianę instrukcji lub reguły, uruchamia zbiór testowy i otwiera PR z raportem porównawczym. Człowiek zatwierdza (D14).

**Kamienie milowe:** US-11.1–11.4 i 11.7 w M1, bo bez nich nie da się mierzyć jakości od pierwszego artysty. US-11.5–11.6 w M4. US-11.8 po pilocie.

### Trzy decyzje do zatwierdzenia
| # | Decyzja | Rekomendacja | Dlaczego |
|---|---|---|---|
| D12 | Skąd zbiór testowy | **tylko materiały artystów, którzy wyrazili zgodę (osobne zaznaczenie przy rejestracji), plus przykłady syntetyczne**; strony pobrane w naszym teście nie wchodzą do trwałego zbioru | przechowywanie cudzych materiałów do testów bez zgody to ryzyko RODO i praw autorskich |
| D13 | Bramka jakości przed wdrożeniem | **twarde reguły 100%, średnia ocena recenzenta nie spada, żaden wymiar nie spada o więcej niż 0,3 punktu** | chroni przed sytuacją, w której poprawka jednej rzeczy psuje inną |
| D14 | Kto zmienia generator | **tylko przez PR zatwierdzony przez człowieka**; brak automatycznych zmian na produkcji | agent może się mylić, a PR daje historię i możliwość cofnięcia |

**Koszt (szacunek):** ocena jednego pakietu tanim modelem to kilka groszy, więc pełny zestaw 50 pakietów to rzędu kilku złotych na wersję. Dokładniej policzymy po wyborze modeli w kroku stosu.


---

## E4 Katalog i wyszukiwanie


E3 (ze standardem jakości) i E11 są zatwierdzone i zapisane. Poniżej E4.

### Cztery decyzje do zatwierdzenia
| # | Decyzja | Rekomendacja | Dlaczego |
|---|---|---|---|
| D15 | Czy katalog wymaga logowania | **nie, katalog i profile są publiczne**; logowanie dopiero przy zapytaniu | wyszukiwarki muszą widzieć profile, a dyrektor ma obejrzeć ofertę bez zakładania konta |
| D16 | Kolejność wyników | **najpierw dopasowanie do filtrów, potem weryfikacja i kompletność profilu, a w obrębie grupy kolejność losowana raz dziennie; bez płatnych wyróżnień w MVP** | losowanie daje mniejszym artystom szansę, a płatne wyróżnienia przed pomiarem popytu zniechęcają szkoły |
| D17 | Słowniki (rodzaje, tematy, grupy wiekowe) | **zamknięte listy zarządzane przez administratora**; AI przypisuje profile do pozycji z listy, artysta poprawia | wolne tagi rozjeżdżają się („profilaktyka uzależnień” i „uzależnienia”), co psuje filtry |
| D18 | Strony regionów i kategorii | **indeksowane tylko przy co najmniej 3 profilach**, inaczej „noindex” | puste strony szkodzą widoczności w Google |

### Historie

**US-4.1 Lista i karty.** Jako dyrektor chcę szybko przejrzeć artystów, żeby wybrać kilku do zapytania.
- Karta pokazuje zdjęcie główne (lub inicjał), nazwę, rodzaj, obszar działania, grupy wiekowe, cenę „od” (jeśli podana) i znacznik „zweryfikowany”.
- 24 karty na stronę z paginacją, którą da się linkować (każda strona ma swój adres).

**US-4.2 Filtry.**
- Filtry: województwo (według obszaru działania artysty, nie siedziby), rodzaj, grupa wiekowa lub klasy, tematyka (np. uzależnienia, hejt, bezpieczeństwo, emocje, ekologia), forma (spektakl, warsztaty, pokaz), cena maksymalna, czas trwania.
- Ustawione filtry są w adresie, więc link z wynikami można przesłać innemu nauczycielowi.
- **Brak wyników** pokazuje propozycję poszerzenia filtrów i przycisk „Opublikuj ogłoszenie, a artyści zgłoszą się sami” (E6). To łączy katalog z ogłoszeniami w jeden przepływ.

**US-4.3 Wyszukiwanie tekstowe.**
- Wyszukiwanie po nazwie artysty, tytule spektaklu i temacie, z obsługą polskiej odmiany („spektakl o hejcie” znajduje „Cena hejtu”) i literówek. Konkretny mechanizm wybierzemy w kroku stosu.

**US-4.4 Kolejność wyników.** Działa według D16. Artysta nie może kupić wyższej pozycji.

**US-4.5 Strony regionów i kategorii.**
- Adresy typu `/artysci/lodzkie/spektakle-profilaktyczne` z krótkim, generowanym raz i sprawdzanym opisem, listą artystów i danymi strukturalnymi.
- Indeksacja według D18, a wszystkie indeksowane strony są w mapie strony.

**US-4.6 Słowniki w panelu administratora.** Administrator dodaje, zmienia nazwy i łączy pozycje słowników. Połączenie dwóch pozycji przenosi przypisane profile.

**US-4.7 Wydajność.** Lista z filtrami odpowiada w czasie poniżej 1 sekundy dla 95% zapytań przy 10 tys. profili (cel do potwierdzenia testem obciążeniowym).

**Zdarzenia do analityki:** wyszukiwanie (filtry i liczba wyników, bez danych osobowych), brak wyników, kliknięcie karty, kliknięcie „Opublikuj ogłoszenie” z pustych wyników.

**Co zostaje poza E4:** mapa, wyszukiwanie po wolnych terminach (wymaga kalendarza, który jest po pilocie), ulubione i porównywanie artystów.


---

## E5 Zapytania ofertowe


E4 jest zatwierdzony i zapisany. E5 to cykl życia zapytania: od formularza szkoły do potwierdzenia, że występ się odbył, bo to ostatnie jest jednym z progów pilota.

### Cykl życia zapytania
```
nowe → (artysta) oferta wysłana / odmowa
oferta wysłana → (placówka) zaakceptowana / odrzucona / wygasła
zaakceptowana → (po dacie) występ potwierdzony / nie odbył się
każdy status przed datą → anulowane (z powodem)
```

### Cztery decyzje do zatwierdzenia
| # | Decyzja | Rekomendacja | Dlaczego |
|---|---|---|---|
| D19 | Do ilu artystów jedno zapytanie | **do 3 naraz, a artysta widzi, że zapytanie trafiło do kilku osób** | szkoła szybciej porównuje oferty, a jawność jest uczciwa wobec artystów; więcej niż 3 zamienia się w ogłoszenie (E6) |
| D20 | Co oznacza akceptacja | **wstępną rezerwację; umowę, fakturę i płatność strony załatwiają poza platformą** | płatności są poza MVP, a szkoły i tak mają własne procedury zamówień |
| D21 | Jak artysta podaje cenę | **zawsze kwota brutto do zapłaty przez placówkę i forma rozliczenia** (faktura VAT, faktura bez VAT, rachunek) | dyrektor porównuje kwoty, które faktycznie zapłaci, i wie, jaki dokument dostanie |
| D22 | Kiedy występ jest „potwierdzony” | **gdy po dacie występu potwierdzi to placówka** (artysta też jest pytany, ale jego potwierdzenie nie wystarcza) | to próg pilota i później warunek wystawienia opinii, więc musi pochodzić od płacącego |

### Historie

**US-5.1 Formularz zapytania.** Jako nauczyciel chcę opisać potrzebę w jednym formularzu, żeby artysta mógł podać konkretną ofertę.
- Pola:
  - termin (konkretna data, przedział dat albo „elastycznie”) i orientacyjna godzina;
  - miejsce (domyślnie adres placówki);
  - liczba dzieci i grupa wiekowa lub klasy;
  - wybrana oferta z repertuaru (opcjonalnie);
  - budżet (opcjonalnie);
  - uwagi o sali i warunkach.
- Walidacja: data nie może być w przeszłości, a liczba dzieci musi być między 1 a 1000.
- Formularz zapisuje szkic, gdy użytkownik musi potwierdzić e-mail w trakcie (powiązane z US-3.5).

**US-5.2 Wysyłka do 1–3 artystów.** Mogę zaznaczyć do 3 artystów na liście wyników i wysłać im to samo zapytanie, zgodnie z D19. Po wysłaniu widzę dane kontaktowe artystów (D9).

**US-5.3 Skrzynka artysty.**
- Lista zapytań ze statusami, oznaczeniem nieprzeczytanych i informacją, ilu artystów dostało to samo zapytanie.
- Widzę też, czy placówka jest zweryfikowana (E1).

**US-5.4 Oferta lub odmowa.**
- Oferta: kwota brutto i forma rozliczenia (D21), co zawiera, warunki (dojazd, wymagania techniczne), proponowany termin, ważność (domyślnie 14 dni).
- Odmowa: powód z listy (termin zajęty, poza obszarem, inny) i opcjonalny komentarz.

**US-5.5 Decyzja placówki.**
- Widzę oferty obok siebie, gdy zapytanie poszło do kilku artystów.
- Akceptacja zmienia status na „zaakceptowana” (D20) i obie strony dostają e-mail z podsumowaniem i danymi kontaktowymi.
- Gdy zapytanie poszło do kilku artystów, pozostali dostają informację, że placówka wybrała innego wykonawcę.

**US-5.6 Wątek wiadomości.** Krótkie wiadomości tekstowe w ramach zapytania, z powiadomieniem e-mail (E7). Załączniki dopiero po pilocie.

**US-5.7 Przypomnienia, wygasanie, potwierdzenie.**
- Artysta dostaje przypomnienie, jeśli nie odpowie w 48 godzin.
- Zapytanie bez odpowiedzi wygasa po 14 dniach. Oferta wygasa po upływie swojej ważności.
- Dzień po dacie występu obie strony dostają pytanie „Czy występ się odbył?”. Liczy się odpowiedź placówki (D22).

**US-5.8 Anulowanie.** Każda strona może anulować przed datą występu, z powodem. Druga strona dostaje powiadomienie, a historia zostaje zachowana.

**US-5.9 Limity antyspamowe.** Placówka niezweryfikowana może wysłać 5 zapytań dziennie, a zweryfikowana 20. Artysta może zgłosić zapytanie jako spam, co trafia do moderacji (E9).

**Zdarzenia do analityki:** zapytanie wysłane (do ilu artystów), oferta wysłana (czas odpowiedzi), odmowa (powód), akceptacja, odrzucenie, wygaśnięcie, anulowanie, występ potwierdzony.

**Co zostaje poza E5:** płatności, umowy generowane w platformie, kalendarz dostępności, załączniki w wiadomościach, opinie po występie.


---

## E6 Ogłoszenia placówek


E5 jest zatwierdzony i zapisany. E6 to odwrócony przepływ: placówka opisuje potrzebę, a artyści zgłaszają się z ofertami. Wybrana oferta staje się zwykłym zaakceptowanym zapytaniem z E5, więc dalej (kontakty, potwierdzenie występu, analityka) wszystko działa tak samo.

### Trzy decyzje do zatwierdzenia
| # | Decyzja | Rekomendacja | Dlaczego |
|---|---|---|---|
| D23 | Kto i jak publikuje | **tylko zweryfikowane placówki (D3), bez ręcznej akceptacji**; automatyczny filtr treści i moderacja po fakcie | ręczna akceptacja spowalnia pierwsze wrażenie szkoły, a weryfikacja placówki już ogranicza spam |
| D24 | Ilu artystów dostaje powiadomienie | **do 30 najlepiej dopasowanych**, a pozostali pasujący widzą ogłoszenie na tablicy | chroni artystów przed zalewem e-maili i szkołę przed zbyt wieloma ofertami; próg pilota to co najmniej 2 oferty |
| D25 | Czy ogłoszenia są publiczne | **publiczny skrót bez nazwy placówki** (np. „Szkoła podstawowa, okolice Łodzi, klasy 4–6, profilaktyka hejtu, marzec”); szczegóły i zgłoszenie tylko dla zalogowanych artystów | widoczne zapotrzebowanie przyciąga nowych artystów, a szkoła nie jest publicznie wskazana |

### Historie

**US-6.1 Utworzenie ogłoszenia.** Jako dyrektor chcę opisać, czego szukam, żeby artyści sami się zgłosili.
- Pola:
  - tytuł i czego szukam (rodzaj, tematyka, forma, ze słowników z D17);
  - grupy wiekowe i liczba dzieci;
  - termin lub przedział dat i miejsce;
  - budżet (opcjonalny, z zachętą do podania przedziału);
  - termin zbierania ofert (domyślnie 7 dni, najwyżej 30);
  - uwagi.
- Formularz podpowiada uzupełnienie braków, np. „Bez grupy wiekowej artyści nie dopasują oferty”.
- Ogłoszenie można zacząć z pustych wyników katalogu (US-4.2), a wtedy filtry przenoszą się do formularza.

**US-6.2 Moderacja.**
- Automatyczna kontrola: brak danych osobowych dzieci, numerów telefonów w treści, linków i treści niezwiązanych z ofertą.
- Ogłoszenie z flagą trafia do kolejki administratora (E9), a reszta publikuje się od razu.
- Artysta może zgłosić ogłoszenie.

**US-6.3 Dopasowanie artystów.**
- Artysta pasuje, gdy jego obszar działania obejmuje województwo ogłoszenia i zgadza się przynajmniej rodzaj albo tematyka, a także grupa wiekowa.
- Kolejność dopasowanych jak w D16 (dopasowanie, weryfikacja, kompletność, losowanie w grupie).
- Wynik dopasowania jest zapisywany, żeby można było sprawdzić, dlaczego artysta dostał lub nie dostał powiadomienia.

**US-6.4 Powiadomienia artystów.**
- Do 30 najlepiej dopasowanych (D24) według ustawienia artysty: e-mail od razu albo raz dziennie w zestawieniu (E7).

**US-6.5 Tablica ogłoszeń.**
- Zalogowany artysta widzi otwarte ogłoszenia z filtrami (województwo, rodzaj, termin), z oznaczeniem tych, które do niego pasują.
- Publiczna wersja tablicy pokazuje skróty (D25) i zachętę „Załóż profil, żeby się zgłosić”.

**US-6.6 Zgłoszenie artysty.**
- Ten sam format oferty co w E5 (kwota brutto, forma rozliczenia, warunki, termin) plus krótka wiadomość.
- Jedno zgłoszenie na artystę na ogłoszenie, z możliwością edycji do terminu zbierania ofert.
- Limit 10 zgłoszeń dziennie na artystę.

**US-6.7 Porównanie i wybór.**
- Placówka widzi oferty obok siebie, z linkiem do profilu każdego artysty.
- Wybór tworzy zaakceptowane zapytanie z cyklem E5 i ujawnia kontakty. Pozostali artyści dostają informację o wyborze.

**US-6.8 Zamknięcie i przedłużenie.**
- Po terminie nie można składać nowych ofert. Placówka może raz przedłużyć termin.
- Gdy nie ma ofert, placówka dostaje propozycje: poszerzyć kryteria albo napisać bezpośrednio do artystów z katalogu.

**US-6.9 Widoczność.** Zgodnie z D25. Nazwa placówki i dane kontaktowe nie trafiają do publicznego skrótu ani do kodu strony.

**Zdarzenia do analityki:** ogłoszenie opublikowane, liczba dopasowanych i powiadomionych artystów, liczba ofert, czas do pierwszej oferty, wybór, zamknięcie bez ofert. Na tych danych liczymy próg pilota „co najmniej 30% z co najmniej 2 ofertami”.

**Co zostaje poza E6:** łączenie ogłoszeń w trasy, ogłoszenia cykliczne (np. „co miesiąc warsztaty”), przetargi publiczne.


---

## E7 Powiadomienia


E6 jest zatwierdzony i zapisany. E7 zbiera w jeden katalog wszystkie powiadomienia z E1–E6 i dba o to, żeby dochodziły, także do szkolnych skrzynek z ostrymi filtrami.

### Cztery decyzje do zatwierdzenia
| # | Decyzja | Rekomendacja | Dlaczego |
|---|---|---|---|
| D26 | Dostawca wysyłki e-maili | **dostawca z przetwarzaniem danych w UE**; konkretną usługę wybierzemy w kroku stosu | e-maile zawierają dane osobowe, więc umowa powierzenia i miejsce przetwarzania mają znaczenie dla RODO |
| D27 | Wiadomości z wątku | **grupowane: najwyżej jeden e-mail na wątek co 15 minut** | rozmowa nie zasypuje skrzynki, a odbiorca nadal szybko wie o nowej wiadomości |
| D28 | Kanały | **tylko e-mail i powiadomienia w serwisie**; bez SMS i powiadomień push w MVP | mniej integracji i kosztów; SMS ma sens dopiero przy pilnych sprawach po pilocie |
| D29 | Śledzenie e-maili | **bez pikseli śledzących otwarcia i bez przepisywania linków** | prywatność i lepsza dostarczalność; skuteczność mierzymy wejściami do serwisu, nie otwarciami |

### US-7.1 Katalog powiadomień
| # | Powiadomienie | Odbiorca | Wyzwalacz | Można wyłączyć? |
|---|---|---|---|---|
| 1 | Link i kod logowania | każdy | E1 | nie |
| 2 | Placówka zweryfikowana | placówka | E1 | nie |
| 3 | Profil wygenerowany lub wymaga uwagi | artysta | E2 | nie |
| 4 | Profil opublikowany lub wycofany | artysta | E2 | nie |
| 5 | Nowe zapytanie | artysta | E5 | nie |
| 6 | Przypomnienie po 48 h bez odpowiedzi | artysta | E5 | nie |
| 7 | Otrzymano ofertę lub odmowę | placówka | E5, E6 | nie |
| 8 | Oferta zaakceptowana (z kontaktami) | obie strony | E5, E6 | nie |
| 9 | Wybrano innego artystę | artysta | E5, E6 | nie |
| 10 | Zapytanie lub oferta wygasła | obie strony | E5 | nie |
| 11 | Anulowanie | druga strona | E5 | nie |
| 12 | Czy występ się odbył? | obie strony | E5 | nie |
| 13 | Nowa wiadomość w wątku | druga strona | E5 | tak (z grupowaniem D27) |
| 14 | Nowe pasujące ogłoszenie | artysta | E6 | tak: od razu, raz dziennie, wyłączone |
| 15 | Nowa oferta do ogłoszenia | placówka | E6 | tak: od razu albo raz dziennie |
| 16 | Termin ogłoszenia mija bez ofert | placówka | E6 | nie |
| 17 | Decyzja moderacji | autor treści | E9 | nie |

### Historie

**US-7.2 Szablony.**
- Jeden spójny, prosty wygląd po polsku, z wersją czysto tekstową.
- Każdy e-mail ma jeden główny przycisk prowadzący do właściwego miejsca w serwisie.
- Wiadomości z wątku pokazują najwyżej 200 znaków podglądu. Żaden e-mail nie zawiera danych dzieci.

**US-7.3 Preferencje i rezygnacja.**
- Powiadomienia oznaczone w tabeli jako niewyłączalne są niezbędne do działania zapytań. Pozostałe użytkownik ustawia w profilu.
- Każdy e-mail, który da się wyłączyć, ma link rezygnacji działający jednym kliknięciem, bez logowania.

**US-7.4 Dostarczalność.**
- Wysyłka z własnej domeny z poprawnymi SPF, DKIM i DMARC, sprawdzanymi testem.
- Twarde odbicie oznacza adres jako nieaktywny, a użytkownik po zalogowaniu widzi prośbę o poprawę. Zgłoszenie spamu wyłącza powiadomienia opcjonalne.
- W pilocie sprawdzamy dostarczenie do kilku popularnych szkolnych skrzynek (np. w domenach gmin i `edu.pl`).

**US-7.5 Niezawodność.**
- Wysyłka w tle z ponowieniami (do 5 prób z rosnącym odstępem). Każde zdarzenie wysyła najwyżej jeden e-mail, nawet przy ponowieniu (idempotencja).
- Dziennik wysyłek (odbiorca, typ, status, czas) dostępny dla administratora, bez treści wiadomości.

**US-7.6 Powiadomienia w serwisie.** Dzwonek z licznikiem nieprzeczytanych i listą ostatnich powiadomień. Kliknięcie prowadzi do zapytania, oferty lub ogłoszenia.

**Zdarzenia do analityki:** wysłano, dostarczono, odbito, rezygnacja (według typu). Bez otwarć i kliknięć (D29).


---

## E8 Zaufanie i zgodność


E7 jest zatwierdzony i zapisany. E8 ma dwie części: mechanizmy w kodzie (dla agentów) i zadania, których agenci nie powinni wykonywać (treści prawne, umowy). Nie jestem prawnikiem, więc wymagania prawne poniżej to lista rzeczy do potwierdzenia, a nie gotowa interpretacja.

### Cztery decyzje do zatwierdzenia
| # | Decyzja | Rekomendacja | Dlaczego |
|---|---|---|---|
| D30 | Kto pisze regulamin i politykę prywatności | **zmienione przez D116:** agent przygotowuje projekty tekstów na podstawie tego, co serwis faktycznie robi (US-8.10), **prawnik je przegląda, zatwierdzasz Ty**; bez przeglądu i akceptacji teksty nie są publikowane | błąd w regulaminie platformy dla szkół jest kosztowny, a model językowy nie zastąpi porady prawnej |
| D31 | Jak pokazujemy zaufanie | **dwie osobne odznaki: „Oświadczenie artysty” i „Zweryfikowany przez serwis”, ze stroną opisującą dokładnie, co sprawdzamy**; nigdy nie sugerujemy sprawdzenia w rejestrach karnych | dyrektor nie może pomylić deklaracji artysty z naszą weryfikacją; przepisy o weryfikacji osób pracujących z dziećmi są niejasne ([Prawo.pl](https://www.prawo.pl/biznes/kogo-trzeba-sprawdzac-w-rejestrze-i-czy-mozna-przytulic-ucznia,529536.html)) |
| D32 | Ciasteczka | **analityka bez ciasteczek i tylko ciasteczka niezbędne, więc bez banera zgody** (do potwierdzenia z prawnikiem); gdyby pojawiły się inne, baner z równorzędnym „Odrzuć” | prostsza i bardziej przyjazna strona, mniej ryzyka |
| D33 | Usunięcie konta | **30 dni na cofnięcie, potem trwałe usunięcie danych i plików**; w historii drugiej strony zostaje „Użytkownik usunięty” | prawo do usunięcia danych, a jednocześnie szkoła nie traci historii swoich zapytań |

### Historie

**US-8.1 Dokumenty prawne (M1).**
- Regulamin, polityka prywatności i informacja o ciasteczkach są wersjonowane. Akceptacja przy rejestracji zapisuje wersję i datę (powiązane z US-1.1).
- Przy istotnej zmianie użytkownik po zalogowaniu widzi nową wersję i musi ją zaakceptować przed dalszym korzystaniem.

**US-8.2 Oświadczenia artysty (minimum w M1).**
- Oświadczenia:
  - o stosowaniu standardów ochrony małoletnich (wymagane do publikacji, D6);
  - o prawach do materiałów (D4) i zgodach na wizerunek (D7);
  - o formie rozliczenia;
  - o posiadaniu OC, opcjonalnie z datą ważności.
- Każde zapisane z datą i wersją treści. Na profilu pokazane jako „Oświadczenie artysty” (D31).
- Wygaśnięcie OC zdejmuje odznakę i wysyła przypomnienie.

**US-8.3 Weryfikacja artysty przez administratora (M4).**
- Lista kontrolna z jawnym zakresem: firma lub działalność istnieje (CEIDG, KRS albo oświadczenie o działalności nierejestrowanej), dane kontaktowe potwierdzone, materiały przejrzane.
- Odznaka „Zweryfikowany przez serwis” z datą. Strona „Co oznacza weryfikacja” opisuje dokładny zakres i to, czego nie sprawdzamy.

**US-8.4 Pakiet dokumentów dla szkoły (M4).**
- Po akceptacji oferty placówka może pobrać PDF z danymi artysty, jego oświadczeniami i zakresem weryfikacji, do włączenia do dokumentacji szkoły.
- Wzór oświadczenia przygotowuje agent (US-8.10), przegląda prawnik, zatwierdzasz Ty (D30, D116).

**US-8.5 Zgłaszanie treści (M4).**
- Przy każdym profilu, ogłoszeniu i wiadomości jest „Zgłoś” z listą powodów. Zgłaszający dostaje potwierdzenie, a autor treści uzasadnienie decyzji.
- Zgłoszenia trafiają do kolejki administratora (E9).
- Mechanizm ma spełniać wymagania unijnego aktu o usługach cyfrowych (DSA) dla usług hostingu, co trzeba potwierdzić z prawnikiem.

**US-8.6 Eksport i usunięcie danych (M4).**
- Użytkownik pobiera swoje dane jako plik ZIP z JSON i plikami.
- Usunięcie według D33, łącznie z plikami w magazynie i kopiami w zbiorze testowym E11.

**US-8.7 Retencja i minimalizacja (M4).**
- Zakończone zapytania i ogłoszenia archiwizowane po 24 miesiącach. Dzienniki techniczne przechowywane 90 dni.
- W analityce brak danych osobowych i skracane adresy IP.
- System nigdy nie wymaga podawania danych dzieci.

**US-8.8 Ciasteczka (M1).** Zgodnie z D32. Automatyczny test sprawdza, że strona nie ustawia ciasteczek innych niż niezbędne.

**US-8.9 Zadania dla Ciebie poza kodem.**
- Regulamin, polityka prywatności, wzór oświadczenia artysty i strona „Co oznacza weryfikacja”: projekty przygotowuje agent (US-8.10), Ty umawiasz jeden przegląd u prawnika (IT/RODO), poprawki wnosi agent, a ostateczną wersję akceptujesz Ty (D116).
- Umowy powierzenia z dostawcami (hosting, e-mail, AI, wideo).
- Rejestr czynności przetwarzania.
- Wymóg kontaktu i wymagania DSA dla serwisu.

Poza projektami dokumentów (US-8.10) te zadania nie trafią do kolejki agentów, a serwis nie może wystartować publicznie bez pierwszych trzech dokumentów po przeglądzie prawnika.

**US-8.10 Projekty dokumentów prawnych do przeglądu (M4, D116).**
- Agent przygotowuje po polsku: regulamin (z elementami DSA i P2B: punkt kontaktowy, zasady moderacji i zgłoszeń, uzasadnienia decyzji), politykę prywatności (administrator, cele, podstawy, odbiorcy, w tym OpenRouter i transfer poza UE z D59 i D60, okresy retencji z US-8.7, prawa osób), informację o ciasteczkach (D32), wzór oświadczenia artysty (US-8.2, D4, D6, D7), stronę „Co oznacza weryfikacja” (D31) i informację, że teksty profili generuje AI (AI Act, art. 50).
- Każde zdanie wynika z faktycznego działania kodu: agent podaje przy każdej sekcji, z którego modułu lub decyzji pochodzi, a w osobnym pliku zbiera listę otwartych pytań do prawnika (m.in. D32 bez banera, ustawa o ochronie małoletnich, DSA dla małej platformy, umowy powierzenia, transfer poza UE).
- Teksty trafiają do `apps/trust` jako wersje robocze, wyraźnie oznaczone „projekt, przed przeglądem prawnika”; publikacja wersji jest możliwa dopiero po akceptacji właściciela (D30).
- Po przeglądzie agent wnosi poprawki prawnika jako nową wersję i podaje różnice.
- Agent nie przedstawia projektów jako porady prawnej i nie usuwa uwag prawnika bez zgody właściciela.


---

## E9 Panel administratora


E8 jest zatwierdzony i zapisany. E9 zbiera w jednym miejscu wszystkie kolejki z poprzednich epików. Konto administratora ma dostęp do danych wszystkich użytkowników, więc dostaje mocniejsze zabezpieczenia.

### Cztery decyzje do zatwierdzenia
| # | Decyzja | Rekomendacja | Dlaczego |
|---|---|---|---|
| D34 | Logowanie administratora | **link lub kod z E1 plus drugi składnik (aplikacja z kodami TOTP)**; każde działanie w dzienniku | przejęcie konta administratora oznacza dostęp do wszystkich danych |
| D35 | „Zaloguj jako użytkownik” | **nie w MVP** | to częsty kierunek nadużyć i wycieków; do wsparcia wystarczy podgląd tylko do odczytu |
| D36 | Treść wiadomości między stronami | **widoczna tylko w zgłoszonych wątkach albo po wpisaniu uzasadnienia, zapisywanego w dzienniku** | minimalizacja dostępu do korespondencji (RODO) |
| D37 | Role administracyjne | **jedna rola administratora w MVP** | w pilocie administratorem jesteś Ty; role pośrednie (np. moderator) po pilocie |

### Historie

**US-9.1 Dostęp i dziennik działań.**
- Panel jest dostępny tylko dla kont administratora utworzonych z konfiguracji serwera (US-1.5), z drugim składnikiem (D34).
- Każde działanie (zatwierdzenie, odrzucenie, blokada, podgląd wiadomości, import) zapisuje kto, co, kiedy i dlaczego. Dziennika nie da się edytować z panelu.

**US-9.2 Pulpit z kolejkami.** Na pierwszym ekranie liczniki i listy:
- profile, które nie przeszły automatycznej naprawy (US-2.5);
- zgłoszone treści (US-8.5);
- ogłoszenia z flagą (US-6.2);
- placówki i artyści do weryfikacji.

Najstarsze sprawy są na górze, z oznaczeniem czasu oczekiwania.

**US-9.3 Przegląd profili.**
- Podgląd profilu z raportem walidatora i ocenami recenzenta (E11).
- Akcje: zatwierdź, poproś o poprawki (z komentarzem), ukryj. Artysta dostaje powiadomienie nr 17 z E7.

**US-9.4 Moderacja zgłoszeń i ogłoszeń.**
- Podgląd zgłoszonej treści i powodu zgłoszenia.
- Akcje: odrzuć zgłoszenie, ukryj treść, zablokuj autora, zawsze z uzasadnieniem dla autora (wymóg z US-8.5).

**US-9.5 Weryfikacja placówek.**
- Import CSV z RSPO z raportem: ile dodano, ile zaktualizowano, ile błędów.
- Ręczne zatwierdzanie placówek i łączenie duplikatów kont tej samej placówki (US-1.2).

**US-9.6 Weryfikacja artystów.** Lista kontrolna z US-8.3 i nadanie odznaki z datą.

**US-9.7 Użytkownicy i blokady.**
- Wyszukiwanie po nazwie i e-mailu, podgląd konta tylko do odczytu.
- Blokada z powodem: zablokowany użytkownik nie może się zalogować, jego profil i ogłoszenia znikają, a otwarte zapytania drugiej strony dostają status „anulowane przez serwis”. Odblokowanie przywraca stan.

**US-9.8 Podgląd zapytań i ogłoszeń.** Lista tylko do odczytu do wsparcia użytkowników. Treść wiadomości według D36.

**Należą też do panelu (opisane wcześniej):** słowniki (US-4.6) i ocena ludzka stron (US-11.6).

**Co zostaje poza E9:** rozbudowane raporty (te w E10), role moderatorów, „zaloguj jako”, masowe wysyłki do użytkowników.


---

## E10 Analityka pilota


E9 jest zatwierdzony i zapisany. E10 ma jedno zadanie: pod koniec pilota odpowiedzieć liczbami, czy kontynuować. Dlatego wszystko jest podporządkowane progom, które ustaliliśmy na początku.

### Trzy decyzje do zatwierdzenia
| # | Decyzja | Rekomendacja | Dlaczego |
|---|---|---|---|
| D38 | Gdzie trzymamy dane | **zdarzenia biznesowe (zapytanie, oferta, akceptacja) zapisuje serwer we własnej bazie; wizyty stron mierzy analityka bez ciasteczek, hostowana u nas lub w UE** | zdarzenia z serwera są pełne (blokery reklam ich nie zjadają), a analityka bez ciasteczek jest zgodna z D32 |
| D39 | Dane osobowe w zdarzeniach | **tylko identyfikatory pseudonimowe**, bez e-maili, nazw i treści | analityka nie powinna być kolejnym miejscem z danymi osobowymi; łatwiejsze usuwanie (D33) |
| D40 | Jak mierzymy gotowość płacenia | **krótka ankieta w serwisie plus Twoje rozmowy z artystami poza systemem** | to próg pilota („co najmniej 3 z 10”), a deklaracja w ankiecie bez rozmowy bywa myląca |

### Historie

**US-10.1 Katalog zdarzeń.**
- Jedna lista wszystkich zdarzeń z E1–E9 i E11 z nazwą, właściwościami i epikiem źródłowym, utrzymywana w repozytorium.
- Nowe zdarzenie w kodzie bez wpisu w katalogu nie przechodzi testów (US-10.6).

**US-10.2 Zbieranie.**
- Zdarzenia biznesowe zapisywane w tej samej transakcji co zmiana danych, więc nie gubią się przy błędach.
- Wizyty stron bez ciasteczek, ze skracanymi adresami IP (US-8.7).

**US-10.3 Pulpit pilota (w panelu administratora).**
- **Progi pilota z paskiem postępu:**
  - 50 opublikowanych profili;
  - 30 zapytań lub ogłoszeń w 2 miesiące;
  - co najmniej 30% z co najmniej 2 ofertami;
  - 5 potwierdzonych występów;
  - co najmniej 3 z 10 artystów deklarujących płatność.
- **Lejek artysty:** rejestracja, potwierdzenie, import lub materiały, generowanie, publikacja (z kompletnością przy publikacji).
- **Lejek placówki:** wizyta, zapytanie lub ogłoszenie, pierwsza oferta, akceptacja, potwierdzony występ.
- **Czasy:** do pierwszej oferty, do publikacji profilu.
- Filtr po województwie i okresie.

**US-10.4 Ankiety.**
- **Dla artystów:** po 30 dniach od publikacji albo po 3 zapytaniach jedno krótkie pytanie o gotowość płacenia (np. abonament 29, 49, 99 zł albo opłata za zapytanie), z możliwością pominięcia. Pokazujemy ją jednej osobie najwyżej raz.
- **Dla placówek:** po potwierdzonym występie jedno pytanie o zadowolenie (1–5) i opcjonalny komentarz. To też fundament późniejszych opinii (D10).

**US-10.5 Eksport.** Eksport zdarzeń i odpowiedzi z ankiet do CSV z zakresu dat, bez danych osobowych, do analizy poza systemem.

**US-10.6 Testy zdarzeń.** Testy sprawdzają, że każdy kluczowy krok przepływu (rejestracja, publikacja, zapytanie, oferta, akceptacja, potwierdzenie) zapisuje właściwe zdarzenie z wymaganymi polami.

### Gdzie jesteśmy w procesie
Po zatwierdzeniu E10 kończymy krok 3: mamy 11 epików funkcjonalnych (E1–E11) z historiami, kryteriami akceptacji i 40 decyzjami, wszystko zapisane w planie roboczym. Pozostaje E0 (fundament), który zależy od technologii. Następny będzie krok 4: wybór stosu technologicznego, a potem rozbijanie historii na zadania dla agentów, epik po epiku.


---

## E0 Fundament (wersja EC2, część chmurowa zawieszona przez D91)


Wybór jest zapisany. Jedna EC2 oznacza brak load balancera i zarządzanych kontenerów, więc kilka rzeczy, które Fargate robiłby za nas, trafia do E0: TLS na serwerze, wdrożenia bez SSH, łatanie systemu i procedura odtworzenia po awarii.

### Pięć decyzji do zatwierdzenia
| # | Decyzja | Rekomendacja | Dlaczego |
|---|---|---|---|
| D50 | Gdzie baza | **RDS PostgreSQL**, nie kontener na EC2 | automatyczne kopie i odtwarzanie do punktu w czasie; awaria EC2 nie dotyka danych; kosztuje mniej więcej 15–20 USD więcej (szacunek) |
| D51 | TLS i ruch | **Caddy na EC2 z automatycznymi certyfikatami Let's Encrypt; CloudFront tylko dla zdjęć i wideo** | bez load balancera (oszczędność około 20 USD), a pliki i tak idą przez CDN |
| D52 | Dostęp do serwera | **wyłącznie przez SSM Session Manager, bez otwartego portu SSH**; grupa bezpieczeństwa wpuszcza tylko 80 i 443 | brak kluczy SSH do zgubienia, a każda sesja jest zapisywana |
| D53 | Rozmiar instancji | **t4g.medium (ARM, 4 GB pamięci)** | worker uruchamia ffmpeg i Chromium do zrzutów ekranu, a 2 GB może nie wystarczyć |
| D54 | Środowiska | **`dev` tańsze (t4g.small, Postgres w kontenerze), na którym pracują agenci, i `prod` z RDS** | agenci testują infrastrukturę bez ryzyka dla danych produkcyjnych |

**Szacunkowy koszt miesięczny:** prod około 50–55 USD (EC2, RDS, publiczny adres IPv4, S3, CloudFront, Route 53, CloudWatch, sekrety), dev około 15–20 USD, razem około 65–75 USD. To liczby z pamięci, nie z cennika AWS. Sprawdzę je w kroku 5.

### Historie

**US-0.1 Szkielet aplikacji.**
- Projekt Django w `projects/<nazwa>/` z aplikacjami według epików: `accounts`, `institutions`, `artists`, `generator`, `catalog`, `inquiries`, `listings`, `notifications`, `compliance`, `adminpanel`, `analytics`, `quality_lab`.
- Ustawienia z zmiennych środowiskowych (dev, test, prod), język polski i strefa czasowa Europe/Warsaw.

**US-0.2 Środowisko lokalne.**
- Jedno polecenie uruchamia całość w Docker Compose: Postgres, web, worker, Mailpit (podgląd e-maili) i MinIO (lokalny odpowiednik S3).
- Dane testowe: syntetyczni artyści i placówki (zgodnie z D12, bez prawdziwych materiałów).

**US-0.3 CI w GitHub Actions** (wymagane do scalenia PR):
- formatowanie i lint (ruff), testy pytest z progiem pokrycia;
- sprawdzenie, czy migracje są kompletne;
- skan podatności zależności (pip-audit) i kodu (bandit);
- budowa obrazu, test E2E w Playwright, test dostępności (axe).

**US-0.4 Terraform.**
- Stan w S3 z blokadą.
- Moduły: sieć (EC2 w podsieci publicznej, RDS w prywatnej), EC2 (szablon, rola IAM, grupa bezpieczeństwa, stały adres IP), RDS, S3 i CloudFront, SES, ECR, Route 53, alarmy CloudWatch, AWS Budgets i rola OIDC dla GitHub Actions.
- Oddzielne konfiguracje dla `dev` i `prod`.

**US-0.5 Wdrożenie.**
- CI buduje obraz i wysyła go do ECR, a potem przez SSM Run Command (bez SSH) serwer pobiera nowy obraz, uruchamia migracje i restartuje usługi.
- Cofnięcie do poprzedniej wersji jednym poleceniem. Krótka przerwa przy wdrożeniu jest w pilocie akceptowalna.

**US-0.6 Zadania w tle i harmonogram.** Kolejka Procrastinate w Postgresie i zadania cykliczne: przypomnienia po 48 godzinach, wygasanie, pytania o potwierdzenie występu, dzienne zestawienia.

**US-0.7 Magazyn plików.** Pliki prywatne (materiały, PDF) dostępne przez podpisane linki z krótką ważnością. Pliki publiczne profili przez CloudFront.

**US-0.8 Logi, zdrowie i alarmy.**
- Logi w formacie JSON wysyłane do CloudWatch i adres sprawdzania zdrowia aplikacji.
- Alarmy: błędy 5xx, procesor, dysk, miejsce w RDS, opóźnienie kolejki.
- Zewnętrzne sprawdzanie dostępności (health check w Route 53).

**US-0.9 Kopie i odtwarzanie.**
- RDS: kopie automatyczne przez 7 dni i miesięczna migawka. S3 z wersjonowaniem.
- Spisana procedura odtworzenia po utracie EC2 (Terraform odtwarza serwer, wdrożenie przywraca aplikację), sprawdzona raz przed pilotem.
- Łatanie systemu: automatyczne aktualizacje bezpieczeństwa.

**US-0.10 Adapter AI.**
- Jeden interfejs do modeli z implementacją dla Amazon Bedrock i atrapą do testów, żeby testy nie wywoływały płatnego API.
- Każde wywołanie zapisuje model, tokeny, czas i koszt (dla E11).

**US-0.11 Konwencje dla agentów.**
- `CLAUDE.md` projektu: struktura, polecenia, zasady testów i migracji, zakaz sekretów w kodzie, definicja ukończenia.
- Szablon PR i szablon zadania, żeby każdy agent pracował tak samo.

### Co dalej
Po zatwierdzeniu E0 przechodzimy do kroku 5: wymagania niefunkcjonalne i bezpieczeństwo (w tym zasady dostępu agentów do AWS z poprzedniej wiadomości i sprawdzenie kosztów). Potem rozbijanie na zadania. Do założenia folderu i etykiety w kolejce nadal potrzebuję **nazwy projektu**, a do danych testowych **województwa pilota**.


---

## E0 zmiana: AI przez OpenRouter (US-0.10)

Zapisałem wyjątek: AI idzie przez OpenRouter, a cała reszta zostaje w AWS. Zmienia to historię US-0.10 (adapter AI) i decyzję D46.

### Co sprawdziłem w dokumentacji OpenRouter
- **Prywatność:** parametr `provider.data_collection: "deny"` kieruje zapytania tylko do dostawców, którzy nie zbierają danych, a `zdr: true` ogranicza je do punktów bez przechowywania danych. Na koncie da się też ustawić filtr polityki danych i listę dozwolonych dostawców jako górną granicę dla wszystkich zapytań ([dokumentacja trasowania](https://openrouter.ai/docs/features/provider-routing)).
- **Region UE:** adres `eu.openrouter.ai`, który trzyma przetwarzanie w UE, jest dostępny tylko w planach Business i Enterprise.
- **Koszt:** każda odpowiedź zawiera `usage.cost` (kwota pobrana z konta) i liczby tokenów, bez dodatkowych parametrów ([dokumentacja rozliczeń](https://openrouter.ai/docs/use-cases/usage-accounting)). To zasila rejestr generacji w E11.

### Nowa wersja US-0.10 „Adapter AI”
- Jeden interfejs z implementacją OpenRouter i atrapą do testów, więc testy w CI nie wydają pieniędzy.
- Każde zapytanie ma `data_collection: "deny"`. Zapasowi dostawcy są dozwoleni tylko z listy dozwolonych.
- `zdr: true` tam, gdzie wybrany model to wspiera. Sprawdzimy to w E11 przy wyborze modelu, bo może zawęzić wybór.
- Na koncie OpenRouter: włączony filtr polityki danych i lista dozwolonych dostawców.
- Model przypięty w konfiguracji, a jego wersja zapisywana w rejestrze generacji E11.
- Klucz API w AWS Secrets Manager, osobne klucze dla `dev` i `prod`, z limitem wydatków, jeśli Twój plan OpenRouter na to pozwala (tego nie sprawdzałem).

### Co to oznacza poza kodem
Dane artystów (teksty, zdjęcia do analizy) trafiają do OpenRouter, firmy z USA, i dalej do dostawcy modelu. To transfer danych poza UE, więc do US-8.9 (zadania dla Ciebie i prawnika) dochodzi umowa powierzenia z OpenRouter i podstawa transferu. Region UE byłby rozwiązaniem, ale wymaga planu Business, więc zostawiam go poza MVP.


---

## E0 podział: E0a lokalnie na pirx, E0b chmura


### Nowe kamienie milowe
| Kamień | Gdzie działa | Co obejmuje |
|---|---|---|
| **M1 „Artysta ma stronę”** | pirx, lokalnie | E0a, E1, E2, E3, E11 (rdzeń), z E8 mechanizmy zgód |
| **M2 „Szkoła znajduje i pyta”** | pirx, lokalnie | E4, E5, E7 (e-maile tylko do Mailpit) |
| **M3 „Szkoła ogłasza”** | pirx, lokalnie | E6 |
| **M-Chmura** | AWS | E0b: Terraform, wdrożenie, prawdziwe e-maile (SES), kopie, alarmy |
| **M4 „Pilot”** | AWS, publicznie | reszta E8, E9, E10, dokumenty prawne: projekt agenta (US-8.10), przegląd prawnika, Twoja akceptacja (D116) |

Do M-Chmura nie płacisz za AWS. Jedyny koszt to OpenRouter przy testach generatora (grosze na profil), a GitHub Actions w ramach darmowego limitu minut.

### E0a „Fundament lokalny” (teraz)
Bez zmian: szkielet Django (US-0.1), kolejka zadań (US-0.6), adapter AI z OpenRouter (US-0.10) i konwencje dla agentów (US-0.11). Zmienione albo nowe:
- **US-0.2 Środowisko w Docker Compose:** Postgres, web, worker, **MinIO** zamiast S3 i **Mailpit** zamiast prawdziwej wysyłki e-maili.
- **US-0.3 CI:** testy w GitHub Actions jak wcześniej, ale bez kroków wdrożenia do AWS.
- **US-0.7 Magazyn plików:** MinIO z tym samym interfejsem co S3, więc przejście na AWS zmieni tylko konfigurację.
- **US-0.12 Uruchomienie na pirx (nowe):**
  - porty wybrane tak, żeby nie kolidowały z usługami już działającymi na pirx (galeria zdjęć, phone-farm, Hermes), wpisane w pliku konfiguracyjnym;
  - baza, pliki i logi w `~/runtime/<projekt>`, nie w repozytorium, zgodnie z zasadami Twojego workspace'u;
  - usługi same wstają po restarcie serwera;
  - jedno polecenie do aktualizacji wersji (pobranie z `main` i restart).

### E0b „Chmura” (przed pilotem)
Terraform (US-0.4), wdrożenie przez SSM (US-0.5), CloudWatch i alarmy (US-0.8) oraz kopie i odtwarzanie (US-0.9). Decyzje D50–D54 (RDS, Caddy, SSM bez SSH, t4g.medium, dev i prod) obowiązują w tej fazie bez zmian, a sprawdzenie kosztów AWS przesuwam na moment jej startu.

### Cztery nowe decyzje do zatwierdzenia
| # | Decyzja | Rekomendacja | Dlaczego |
|---|---|---|---|
| D55 | Dostęp do aplikacji na pirx | **tylko w sieci lokalnej, ewentualnie przez prywatną sieć typu Tailscale; bez przekierowania portów na routerze i bez publicznych tuneli** | niedokończona aplikacja z kontami i plikami nie powinna być wystawiona z domowego serwera |
| D56 | Gdzie działa CI | **hostowane runnery GitHub Actions**; własny runner na pirx tylko, gdy zabraknie darmowych minut | testy w odizolowanym środowisku i bez dodatkowego obciążenia pirx |
| D57 | Dane na pirx | **tylko dane syntetyczne, e-maile wyłącznie do Mailpit, osobny klucz OpenRouter `dev` z niskim limitem** | brak prawdziwych danych osobowych przed dokumentami prawnymi (E8) i brak przypadkowych e-maili do prawdziwych szkół |
| D58 | Przenośność | **obrazy budowane dla amd64 i arm64, cała konfiguracja przez zmienne środowiskowe, MinIO zamiast S3 i Mailpit zamiast SES** | przejście z pirx na EC2 t4g (ARM) ma być zmianą konfiguracji, nie przebudową |

Jedna rzecz do sprawdzenia przy pierwszym zadaniu: architektura procesora pirx (zakładam amd64). D58 obsługuje obie, więc nie blokuje startu.


---

## Dane poza UE (D59, D60)


**Krótko: to nie blokuje biznesu, jeśli od początku zaprojektujemy, które dane w ogóle trafiają do AI.** Ryzyko jest umiarkowane i da się je ograniczyć do małego, dobrze opisanego wycinka. To moja ocena na podstawie dokumentów, nie porada prawna. Ostateczną konfigurację powinien potwierdzić prawnik (US-8.9).

### Stan prawny (sprawdzony dzisiaj)
- **DPF obowiązuje:** 3 września 2025 Sąd UE oddalił skargę na unijno-amerykańskie ramy ochrony danych (sprawa T-553/23). Odwołanie (C-703/25 P) czeka na rozstrzygnięcie, a w czerwcu 2026 nadal nie było wyroku ([WilmerHale](https://www.wilmerhale.com/en/insights/blogs/wilmerhale-privacy-and-cybersecurity-law/20251201-european-court-of-justice-to-review-challenge-to-eu-us-data-privacy-framework), [Baker McKenzie](https://connectontech.bakermckenzie.com/eu-us-data-privacy-framework-still-business-as-usual/)). Ramy mogą więc w przyszłości upaść, tak jak dwie poprzednie umowy.
- **OpenRouter nie opiera się na DPF, tylko na standardowych klauzulach umownych (SCC, moduł 2: administrator do podmiotu przetwarzającego).** Jego [umowa powierzenia](https://openrouter.ai/data-processing-agreement) obowiązuje każdego klienta, który zaakceptuje regulamin, więc nie trzeba planu firmowego. Ewentualne unieważnienie DPF nie uchyla bezpośrednio SCC.
- **Co obiecuje OpenRouter:** usuwa wejścia i wyjścia zaraz po wygenerowaniu odpowiedzi, jeśli nie włączysz zapisywania promptów. Daje opcję kierowania zapytań tylko do dostawców bez przechowywania danych (ZDR) i możliwość wykluczenia wybranych dostawców. Sam zaznacza, że nie gwarantuje, że dostawcy modeli tego przestrzegają.

### Dlaczego w Twoim projekcie ryzyko jest małe
Kluczowe jest to, **czyje dane i jakie**:
| Dane | Trafiają do AI? |
|---|---|
| Dane placówek, nauczycieli, zapytania, wiadomości, ogłoszenia | **nie, nigdy** |
| Dzieci | **nie**, system nie zbiera ich danych, a w MVP nie wysyłamy zdjęć do AI |
| Materiały marketingowe artystów (opisy, oferty, ceny), za zgodą | tak |
| Kontakty i nazwiska osób z materiałów artysty | **nie**, usuwane przed wysłaniem |

Artysta i tak chce te teksty opublikować w internecie. Szkoły, czyli instytucje publiczne, które mogą pytać o miejsce przetwarzania danych, dostaną prostą odpowiedź: „Dane placówek zostają w UE (AWS we Frankfurcie), a AI przetwarza tylko materiały reklamowe artystów, za ich zgodą”. To może być nawet argument sprzedażowy.

### Dwie decyzje do zatwierdzenia
| # | Decyzja | Rekomendacja |
|---|---|---|
| D59 | Minimalizacja danych dla AI | AI przetwarza tylko materiały artystów za zgodą; nigdy danych placówek, zapytań i wiadomości. Kontakty i nazwiska usuwane przed wysłaniem. W MVP **bez zdjęć w AI** (tylko metadane i opisy, co w naszym teście działało). Zapisywanie promptów w OpenRouter wyłączone, kierowanie tylko do dostawców ZDR. Transfer udokumentowany: SCC z umowy OpenRouter plus ocena skutków transferu przygotowana przez prawnika |
| D60 | Droga wyjścia | adapter AI (US-0.10) pozwala przełączyć się na model przetwarzany w UE, np. Amazon Bedrock we Frankfurcie albo region UE w OpenRouter (plan Business), samą zmianą konfiguracji, gdyby wymagała tego szkoła, regulator albo upadek podstaw transferu |

### Kiedy to stałoby się poważnym problemem
- Gdyby do AI trafiały dane szkół, wiadomości albo zdjęcia dzieci. D59 to wyklucza.
- Gdyby duży klient publiczny (np. miasto w programie dla wielu szkół) wymagał przetwarzania wyłącznie w UE. Wtedy uruchamiamy D60.
- Gdyby brakowało dokumentacji (polityka prywatności bez informacji o odbiorcach i transferze, brak oceny skutków transferu). To zadanie dla prawnika z US-8.9.

Podstawowe dokumenty, które trzeba mieć: polityka prywatności wskazująca OpenRouter jako odbiorcę i transfer do USA, akceptacja umowy OpenRouter, ocena skutków transferu i wpis w rejestrze czynności przetwarzania. Wszystkie są już w zadaniach dla Ciebie poza kodem.


---

## Krok 5: wymagania niefunkcjonalne i bezpieczeństwo (D61-D65)


D55–D60 są zatwierdzone. Poniżej wymagania, które będą obowiązywać wszystkie zadania. Każde da się sprawdzić testem albo kontrolą w CI. Kolumna „Faza”: **L** oznacza od początku na pirx, **C** dopiero w chmurze.

### Pięć decyzji do zatwierdzenia
| # | Decyzja | Rekomendacja |
|---|---|---|
| D61 | Standard bazowy | **OWASP ASVS (aktualna wersja), poziom 1 dla całości i wybrane wymagania poziomu 2** dla uwierzytelniania, kontroli dostępu i plików. Agenci dostają konkretną listę do odhaczania, a nie ogólne „ma być bezpiecznie” |
| D62 | Pliki użytkowników | **serwowane z osobnej domeny** (np. `media.<domena>`), nigdy z domeny aplikacji. Złośliwy plik nie może wtedy przejąć sesji użytkownika |
| D63 | Koszty AI | **globalny dzienny limit wydatków z automatycznym wyłącznikiem** (np. 20 zł na dzień w `dev`) plus limit na konto (D5) |
| D64 | Odtwarzanie w pilocie | **utrata danych najwyżej 24 godziny, przywrócenie w 4 godziny**. RDS z odtwarzaniem do punktu w czasie zwykle daje lepszy wynik, a jedna EC2 to świadomie przyjęty pojedynczy punkt awarii |
| D65 | Bramka przed pilotem | **automatyczny skan OWASP ZAP, testy macierzy uprawnień i lista kontrolna z D61**; zewnętrzny test penetracyjny opcjonalnie, zależnie od budżetu |

### Wymagania
| Obszar | Wymagania | Jak sprawdzane | Faza |
|---|---|---|---|
| **Logowanie i sesje** | kody i linki jednorazowe, ważne 15 min, przechowywane jako skrót; nowa sesja przy logowaniu; ciasteczka `Secure`, `HttpOnly`, `SameSite=Lax`; drugi składnik dla administratora (D34) | testy jednostkowe, test konfiguracji ciasteczek | L |
| **Uprawnienia** | domyślnie brak dostępu; każdy widok sprawdza właściciela obiektu (zapytanie, oferta, plik), żeby nie dało się podejrzeć cudzego zasobu przez zmianę numeru w adresie | **macierz uprawnień**: test dla każdej ścieżki i każdej roli | L |
| **Ochrona stron** | ochrona przed CSRF włączona; Content Security Policy bez skryptów wstawianych ręcznie (z nonce dla HTMX); w prod HSTS, `X-Frame-Options: DENY`, `Referrer-Policy`, `Permissions-Policy`; treści użytkowników zawsze escapowane | test nagłówków w CI | L (HSTS: C) |
| **Pliki** | rodzaj sprawdzany po zawartości, limity z D8, zdjęcia przetwarzane od nowa (usuwa metadane i ukryte treści), skan ClamAV, losowe nazwy, prywatne pliki tylko przez podpisane linki z krótką ważnością; ffmpeg z limitem czasu i pamięci | testy ze złośliwymi plikami próbnymi | L |
| **Import ze strony** | tylko `http` i `https`; blokada adresów prywatnych, lokalnych i metadanych serwera (np. `169.254.169.254`), także po przekierowaniach; najwyżej 3 przekierowania; limity czasu i rozmiaru z US-2.2 | testy SSRF z listą adresów zakazanych | L |
| **AI** | tekst ze stron artystów traktowany jako dane, nie polecenia (strona może zawierać próbę wstrzyknięcia instrukcji); AI nie ma żadnych narzędzi ani dostępu do bazy; wynik zawsze przechodzi schemat i walidator; D59 i D63 | testy z materiałami zawierającymi wstrzyknięte instrukcje | L |
| **Dane osobowe** | szyfrowanie bazy i plików w prod; TLS wszędzie w prod; brak danych osobowych w logach (filtr); analityka pseudonimowa (D39); retencja z US-8.7 | test filtra logów | L (szyfrowanie: C) |
| **Sekrety** | nigdy w repozytorium; lokalnie plik `.env` poza repo (np. w `~/runtime/<projekt>`); w prod Secrets Manager; skaner sekretów (gitleaks) w CI; osobne klucze `dev` i `prod` | CI blokuje PR z sekretem | L |
| **Zależności i obrazy** | wersje przypięte w pliku blokady z sumami kontrolnymi; pip-audit w CI; automatyczne PR z aktualizacjami; obrazy bazowe przypięte; kontenery bez uprawnień roota | CI | L |
| **Proces agentów** | agenci pracują na gałęziach i otwierają PR; zero zapisu bezpośrednio do `main`; każdy PR wymaga zielonego CI i Twojej akceptacji; agenci nie mają dostępu do sekretów `prod`; zmiany infrastruktury tylko przez PR z planem Terraform (D49) | ochrona gałęzi na GitHubie | L |
| **Logi i audyt** | zdarzenia bezpieczeństwa (logowanie, błędne kody, odmowa dostępu, działania administratora) w dzienniku audytu; logi 90 dni | testy zdarzeń | L |
| **Infrastruktura AWS** | D49–D52; wymuszone IMDSv2; tylko porty 80 i 443; szyfrowanie EBS, RDS i S3; CloudTrail włączony; OIDC dla CI; alarmy budżetu | `terraform plan` w PR i reguły skanera IaC (np. tfsec lub checkov) | C |
| **Wydajność** | strona odpowiada w czasie poniżej 500 ms dla 95% zapytań (bez AI); katalog poniżej 1 s (US-4.7); generowanie profilu poniżej 2 min (US-2.5); Lighthouse mobile co najmniej 85 | testy obciążeniowe i Lighthouse CI | L |
| **Dostępność i przeglądarki** | WCAG 2.1 AA bez błędów krytycznych (axe); dwie ostatnie wersje Chrome, Edge, Firefox i Safari, w tym iOS; od 360 px szerokości | axe i Playwright w CI | L |
| **Jakość kodu** | pokrycie testami co najmniej 80% dla logiki domenowej; każde kryterium akceptacji ma test; migracje odwracalne; ruff i formatowanie | CI | L |
| **Język i formaty** | interfejs po polsku, strefa czasowa Europe/Warsaw, kwoty w PLN w formacie polskim | testy | L |
| **Kopie i incydenty** | D64; procedura odtworzenia sprawdzona raz przed pilotem (US-0.9); spisany plan reakcji na wyciek: unieważnienie kluczy, zmiana sekretów, zgłoszenie do UODO w 72 godziny (Twoje zadanie) | ćwiczenie odtworzenia | C |

### Co dalej
Po zatwierdzeniu kończymy planowanie wysokiego poziomu. Następny etap to rozbicie na **zadania dla agentów**, epik po epiku, zaczynając od E0a. Każde zadanie wielkości jednego małego PR-a z szablonem: cel, kontekst, zakres w i poza, kryteria akceptacji, testy, zależności, definicja ukończenia.

Przed pierwszym zadaniem potrzebuję **nazwy projektu**, bo od niej zależy folder `projects/<nazwa>/` i etykieta `project:<nazwa>` w kolejce. Województwo pilota może poczekać do danych testowych w E1.
