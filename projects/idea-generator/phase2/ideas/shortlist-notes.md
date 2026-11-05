# Shortlist notes (T20)

Companion to [shortlist.csv](shortlist.csv). Written 2026-11-05. Rejected and merged ideas are in [rejected.md](../rejected.md) (section "T20").

## Counts
- Longlist: 167 ideas (L001–L167). **Shortlisted: 59.** **Rejected: 61.** **Merged into a shortlisted idea: 47.** 59 + 61 + 47 = 167 (checked by script: every id appears exactly once across shortlist.csv and rejected.md).
- **Write-ups: 24** (`write_up = y`), numbered 001–024 by quick score; batch A = 001–008, B = 009–016, C = 017–024.
- Write-ups by field: property 4 (L079, L083, L092, L097), accounting-tax 4 (L014, L023, L005, L001), legal-compliance 4 (L069, L063, L059, L072), employment-migration 4 (L036, L052, L040, L048), health-care 3 (L115, L108, L103), education 2 (L126, L128), sme-ops 3 (L145, L131, L142). B2C: 7 (L079 and L092, both with a B2B tier; L014, L063, L126, L040, L048). B2B: 17.

## Method
- **Quick scores** (criteria.md §2, "quick"): L1–L9 from the Poland-check files ([A](../poland-check/A/README.md), [B](../poland-check/B/README.md), [C](../poland-check/C/README.md)) and the theme stats in [THEMES.md](../themes/THEMES.md); no new product trials. A 4 or 5 rests on a source already cited in the linked check file; otherwise the score is capped at 3.
- **L2** follows the theme durability verdicts (no theme has retention data, so nothing is above 4). Themes with a hype warning or with evidence from 1–2 countries get L2 ≤ 2 (TH12, TH36, TH39, TH52, TH55, TH57, TH60, TH63, TH64, TH67, TH69). The brief's cap (only hype → L2 ≤ 3) is never binding because these are already lower.
- **Weighted** = Σ score × weight, rounded half-up to one decimal. **Bands** from criteria.md §3. No idea reaches `15–30%`: the two ideas above 3.5 (L079 3.7, L036 3.6) have only one of L5/L6/L8 at 4, so they fall to `5–15%`. 41 ideas are `5–15%`, 18 are `<5%`. Opportunity/risk band moves are left to the write-ups (T21–T23), which list them in full.
- **Field balance.** The top 24 by raw score would include L088 (3.1, property), L033 (3.0), L106 (3.0) and L046 (3.0) instead of L131 (3.0) and L142 (2.95). L131 and L142 were taken instead so that SME operations has three write-ups and property no more than four. L142 is therefore the weakest write-up and should be the first one dropped if T21–T23 run short of time.

## Merges (cluster → kept idea)
- Foreign-worker legalisation: L027, L037, L038, L039, L041 → **L036** (B2B case file for agencies and staffing firms); L045 → **L040** (B2C MOS assistant). L036 and L040 share one rules engine; the write-ups should say so.
- Parcel and title checks: L080, L081, L082 → **L079** (KW risk report with B2B tier); L090 → **L092** (plot buildability). L079 and L092 share the Geoportal/ULDK stack and could become one product.
- Accounting-office agents: L006, L007, L008, L011, L013, L154 → **L005**; L010 stays separate (automated-access risk); L009 rejected (taken).
- Installers: L098, L099, L100 → **L097**; L101 rejected.
- Others: L002, L004 → L001; L015 → L014; L026 → L023; L034 → L033; L060, L061 → L059; L064–L067 → L063; L070, L071 → L069; L084–L086 → L083; L087 → L018; L091 → L072; L104 → L103; L113 → L120; L116, L119 → L115; L127 → L126; L132 → L131; L146, L147 → L145; L155 → L153; L160 → L159.

## Regulatory flags applied
- **AI Act hiring** (L033, L034): kept as L033 with "no scoring or ranking" by design, not marked for write-up; needs a counsel opinion before any build.
- **MDR** (L110, L111, L107): all rejected. L108 (NFZ settlement checks) and L103 (booking) make no clinical decisions.
- **Tax-advice wording** (L003, L007, L014): L014 hands a pre-checked return to Twój e-PIT and explains rules, no advice; L007 merged into L005 as an explanation letter; L003 shortlisted low (absorbed by LEX).
- **Automated access terms** (ZUS PUE L010, PISP L059, EKW L079, Allegro L142, Otodom/OLX L156): each carries the risk in its row and L7 ≤ 3; L079 is designed around the user uploading the odpis PDF.
- **Founder fit:** TH62 ideas (L095, L096) rejected; L001 kept with L7 = 2 (partner office and support hours).

