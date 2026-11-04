# TH35 — Teacher copilot (Poland check)

Theme: [THEMES.md#th35](../../themes/THEMES.md#th35) · rank 32, batch B · sources accessed **2026-11-04** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| Nowa Era "Asystent AI Nowej Ery" (pilot) | Publisher-run pilot: webinars and ready prompts for preparing tests, kartkówki and sprawdziany on Nowa Era materials | pilot (free to participants) | Nowa Era's teacher base (not quantified) | [Nowa Era webinar materials](https://cms.nowaera.pl/data/download/cf/93/da1be73fb26b6b5528d6a637a9c0b696cf93853fecc7ffcf51b813831ab42ecf.pdf/Materia%C5%82y%20po%20webinarze%20-%20Przygotowywanie%20test%C3%B3w%2C%20kartk%C3%B3wek%20i%20sprawdzian%C3%B3w%20%201.pdf) |
| Publishers' classic test generators (Nowa Era, WSiP and others) | Non-AI test and sprawdzian generators bundled with textbooks | free with adoption | most schools using those textbooks | first-thought, not re-verified |
| Training market | Many PARP-listed courses on AI for lesson scenarios, tests and feedback, e.g. 725.70 PLN gross; warnings not to paste pupils' names or psychological opinions into ChatGPT | 700–1,000+ PLN per course | teachers, schools | [PARP BUR course](https://uslugirozwojowe.parp.gov.pl/wyszukiwarka/uslugi/drukuj-pdf?id=3462717); [Antyweb guide](https://antyweb.pl/ai-dla-nauczyciela-jak-sztuczna-inteligencja-moze-pomoc-w-pracy) |
| Wolters Kluwer (LEX Edukacja) | Published expert articles "Asystent AI dla nauczyciela" (2026-02); product status unverified (page returned 403) | — | school directors (LEX Edukacja users) | [wolterskluwer.com/pl-pl](https://www.wolterskluwer.com/pl-pl/news/asystent-ai-dla-nauczyciela-katarzyna-polak) |

No independent Polish AI teacher-copilot startup with users was found in two Polish searches; teachers are being trained to use ChatGPT, and publishers are piloting their own assistants.

## 2. Does the Western leader already serve Poland?
- **MagicSchool** (US): LLM-generated translations into "25+ languages" (secondary source); a Polish review exists and autocomplete shows "magic school po polsku" searches; Polish curriculum (podstawa programowa) not built in. **Usable in Polish, not localised** ([MagicSchool help](https://help.magicschool.ai/en/articles/10270820-what-translation-tool-does-magicschool-use-for-its-services); [plisio.net PL review](https://plisio.net/pl/ai/magic-school-ai)).
- **Brisk** (US), **TeachMateAI** (UK), **Nurture** (IE), **fobizz** (DE, German schools and data protection), **Ed.ai** (FR, grading of handwritten papers): home markets; fobizz and Ed.ai are tied to national curricula and school procurement.
- Could not check: MagicSchool Polish output quality (no account created).

## 3. Polish demand signals
- Autocomplete (2026-11-04): "ai dla nauczycieli" → 10, mostly **szkolenie/kurs/cena/darmowe**, plus "narzędzia", "aplikacje", "angielskiego", "przedszkola"; "kompas jutra" → 10 (2026, podstawa programowa, klasa 1, reforma, szkolenie online); "magicschool po polsku" → "magic school po polsku"; "scenariusz lekcji ai", "sprawdzanie wypracowań ai", "ocena opisowa generator" → none.
- Demand is for **training**, not tools; the reform "Kompas Jutra" is heavily searched.

## 4. What adaptation needs
Podstawa programowa under Kompas Jutra (new curriculum from 2026-09 for grades I and IV, 2027 for secondary), CKE exam formats, M25/M26 Librus and Vulcan e-registers (no public API), publishers' textbook alignment (Nowa Era, WSiP, GWO, MAC), Karta Nauczyciela documentation duties, RODO for pupils' data (schools need a DPA). **AI Act:** AI used to evaluate learning outcomes is high-risk (Annex III), so automated grading needs a compliance plan; lesson-material generation is not.

## 5. Demographic or social driver
DD11: new curriculum from 2026-09 forces teachers to rewrite lesson plans and tests; teacher shortages; more children of migrants in classes (Ukrainian pupils need differentiated materials).

## 6. CEE check
No CZ/SK/RO/HU teacher copilot in R6 ([R6 catalogue](../../catalogue/R6-cee-peers.csv)).

## 7. Verdict: **partial**
Lesson and test generation is being absorbed by ChatGPT, MagicSchool (usable in Polish) and the textbook publishers' own pilots, who own curriculum alignment and distribution. A gap remains for **Kompas Jutra-aligned materials for teachers of mixed Polish–Ukrainian classes** and for teacher paperwork, but buyers (teachers) pay little and schools buy slowly; grading is AI Act high-risk.

**Seed idea:** "Kompas Jutra w 5 minut": lesson plans, worksheets and kartkówki mapped to the new podstawa programowa learning outcomes for grades I and IV (rolling up a year at a time), with an automatic simplified-Polish/Ukrainian version for pupils with migration background; 19–29 PLN/month per teacher or a school licence; overlaps with TH36 teacher paperwork (batch C).
