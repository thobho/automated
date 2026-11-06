# Faza 3 – podsumowanie: usuwanie tarcia przy kupowaniu i zamawianiu

Napisane 2026-11-06 przez T16. Streszcza zadania T01–T15 fazy 3. Wszystkie liczby pochodzą z plików na tej gałęzi (link obok), szacunki są oznaczone jako szacunki. Pełna wersja angielska: [phase3-summary.md](phase3-summary.md).

## Najważniejsze

- **Żaden pomysł nie doszedł do pasma `5–15%`** szans na 10 000 zł miesięcznie zysku brutto lub opłat w 12 miesięcy. Wszystkie 10 opracowań kończy się na `<5%`.
- Po sceptycznym przeglądzie (T15) **zostały 4 pomysły**, 6 odpadło. Nie ma więc uczciwej „top 5”: niżej są 4 pozostałe plus jeden odrzucony, wyraźnie oznaczony jako „odrzucony, ale najbliżej”.
- Przegląd trzy razy trafiał na to samo: (1) jednorazowy zakup konsumencki zostawia 1–16 zł na zamówieniu, a klient z Google Ads kosztuje 50–125 zł (słabe źródła CPC); (2) paczka z Niemiec (cennik DHL UE, ok. 70–108 zł za 5–10 kg) zjada marżę na częściach z DE; (3) **żaden dostawca nie publikuje warunków dropshippingu, odsprzedaży ani afiliacji**, a do żadnego jeszcze nie pisaliśmy.
- Trzy z czterech pozostałych pomysłów rozstrzygną **darmowe maile do dostawców**. Pierwszy miesiąc: maile i jedna przedsprzedaż do sprzedawców Allegro, bez kodu i prawie bez reklam.

## 1. Metoda i zakres w liczbach

| Etap | Zadanie | Wynik | Plik |
|---|---|---|---|
| Baza: handel w Polsce | T02 | ~47 źródłowych ustaleń: marketplace'y, prowizje, paczki, zwroty, programy partnerskie | [research/poland/](../research/poland/ecommerce.md) |
| Wzorce tarcia | T03 | 22 przypadki zwycięzców, 10 wzorców (P1–P10), 7 porażek i „sufitów” | [friction-patterns.md](../research/global/friction-patterns.md) |
| Skany branż V1–V5 | T04–T08 | 201 firm w katalogu (V1 48, V2 42, V3 39, V4 37, V5 35) z 20 krajów | [catalogue/](../catalogue/V1-vehicle-parts.csv) |
| Popyt w Polsce | T09 | 114 sygnałów, 84 kandydatów; głównie podpowiedzi Google, bez wolumenów | [demand/](../demand/V1-vehicle-parts.md) |
| Test „czy da się znaleźć” | T10 | 87 trudnych do znalezienia rzeczy szukanych ręcznie (Ceneo, OLX, wyszukiwarka) | [findability/](../findability/V1-vehicle-parts.md) |
| Długa lista | T11 | 95 pomysłów w 20 tematach | [longlist.md](../ideas/longlist.md) |
| Krótka lista | T12 | 26 z szybką oceną, 69 odrzuconych z powodem | [shortlist.md](../ideas/shortlist.md), [rejected.md](../rejected.md) |
| Opracowania | T13–T14 | 10 pełnych opracowań | `ideas/<branża>/NNN-*.md` |
| Przegląd sceptyczny | T15 | 6 odrzuconych, 4 zostają; 131 linków, 0 martwych, 14 nieweryfikowalnych | sekcja **Devil's advocate** w każdym opracowaniu |

Ocena: 9 soczewek F1–F9 z wagami z [criteria.md](../method/criteria.md); wynik 2,8–3,4 daje `5–15%`, poniżej 2,8 daje `<5%`; pasmo spada o stopień, gdy ryzyka przeważają szanse o 6+ punktów albo jest nieosłonięte ryzyko wysokie × wysokie. T15 dodał regułę: pomysł odpada, gdy F4 (ekonomia jednostkowa) spada do 1, czyli zamówienie lub klient nie zwraca kosztu pozyskania z reklam ([CHANGELOG](../CHANGELOG.md)).

Szybkie oceny spadły o 0,34–0,99 pkt między krótką listą a końcem przeglądu (policzone z [shortlist.md](../ideas/shortlist.md)): każdy pomysł wyglądał lepiej, zanim go zbadano.

## 2. Test „czy da się znaleźć” w pięciu branżach

Do 3 prób na rzecz, 2026-11-06. **E** łatwo, **W** z trudem albo tylko używane/ogłoszenia, **N** nie znaleziono lub tylko za granicą.

