# TH36 — Teacher and school paperwork (Poland check)

Theme: [THEMES.md#th36](../../themes/THEMES.md#th36) · rank 58, batch C · sources accessed **2026-11-05** · method: [README](README.md#method). Lesson and test generation is in batch B [TH35](../B/TH35-teacher-copilot.md); this file covers mandatory records.

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| **Smart IPET** | Drafts an IPET from the *orzeczenie o potrzebie kształcenia specjalnego* and the WOPFU; "intelligent suggestions", FAQ mentions LLMs; .doc export; content based on ePedagogika.pl experts and Portal Oświatowy standards (operator not named on the page) | Mini 890.03 PLN gross/year (1 user); Pro 2,997.76 PLN gross/year (30 users) | testimonials from a director, support teacher, pedagogue; recommended by NPDN Educado council members | [smartipet.pl](https://smartipet.pl/ipet-w-kilka-minut/); [ePedagogika](https://epedagogika.pl/slowa-kluczowe/spektrum-autyzmu-ipet-wopfu-9163) |
| Wolters Kluwer "Dyrektor Szkoły" | Articles on AI as teacher's assistant (content, not a tool) | subscription | school leaders | [Wolters Kluwer, 2026-02-19](https://www.wolterskluwer.com/pl-pl/news/asystent-ai-dla-nauczyciela-katarzyna-polak) |
| Training providers | Courses on IPET/WOPFU templates (199 PLN per person) and on using AI for documentation and IPETs (3,500 PLN net) listed in the BUR database | per course | teachers | [BUR: IPET/WOPFU course](https://uslugirozwojowe.parp.gov.pl/wyszukiwarka/uslugi/drukuj-pdf?id=2255477) (read from search excerpt) |
| Template sites (wzory) | Free or paid Word templates for IPET, WOPFU, sprawozdania, plans | free / small fees | teachers | §3 autocomplete |

No AI tool found for the other recurring records: *sprawozdanie z pracy nauczyciela* (incl. support teachers), *plan rozwoju zawodowego* for awans, *opinia o uczniu* for a poradnia or a family court.

## 2. Does the Western leader already serve Poland?
The theme leaders (Öğretmen Evrak TR, Shawahid / Al-Mu'allim Al-Dhaki / Al-Muwajjih SA) are built for Turkish and Saudi ministry formats and are not in Poland; they are mostly template-based, not LLM. MagicSchool (US) generates IEP drafts for US law but does not know IPET/WOPFU rules (batch B TH35 found MagicSchool usable in Polish for lessons). ChatGPT is the de facto tool, but advisers warn teachers not to paste personal data, psychological opinions or named student work into chatbots ([Antyweb](https://antyweb.pl/ai-dla-nauczyciela-jak-sztuczna-inteligencja-moze-pomoc-w-pracy)).

## 3. Polish demand signals
- Autocomplete (2026-11-05): "ipet" → 10 incl. "ipet i wopfu", "wzór wypełniony", "wzór 2026", "**ipet według nowego rozporządzenia wzór**", "ipet expert"; "wopfu" → 10 incl. "wzór wypełniony", "przykład", "ile razy w roku"; "sprawozdanie z pracy nauczyciela" → 8 incl. support-teacher, autism, preschool, beginner; "plan rozwoju zawodowego nauczyciela" → 10 (all stages of awans); "opinia o uczniu" → 10 incl. "do poradni", "do sądu", "do sądu rodzinnego przykład", "z zaburzeniami zachowania i emocji". **Strong, recurring, template-seeking demand.** "ipet ai" → English noise only, so teachers do not yet search for AI.
- Inspection pressure: in April 2026 a kuratorium inspection found a school's IPET lacked legally required information, was vague in parts and undated ([Kuratorium Kielce, 2026-04](https://kuratorium.kielce.pl/wp-content/uploads/2026/04/informacja-o-wynikach-kontroli-szkola-podstawowa-nr-32-im.-janusza-kusocinskiego-w-kielcach.pdf)).
- An IPET must be prepared within 30 days of the orzeczenie being filed (school procedure documents; e.g. [ORKE guide, 2026-06](https://orke.pl/app/uploads/2026/06/WOPFU-i-IPET-–-od-przepisow-prawa-do-praktycznej-realizacji.pdf)). Whether a new IPET regulation applies in 2026 was **not verified** (autocomplete suggests teachers think so).

## 4. What adaptation needs
Rozporządzenia MEN on special education and psychological-pedagogical help (required IPET/WOPFU elements), Karta Nauczyciela and the 2022 awans zawodowy rules, statut szkoły, new podstawa programowa (DD11), M25/M26 Librus and Vulcan (data lives there, no API), RODO: health data of children (orzeczenia) are special-category data, so EU hosting, no training on inputs and a DPA with the school are needed. AI Act: drafting records is not scoring; keep it away from grading.

## 5. Demographic or social driver
DD11: teachers are short and classes more diverse, including children of migrants; special-education orzeczenia are growing (number not checked here). DD4: child mental-health demand raises poradnia referrals, each needing an *opinia o uczniu*.

## 6. CEE check
No CZ/SK/RO/HU teacher-paperwork tool in the [R6 catalogue](../../catalogue/R6-cee-peers.csv).

## 7. Verdict: **partial**
The highest-value record (IPET from WOPFU) already has an LLM tool from the Portal Oświatowy/ePedagogika ecosystem at 890 PLN/year per user, which owns teacher trust and content. The rest of the paperwork (support-teacher reports, awans plans, opinions for poradnie and courts) has strong template-seeking search demand and no AI product, but buyers are individual teachers with low budgets.

**Seed idea:** "Opinia i sprawozdanie w 10 minut": guided form plus LLM for *opinia o uczniu* (poradnia / sąd rodzinny variants), *sprawozdanie nauczyciela wspomagającego* and *plan rozwoju zawodowego*, with pseudonymised input (no names leave the browser) and the legally required sections checked; 19–29 PLN/month per teacher or 49 PLN per school year; SEO on the "wzór/przykład" queries above.
