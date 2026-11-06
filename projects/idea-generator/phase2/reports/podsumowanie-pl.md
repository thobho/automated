# Faza 2 – podsumowanie: innowacyjne produkty LLM do przeniesienia do Polski

Napisane 2026-11-06 (T25). Streszcza zadania T01–T24 fazy 2. Liczby są policzone z plików na tej gałęzi. Szacunki są oznaczone. Pełna wersja angielska: [phase2-summary.md](phase2-summary.md).

## Najważniejsze
- Faza 2 dała pomysły bardziej innowacyjne niż faza 1, ale nie mocniejsze.
- Po krytycznym przeglądzie (T24) tylko **jeden** pomysł ma szansę `5–15%` na 10 000 PLN MRR w 12 miesięcy: [011 Agent porównujący OWU dla małych brokerów](../ideas/sme-ops/011-broker-owu-comparison.md) (wynik 3,2).
- Wszystkie inne przejrzane pomysły mają `<5%`.
- Z 24 opisów 10 odrzucono lub połączono z innymi.
- Przegląd wciąż trafiał na dwie przeszkody:
  - polski gracz już ma tę funkcję albo doda ją w jednym wydaniu (Comarch, Wolters Kluwer, Docplanner, Allegro);
  - państwo daje to samo za darmo (MOS 2.0, mObywatel, e-mapa, Twój e-PIT).
- Żaden pomysł nie uzasadnia pisania kodu przed testem.
- Następny miesiąc: pięć tanich testów z sekcji 4. Jeśli wszystkie padną, kończymy research zza biurka i robimy wywiady z klientami (sekcja 9).

## 1. Metoda w 5 punktach
1. Baza o Polsce: demografia (50 ustaleń, 12 czynników popytu), rynek AI, 53 lokalne „fosy” ([research/poland/](../research/poland/demography.md)).
2. Listy trendów i skany 51 krajów w 10 regionach. Szukanie po angielsku, polsku i w językach lokalnych. Każdy produkt to wiersz katalogu z trakcją i sygnałami trwałości.
3. 531 produktów → 69 tematów ([THEMES.md](../themes/THEMES.md)). Dla każdego tematu werdykt luki w Polsce: otwarta, częściowa, zajęta.
4. 167 pomysłów ([longlist.md](../ideas/longlist.md)) → 59 z szybką oceną ([shortlist.csv](../ideas/shortlist.csv)) → 24 pełne opisy → niezależny przegląd „adwokata diabła”.
5. Dziewięć soczewek z wagami ([criteria.md](../method/criteria.md)) daje wynik i przedział szans. Potem reguła §4: jeśli ryzyka przeważają szanse o 6+ albo jest ryzyko wysokie × wysokie bez łagodzenia, spadek o jeden przedział. Ta reguła zepchnęła 13 z 14 pozostałych pomysłów do `<5%`.

## 2. Liczby

**Zasięg**

| Co | Ile | Jak liczone |
|---|---|---|
| Kraje | 51 z 51 | kolumna `country` w katalogu; wszystkie „done” w [countries.md](../method/countries.md) |
| Kraje z <5 produktami (z uzasadnieniem) | 11 | LU, IS, GR, MT, CY, SI, HR, QA, KW, BH, CR |
| Produkty w katalogu | 531 | 104 globalne (R0) + 427 regionalnych |
| B2B / B2C / B2B2C / B2G | 387 / 112 / 29 / 3 | kolumna `b2b_b2c` |
| „Działa po polsku?” = nieznane | 421 z 531 (79%) | kolumna `works_in_polish` |
| Tematy | 69 | TH01–TH69 |
| Werdykty luki | 7 otwarte, 30 częściowe, 32 zajęte | README w [A](../poland-check/A/README.md), [B](../poland-check/B/README.md), [C](../poland-check/C/README.md) |
| Unikalne URL źródeł | 2 305 | grep po wszystkich plikach fazy 2 |

**Lejek**

| Etap | Ile |
|---|---|
| Longlista | 167 |
| Odrzucone w T20 | 61 |
| Połączone w T20 | 47 |
| **Shortlista** | **59** |
| **Pełne opisy** | **24** |
| **Odrzucone w przeglądzie** | **7** (009, 015, 018, 019, 020, 022, 024) |
| **Połączone w przeglądzie** | **3** (006 → 001; 007 i 017 → 002) |
| **Opisy, które przetrwały** | **14** |
| Z shortlisty, nigdy niebadane głębiej | 35 |
| Wszystkie odrzucenia i połączenia | 118 linii w [rejected.md](../rejected.md) |

- Na shortliście 18 wierszy ma `5–15%`, 41 ma `<5%`.
- Z tych 18 tylko jeden to przejrzany opis (011). Pozostałe 17 to szybkie oceny bez reguły §4.
- Traktuj je jako raczej `<5%`: 23 z 24 opisów skończyły na `<5%`.
- Faza 1 też skończyła się jednym pomysłem w `5–15%` ([phase1-summary.md](../../reports/phase1-summary.md)).
- Pomysły z fazy 2 są bardziej „LLM-native” (L1 = 4 w 11 z 14 opisów). Ale popyt w Polsce (L5) i dystrybucja (L8) są równie słabe jak w fazie 1.