| Branża | Rzeczy | E | W | N | Luka (W+N) | Gdzie były luki |
|---|---|---|---|---|---|---|
| [V1 części samochodowe](../findability/V1-vehicle-parts.md#verdict-table) | 17 | 7 | 6 | 4 | 59% | nowe marki chińskie, części zabudowy kamperów, niektóre quady, okna przesuwne do busów |
| [V2 dom, klimat, AGD](../findability/V2-home-climate-appliance.md#verdict-table) | 18 | 11 | 2 | 5 | 39% | moduły i części do wycofanego AGD; pompy ciepła marek dystrybutorskich |
| [V3 hobby](../findability/V3-hobby-niches.md#verdict-table) | 16 | 11 | 5 | 0 | 31% | używane części po kodzie (kołowrotki, maszyny do szycia), baterie holenderskich e-rowerów, pojedyncze klocki LEGO |
| [V4 usługi z logistyką](../findability/V4-services-with-logistics.md#verdict-table) | 19 | 4 | 10 | 5 | 79% | pogwarancyjna naprawa elektroniki markowej, naprawa kurtek puchowych, moduły audio (tylko za granicą) |
| [V5 zakupy firmowe](../findability/V5-small-business-buying.md#verdict-table) | 17 | 6 | 4 | 7 | 65% | części do sprzętu gastronomicznego, osierocone maszyny budowlane, części Juki |
| **Razem** | **87** | **39** | **27** | **21** | **55%** (policzone) | |

Na ile temu ufać:
- **Allegro nie było testowane** (HTTP 403 w T10 i T15), a zamiast google.pl używano ogólnej wyszukiwarki. Oba fakty **zawyżają** luki.
- **Późniejsze sprawdzenia osłabiły co najmniej 4 z 21 werdyktów N:** jest polski sklep z częściami gastronomicznymi (Gastroparts, Toruń; V5 #8 i #9), klocki do Jaecoo 7 sprzedają już Inter Cars i Iparts.pl (V1 #1), części Kaisai zamówisz w dziale serwisu dystrybutora (V2 #5). Reimo sprzedaje po polsku uszczelki okien Seitz/Dometic (V1 #17).
- Wniosek: rzeczy z numerem modelu lub części, które są dziś w sprzedaży, Polacy zwykle znajdują. Prawdziwe luki to **marki osierocone**, **części tylko u dystrybutora przez telefon** i **pogwarancyjna naprawa wysyłkowa**. To w większości małe, rzadkie zakupy.

## 3. Ranking wszystkich 10 opracowań

Kolejność wg oceny po T15. „Szybka” = krótka lista T12, „opracowanie” = T13/T14, „T15” = ocena końcowa ([shortlist.csv](../ideas/shortlist.csv)).

| Miejsce | Opracowanie | # | Model | Szybka → opracowanie → T15 | Status | Główny powód |
|---|---|---|---|---|---|---|
| 1 | [009 Dane „Pasuje do” dla sprzedawców części na Allegro i Shoper](../ideas/v1-vehicle/009-fitment-data-for-parts-sellers.md) | 19 | abonament B2B | 3,2 → 3,01 → **2,86** | zostaje, `<5%` | brak narzędzia, które uzupełnia „Pasuje do”; ~97 zł zysku na sprzedawcy miesięcznie, ale pozyskanie z reklam 400–1070 zł; Allegro może to wchłonąć |
| 2 | [001 Części do sprzętu gastronomicznego](../ideas/v5-small-business/001-catering-equipment-parts.md) | 81 | marża B2B | 3,5 → 2,79 → **2,64** | zostaje, `<5%` | Gastroparts i REPA (dawniej GEV) już sprzedają online; pierwsze zamówienie traci ~53 zł |
| 3 | [005 Części zabudowy kamperów](../ideas/v1-vehicle/005-camper-habitation-parts.md) | 8 | marża B2C | 3,3 → 3,00 → **2,63** | zostaje, `<5%` | Reimo dostarcza „tylko do Niemiec”; paczka DE→PL 91–108 zł daje ok. −2 zł na zamówieniu |
| 4 | [008 Części blacharskie do aut chińskich](../ideas/v1-vehicle/008-chinese-brand-collision-parts.md) | 1 | opłata za usługę | 3,2 → 2,67 → **2,57** | odrzucony (F8 = 1, T14) | telefony przy każdej sprawie rozbijają 40 h/mies.; importerzy trzymają zapas |
| 5 | [006 Części do pomp ciepła dla instalatorów](../ideas/v2-home-appliance/006-heat-pump-parts-for-installers.md) | 24 | marża B2B | 3,3 → 2,71 → **2,56** | zostaje, `<5%` | każda marka ma jednego dystrybutora, który sprzedaje części swoim instalatorom; realna marża 0–10%, ~45 zł na zamówieniu |
| 6 | [004 Diagnoza, potem część](../ideas/v2-home-appliance/004-diagnosis-then-part.md) | 36 | usługa + marża | 3,4 → 2,78 → **2,53** | odrzucony (T15) | ~16 zł na kliencie przy pozyskaniu 50–83 zł; Bosch i LG robią zdalną diagnozę |
| 7 | [003 Natychmiastowa wycena druku 3D](../ideas/v3-hobby/003-3d-print-instant-quote.md) | 52 | prowizja | 3,4 → 2,79 → **2,52** | odrzucony (T15) | 11 zł na zamówieniu przy pozyskaniu 75–125 zł; wtyczki Shopify/WooCommerce dają drukarniom wycenę po polsku |
| 8 | [002 Wycena szkody blacharskiej ze zdjęć](../ideas/v1-vehicle/002-body-damage-photo-quote.md) | 17 | opłata za lead | 3,5 → 2,88 → **2,51** | odrzucony (T15) | Oferteo ma kategorię blacharstwa; PZU i LINK4 wyceniają szkody ze zdjęć; ~0 zł na zapytaniu |
| 9 | [007 Używane moduły do pralek](../ideas/v2-home-appliance/007-used-washer-modules.md) | 33 | prowizja | 3,3 → 2,67 → **2,45** | odrzucony (T15) | 1–7 zł na zamówieniu; naprawa modułu wysyłkowo (~110 zł) jest tańsza |
| 10 | [010 Wędkarski box w abonamencie](../ideas/v3-hobby/010-fishing-subscription-box.md) | 53 | abonament B2C | 3,1 → 2,40 → **2,28** | odrzucony (T15) | 7–9 zł na boxie przy pozyskaniu 20–120 zł; amerykański odpowiednik sprzedał aktywa po 56 mln USD |

## 4. Top 5 do walidacji (4 pozostałe + 1 odrzucony)

| # | Pomysł | Ocena, pasmo | Status | Pierwszy krok (darmowy) | Budżet reklam | Sukces w 2 tygodnie | Zabija pomysł |
|---|---|---|---|---|---|---|---|
| 4.1 | [009 Dane „Pasuje do”](../ideas/v1-vehicle/009-fitment-data-for-parts-sellers.md) | 2,86, `<5%` | zostaje | 30 darmowych raportów dla sprzedawców Allegro + pytanie do Cairo o licencję TecDoc | 0 zł (ok. 50 zł na wywołania modelu) | ≥3 z 30 na płatny pilot po 149 zł/mies., ≥80% dopasowań przyjętych | <3 z 30; <80% dopasowań; licencja >2000 zł/mies. |
| 4.2 | [001 Części gastro](../ideas/v5-small-business/001-catering-equipment-parts.md) | 2,64, `<5%` | zostaje | maile do Gastroparts, REPA, Parts Town o rabat dla odsprzedawcy | 250 zł (dopiero po rabacie ≥15%) | ≥5 zapytań ze zdjęciem; klienci płacą 15–20% ponad cenę Gastroparts | brak rabatu ≥15% w 3 tygodnie; <5 zapytań; klienci idą do Gastroparts |
| 4.3 | [005 Części do kamperów](../ideas/v1-vehicle/005-camper-habitation-parts.md) | 2,63, `<5%` | zostaje | maile do Frankana, Reimo (warunki **dealera**) i 2 dealerów Knaus/Hymer w DE | 200 zł, **w sezonie (marzec–kwiecień 2027)** | ≥15 zapytań o części; <połowa tylko u dealera; marża ≥20% po transporcie | brak dostawcy z wysyłką do PL przy ≥20%; <15 zapytań; jedyna droga to dealer z zapasem |
| 4.4 | [006 Części do pomp ciepła](../ideas/v2-home-appliance/006-heat-pump-parts-for-installers.md) | 2,56, `<5%` | zostaje | maile do Klima-Therm, Refsystem, przedstawiciela Gree, CNC Pompy Ciepła + 15 telefonów do instalatorów | 250 zł (po rabacie) | ≥1 dystrybutor daje rabat; ≥5 z 15 instalatorów widzi problem; ≥5 zapytań z reklam | brak rabatu; <5 z 15; <5 zapytań |
| 4.5 | [004 Diagnoza, potem część](../ideas/v2-home-appliance/004-diagnosis-then-part.md) | 2,53 | **odrzucony, ale najbliżej** | strona z darmową diagnozą AI i przyciskiem „rozmowa z serwisantem 39 zł” | 250 zł | ≥3% płaci; serwisant potwierdza ≥40% diagnoz; hurtownia daje ≥15% | jak w sukcesie, odwrotnie |

Dlaczego 4.5 jest odrzucony: T15 policzył ~16 zł zysku na kliencie przy pozyskaniu 50–83 zł, a Bosch i LG już diagnozują zdalnie. #1 (008) ma wyższą ocenę, ale odpadł na godzinach założyciela (F8 = 1), czego żaden test nie zmieni. Tuż za 004 są #52 (2,52) i #17 (2,51). Uruchamiać 4.5 tylko, jeśli 4.1–4.4 zawiodą.

### Skrypt ręcznej obsługi (krótko)
- **009:** wybierasz ręcznie w przeglądarce 30 sprzedawców z wieloma ofertami motoryzacyjnymi bez „Pasuje do” (agent dostaje 403). Dla każdego 20 ofert, model proponuje listę pojazdów z identyfikatorami Allegro ([dokumentacja API](https://developer.allegro.pl/compatibility_list)). Wysyłasz raport „tych ofert nie widać w wyszukiwaniu po VIN, to byśmy dodali” i propozycję pilota. Liczysz przyjęte i odrzucone dopasowania.
- **001:** czytasz tabliczkę ze zdjęcia, numer części z katalogu dystrybutora, wycena z terminem w 2 h, płatność przelewem lub BLIK z fakturą VAT, zamówienie ręcznie, dostawca wysyła do restauracji. Notujesz, czy pisze restauracja, czy serwisant.
- **005:** rozpoznajesz markę zabudowy i część ze zdjęć, wycena w 24 h z **osobno pokazanym transportem** (darmowa wysyłka z DE daje ok. −2 zł), zamówienie u dostawcy, on wysyła.
- **006:** tabliczka + kod błędu → numer części, zapytanie do dystrybutora mailem lub telefonem, cena z marżą i terminem, płatność, dostawca wysyła do instalatora. Mierzysz czas na zamówienie (powyżej 20 minut rozbija limit 40 h przed 100 zamówieniami).
- **004:** model proponuje uszkodzoną część, serwisant płatny za rozmowę potwierdza, część zamawiana ręcznie w CzęściAGD.pl. Tylko starsze, niepodłączone i marketowe pralki.

**Niezbadane, może warte opracowania przed testem:** z krótkiej listy nigdy nie opisano #84 (części Juki dla szwalni z okolic Łodzi), #87 (aplikacja zamówień restauracja–hurtownia), #67 (naprawa kurtek puchowych wysyłkowo), #72 (naprawa modułów audio wysyłkowo); mają szybką ocenę 3,2. Każdy opisany pomysł tracił 0,34–0,99 pkt, więc pewnie też skończą na `<5%`.

## 5. Które modele biznesowe mają sens

| Model | Pomysły | Zysk przed kosztem pozyskania | Ocena |
|---|---|---|---|
| Prowizja / afiliacja, konsument | 003, 007 | 1–11 zł na zamówieniu; afiliacja na częściach ~3–8%, tylko nowi klienci, niezweryfikowane ([monetisation](../research/poland/monetisation.md)) | nie działa na płatnym ruchu |
| Opłata za lead, konsument | 002 | ~0 zł | nie działa; Oferteo i Fixly mają ten format |
| Usługa + marża, jednorazowo | 004, 008 | ~16 zł (004); 008 pada na godzinach | nie działa na płatnym ruchu |
| Abonament konsumencki | 010 | 7–9 zł na boxie; Allegro Smart! kosztuje 59,90 zł rocznie | nie działa: konsument nie płaci abonamentu, żeby raz coś znaleźć |
| Marża, konsument, z zagranicy | 005 | ok. −2 zł przy darmowej wysyłce z DE | tylko jeśli klient płaci transport i dostawca wysyła wprost; nieudowodnione |
| Marża na częściach, B2B | 001, 006 | 72 zł (001), 45 zł (006) | jedyny model marżowy z zyskiem na kolejnym zamówieniu, ale zależy od rabatów, których nikt jeszcze nie dał |
| Abonament B2B (oprogramowanie) | 009 | ~97 zł na sprzedawcy miesięcznie | **najlepszy na papierze**: powtarzalny, bez paczek i zwrotów; ryzyko to Allegro i licencje danych |

Twoja wyjściowa hipoteza (mały abonament) trzyma się **tylko dla profesjonalistów**. Pomysły konsumenckie działają tylko na darmowym ruchu (SEO, społeczności), a żadne opracowanie nie pokazało takiego kanału w skali.

## 6. Co sprawdzić najpierw

1. **W tym tygodniu, za darmo, ~6 h (szacunek):** wysłać wszystkie maile do dostawców naraz: Gastroparts, REPA, Parts Town (001); Klima-Therm, Refsystem, przedstawiciel Gree, CNC Pompy Ciepła (006); Frankana, Reimo – warunki dealera, 2 dealerów Knaus/Hymer (005); Cairo – czy dane o dopasowaniu z TecDoc można sprzedawać dalej i za ile (009).
2. **Tygodnie 1–3, ~50 zł, ~12–15 h:** przedsprzedaż 009 – 30 sprzedawców, 30 raportów, propozycja pilota. To jedyny test, który nie zależy od odpowiedzi dostawcy.
3. **Tydzień 2, za darmo, ~5 h:** 15 telefonów do instalatorów pomp ciepła (006).
4. **Tygodnie 3–4, 250 zł:** jeden test reklamowy, dla 001 albo 006, tylko jeśli dostawca dał warunki powyżej progu.
5. **Ty sam, jeden wieczór:** to, czego agent nie mógł sprawdzić – wyszukiwanie na Allegro w przeglądarce, Google Keyword Planner (wolumeny i CPC, wymaga logowania), stawki afiliacyjne w panelach sieci. To zastąpi najsłabsze liczby w tym raporcie.
6. **Marzec–kwiecień 2027, 200 zł:** test 005 w sezonie, tylko jeśli dostawca z DE zgodził się wysyłać.

Reguła decyzji: budować tylko to, co przejdzie próg sukcesu. Jeśli 009 przejdzie, idzie pierwszy (bez paczek, zwrotów i pracy fizycznej): MVP w grudniu–styczniu na stosie agentowym, Twój czas na płatnych pilotów. Jeśli żaden dostawca nie da warunków, a 009 nie przejdzie, przerwij research zza biurka. Faza 1 skończyła się jednym pomysłem w `5–15%`, fazy 2 i 3 żadnym. Następny krok to rozmowy z klientami w jednej branży, nie kolejny skan.

## 7. Pytania do Ciebie

1. Czy ~8 h pracy fizycznej miesięcznie to nadal limit? 005 może działać tylko jako dealer Reimo lub Frankana, czyli z krótkim trzymaniem towaru.
2. 009 i 006 wymagają telefonów do firm (8–20 h miesięcznie wg szacunków z opracowań). Chcesz to robić?
3. Maile do dostawców: z Twojej firmy czy z nowej marki? Hurtownie zwykle odpowiadają zarejestrowanym firmom.
4. Jeśli testy zawiodą: opracować cztery niezbadane pomysły (#84, #87, #67, #72) czy przejść do rozmów z klientami?

## 8. Ograniczenia (uczciwie)

- **Allegro niesprawdzone** (403 w T10 i T15), więc luki są zawyżone, a konkurencja zaniżona.
- **Brak prawdziwego Google:** ogólna wyszukiwarka zamiast google.pl; przy usługach V4 nie używano Map Google, Booksy ani Fixly.
- **Popyt to słabe dowody:** podpowiedzi Google, bez wolumenów, bez Google Trends i bez wielkości grup na Facebooku.
- **CPC i konwersje słabe:** jedyne polskie źródło CPC (Ardura Lab) nie podaje metody; konwersje z benchmarków USA i bloga bez źródła. Na nich stoi każdy koszt pozyskania.
- **Wskaźniki zwrotów pożyczone:** 15–25% z bloga o częściach samochodowych, 13% błędnych części z amerykańskiej organizacji branżowej, oba ze streszczeń wyszukiwarki.
- **Warunki dostawców niezweryfikowane:** nikt nie był pytany, nikt nie publikuje warunków; każda marża 15–25% to szacunek.
- **Ceny paczek katalogowe:** DHL UE to cennik detaliczny; stawki umowne niższe, niesprawdzone. Kursy walut szacunkowe.
- **Wiele faktów ze streszczeń wyszukiwarki**, nie z otwartych stron (opracowania zaznaczają to przy każdym wierszu); 14 linków nieweryfikowalnych po T15 ([PROGRESS.md](../PROGRESS.md)).
- **Wielkość grup docelowych przeważnie bez źródła:** liczba sprzedawców motoryzacyjnych na Allegro, instalatorów pomp ciepła, restauracji kupujących części same, flota kamperów w Polsce.
- **Jedno przejście, jeden dzień:** wszystkie zadania 2026-11-06, wykonane przez agenta, z jednym przeglądem. Nic nie było testowane na prawdziwych klientach.
