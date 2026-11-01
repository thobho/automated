# Poland baseline: localization moat inventory (T03, part 2)

Polish-specific building blocks a foreign product would struggle with. For each item: what it is, how a product can access it (API, file export, scraping, manual), cost, who needs it, and a link. IDs (M01…) let write-ups cite the moat they rely on. All sources accessed **2026-11-01** unless stated otherwise.

**Notes on method and choices**
- Links point to the official portal or developer documentation. Where a fact comes from a secondary source it is cited separately.
- "Access" describes what a small private company can realistically do. "No public API" means none was found; it does not prove one does not exist.
- "Cost" is the fee to the data owner. It excludes integration effort. "Free" means no fee found on the official page; "unverified" means not checked.
- **Moat strength** is my judgement (H/M/L): how hard it is for a foreign entrant to replicate the integration plus the domain knowledge around it. H = hard access *and* complex rules; L = easy open API anyone can use.
- Phase 1 notes on KSeF and Allegro (`../../../research/07-founder-fit/api-access.md`, L7-F01–F03) are reused and cited as "Phase 1".

## A. Tax, invoicing and accounting

| ID | Building block | What it is | Access | Cost | Who needs it | Moat | Link |
|---|---|---|---|---|---|---|---|
| M01 | **KSeF** (Krajowy System e-Faktur) | Mandatory national e-invoicing (FA(3) XML) since 2026; every B2B invoice passes through it | Public REST API, OpenAPI spec, TEST/DEMO/PROD environments, no certification; XAdES or KSeF-token auth; tight rate limits per (context, IP) (Phase 1 L7-F02/F03). Login via mObywatel/login.gov.pl since 14 Feb 2026 | Free | Every VAT business, accounting offices, ERP and invoicing vendors, e-commerce | M (open API, but complex protocol, permissions, offline modes; market crowded per Phase 1) | [KSeF portal](https://ksef.podatki.gov.pl/); [integrator docs (GitHub)](https://github.com/CIRFMF/ksef-docs); mObywatel login via [inFakt blog](https://www.infakt.pl/blog/?p=81823) |
| M02 | **JPK** (Jednolity Plik Kontrolny: JPK_V7M/K VAT returns, JPK_KR, JPK_FA, JPK_MAG on demand; JPK_CIT from 2025+) | Structured XML files that firms send to or produce for the tax authority | XML schemas published by MF; submission via the MF gateway (*bramka e-Deklaracje*) with signature or authorisation data | Free | Accounting software, offices, auditors | M | [podatki.gov.pl JPK](https://www.podatki.gov.pl/jednolity-plik-kontrolny/) |
| M03 | **e-Deklaracje / e-Urząd Skarbowy** | Electronic filing of PIT, CIT, VAT; e-US online tax office for individuals and firms | e-Deklaracje gateway (SOAP) for software; e-US web only (no public API found) | Free | Tax and payroll software, accountants, PIT-filing apps | M | [e-Deklaracje](https://www.podatki.gov.pl/e-deklaracje/); [e-Urząd Skarbowy](https://www.podatki.gov.pl/e-urzad-skarbowy/) |
| M04 | **Biała lista VAT** (Wykaz podatników VAT) | Register of VAT payers and their bank accounts; paying to an unlisted account above 15k PLN loses tax deductibility | REST API wl-api.mf.gov.pl; `search` method reportedly 100 requests/day × 30 entities (secondary source); daily flat files | Free | Any firm paying invoices, ERP, AP-automation tools | L | [API](https://wl-api.mf.gov.pl/); limits via [Invoice Data Extraction blog](https://invoicedataextraction.com/blog/biala-lista-vat-automatyzacja-weryfikacji-rachunkow) |
| M05 | **Interpretacje podatkowe (EUREKA)** | Database of individual tax rulings and explanations from KIS | Web search; no public API found (scraping) | Free | Tax-advice tools, accountants, AI tax Q&A | M (content needs Polish tax expertise; tax advice is a regulated profession) | [EUREKA](https://eureka.mf.gov.pl/) |
| M06 | **PPK** (Pracownicze Plany Kapitałowe) | Employee capital plans every employer must run; contributions via payroll | Via the PPK provider's systems; registry portal mojePPK | Free (to employer) | Payroll/HR software, accountants | L–M | [mojePPK](https://www.mojeppk.pl/) |

## B. Social insurance and employment

| ID | Building block | What it is | Access | Cost | Who needs it | Moat | Link |
|---|---|---|---|---|---|---|---|
| M07 | **ZUS PUE / eZUS** | Social-insurance portal: contribution declarations (DRA, RCA), e-ZLA sick notes, certificates, pension account; profile mandatory for every payer since 2023 | **No public API for third parties found**; declarations are produced by payroll software (KEDU XML) and sent via ZUS *Płatnik* or PUE; access for accountants by power of attorney (PEL), can be limited to e-ZLA | Free | Payroll and accounting software, accounting offices, HR | H (no API, many forms, rules change yearly) | [eZUS / PUE login](https://www.zus.pl/ezus/logowanie); PUE obligation and PEL via [podatki.biz](https://www.podatki.biz/artykuly/pue-zus-obowiazkowe-profile-dla-platnikow-skladek_33_52389.htm); e-ZLA via [podatki.biz](https://www.podatki.biz/artykuly/elektroniczne-zwolnienia-lekarskie-e-zla-wszystko-co-powinni-wiedziec-platnicy_10_39487.htm) |
| M08 | **praca.gov.pl / foreign-worker permits** | Online applications for work permits and *oświadczenia o powierzeniu pracy* for foreigners | Web forms with Profil Zaufany/qualified signature; no public API found | Application fees per permit (unverified amounts) | Employers and staffing agencies hiring Ukrainians and others (demography DD6) | H | [praca.gov.pl](https://www.praca.gov.pl/) |

## C. Business and legal registries

| ID | Building block | What it is | Access | Cost | Who needs it | Moat | Link |
|---|---|---|---|---|---|---|---|
| M09 | **KRS** (Krajowy Rejestr Sądowy) | Register of companies, foundations, associations: board, shareholders (sp. z o.o. via filings), financial statements | Open REST API for current/full extracts by KRS number (no key); financial statements in eKRS (RDF) as XML downloads | Free | KYC/AML, B2B sales tools, credit checks, legal tech | L (open), M with financial statements parsing | [KRS Open API](https://prs.ms.gov.pl/krs/openApi); [eKRS search](https://ekrs.ms.gov.pl/) |
| M10 | **CEIDG** | Register of sole traders (JDG, ~2.5M+ active) | REST API on dane.biznes.gov.pl after free registration (token) | Free | Lead generation, KYC, invoicing apps | L | [dane.biznes.gov.pl](https://dane.biznes.gov.pl/) |
| M11 | **GUS BIR / REGON** | Statistical business register: REGON, PKD codes, addresses for all entities | SOAP API "BIR1.1"; free key on request by e-mail | Free | Invoicing/ERP autocompletion, data enrichment | L | [GUS API portal](https://api.stat.gov.pl/Home/RegonApi) |
| M12 | **KRZ** (Krajowy Rejestr Zadłużonych) | Insolvency and restructuring register | Web search; no public API found | Free | Credit risk, debt collection, B2B onboarding | M | [krz.ms.gov.pl](https://krz.ms.gov.pl/) |
| M13 | **CRBR** (Centralny Rejestr Beneficjentów Rzeczywistych) | Ultimate beneficial owners register (AML) | Web search; API status unverified | Free | AML obliged entities (accountants, estate agents) | M | [CRBR](https://crbr.podatki.gov.pl/) |
| M14 | **TERYT / PRG** | Official territorial division and address points (gmina, street codes) | GUS web service (TERYT WS1) and file downloads | Free | Any address handling, logistics, public-data products | L | [eTERYT](https://eteryt.stat.gov.pl/) |
| M15 | **BDL GUS** (Bank Danych Lokalnych) | Local statistics at gmina level | REST API | Free | Market sizing, location analytics | L | [BDL API](https://api.stat.gov.pl/Home/BdlApi) |
| M16 | **dane.gov.pl** | National open-data portal (thousands of datasets) | REST API | Free | Any data product | L | [dane.gov.pl](https://dane.gov.pl/) |

## D. Identity and e-government

| ID | Building block | What it is | Access | Cost | Who needs it | Moat | Link |
|---|---|---|---|---|---|---|---|
| M17 | **ePUAP** | Platform for sending official letters (*pisma ogólne*) to public bodies, with Profil Zaufany signature | Web; machine integration exists for public institutions (ESP boxes); no open API for private apps found | Free | Citizens and firms filing letters; products that draft official letters | H (no API; product must hand off to the user to sign) | [epuap.gov.pl](https://epuap.gov.pl/) |
| M18 | **Profil Zaufany / login.gov.pl (Węzeł Krajowy)** | National login and e-signature; links ePUAP, biznes.gov.pl, PUE ZUS, pacjent.gov.pl, CEIDG, KSeF | Integration via the "Współpraca Cyfrowa Tożsamość" portal with certificates; documented for public systems; **eligibility of private firms unverified** | Free (public) | Any product needing strong identity | H | [gov.pl: Krajowy Węzeł](https://www.gov.pl/cyfryzacja/budowa-krajowego-wezla-identyfikacji-elektronicznej) |
| M19 | **mObywatel** | State app with mDowód (ID), driving licence, vehicle data; PLLuM assistant since Dec 2025 (ai-landscape A12) | Businesses verify mDowód in-person via the app; online verification only through third-party providers (dPay, TransactionLink, inFakt); no official business API found | Free (app); provider fees vary | KYC for rentals, car hire, telecom, fintech, marketplaces | M | [gov.pl mDokumenty](https://www.gov.pl/cyfryzacja/nowe-funkcjonalnosci-w-mdokumentach); [dPay docs](https://docs.dpay.pl/en/eid/metody-weryfikacji/mobywatel/) |
| M20 | **BIP** (Biuletyn Informacji Publicznej) | Every public body's official bulletin: resolutions, tenders, budgets, decisions | Thousands of separate sites, different CMSs; scraping only | Free | Public-affairs monitoring, local-government tools, investors, journalists | M (fragmentation is the moat) | [BIP main page](https://www.gov.pl/web/bip) |
| M21 | **CEPiK / historiapojazdu.gov.pl** | Vehicle register: history, mileage, inspections by VIN + registration | Web form needing VIN, plate and first-registration date; no open API | Free | Used-car marketplaces, dealers, buyers | M | [historiapojazdu.gov.pl](https://historiapojazdu.gov.pl/) |

## E. Health

| ID | Building block | What it is | Access | Cost | Who needs it | Moat | Link |
|---|---|---|---|---|---|---|---|
| M22 | **NFZ open APIs** (*Terminy leczenia* waiting times, providers, contracts) | Waiting times per provider and benefit, list of NFZ contracts | Public REST APIs (no key) | Free | Appointment finders, patient navigation (demography DD3) | L | [api.nfz.gov.pl](https://api.nfz.gov.pl/); [Terminy leczenia](https://terminyleczenia.nfz.gov.pl/) |
| M23 | **IKP** (Internetowe Konto Pacjenta, pacjent.gov.pl) | Patient's record: e-prescriptions, referrals, sick notes, vaccinations, test results | Patient web/app only; no third-party API found | Free | Patient apps, family caregivers (DD1) | H | [pacjent.gov.pl](https://pacjent.gov.pl/) |
| M24 | **P1 platform (e-recepta, e-skierowanie, EDM)** | Central e-health platform run by Centrum e-Zdrowia; all prescriptions and referrals | Only via registered medical software with provider certificates; integration tests with CeZ | Free (fees for certificates unverified) | Clinic/practice software, telemedicine | H (medical regulation; out of the founder's scope for clinical features) | [Centrum e-Zdrowia](https://cez.gov.pl/) |

## F. Education

| ID | Building block | What it is | Access | Cost | Who needs it | Moat | Link |
|---|---|---|---|---|---|---|---|
| M25 | **e-Dziennik Librus Synergia** | Dominant school e-register (grades, homework, messages, attendance) | No public developer API found; logins issued by schools; unofficial clients exist (ToS risk) | Parents' premium tier paid (price unverified); schools licence | Parents, tutoring apps, homework helpers (DD11) | H (no API, school-controlled) | [Librus Synergia](https://synergia.librus.pl/) |
| M26 | **Vulcan UONET+ / Dzienniczek VULCAN** | Second major e-register | Unofficial Python client using the mobile API (`vulcan-api`); no official API | Free for parents | Same as M25 | H | [vulcan-api on PyPI](https://pypi.org/p/vulcan-api) |

## G. Property, land and law

| ID | Building block | What it is | Access | Cost | Who needs it | Moat | Link |
|---|---|---|---|---|---|---|---|
| M27 | **EKW** (Elektroniczne Księgi Wieczyste) | Land and mortgage registers: ownership, mortgages, easements, claims | Browse by KW number on the web; CAPTCHA and no API; official copies/extracts for a fee | Browsing free; official extract fees (amounts unverified) | Flat buyers, notaries, banks, estate agents, developers (DD10) | H (no API, human-readable sections need legal reading) | [ekw.ms.gov.pl](https://ekw.ms.gov.pl/) |
| M28 | **Geoportal / GUGiK services** | Cadastral parcels, orthophotos, zoning (MPZP), buildings | WMS/WFS services; ULDK API returns parcel geometry by ID or point | Free | Property tools, solar/PV installers, developers, agriculture | L–M | [geoportal.gov.pl](https://www.geoportal.gov.pl/); [ULDK](https://uldk.gugik.gov.pl/) |
| M29 | **SAOS** (System Analizy Orzeczeń Sądowych) | Court rulings from common courts, Supreme Court, Constitutional Tribunal, KIO | Open REST API and bulk dumps | Free | Legal research tools (Gaius-Lex, S22), lawyers | M (data open, but legal reasoning in Polish is the moat) | [saos.org.pl](https://www.saos.org.pl/) |
| M30 | **Portal Orzeczeń Sądów Powszechnych** | Anonymised judgments of common courts | Web search; scraping | Free | Legal research | M | [orzeczenia.ms.gov.pl](https://orzeczenia.ms.gov.pl/) |
| M31 | **ISAP / ELI API (Sejm)** | All acts in Dziennik Ustaw and Monitor Polski with metadata, in-force dates, amending acts, PDF texts | Open REST API (ELI), no key; used in this research (ai-landscape A24) | Free | Legal AI, compliance tracking, change alerts | L (open), M with consolidated-text tracking | [ISAP](https://isap.sejm.gov.pl/); [ELI API example](https://api.sejm.gov.pl/eli/acts/DU/2026/1003) |

## H. Payments and commerce rails

| ID | Building block | What it is | Access | Cost | Who needs it | Moat | Link |
|---|---|---|---|---|---|---|---|
| M32 | **BLIK** | Mobile payment code in banking apps; **2.9 bn transactions worth 441.5 bn PLN in 2025**, ~1.4 bn e-commerce payments (48% of BLIK); BLIK e-commerce value ~3.4× cards (PSP estimate); 20.7M active users | Merchants accept via a payment gateway (Przelewy24, PayU, Tpay etc.), not directly | Gateway fee per transaction | Any B2C product selling to Poles (subscriptions need BLIK recurring) | M (foreign Stripe-first products often lack it) | [blik.com](https://www.blik.com/); 2025 figures via [ITwiz](https://itwiz.pl/blik-w-2025-roku-29-mld-transakcji-i-dynamiczny-rozwoj-e-commerce/) and [Bank.pl](https://bank.pl/blik-ma-juz-207-mln-aktywnych-uzytkownikow/) |
| M33 | **Przelewy24** | Leading Polish payment gateway (pay-by-link bank transfers, BLIK, cards) | REST API, sandbox | Per-transaction fees (unverified) | Polish e-commerce and SaaS | L | [developers.przelewy24.pl](https://developers.przelewy24.pl/) |
| M34 | **PayU** | Payment gateway (Prosus), BLIK, pay-by-link, PayU Pay Later | REST API, sandbox | Per-transaction fees (unverified) | E-commerce, marketplaces | L | [developers.payu.com](https://developers.payu.com/) |
| M35 | **Tpay** | Payment gateway popular with small shops and SaaS | REST API | Per-transaction fees (unverified) | Small e-commerce, SaaS | L | [docs.tpay.com](https://docs.tpay.com/) |
| M36 | **Allegro** | Dominant marketplace; seller tools ecosystem | REST API; every app reviewed, refusal needs no reason; terms changed Sept 2025 (Phase 1 L7-F01, L6-F10) | Free API; seller commissions | Seller tools, repricers, listing generators, customer-message agents | H (platform risk + Allegro-specific rules) | [developer.allegro.pl](https://developer.allegro.pl/) |
| M37 | **InPost (Paczkomaty, ShipX)** | Parcel-locker network that dominates Polish e-commerce delivery | ShipX REST API for labels, tracking, locker search | Per-parcel prices (unverified) | Shops, marketplaces, returns tools | M | [InPost developers](https://dokumentacja-inpost.atlassian.net/wiki/spaces/PL/overview) |
| M38 | **Ceneo** | Main price-comparison site; product reviews ("Zaufane Opinie") | XML product feeds for shops; partner programme; no open data API found | CPC fees for shops | Shops, price-intelligence tools | M | [Ceneo for shops](https://shops.ceneo.pl/) |
| M39 | **BaseLinker (Base)** | Order-management hub connecting Allegro, shops, couriers, invoicing; de facto integration layer of Polish e-commerce | REST API | Subscription for merchants | E-commerce tools that want reach without one-by-one integrations | M (distribution channel as much as data) | [BaseLinker API](https://api.baselinker.com/) |
| M40 | **OLX Polska** | Largest classifieds (jobs, real estate, cars, goods) | Partner API for professional advertisers | Listing fees | Real-estate and job tools, reposting | M | [OLX developer](https://developer.olx.pl/) |

## I. Leading domestic software (integration targets and incumbents)

| ID | Product | What it is | Access | Cost | Who needs it | Moat | Link |
|---|---|---|---|---|---|---|---|
| M41 | **Comarch ERP Optima / XL / Altum** | Most common SME accounting/ERP suite in Poland; also Comarch e-invoicing | Optima has an API/SDK for partners; partner programme | Partner terms unverified | Add-ons for accounting offices and SMEs (document intake, KSeF, reporting) | M–H (installed base, partner channel) | [Comarch ERP Optima](https://www.comarch.pl/erp/comarch-optima/) |
| M42 | **Symfonia** | Accounting, HR/payroll and ERP for SMEs | Integration via partner tools / import formats (API status unverified) | Unverified | Same | M | [symfonia.pl](https://symfonia.pl/) |
| M43 | **enova365 (Soneta)** | ERP/HR-payroll popular with accounting offices | Extension SDK (.NET); partner network | Unverified | Same | M | [enova.pl](https://www.enova.pl/) |
| M44 | **InsERT (Subiekt, Rachmistrz, Rewizor, GT and nexo)** | Very common small-business sales/accounting desktop software | Sfera SDK (paid licence) for GT/nexo | Sfera licence (price unverified) | Shop integrations, document automation | M | [insert.com.pl](https://www.insert.com.pl/) |
| M45 | **Asseco WAPRO** | SME sales and accounting software | Integration via database/partner tools (unverified) | Unverified | Same | M | [wapro.pl](https://wapro.pl/) |
| M46 | **Fakturownia, inFakt, wFirma** | Online invoicing and accounting for JDG and small firms | Public REST APIs (Fakturownia documented on GitHub) | Subscription | Any product that needs invoices issued in Polish format with VAT | L | [Fakturownia API](https://github.com/fakturownia/API); [inFakt](https://www.infakt.pl/infakt-plus/) |
| M47 | **Librus / Vulcan** | School e-registers (see M25–M26) | — | — | — | H | see M25 |
| M48 | **Booksy** | Booking app for beauty and wellness; strong in Poland | Partner/API status unverified | Merchant subscription | Salon tools, marketing | M (owns salon distribution) | [booksy.com/pl-pl](https://booksy.com/pl-pl/) |
| M49 | **ZnanyLekarz (Docplanner)** | Leading doctor booking marketplace with clinic software and Noa AI scribe (ai-landscape S28) | Integrations for clinic software partners (terms unverified) | Doctor subscriptions | Private-practice tools (admin only, DD3) | H (owns doctor distribution, already ships AI) | [znanylekarz.pl](https://www.znanylekarz.pl/) |

## J. Other Polish-specific factors (non-system)

| ID | Factor | Why a foreign entrant struggles | Who it matters for | Source |
|---|---|---|---|---|
| M50 | **Invoices with Polish VAT details and KSeF numbers** | Polish firms expect a VAT invoice (NIP, KSeF number from 2026) for every subscription; USD card receipts are a purchase blocker for many SMEs and accountants | Any B2B SaaS | KSeF (M01); Phase 1 `../../../research/03-monetization/poland-smb-pricing.md` |
| M51 | **Accounting offices as gatekeepers** | Many SMEs outsource all paperwork to an *biuro rachunkowe*; tools reach SMEs through them | B2B SaaS for SMEs | Phase 1 `../../../research/06-pain-evidence/ksef-and-accounting-pain-pl.md`; demography DD7 |
| M52 | **Polish legal language and forms** | Official letters, *pełnomocnictwa*, KRS filings, court pleadings follow Polish templates and statutes (ISAP M31, SAOS M29); generic LLMs answer fluently but need grounding | Legal, HR, public-affairs products | ai-landscape A13–A15 |
| M53 | **No Polish voice assistants** | Siri and Alexa do not speak Polish; Apple Intelligence lacks Polish (ai-landscape A19–A20) | Voice products for seniors and homes | ai-landscape A19–A20 |

## Coverage

- **Moat items:** 53 (M01–M53): tax/invoicing 6, social insurance/employment 2, registries 8, identity/e-government 5, health 3, education 2, property/law 5, payments/commerce 9, domestic software 9, non-system factors 4.
- **All items in the task list are covered:** KSeF, JPK, ZUS PUE/eZUS, KRS, CEIDG, GUS BIR/REGON, ePUAP, mObywatel, Profil Zaufany, NFZ/IKP/P1, Librus/Vulcan, EKW, Geoportal, SAOS, ISAP, BIP, BLIK, Przelewy24, PayU, Allegro, InPost, Ceneo, Comarch, Symfonia, enova, InsERT, Librus, Booksy, ZnanyLekarz. Added: Biała lista, EUREKA, PPK, praca.gov.pl, KRZ, CRBR, TERYT, BDL, dane.gov.pl, CEPiK, Portal Orzeczeń, Tpay, BaseLinker, OLX, WAPRO, Fakturownia/inFakt/wFirma, and four non-system factors.
- **Sources:** 62 distinct URLs (link check 2026-11-01: 0 dead); primary official portals for nearly every item, secondary sources for limits (Biała lista), ZUS PEL rules, mObywatel verification and BLIK figures.
- **Searches run:** about 8 for this file (ZUS API, Węzeł Krajowy for private firms, mObywatel business verification, Biała lista limits, BLIK figures, Librus/Vulcan API), plus Phase 1 notes reused.
- **Searched for and found nothing:** an official ZUS API for third-party software; rules letting private companies integrate login.gov.pl outside mandated systems; an official mObywatel business API; any Librus developer API.

## Gaps

- **Fees** for payment gateways, InPost, EKW extracts, P1 certificates, work permits and Sfera SDK were not verified; check before unit economics.
- **API status unverified** for Symfonia, WAPRO, Booksy, ZnanyLekarz partner programmes and CRBR.
- **login.gov.pl for private products:** the key question for any identity-heavy idea; ask the Ministry of Digital Affairs or read the integration rules before relying on it.
- **Scraping legality:** EKW, BIP, Portal Orzeczeń, Librus may forbid automated access in their terms; not reviewed.
- **Biała lista limit** comes from a secondary blog; confirm in the MF API documentation.
