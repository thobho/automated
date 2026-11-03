# TH01 — Ambient clinical scribe (Poland check)

Theme: [THEMES.md#th01](../../themes/THEMES.md#th01) · rank 4, batch A · sources accessed **2026-11-03** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| Noa Notes (Docplanner / ZnanyLekarz, Warsaw) | AI scribe working in the background of a visit; Chrome extension; Polish site noa.ai/pl with visit and specialty templates; sister tool Noa Evidence free for all Polish doctors | plans page linked, prices not shown | 9k doctors in Brazil alone (ai-landscape S28); Polish user count not shown | [noa.ai/pl](https://noa.ai/pl/); [Eska on Noa Evidence](https://www.eska.pl/rozrywka/ciekawostki/polscy-lekarze-tona-w-wiedzy-ai-pomoze-im-odzyskac-czas-dla-pacjentow-aa-pJpK-M4hB-4JAA.html) |
| "Skryba AI" (vendor not identified) | Ambient scribe; a Poznań hospital emergency department displays that it is supported by Skryba AI | not found | at least one hospital SOR (photo report) | [android.com.pl](https://android.com.pl/tech/1045814-uzywanie-ai-w-szpitalach/) (vendor unverified) |
| Jutro Medical | Own EHR with AI agents in its own clinic chain (not sold to others) | n/a | ~120k patients | ai-landscape S14 |
| Generic tools | Zoom offers clinical-notes in Polish ([zoom.com/pl](https://www.zoom.com/pl/industry/healthcare/solutions/clinical-notes/)); doctors also use ChatGPT (press on a Bydgoszcz case) | — | — | android.com.pl above |

## 2. Does the Western leader already serve Poland?
- **Heidi Health** (AU; 2M+ consults/week): has a **Polish-language help centre** describing up to three input languages, a separate output language and auto-detect; free plan limited (e.g. 10 in-session evidence uses/month); works "without EHR integration" ([support.heidihealth.com/pl](https://support.heidihealth.com/pl/articles/14648718-wiecej-mozliwosci-heidi)); third-party listings name Polish among 110 languages ([GoodFirms](https://www.goodfirms.co/software/heidi-health)). Homepage lists GDPR among compliance pages ([heidihealth.com](https://www.heidihealth.com/)). **Usable in Polish today, free tier exists.**
- Could not check: PLN pricing, Polish EHR integrations (no Polish EHR named), quality on Polish medical speech; Tandem Health's Polish status not found in one search.

## 3. Polish demand signals
- Autocomplete: "notatki lekarskie ai" → none; "asystent ai lekarz" → "asystent ai lekarza"; "voicebot" → "voicebot medyczny". Low consumer-search volume (expected: buyers are clinicians).
- Press: Polish coverage of AI scribes in hospitals (Radio Eska Poznań, android.com.pl, Demagog analysis) ([Demagog](https://demagog.org.pl/analizy_i_raporty/ai-w-medycynie-latwiejsza-dokumentacja-i-szybsza-diagnoza/)).

## 4. What adaptation needs
M24 P1/EDM (structured documentation via certified software only), M49 ZnanyLekarz distribution, M23 IKP; Polish ICD-10/ICD-9-PL coding for NFZ reporting, e-zwolnienie (M07) and e-skierowanie drafting; RODO for health data (special category) and medical secrecy. Founder exclusions: medical regulation and high liability.

## 5. Demographic or social driver
DD3: specialist queues 4.2–4.3 months and doctor shortages (D18–D19, D38), so time saved per visit has value; DD1: 115.6M outpatient visits by people 65+ a year (D15).

## 6. CEE check
No CZ/SK/RO/HU scribe found in R6; Mediately (SI) is already in PL with drug/guideline Q&A, a likely add-on path ([R6 README](../../research/regions/R6-cee-peers/README.md)).

## 7. Verdict: **taken**
Docplanner owns Polish doctor distribution and ships Noa Notes with a Polish site; Heidi works in Polish with a free tier and a Polish help centre; hospitals already deploy a Polish-branded scribe. A solo founder without medical-software certification cannot beat them on the core physician use case.

**Seed idea (adjacent, outside the taken core):** scribe and visit-report generator for **non-physician practices that pay privately and are ignored by Noa/Heidi templates**: veterinary clinics (Polish vet history format, client letters) or physiotherapists; check vet-software incumbents before shortlisting.
