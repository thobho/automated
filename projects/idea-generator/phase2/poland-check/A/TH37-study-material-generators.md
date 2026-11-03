# TH37 — Study material generators (Poland check)

Theme: [THEMES.md#th37](../../themes/THEMES.md#th37) · rank 16, batch A · sources accessed **2026-11-03** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| Odrabiamy | Homework solutions app for Polish textbooks (long-established) | subscription (not re-checked) | Polish pupils | [App Store PL](https://apps.apple.com/pl/app/odrabiamy-pomoc-w-nauce/id1146781202?l=pl) |
| maturai | AI tutor, 1,700+ maths tasks aligned to CKE requirements | app store (not checked) | matura candidates | [App Store PL](https://apps.apple.com/pl/app/maturai/id6495065099) |
| egzamin.ai | Builds study apps from user-supplied material | not checked | mixed Trustpilot reviews (~4.1/5, a dozen or so reviews) | [Trustpilot](https://ch.trustpilot.com/review/egzamin.ai) |
| Stimy AI (PL/US) | AI maths tutor in Polish; 337k USD pre-seed | not checked | not stated | [instalki.pl](https://www.instalki.pl/news/software/sztuczna-inteligencja-jako-korepetytor-polsko-amerykanska-platforma-stimy-ai-pomaga-w-nauce-matematyki/) |
| Smartschool | AI-guided K-12 learning system, raised 1.5M (per Vestbee) | not checked | not stated | [Vestbee](https://www.vestbee.com/blog/articles/polish-smartschool-secures-1-5-m) |
| Polish oral-matura AI simulator (micro-SaaS) | Sold listing: built in 4 days, seller-reported 4,500 USD ARR, 335 customers | — | matura candidates | [Microns listing](https://www.microns.io/startup-listings/polish-high-school-exam-simulator) |
Also SKRIBU (English for matura/E8), Owler, Maturalni (courses), BorygoAI (made by pupils).

## 2. Does the Western/foreign leader already serve Poland?
- **Knowunity** (DE): full Polish site [knowunity.pl](https://knowunity.pl/) with "Fiszki AI", "Quizy AI", "Egzaminy próbne AI", AI tutor; global 30M+ students, 32 countries; no matura/E8 mention, no PLN price on the page. **Serves Polish.**
- **StudyFi** (CZ, `R6-CZ-010`): Polish site [studyfi.com/pl](https://www.studyfi.com/pl), free to start, claims 374,000+ students and lists students from UJ, AGH, PW, WUM, UAM. **Serves Polish, already marketed to Polish students.**
- **Quizlet, NotebookLM, Gizmo, RemNote**: work in Polish; "notebooklm po polsku" and "quizlet ai" autocomplete suggestions exist. Quizlet's Polish page returned 403 to the checker.
- Could not check: in-app pricing in PLN (requires app install/account).

## 3. Polish demand signals
- Autocomplete: "fiszki ai" → "… za darmo", "… z pdf", "… ze zdjecia", "… z notatek", "… po polsku", "quizlet fiszki ai"; "knowunity" → "… opinie", "… ile kosztuje", "… pro"; "notebooklm po polsku" → "czy notebooklm dziala po polsku". Real search demand, but "za darmo" dominates.
- "matura ai" → none; "ściąga ai" → echo only.

## 4. What adaptation needs
Curriculum alignment: CKE exam formats (matura, egzamin ósmoklasisty), the Reforma26 core curriculum (D43), M25/M26/M47 Librus and Vulcan (homework and grades) as a possible hook. Payment via M32 BLIK for parents. Generating flashcards from a PDF needs no local knowledge.

## 5. Demographic or social driver
DD11: new curriculum from Sept 2026 (grades I, IV) and 2027 (secondary), first new exams 2030/31; shrinking cohorts (D44) shrink the market; DD12 rising incomes support paid tutoring (korepetycje), the real budget line.

## 6. CEE check
StudyFi (Brno) has already entered Poland, with Polish university names on its site: a CEE adaptation moved in, as the brief warns.

## 7. Verdict: **taken**
The generic generator is served in Polish by Knowunity, StudyFi, Quizlet and NotebookLM for free, and a crowd of Polish matura apps exists. The theme is rated hype and absorbable; the only residue is exam-format practice (oral matura, CKE-graded open answers), where a micro-SaaS has shown small revenue.

**Seed idea (weak):** CKE-rubric grader for **written matura answers** (wypracowanie z polskiego, rozprawka, English essay) scored against published CKE criteria, sold to parents per pack (e.g. 29 PLN / 10 essays); note AI Act high-risk for education scoring applies only if used by institutions to assess, not for self-practice (to verify).
