# TH68 — Fraud, identity and trust (Poland check)

Theme: [THEMES.md#th68](../../themes/THEMES.md#th68) · rank 40, batch B · sources accessed **2026-11-04** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| State and operators (CERT Polska 8080, ustawa o zwalczaniu nadużyć w komunikacji elektronicznej) | Operators must block smishing SMS by NASK patterns (from 2024-03) and spoofed calls; citizens report SMS to 8080 (217,685 reports in 2022) | free | all mobile users | [gov.pl Cyfryzacja](https://www.gov.pl/web/cyfryzacja/ustawa-o-zwalczaniu-naduzyc-w-komunikacji-elektronicznej-w-realny-sposob-przyczynia-sie-do-zwiekszenia-poziomu-cyberbezpieczenstwa-w-naszym-kraju--oto-kilkanascie-kluczowych-korzysci); [act text (ELI)](https://eli.gov.pl/eli/DU/2024/1803/ogl/pol/pdf) |
| Phone-level spam filters (Google Phone, Hiya, Norton Mobile Scam Defense) | Caller ID and spam/scam flags; Norton sold in Polish retail as an annual subscription | free / annual licence | Polish smartphone users | [instalki.pl on Google Phone](https://www.instalki.pl/news/software/aplikacja-google-phone-z-opcja-blokowania-i-zglaszania-spamu/); [Komputronik Norton](https://www.komputronik.pl/product/1017336/norton-mobile-scam-defense-esd-pl-1-desktop-subskrypcja-na-rok.html) |
| Operators' senior protection (Play and others) | 2026 materials on how operators protect seniors from AI-voice scams | in plans | operator subscribers | [play.pl](https://www.play.pl/play-expert/porady/bezpieczny-internet-dla-seniora-jak-operatorzy-w-2026-roku-chronia-najstarszych-uzytkownikow-przed-nowymi-oszustwami-ai) |
| Allegro "Współpraca w Ochronie Praw" (WOP) | Brand-owner programme to report counterfeits and IP infringements with priority handling; 1,700+ brands (Allegro, via press) | free for rights holders | brand owners | [antyweb.pl](https://antyweb.pl/jak-allegro-walczy-z-podrobkami/); [spidersweb 2024-06](https://spidersweb.pl/2024/06/allegro-nowy-regulamin-ochrona-marek.html) |
| ID verification (Microblink HR, mObywatel verifiers M19) | Document and identity checks for fintech, rentals, marketplaces | enterprise / per check | Polish fintechs (not checked) | [local-moats M19](../../research/poland/local-moats.md) |

## 2. Does the Western leader already serve Poland?
- **Whoscall** (TW, 24M MAU): markets reported by Taiwanese press are East and Southeast Asia (plus Brazil); Europe is only a stated intention. **Not in PL** as far as found ([LTN 2026](https://ec.ltn.com.tw/article/breakingnews/5505207)). Its role in Poland is partly filled by Google Phone and Hiya.
- **Signa** (CO, MRR USD 138k, 8 countries, P&G, Roche): online-channel monitoring, undercover purchases and evidence packs for authorities. **Not in PL** (Latin America).
- **elv.ai** (SK): comment moderation for SK/CZ media. **Not in PL** (no Polish client found).
- **Microblink** (HR): global ID verification, sells across EU. **Serves PL** (core product not LLM-native).
- Could not check: Hiya's Polish database coverage.

## 3. Polish demand signals
- Autocomplete (2026-11-04): "oszustwo na wnuczka" → 10 (kk, policja, wyrok, gdzie zgłosić, city names); "kto dzwonił z numeru" → 10 (specific numbers, prywatnego, stacjonarnego); "podróbki allegro" → 10 (policja, perfum, lego, kosmetyków, "gdzie zgłaszać", karty pokemon); "aplikacja blokująca spam telefoniczny" → empty.
- Allegro community threads from sellers about accounts impersonating their brand and counterfeits ([spolecznosc.allegro.pl](https://spolecznosc.allegro.pl/t5/zaawansowani-sprzedawcy/konta-podszywaj%C4%85ce-si%C4%99-pod-nasz%C4%85-mark%C4%99/td-p/1017606)).

## 4. What adaptation needs
Polish scam scripts ("na wnuczka", "na policjanta", fake BLIK requests M32, fake InPost/courier SMS M37), CERT Polska lists and 8080 reporting, Allegro WOP procedure (M36), OLX (M40), Polish IP law and evidence formats for police and prosecutors, mObywatel identity (M19). Phone-call interception is operator territory and regulated (telecom secrecy).

## 5. Demographic or social driver
DD1/DD8: 7.9 million people 65+, many living alone, are the main target of phone scams; families act on their behalf.

## 6. CEE check
elv.ai (SK) and Microblink (HR) are in R6 ([R6 catalogue](../../catalogue/R6-cee-peers.csv)); Microblink already sells in Poland, elv.ai could add Polish media.

## 7. Verdict: **partial**
Scam call and SMS filtering is handled by the state-mandated operator blocking plus free phone-level filters, which leaves little room for a paid B2C app. Brand protection on Allegro has a free official channel but no Polish product found that does the Signa job: monitoring Allegro/OLX/Facebook Marketplace, test purchases and evidence packs for mid-size Polish brands.

**Seed idea:** counterfeit and impersonation monitor for Polish brands on Allegro, OLX and social shops: daily scan of listings with image and text matching, scoring, ready-to-file WOP reports and evidence packs (screenshots, seller data, test-purchase records) for police; 499–1,499 PLN/month per brand. Allegro's ToS on automated access must be checked first.