## † rules sourced in T20
Sources accessed 2026-11-05. Only the rules needed by shortlisted or merged ideas were searched; other † ideas were rejected or kept with the relevant lens capped at 3 (noted in the row).

| Idea | Rule | Finding | Source |
|---|---|---|---|
| L028 | EU Pay Transparency Directive in Polish law | Poland did not transpose it by 2026-06-07; MRPiPS signals a longer vacatio legis, so the trigger is delayed | [infor.pl Kadry](https://kadry.infor.pl/kadry/wynagrodzenia/ochrona_wynagrodzenia/7550429,dyrektywa-placowa-i-polska-ustawa-nie-rewolucja-a-ewolucja-i-to-nie-7-czerwca-2026-r-a-pozniej-mrpips-wstepnie-zapowiada-wydluzenie-vacatio-legis.html) |
| L016 | Ulga abolicyjna | Exists for foreign income settled by proportional deduction, declared via PIT/ZG and PIT/O; now capped (cap amount and start year from secondary sources, unverified) | [pitax.pl](https://www.pitax.pl/wiedza/mniejsze-podatki/ulga-abolicyjna) |
| L039 → L036 | Ponaglenie before skarga na bezczynność | Art. 37 KPA ponaglenie must precede the complaint; WSA rulings in 2026 on voivodes' inaction in residence cases | [WSA Wrocław II SAB/Wr 287/26](https://dlajurysty.pl/orzeczenia/pokaz/489740/II-SAB-Wr-287-26) |
| L064 → L063 | EPU sprzeciw and limitation | Two-week sprzeciw deadline; general limitation six years, three for business-related and periodic claims; consumer rules since 2018-07-09 | [poradnikprzedsiebiorcy.pl](https://poradnikprzedsiebiorcy.pl/-termin-przedawnienia-roszczen-konsumentow-jak-liczyc) |
| L065 → L063 | Odwołanie od decyzji ZUS | One month from delivery, lodged through the ZUS branch, no court fee | [poradnikprzedsiebiorcy.pl](https://poradnikprzedsiebiorcy.pl/-odwolanie-od-decyzji-zus-wszystko-co-nalezy-wiedziec) |
| L071 → L069 | Patient compensation fund | Fundusz Kompensacyjny Zdarzeń Medycznych at the Rzecznik Praw Pacjenta takes applications since 2023-09-06 (not 2024 as the longlist said): 111 in 2023, 1,574 in 2024 | [Sejm interpellation 8909 answer (PDF)](https://api.sejm.gov.pl/sejm/term10/interpellations/attachment/ATTDGMHRA/i08909-o1.pdf) |
| L003 | Ryczałt rates by PKWiU | Rates set in art. 12 of the ryczałt act, tied to PKWiU codes; 2026 rates listed by Symfonia | [Symfonia blog](https://symfonia.pl/blog/finanse-i-ksiegowosc/stawki-ryczaltu-od-przychodow-ewidencjonowanych-w-2026-roku/) |

**Still unsourced (†) inside kept ideas:** L082 (spółdzielcze prawo without KW, a module of L079), L086 (developer-act odbiór rules, module of L083), L066/L070 (consumer-rights and work-accident rules, later modules of L063/L069), L061 (e-protokół access, module of L059), L117 (DPS standards), L068 (SD-Z2 window), L043 (KFS rules), L055 (najem okazjonalny), L076 (Allegro GPSR fields), L137 (transport-licence register). Write-ups must source these or drop the module.

## Caveats
- Quick scores only: no Western leader was re-tried, no new demand data. Most B2B demand (wholesalers, carriers, property managers, brokers, clinics) is unproven until outreach.
- Several top ideas earn money one-off (L079, L092, L023, L063, L014 is seasonal): the write-ups must show a recurring B2B tier or the 10k PLN MRR target is out of reach.
- Coverage: 7 web searches run in T20 (all for † rules); 7 sources used above.
