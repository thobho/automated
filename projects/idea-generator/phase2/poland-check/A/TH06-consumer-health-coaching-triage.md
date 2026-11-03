# TH06 — Consumer health coaching and triage (Poland check)

Theme: [THEMES.md#th06](../../themes/THEMES.md#th06) · rank 20, batch A · sources accessed **2026-11-03** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| **Infermedica** (Wrocław) | Symptom checker, call-centre triage, ER triage, API (B2B2C); itself a global leader in the theme | B2B | PZU Zdrowie: 37% of patients with new problems routed to teleconsultation (2019 figure) | [Infermedica case study](https://infermedica.com/case-studies/pzu-zdrowie) |
| **Fitatu** (Polish), Premium+AI | Calorie and macro estimate from a meal photo, matched to its own Polish product database incl. local brands | Premium+AI 49.99 PLN/month (per Telepolis) | Polish calorie-app users (count not checked) | [Telepolis](https://www.telepolis.pl/tech/aplikacje/fitatu-ai-kalorie-ze-zdjecia-posilku); [Fitatu help](https://www.fitatu.com/pl/help/jakie-funkcje-ai-oferuje-aplikacja-fitatu) |
| Diagnostyka (lab chain) app built with Miquido | AI-powered patient health app; headline claims 360% user growth (2026-03, not read: 403) | free to lab patients | Diagnostyka patients | [Techleap feed](https://finder.techleap.nl/news/feed/diagnostyka-miquido-launch-ai-powered-health-app-with-360-user-growth) |
| Medicover, LuxMed, PZU Zdrowie apps | Private-care apps with triage/teleconsultation | subscription packages | millions of insured members (not re-checked) | ai-landscape |

## 2. Does the Western leader already serve Poland?
- **Cal AI** (US, photo calorie counter): App Store app usable in Polish markets; Polish equivalent Fitatu already ships the feature with a local food database. **Effectively served.**
- **Sword Health** (PT, B2B employer/insurer physio): no Polish customer found.
- **Limbic** (UK, NHS talking therapies), **XUND** (AT, CE-marked symptom checker), **Persly** (KR): no Polish presence found.
- **ChatGPT Health** (OpenAI): health section with uploaded medical records; on 2026-01-08 the waitlist excluded the EU and UK ([android.com.pl](https://android.com.pl/tech/1007047-chatgpt-health-nowy-modul/)). When it reaches the EU it absorbs most "explain my results / what does this symptom mean" use cases.
- Could not check: in-app Polish language of Cal AI and Ada (app install needed).

## 3. Polish demand signals
- Autocomplete: "psycholog ai" → "… chat", "… za darmo", "… opinie", "twój psycholog ai"; "dietetyk ai" → "… za darmo", "chat ai dietetyk"; "interpretacja wyników badań" → "… krwi", "… laboratoryjnych", "… online"; **"ikp wyniki badań" → "… krwi", "… dziecka", "… laboratoryjnych", "aplikacja ikp wyniki badań"**; "chatgpt wyniki badań" → echo only.
- Strong consumer interest in **understanding lab results** (IKP now shows them) and free AI therapy; "za darmo" recurs.

## 4. What adaptation needs
M23 IKP (lab results, e-recepty, history; access only by the patient, no third-party API), M24 P1/EDM, M22 NFZ waiting-time data (Terminy leczenia) for "where can I get seen sooner", Polish lab reference ranges per lab, M49 ZnanyLekarz for booking. Regulation: MDR (a symptom checker or result interpreter that suggests diagnoses is a medical device, class IIa+), AI Act high-risk via MDR, RODO special-category data; Fitatu-style wellness avoids MDR.

## 5. Demographic or social driver
DD3 (4.2–4.3-month specialist waits, 76 bn PLN private health spend), DD4 (mental-health demand, 117-day waits), DD1 ageing, D24 66.5% of 60–74 online.

## 6. CEE check
No CZ/SK/RO/HU consumer health-coaching product in R6; Persikas (LT, R4) is Baltic ([R6 catalogue](../../catalogue/R6-cee-peers.csv)).

## 7. Verdict: **partial**
Triage is led by a Polish company (Infermedica) selling to insurers, photo nutrition is shipped by Fitatu with a local database, and private-care apps own their members. The residue is **lab-result understanding** tied to IKP and Polish labs, where search demand is visible, but it sits on the MDR line and will be absorbed by ChatGPT Health once it reaches the EU.

**Seed idea (risky):** "Wyniki bez stresu": non-diagnostic explainer of Polish lab results (PDF from Diagnostyka/ALAB/IKP), trend charts across labs, and a "what to ask your doctor / which NFZ specialist and current wait" sheet using NFZ Terminy leczenia; one-off 19 PLN or family plan; MDR classification must be checked before any build.
