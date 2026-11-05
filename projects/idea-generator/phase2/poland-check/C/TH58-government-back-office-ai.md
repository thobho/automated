# TH58 — Government back-office AI (Poland check)

Theme: [THEMES.md#th58](../../themes/THEMES.md#th58) · rank 52, batch C · sources accessed **2026-11-05** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| PLLuM / HIVE AI (state consortium) | Polish public LLM family; Ministry of Digital Affairs funded 14.5M PLN for the model and planned 19M PLN for rollout in administration | public money | ministries, KPRM, local governments | [Spider's Web, 2025-02](https://spidersweb.pl/2025/02/pllum-polska-szutczna-inteligencja-mobywatel-administracja-publiczna.html) |
| "Asystent urzędnika" pilots on PLLuM | Drafting replies in repetitive cases (Ministry of Digital Affairs, KPRM); Senate Chancellery and Prokuratoria Generalna testing Q&A, a legal assistant and automatic anonymisation; Lubuskie marshal's office building an assistant on internal data; Gdynia pilot (city chatbot + BIP search); Częstochowa first local pilot | public | pilots | [xyz.pl: Gdynia](https://xyz.pl/?p=120763); [iMagazine: Częstochowa, 2025-08-10](https://imagazine.pl/2025/08/10/polska-sztuczna-inteligencja-wchodzi-do-urzedow-czestochowa-pierwsza-przetestuje-model-pllum/) (read from search excerpts) |
| mObywatel assistant (PLLuM) | Citizen-facing guide to procedures, 730k+ conversations | free | citizens | [xyz.pl](https://xyz.pl/?p=241778) (excerpt) |
| Britenet (PL software house) | AI verification of EU-funds applications at the Ministry of Funds | project | Ministry of Funds and Regional Policy | [Britenet press release](https://britenetpro.prowly.com/442678-britenet-implements-ai-at-the-ministry-of-funds-a-revolution-in-the-verification-of-eu-applications) |
| LEX Budownictwo with Expert AI | Marketed as help with checking investment compliance with MPZP and building rules (for professionals) | LEX subscription | architects, investors, offices | [Wolters Kluwer: LEX MPZP](https://www.wolterskluwer.com/pl-pl/solutions/lex/mpzp) |
| OnGeo | Plot reports with MPZP name, resolution number and plan boundaries (non-LLM; see batch B TH15) | per report | buyers, agents | [OnGeo blog](https://blog.ongeo.pl/uprawnienia-architekta-nie-decyduja-o-zgodnosci-projektu-z-mpzp) |

## 2. Does the Western leader already serve Poland?
- **GovWell, Govstream.ai, Madison AI** (US permitting and civil-servant assistants), **Pair** (SG government), **Intric** (SE, municipal AI platform), **HKGAI** (HK): all sold to their own governments or municipalities; none in Poland.
- The buyer is the public sector, which in Poland buys through public tenders (excluded by the brief), and the state is building its own stack on PLLuM.

## 3. Polish demand signals
- Autocomplete (2026-11-05): "ai dla urzędu" → echo only. Low commercial search volume; activity is state-driven pilots.
- Planning reform creates private-side demand: the deadline for *plany ogólne* moved from end-2025 to 2026-06-30, then (April 2026) to 2026-08-31; WZ decisions are to be issued only in infill areas defined by the plan ogólny ([wartowiedziec.pl](https://wartowiedziec.pl/zarzadzanie-przestrzenia/81585-ostatni-dzwonek-dla-gmin-konczy-sie-czas-na-uchwalenie-planow-ogolnych); [DWF, 2026-05](https://dwfgroup.com/pl-pl/news-and-insights/insights/2026/5/plan-ogolny-i-co-dalej)). Read from excerpts; how many gminas met the deadline is unverified.

## 4. What adaptation needs
KPA procedure, Prawo budowlane, the 2023 planning act (plan ogólny, *obszar uzupełnienia zabudowy*), M20 BIP fragmentation, M17 ePUAP, M28 Geoportal and MPZP/plan-ogólny datasets (machine-readable format and coverage unverified), M31 ISAP. Courts stress that the authority itself must assess MPZP compliance, so any private tool is preparation support, not a decision ([OnGeo blog](https://blog.ongeo.pl/uprawnienia-architekta-nie-decyduja-o-zgodnosci-projektu-z-mpzp)).

## 5. Demographic or social driver
DD9 suburbanisation (plots on rural rings depend on WZ/plan ogólny) and DD10 housing revival.

## 6. CEE check
No CZ/SK/RO/HU government back-office product in the [R6 catalogue](../../catalogue/R6-cee-peers.csv); BgGPT (BG) is a sovereign model (see TH43).

## 7. Verdict: **partial**
The government side is closed: buyers use tenders and the state builds on PLLuM/HIVE AI. The private side of the same paperwork is open in a narrow way: architects, plot buyers and developers must now read new *plany ogólne* and WZ eligibility, and only LEX (generic) and OnGeo (plot reports, non-LLM) touch it.

**Seed idea:** "Czy tu zbuduję?": parcel ID → which plan ogólny zone and MPZP apply, whether the plot is in an infill area (WZ possible), and the key parameters (height, intensity, biologically active share) extracted from the resolution text; 49–149 PLN per plot for buyers, a monthly plan for architects. Overlaps TH15 (property diligence), so it could be one product.