## 3. Top 20 po przeglądzie
Bez odrzuconych i połączonych. 14 opisów ma oceny po przeglądzie. 6 wierszy to najlepsze szybkie oceny bez opisu (link do pliku z analizą luki). Szybkie oceny zwykle spadały po badaniu.

| # | Pomysł | Wynik | Szansa | Status | Uwaga |
|---|---|---|---|---|---|
| 1 | [002 Teczka legalizacyjna (MOS dla agencji)](../ideas/employment-migration/002-teczka-legalizacyjna.md) | 3,6 | <5% | opis | najmocniejsza fosa; MOS sam wskaże załączniki, więc MVP: załącznik pracodawcy, korekty, terminy |
| 2 | [001 Raport ryzyk KW i działki](../ideas/property/001-kw-plot-risk-report.md) | 3,4 | <5% | opis (+006) | nikt nie sprawdził darmowego ChatGPT na prawdziwym odpisie |
| 3 | [004 Asystent akt dla kancelarii odszkodowawczych](../ideas/legal-compliance/004-claim-file-assistant.md) | 3,4 | <5% | opis | wzorzec EvenUp; liczba kancelarii nieznana |
| 4 | [012 Kontrola rozliczeń NFZ](../ideas/health-care/012-kontrola-rozliczen-nfz.md) | 3,3 | <5% | opis | najgłębsza fosa; wymaga danych przychodni |
| 5 | [011 Porównanie OWU dla brokerów](../ideas/sme-ops/011-broker-owu-comparison.md) | 3,2 | **5–15%** | opis | jedyny w 5–15% |
| 6 | [005 AI biuro zarządcy](../ideas/property/005-ai-biuro-zarzadcy.md) | 3,2 | <5% | opis | dane mają dostawcy portali |
| 7 | [013 Szkice tłumaczeń przysięgłych](../ideas/employment-migration/013-sworn-translation-drafts.md) | 3,2 | <5% | opis | tani test; liczba tłumaczy nieznana |
| 8 | [016 Asystent klienta biura](../ideas/accounting-tax/016-asystent-klienta-biura.md) | 3,2 | <5% | opis | Comarch ma agentów dopasowania banku |
| 9 | [003 Karta usług opiekuńczych](../ideas/health-care/003-karta-uslug-opiekunczych.md) | 3,1 | <5% | opis | SeniorApp po stronie gminy |
| 10 | [014 Sekretariat PISP](../ideas/legal-compliance/014-sekretariat-pisp.md) | 3,1 | <5% | opis | Wolters Kluwer ma PISP i Libra AI |
| 11 | [021 Licencja szkolna dla pedagogów](../ideas/education/021-school-pedagogue-licence.md) | 3,1 | <5% | opis | przewodnik ZPE zakazuje AI przy WOPFU |
| 12 | [023 Oferta z maila (hurtownie)](../ideas/sme-ops/023-oferta-z-maila.md) | 3,1 | <5% | opis | najczystsza luka; popyt nieznany |
| 13 | L088 Raport CMA z RCN dla pośredników ([B/TH57](../poland-check/B/TH57-real-estate-agency-investor-tools.md)) | 3,1 | 5–15% (szybka) | tylko szybka ocena | Otodom może to dodać |
| 14 | [008 Wycena z notatki (instalatorzy)](../ideas/property/008-wycena-z-notatki.md) | 3,0 | <5% | opis | potrzebny partner: hurtownia lub producent |
| 15 | [010 Teczka sprzedażowa](../ideas/accounting-tax/010-teczka-sprzedazowa.md) | 3,0 | <5% | opis | jednorazowy zakup |
| 16 | L033 Wstępna selekcja kandydatów dla agencji ([A/TH33](../poland-check/A/TH33-ai-recruiting-interviews-screening.md)) | 3,0 | 5–15% (szybka) | tylko szybka ocena | AI Act: rekrutacja |
| 17 | L106 Skryba dla fizjoterapeutów ([A/TH01](../poland-check/A/TH01-ambient-clinical-scribe.md)) | 3,0 | 5–15% (szybka) | tylko szybka ocena | Heidi i Noa działają po polsku |
| 18 | L046 Wiedza o Polsce + B2 do obywatelstwa ([B/TH39](../poland-check/B/TH39-national-migration-exam-prep.md)) | 3,0 | 5–15% (szybka) | tylko szybka ocena | zależy od projektu ustawy |
| 19 | L010 Urzędowa skrzynka biura ([A/TH17](../poland-check/A/TH17-agents-accounting-tax-firms.md)) | 3,0 | 5–15% (szybka) | tylko szybka ocena | automatyczny dostęp do ZUS PUE może łamać regulamin |
| 20 | L163 Testy jakości polskich voicebotów ([A/TH24](../poland-check/A/TH24-local-language-voice-cs-agents.md)) | 2,9 | 5–15% (szybka) | tylko szybka ocena | za mały rynek |

## 4. Top 5 do walidacji
**Jak wybrane.** Tylko opisy, które przetrwały. Liczyły się: przedział i wynik, fosa nienaruszona w przeglądzie, test rozstrzygający w tydzień za ≤200 PLN.
- [012](../ideas/health-care/012-kontrola-rozliczen-nfz.md) ma wyższy wynik, ale bez danych przychodni nie da się go przetestować. Jest w „dzikich kartach” (sekcja 7).
- Rezerwowy: [013](../ideas/employment-migration/013-sworn-translation-drafts.md). Pierwszy krok nic nie kosztuje: policz tłumaczy ukraińskiego na liście Ministerstwa Sprawiedliwości.

