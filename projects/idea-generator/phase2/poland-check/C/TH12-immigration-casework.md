# TH12 — Immigration casework (Poland check)

Theme: [THEMES.md#th12](../../themes/THEMES.md#th12) · rank 53, batch C · sources accessed **2026-11-05** · method: [README](README.md#method). The consumer side (foreigners filing their own MOS applications) is covered in batch B [TH59](../B/TH59-citizen-sme-public-service-navigators.md); this file covers the **professional side**: law firms, legalisation agencies and employers' HR teams that prepare cases.

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| HRappka | HR/payroll software for staffing agencies with a "Legalizacja cudzoziemców" module: permits and deadline tracking; no AI or MOS application drafting described | not listed; 14-day trial | staffing agencies (none named) | [HRappka, 2026-03-30](https://hrappka.pl/?p=63478) |
| Legalisation agencies and law firms | Human preparation of residence and work-permit cases | average 4,457 PLN per person (2026, aggregator) | foreigners and employers | [cenauslug.pl](https://cenauslug.pl/firma-i-biuro/legalizacja-pobytu-i-zatrudnienia-cudzoziemcow) (via TH59) |
| In-house legalisation specialists | Staffing firms hire dedicated staff (Career Peak in Gorzów, InexGroup in Poznań, Legal HR in Szczecin) | salary | — | [pracuj.pl: Gorzów](https://www.pracuj.pl/praca/specjalista-specjalistka-ds-legalizacji-pobytu-i-pracy-cudzoziemcow-z-j-angielsk-gorzow-wielkopolski,oferta,1004838194); [pracuj.pl: Poznań](https://www.pracuj.pl/praca/specjalista-specjalistka-ds-legalizacji-pobytu-i-zatrudnienia-cudzoziemcow-poznan,oferta,1004917419); [RocketJobs: Szczecin](https://rocketjobs.pl/oferta-pracy/legal-hr-sp-z-o-o--specjalista-specjalistka-ds-legalizacji-pobytu-i-pracy-cudzoziemcow-legalization-specialist--szczecin-hr-office) |
| Right to Protection "Legal Adviser 2.0" | Free NGO Telegram bot for Ukrainians (consumer) | free | — | see TH59 |

No Polish AI tool that drafts a residence or work-permit case file (application fields, attachment checklist, employer annex, justification letter) for professionals was found.

## 2. Does the Western leader already serve Poland?
- **Visalaw.ai, CaseBlink, Alma, Manifest** (US): built on US immigration law (USCIS forms, O-1/EB-1 petitions); not in Poland. The pattern (AI drafts long evidence-heavy petitions) fits US talent visas, whereas Polish cases are form-heavy, short and high-volume.
- EY and Fragomen advise employers in Poland on MOS 2.0 and the 2025 procedure changes, as human services ([EY: MOS 2.0 w praktyce](https://www.ey.com/pl_pl/insights/workforce/mos-2-0-w-praktyce-najwazniejsze-pytania-pracodawcow-i-cudzoziemcow); [Fragomen](https://www.fragomen.com/insights/konfederacja-lewiatan-procedura-legalizacji-zatrudnienia-cudzoziemcow-w-polsce-po-zmianach-w-2025-r.html)).

## 3. Polish demand signals
- Autocomplete (2026-11-05): "legalizacja pobytu" → 10 incl. "… ukraińca w polsce", "… praca", "… dokumenty", "**legalizacja pobytu cennik**"; "zezwolenie na pracę typ a" → 10 incl. "opłata", "jakie dokumenty", four voivodeship offices, "2026", "koszt"; "mos 2.0" → 10 incl. "logowanie", "rejestracja", "cukr", "instrukcja", "karta pobytu"; "kancelaria imigracyjna" → 2; "program do legalizacji cudzoziemców" → none. Strong consumer and HR demand for the procedure; nobody searches for software.
- Rules: since 2026-04-27 residence applications only through MOS (other submissions are left unexamined; some types such as intra-corporate transfer are not in MOS) ([MOS: jak zacząć](https://mos.cudzoziemcy.gov.pl/jak-zaczac/)); fees for employing foreigners rose in 2026 ([infor.pl Kadry](https://kadry.infor.pl/zatrudnienie/zatrudnianie-cudzoziemcow/7485403,zatrudnienie-cudzoziemca-wiecej-kosztuje-w-2026-roku-wyzsze-oplaty-i-nowe-obowiazki-pracodawcow.html.amp)); the Ombudsman (RPO) keeps flagging slow voivodes' proceedings ([RPO BIP](https://bip.brpo.gov.pl/pl/content/rpo-cudzoziemcy-legalizacja-pobytu-przewleklosc-mswia)).

## 4. What adaptation needs
Ustawa o cudzoziemcach and the 2025 act on employing foreigners, M08 praca.gov.pl (work permits, *oświadczenia*), MOS 2.0 with login.gov.pl and e-signature (M18; employer co-signs), voivodeship-specific practice (16 offices, different attachment demands), M07 ZUS (RCA/insurance proof), M10/M09 employer data from CEIDG/KRS, UA/RU/EN/Hindi/Nepali-speaking clients. Representation before the voivode appears not to be reserved for lawyers (KPA art. 33 allows any natural person as *pełnomocnik*; not re-verified here), which is why non-lawyer legalisation agencies exist; a product sold to them needs no licence, but legal-advice wording must be avoided.

## 5. Demographic or social driver
DD6: 1.56 million Ukrainians with valid permits and 1.29 million foreigners insured in ZUS; the end of the special act moves 900k+ people to CUKR and standard permits (TH59). DD7 labour shortages keep employers hiring from Asia.

## 6. CEE check
No CZ/SK/RO/HU immigration-casework AI in the [R6 catalogue](../../catalogue/R6-cee-peers.csv); Czechia and Slovakia also host large Ukrainian populations, so a Polish tool could expand there with new law packs.

## 7. Verdict: **open gap**
No product drafts Polish legalisation cases for professionals: HR software only tracks deadlines and agencies do the work by hand at ~4.5k PLN per person, while volumes jumped with MOS-only filing and CUKR. US leaders solve a different (petition-writing) problem and will not localise.

**Seed idea:** "Teczka legalizacyjna" for legalisation agencies and staffing firms: from a passport scan, employment contract and employer data (KRS/CEIDG) the agent fills the MOS application fields, builds the attachment checklist for the specific voivodeship, drafts the employer's annex and tracks every worker's legal-stay deadline; 30–60 PLN per case or 299–799 PLN/month per agency. Complements the TH59 consumer seed.