Wszystkie pięć to B2B. Wszystkie wymagają telefonów. Każdy test to „concierge”: robisz ręcznie z pomocą LLM, nic produkcyjnego.

Oznaczenia przy szansach i ryzykach: prawdopodobieństwo × wpływ, gdzie W = wysokie, Ś = średnie, N = niskie.

### 4.1 [011 Agent porównujący OWU dla małych brokerów](../ideas/sme-ops/011-broker-owu-comparison.md) – 3,2, `5–15%`
- **Dlaczego:** jedyny pomysł, który zachował `5–15%` (szanse 19, ryzyka 24, brak ryzyka W×W). Czysta luka: brak polskiego i zachodniego narzędzia dla brokera. Wystarczy ~25 biur po 399 PLN/mies.
- **Wzorzec z Zachodu:** FurtherAI (USA), 25 mln USD seria A od a16z (2025-10). Handle (USA/Meksyk), 6 mln USD seed (2026-03), 75+ brokerów. Segura (Brazylia), 8 mln USD seed. Dane od firm, brak danych o retencji.
- **Polska przewaga:** OWU każdego ubezpieczyciela porównane klauzula po klauzuli. Analiza potrzeb klienta (APK) z ustawy o dystrybucji ubezpieczeń. Zapytania do underwriterów mailem. Słownictwo: OC przewoźnika (CMR / krajowe), franszyza integralna / redukcyjna. Publiczny rejestr KNF = pełna lista kontaktów.
- **3 szanse:** mało klientów wystarcza do sprzedaży przez założyciela (Ś×Ś). Biblioteka klauzul OWU rośnie z każdym klientem (Ś×Ś). Odnowienia OC przewoźnika dają stałe użycie (Ś×Ś).
- **3 ryzyka:** przeoczone wyłączenie = odpowiedzialność brokera, więc brak zaufania (Ś×W). Mali brokerzy robią za mało polis firmowych (Ś×W). Konserwatywni klienci i 40 h/mies. = wolna sprzedaż (W×Ś). Do obserwacji: Compensa i PZU automatyzują swoją stronę tych samych zapytań.
- **Najbardziej ryzykowne założenie:** małe biuro brokerskie robi ≥5 polis firmowych miesięcznie przez maile i zaufa tabeli AI na tyle, by zapłacić.
- **Plan (5 dni, ≤100 PLN):**
  1. Dzień 1: pobierz aktualne OWU OC przewoźnika 6 ubezpieczycieli. Z LLM zrób tabelę porównawczą z cytatem (strona, paragraf) w każdej komórce. Sprawdź ręcznie każdą komórkę. Zapisz trafność.
  2. Dzień 1: przeczytaj raport KNF za 2024 i zapisz aktualną liczbę brokerów (opis ma tylko dane z 2017).
  3. Dzień 2: wybierz 40 małych biur z rejestru KNF (mazowieckie, wielkopolskie, łódzkie). Wyślij krótki mail z anonimową tabelą: „Chcesz to przy następnej polisie OC przewoźnika? Pierwsza za darmo”.
  4. Dni 3–5: dzwoń. Pytaj: ile polis firmowych miesięcznie, ile trwa porównanie, za jakie oprogramowanie płacą, czy 399 PLN/mies. jest OK. Kto przyśle prawdziwe zapytanie, dostaje porównanie za darmo.
  - **Co zbudować:** tylko prompt, schemat JSON dla OWU i arkusz.
  - **Idziemy dalej, gdy:** ≥3 rozmowy z 40 maili **i** ≥2 brokerów z ≥5 polisami firmowymi/mies. **i** ≥1 przysyła prawdziwe zapytanie **i** trafność tabeli ≥95% po dwóch poprawkach.
  - **Stop, gdy:** <3 rozmowy z 40 maili, albo mediana <5 polis/mies., albo trafność <95%.

### 4.2 [002 „Teczka legalizacyjna”: akta MOS dla agencji](../ideas/employment-migration/002-teczka-legalizacyjna.md) – 3,6, `<5%`
- **Dlaczego:** najwyższy wynik i najmocniejsza fosa (L4 = 5). Wchłonął [007](../ideas/accounting-tax/007-pit-assistant-foreign-employees.md) i [017](../ideas/employment-migration/017-mos-bez-stresu.md) jako dodatki. Spadł do `<5%`, bo przepisy często się zmieniają (ryzyko W×W), a projekt ustawy UD163 każe MOS samemu pokazywać wymagane załączniki.
- **Wzorzec z Zachodu:** tylko USA, wczesny etap. Alma (17 mln USD seria A, data niezweryfikowana), CaseBlink (2 mln USD, 2025-03), Visalaw.ai (1,6 mln USD). Brak danych o przychodach.
- **Polska przewaga:** MOS 2.0 jedynym kanałem od 2026-04-27 (bez API). Okno CUKR: 2026-05-04 do 2027-03-04. 16 urzędów wojewódzkich z różną praktyką. Kary 3 000–50 000 PLN. Ponaglenie z art. 37 KPA. KRAZ: 8 550 agencji (koniec 2024).
- **3 szanse:** fala CUKR = hurtowy popyt pracodawców (Ś×W). Baza praktyk urzędów od agencji jako zasób sieciowy (Ś×W). Kary sprzedają tablicę terminów działom HR (Ś×Ś).
- **3 ryzyka:** częste zmiany MOS i praktyki urzędów, zła lista kosztuje sprawę (W×W). Agencje nie chcą narzędzia, które spłaszcza ich wiedzę (Ś×W). Państwo samo podpowiada w MOS (W×Ś).
- **Najbardziej ryzykowne założenie:** agencje zatrudnienia (nie agencje legalizacyjne) zapłacą ~399 PLN/mies. za załącznik pracodawcy, korekty i tablicę terminów.
- **Plan (5 dni, ≤100 PLN):**
  1. Dzień 1: pobierz KRAZ. Wybierz ~100 agencji z mazowieckiego i wielkopolskiego, które piszą o cudzoziemcach. Wolą agencje zatrudnienia niż czyste agencje legalizacyjne.
  2. Dzień 1: przygotuj ręcznie to, czego nie daje państwo: szkic Załącznika nr 1 z danych KRS/CEIDG i arkusz terminów na pracownika z przypomnieniem mailowym.
  3. Dni 2–3: dzwoń i pisz: „Załącznik i tablica terminów dla 5 Twoich pracowników, gratis w 24 h, potem 399 PLN/mies.”. Pytaj, który krok MOS boli najbardziej.
  4. Dni 3–5: rób ręcznie z ChatGPT. Zapisuj zaoszczędzone minuty i każdą zmianę w MOS.
  - **Co zbudować:** szablon arkusza i dwa prompty. Domena i narzędzie mailowe w razie potrzeby (~100 PLN).
  - **Idziemy dalej, gdy:** ≥5 agencji przysyła prawdziwe sprawy **i** ≥2 akceptują 399 PLN/mies.
  - **Stop, gdy:** <3 ze 100 odpowiadają, albo oszczędność <30 min na sprawę, albo zmiany MOS dwa razy psują listę w tygodniu testu.

### 4.3 [023 „Oferta z maila”: zapytania → oferty dla hurtowni technicznych](../ideas/sme-ops/023-oferta-z-maila.md) – 3,1, `<5%`
- **Dlaczego:** najczystsza luka i najlepiej udokumentowany wzorzec (L1 4, L2 4, L3 4). Przegląd: pozytywny test uzasadni podniesienie do `5–15%`. ChatGPT nie dopasuje „YDYp 3x2,5” do indeksu i grupy cenowej hurtowni bez katalogu. To najmocniejsza obrona przed wchłonięciem.
- **Wzorzec z Zachodu:** Parspec (USA), 31,5 mln USD, 4 z 5 największych dystrybutorów elektrycznych w USA, przychody ×4 w rok. Mercura (Niemcy), seed od TQ Ventures, SignalFire i Y Combinator, rentowna od startu, klienci w Europie i USA.
- **Polska przewaga:** konektory do Subiekta nexo/GT i Comarch Optima, często lokalnie na Windows. Skróty techniczne (YDYp, YKY, OMY), lokalne marki, własny indeks hurtowni zamiast EAN. Rodzinne hurtownie regionalne; instalatorzy wysyłają listy i zdjęcia mailem.
- **3 szanse:** wystarczy ~20 hurtowni, koszt widoczny (handlowcy 6–12 tys. PLN brutto) (Ś×Ś). Cena od użycia rośnie z wolumenem (Ś×Ś). Jeden konektor Subiekt/Optima obsłuży wiele hurtowni (Ś×Ś).
- **3 ryzyka:** właściciele nie widzą problemu wartego zapłaty (Ś×W). Złe dopasowania produktów = złe oferty (Ś×W). Rodzinne firmy kupują powoli i chcą wizyt (W×Ś). Sygnał stopu: polska strona lub ogłoszenie Mercury.
- **Najbardziej ryzykowne założenie:** wycena trwa dziś ≥10 minut, a LLM dopasuje polskie pozycje do indeksu z trafnością ≥85%.
- **Plan (5–7 dni, ≤100 PLN):**
  1. Dzień 1: lista 20 regionalnych hurtowni elektrycznych i HVAC (Google Maps, CEIDG/KRS po PKD 46.43/46.73/46.74).
  2. Dni 1–2: zadzwoń do 20. Pytaj: ile zapytań mailem dziennie, ile trwa oferta, kto ją robi. Poproś 5 o 50 anonimowych zapytań i eksport katalogu (CSV z Subiekta/Optimy).
  3. Dni 3–5: jednorazowy skrypt w Pythonie: wyciąganie pozycji z PDF/Excela/zdjęcia/tekstu do JSON, embeddingi katalogu, dopasowanie z pewnością, wycena w CSV. Oznacz ręcznie poprawne dopasowania i policz trafność.
  4. Dni 6–7: pokaż wyniki i zapytaj o płatny pilotaż: 499 PLN/mies. + 1 500 PLN wdrożenie.
  - **Co zbudować:** tylko skrypt dopasowania i tabelę wyników. Tokeny poniżej 50 PLN (szacunek z opisu).
  - **Idziemy dalej, gdy:** ≥3 hurtownie przysyłają próbki **i** trafność ≥85% **i** wycena trwa dziś ≥10 min **i** ≥1 pyta o płatny pilotaż.
  - **Stop, gdy:** <3 przysyłają próbki, albo trafność <85%, albo wycena trwa <10 min.

### 4.4 [004 Asystent akt dla kancelarii odszkodowawczych](../ideas/legal-compliance/004-claim-file-assistant.md) – 3,4, `<5%`
- **Dlaczego:** najmocniejszy wzorzec z Zachodu wśród pozostałych i prawdziwa lokalna warstwa danych. Przegląd: test z 50 kancelariami jest tani i rozstrzygający.
- **Wzorzec z Zachodu:** EvenUp (USA), 150 mln USD seria E przy wycenie >2 mld USD (2025-10), 2 000+ kancelarii, ARR ×2 rok do roku (dane firmy). Supio (USA), 60 mln USD seria B (2025-04), ARR ×4.
- **Polska przewaga:** zadośćuczynienie ustala sąd z praktyki (art. 445/446 KC), nie z rachunków medycznych. Rdzeń EvenUp się nie przenosi. W zamian: baza kwot z wyroków SAOS. Fundusz Kompensacyjny Zdarzeń Medycznych (1 574 wnioski w 2024). Polska dokumentacja medyczna.
- **3 szanse:** baza kwot z SAOS jako unikalny zasób (Ś×W). Rosnąca ścieżka FKZM (Ś×Ś). Kancelarie po sprawach frankowych przesuwają ludzi do odszkodowań (Ś×Ś).
- **3 ryzyka:** kancelarie już wklejają akta do ChatGPT (W×Ś). Mały, wrażliwy na cenę rynek (Ś×W). Brak zaufania do jednoosobowego dostawcy przy danych z art. 9 RODO (Ś×W).
- **Najbardziej ryzykowne założenie:** przedział kwot z SAOS daje tyle ponad darmową chronologię z Claude/Gemini, że kancelaria zapłaci ≥300 PLN/mies. I że kancelarii jest dość (potrzeba ~400; liczba nieznana).
- **Plan (5 dni, ≤100 PLN):**
  1. Dzień 1: lista ~100 kancelarii z wyników „kancelaria odszkodowawcza [miasto]” w 8 miastach. To też pierwszy pomiar rynku.
  2. Dzień 1: w SAOS znajdź wyroki z art. 445 KC dla 3 typowych urazów. Zapisz kwoty z 10 wyroków dla każdego.
  3. Dzień 2: mail do 50: „Prześlij jedną zanonimizowaną sprawę. W 24 h dostaniesz chronologię i 5 podobnych wyroków z kwotami, gratis”.
  4. Dni 3–5: zrób ręcznie z LLM. Potem telefon z pytaniem o cenę: 499 PLN/mies. za 20 spraw?
  - **Co zbudować:** prompt do chronologii i arkusz kwot z SAOS. Tylko zanonimizowane akta, napisz to w mailu.
  - **Idziemy dalej, gdy:** ≥5 z 50 przysyła sprawę **i** ≥1 zapłaci ≥300 PLN/mies. **i** lista kancelarii ma ≥400 pozycji (lub jest źródło).
  - **Stop, gdy:** <5 z 50 przysyła sprawę, albo nikt nie zapłaci ≥300 PLN/mies., albo ≥3 odmawiają z powodu danych medycznych.

### 4.5 [001 „Czy ta księga jest czysta?”: raport ryzyk KW i działki](../ideas/property/001-kw-plot-risk-report.md) – 3,4, `<5%`
- **Dlaczego:** mocny wzorzec, prawie zerowy koszt tokenów (marża >95% przy 69 PLN), łatwy do testowania wynik. Pierwszy krok nic nie kosztuje: czy darmowy ChatGPT znajdzie te same ryzyka na prawdziwym odpisie? Wchłonął [006](../ideas/property/006-czy-tu-zbuduje.md) jako dodatek.
- **Wzorzec z Zachodu:** Orbital (Wielka Brytania), 60 mln USD seria B (2026-01), 5 000+ prawników, 250 000+ transakcji rocznie. To jednak B2B dla kancelarii. Wersja B2C istnieje tylko jako darmowa usługa państwowa w Gyeonggi (Korea).
- **Polska przewaga:** struktura KW (działy I–IV, wzmianki, hipoteka przymusowa, służebność przesyłu). Sprawdzenie KW lokalu, budynku i gruntu. Działka przez ULDK/EGiB. Praktyka notarialna. Po przeglądzie: tego da się nauczyć w tygodnie, nie miesiące.
- **3 szanse:** pośrednicy i doradcy kredytowi kupują jako narzędzie sprzedaży (Ś×W). Wspólny produkt z 006 (W×Ś, ale to decyzja budowy, nie dowód rynku). Ożywienie kredytów hipotecznych (Ś×Ś).
- **3 ryzyka:** kupującym wystarcza notariusz i bank (W×W). ChatGPT „przeczytaj odpis” wystarcza (Ś×W). Jeden zakup na dekadę, brak retencji (W×Ś). Do tego: pośrednik może nie chcieć listy ryzyk własnej oferty.
- **Najbardziej ryzykowne założenie:** raport znajduje ryzyka, których nie widzi darmowy asystent, a ktoś (kupujący lub pośrednik) za tę różnicę zapłaci.
- **Plan (7 dni, ≤200 PLN):**
  1. Dni 1–2 (gratis): zbierz 20 prawdziwych odpisów (swoje, znajomych, numery KW z ogłoszeń). Przeglądanie EKW jest za CAPTCHA, więc ręcznie; czy jest bezpłatne, sprawdź (tu niezweryfikowane). Wklej każdy do darmowego ChatGPT, potem uruchom swój prompt i sprawdzenie powierzchni w ULDK. Policz znalezione ryzyka.
  2. Stop, jeśli ChatGPT znajduje to samo w ≥18 z 20.
  3. Dni 3–4: strona „Wgraj odpis księgi wieczystej, w 10 minut dostaniesz listę ryzyk — 69 PLN” z przyciskiem przedsprzedaży (link płatności albo „rezerwuję, płacę przy odbiorze”, to słabszy sygnał). 150 PLN Google Ads na „sprawdzenie księgi wieczystej mieszkania”.
  4. Dni 3–7: 10 biur nieruchomości i 5 doradców kredytowych w jednym mieście: 3 darmowe raporty na ich ofertach.
  - **Co zbudować:** stronę i ręczny szablon raportu. Nic automatycznego.
  - **Idziemy dalej, gdy:** prompt znajduje istotne ryzyka pominięte przez ChatGPT w ≥3 z 20 odpisów **i** (≥5 przedsprzedaży **lub** ≥3 biura pytają o cenę).
  - **Stop, gdy:** ChatGPT pokrywa się w ≥18 z 20, albo <2 przedsprzedaże z ~300 kliknięć i zero zainteresowanych biur. (Czy 150 PLN da ~300 kliknięć, niezweryfikowane; przy mniejszej liczbie oceniaj konwersję.)

### 4.6 Kolejność i reguła decyzji
- **Kolejność:** tydzień 1 → 011. Tydzień 2 → 023 (zacznij telefony wcześnie). Tydzień 3 → 002. Tydzień 4 → 004. Test ChatGPT z 001 jest darmowy, zrób go w wolny wieczór. Reklamy dla 001 na końcu, w tygodniu 5.
- **Koszt:** najwyżej ~600 PLN w 5 tygodni, pewnie mniej. To mniej więcej miesięczny budżet.
- **Decyzja:**
  - pomysł spełnia wszystkie warunki „idziemy dalej” → nowa ocena z nowymi dowodami;
  - jeśli L5 i L8 dochodzą do 4 ze źródłami → `5–15%` lub wyżej i 6 tygodni na MVP;
  - dwa przechodzą → wybierz ten z większą liczbą deklaracji płacenia, nie wyższy wynik;
  - żaden nie przechodzi → nie zaczynaj nowej rundy researchu zza biurka (sekcja 9).

## 5. Mapa szans demograficznych
Które czynniki popytu ([demography.md](../research/poland/demography.md#demand-drivers)) nie mają jeszcze dobrego produktu. „Brak dobrego produktu” = nikt nie robi tego dobrze w Polsce **i** żaden nasz pomysł nie przetrwał przeglądu z realnym płatnikiem.

| Czynnik | Co znaleźliśmy | Pomysły (status) | Werdykt |
|---|---|---|---|
| DD1 Starzenie szybsze niż opieka | Koordynacja opieki rodzinnej, telefony do seniorów: brak polskiego produktu, ale też brak trwałego wzorca i płatnika | L120, L122 (szybka ocena `<5%`) | **niezaspokojone, brak płatnika** |
| DD2 Bon senioralny | Rozliczenia po stronie dostawcy otwarte; SeniorApp po stronie gminy | [003](../ideas/health-care/003-karta-uslug-opiekunczych.md) (`<5%`) | częściowo; moduł dla platform, nie firma |
| DD3 Kolejki w ochronie zdrowia | Boty rezerwacji zajęte (Docplanner Noa, państwowy voicebot CeZ); kontrola rozliczeń NFZ otwarta, ale wymaga wiedzy | [012](../ideas/health-care/012-kontrola-rozliczen-nfz.md) (`<5%`), [020](../ideas/health-care/020-clinic-phone-agent.md) odrzucony | otwarte tylko dla kogoś ze znajomością rozliczeń NFZ |
| DD4 Zdrowie psychiczne | Administracja terapeutów zahacza o MDR i art. 9; skryby zajęte | L107, L114 odrzucone (T20) | **niezaspokojone, blokuje zasada „bez medycyny”** |
| DD5 Niższe emerytury | Objaśnianie luki emerytalnej to doradztwo finansowe; brak płatnika za samą edukację | L021 odrzucony (T20) | **niezaspokojone, licencja** |
| DD6 ~2 mln cudzoziemców | Najbogatszy czynnik: akta legalizacyjne, tłumaczenia, PIT, MOS. Pomoc B2C darmowa (państwo, NGO) lub już sprzedawana (WoBorders, Mova, PolskiTest) | [002](../ideas/employment-migration/002-teczka-legalizacyjna.md), [013](../ideas/employment-migration/013-sworn-translation-drafts.md) żyją; [007](../ideas/accounting-tax/007-pit-assistant-foreign-employees.md), [017](../ideas/employment-migration/017-mos-bez-stresu.md) połączone; [018](../ideas/accounting-tax/018-biuro-dla-obcokrajowcow.md), [022](../ideas/employment-migration/022-b1-bez-stresu.md) odrzucone | **strona B2B (akta) niezaspokojona**; B2C obsłużone lub darmowe |
| DD7 Drogie, brakujące ręce do pracy | Godziny back office w małych regulowanych firmach. Dostawcy systemów szybko dodają agentów | [011](../ideas/sme-ops/011-broker-owu-comparison.md), [023](../ideas/sme-ops/023-oferta-z-maila.md), [004](../ideas/legal-compliance/004-claim-file-assistant.md), [016](../ideas/accounting-tax/016-asystent-klienta-biura.md), [005](../ideas/property/005-ai-biuro-zarzadcy.md), [008](../ideas/property/008-wycena-z-notatki.md) | **niezaspokojone w niszach bez dominującego dostawcy** (brokerzy, hurtownie na Subiekcie/Optimie) |
| DD8 Gospodarstwa jednoosobowe | Ogólni asystenci po polsku obsługują sprawy domowe | L167 odrzucony (T20) | obsłużone |
| DD9 Suburbanizacja | Zabudowa działki prawie darmowa (e-mapa.net, OnGeo); wyceny instalatorów otwarte, ale bez kanału | [006](../ideas/property/006-czy-tu-zbuduje.md) połączony, [008](../ideas/property/008-wycena-z-notatki.md) (`<5%`) | częściowo |
| DD10 Ożywienie mieszkań i kredytów | Brak AI do czytania KW, ale ludzie szukają dostępu, nie interpretacji | [001](../ideas/property/001-kw-plot-risk-report.md), [005](../ideas/property/005-ai-biuro-zarzadcy.md) (`<5%`) | luka jest, płatnik niepewny |
| DD11 Reforma edukacji | Przewodnik ZPE zakazuje AI przy kluczowych opiniach; materiały pokrywa ChatGPT i wydawcy | [015](../ideas/education/015-opinia-i-sprawozdanie.md) odrzucony, [021](../ideas/education/021-school-pedagogue-licence.md) (`<5%`) | **zablokowane wytycznymi**, szkoły kupują powoli |
| DD12 Rosnące dochody | Wspiera gotowość płacenia, sam nie jest rynkiem | — | — |

**Wniosek:** najwyraźniejszy niezaspokojony popyt to praca B2B z DD6 (legalny pobyt cudzoziemców) i DD7 (brak ludzi w małych regulowanych biurach). Najważniejsze społecznie czynniki (starzenie, zdrowie psychiczne, emerytury) zostają bez produktu z powodów, których solowy założyciel nie usunie: brak płatnika, wyrób medyczny, doradztwo finansowe.

## 6. Wzorce
**Regiony** (z sekcji „Western analogues” 14 opisów):
- R1 Ameryka Północna: wzorzec dla 13 z 14 (wszystkie poza 014).
- R3 DACH i Beneluks: 7.
- R2 Wielka Brytania i Irlandia: 2 (001, 003). R9 Zatoka i Turcja: 2 (004 TR, 021 SA).
- Po 1: R4 (016 DK), R5 (012 FR), R7 (003 JP), R8 (003 AU), R10 (011 MX/BR/UY). R6 dał 1 przypadek pokrewny (023: Duvo, Definic).
- Region CEE dał głównie **ostrzeżenia o wejściu**: 9 produktów z regionu już działa w Polsce, 3 zapowiedziane (T10).
- Azja Wschodnia i Zatoka dały wzorce, ale żaden pomysł z nich nie przetrwał.
- USA to najlepsze źródło wzorców B2B. Niemcy to najlepsze źródło wzorców „back office MŚP na krajowym systemie” (plancraft, JUPUS, Mercura). One są najbliżej polskich realiów.

**Tematy:**
- Przetrwały **agenty back office dla małych regulowanych firm**, pracujące na dokumentach, których państwo nie obsługuje: brokerzy (TH55), agencje legalizacyjne i zatrudnienia (TH12), kancelarie odszkodowawcze (TH11), hurtownie (TH61), biura rachunkowe (TH17).
- 6 z 7 opisów B2C odrzucono lub połączono. Siódmy (001) żyje tylko dzięki wersji B2B.
- Tematy z czołówki globalnej (TH16 AI księgowy, TH07 research prawny, TH01 skryba medyczny) są w Polsce „zajęte” lub „częściowe”. Duży zasięg na świecie znaczy, że lokalni gracze też to zauważyli.

**Fosy:**
- **Fosa w darmowym systemie państwowym** (MOS 2.0, EKW/mObywatel, Geoportal/e-mapa, Twój e-PIT, NFZ Terminy, wytyczne ZPE) wygląda głęboko. Ale państwo jest najsilniejszym konkurentem: daje funkcję za darmo albo zakazuje użycia. Zaszkodziło to pomysłom 002, 006, 007, 015, 017, 020, 021.
- **Fosa w prywatnym obiegu dokumentów** (OWU ubezpieczycieli, katalog i ceny hurtowni, akta szkód plus SAOS) trzymała się lepiej. Obie najczystsze luki (011, 023) są tego typu.

**Co zabijało pomysły w przeglądzie:**
- polski gracz już to ma: Comarch (016, 019), Wolters Kluwer (014), Docplanner (020), Allegro/Senvio (024), Mova/PolskiTest (022), WoBorders (018), DocuGov/LEX AI (009);
- darmowa pomoc państwa (006, 007, 015, 017);
- jednorazowy przychód (007, 009, 010, 022).

## 7. Dzikie karty (duże ryzyko, duży potencjał)
- [012 Kontrola rozliczeń NFZ](../ideas/health-care/012-kontrola-rozliczen-nfz.md): najgłębsza fosa (zarządzenia NFZ, SWIAD, ICD-9 PL). Widoczne pieniądze: degresja NFZ za ponadlimitowe TK/MR i endoskopie od 2026-04-01. Wzorzec: Parallel (Francja), seria A w 2026. Tylko jeśli ktoś z Twojej sieci da dane przychodni i wiedzę o rozliczeniach. Klin: śledzenie limitów ASDK (diagnostyka obrazowa, endoskopia).
- [013 Szkice tłumaczeń przysięgłych](../ideas/employment-migration/013-sworn-translation-drafts.md): mały, tani, łatwy do testu, publiczna lista klientów. Pierwszy krok gratis: czy na liście MS jest ≥1 000 tłumaczy ukraińskiego? Mały potencjał, ale strata to jedno popołudnie.
- [010 Teczka sprzedażowa](../ideas/accounting-tax/010-teczka-sprzedazowa.md): fala sukcesji (do 80 000 do 2030, starsze badania), brak polskiego produktu AI. Zależy od partnerstwa z serwisem ogłoszeń (BizShop, sprzedambiznes.pl). Rozmowa z obydwoma nic nie kosztuje.
- [003 Karta usług opiekuńczych](../ideas/health-care/003-karta-uslug-opiekunczych.md) jako **moduł sprzedawany platformom typu SeniorApp lub dużym agencjom opieki**, nie osobna aplikacja. Datowany czynnik (bon senioralny 2026–2028), ale biedni płatnicy.
- L046 Wiedza o Polsce + B2 do obywatelstwa ([B/TH39](../poland-check/B/TH39-national-migration-exam-prep.md), tylko szybka ocena): pierwszy na rynku w dniu uchwalenia nowelizacji MSWiA, jeśli przejdzie. Obserwuj ustawę, nie buduj.

## 8. Co research pokrył słabo
- **Nikt nie wypróbował zachodnich liderów.** Brief każe to zrobić, ale liderzy wymagali dema, a kont nie zakładano. „Działa po polsku?” jest nieznane dla 79% katalogu.
- **Nikt nie sprawdził darmowych asystentów na prawdziwych polskich dokumentach.** To główne ryzyko wchłonięcia dla 001, 004, 011, 013. Opisaliśmy je, ale nie zmierzyliśmy.
- **Dowody popytu są pośrednie:** podpowiedzi Google, ogłoszenia o pracę, prasa. Zero wywiadów i telefonów. Nie sprawdzono Google Trends, Keyword Planner, grup na Facebooku, Wykopu (wymagają logowania lub JavaScriptu).
- **Brak wielkości rynku** dla większości pomysłów B2B: brokerzy (tylko 2017), kancelarie odszkodowawcze, hurtownie techniczne, tłumacze ukraińskiego. Dlatego 004, 013 i 023 nie przechodzą testu liczby klientów (§3).
- **Prawie brak danych o retencji** w katalogu. „Trwały” w THEMES.md to ocena względna; L2 nigdy nie miał danych o NRR czy churnie.
- **Wiele faktów z fragmentów wyszukiwania**, nie z pobranych stron (oznaczone w plikach). 11 krajów cienkich (<5 produktów). W większości regionów nie przejrzano list Google Play ani portfeli akceleratorów.
- **B2C zbadano słabiej** i wypadło gorzej. Profil założyciela (40 h/mies., 500 PLN) pcha w stronę B2B z telefonami, i to przetrwało.

## 9. Pytania do Ciebie
1. **Kontakty.** Znasz kogoś wśród brokerów, agencji zatrudnienia lub legalizacyjnych, kancelarii odszkodowawczych, hurtowni technicznych albo przychodni z kontraktem NFZ? Jedno polecenie zmienia L8 bardziej niż research. Tylko tak da się przetestować 012.
2. **Telefony.** Każdy test to 20–100 telefonów lub maili w tydzień. Mieści się to w 40 h/mies.? Czy przerobić plany na same maile i strony (wolniej, słabsze sygnały)?
3. **Poprzeczka.** Przy „10 000 PLN MRR w 12 miesięcy” tylko 011 przechodzi do `5–15%`. Czy mniejszy pierwszy cel (np. 3–5 tys. PLN MRR jako biznes poboczny) jest OK? Wtedy rosną tanie, małe pomysły jak 013 i 001.
4. **Partnerzy.** Czy budowałbyś z partnerem branżowym (specjalista od rozliczeń NFZ dla 012, broker dla 011) za udziały lub procent przychodu?
5. **Dane medyczne.** 004 i 012 wymagają danych z art. 9 RODO: hosting w UE, umowy powierzenia, polityka usuwania. Chcesz to dźwigać sam?
6. **Co dalej, jeśli wszystkie testy padną.** Rekomendacja: faza 3 z badaniami pierwotnymi. 30 krótkich wywiadów w 3–4 niszach, które ciągle wracały (brokerzy, agencje zatrudnienia, hurtownie, biura rachunkowe). Cel: znaleźć ból, za który już płacą. Nie kolejny skan zagranicznych produktów. Zgadzasz się?
