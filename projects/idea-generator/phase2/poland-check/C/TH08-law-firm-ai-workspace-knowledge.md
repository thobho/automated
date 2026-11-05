# TH08 — Law-firm AI workspace and knowledge (Poland check)

Theme: [THEMES.md#th08](../../themes/THEMES.md#th08) · rank 47, batch C · sources accessed **2026-11-05** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| LEX Expert AI (Wolters Kluwer Polska) | AI answers inside the LEX database; per a search excerpt of the vendor FAQ it **cannot analyse files uploaded by the user**, only LEX content (page returned 403 on fetch, so unverified) | bundled with LEX (list price not published) | LEX subscribers; CMS uses LEX Kompas Orzeczniczy | [WK technology page](https://www.wolterskluwer.com/pl-pl/solutions/lex/expert-ai/technologia) (403); [WK news: CMS](https://wolterskluwer.com/pl-pl/news/lex-kompas-orzeczniczy-w-kancelarii-cms-sprawniejszy-research-prawny-dzieki-ai) |
| Beck-Noxtua for Poland | Legal AI workspace on Legalis content; waitlist, launch in Poland during 2026 | not published | waitlist | [Noxtua press release](https://www.noxtua.com/news/press-releases/beck-noxtua-poland) (via batch A TH07) |
| AI4Legal (TTMS, Warsaw) | Document analysis, template contracts, hearing transcripts, summaries; built by a software house | quote on request | none named | [TTMS article](https://ttms.com/pl/najlepsze-narzedzia-ai-dla-kancelarii-prawnych/) (vendor's own ranking) |
| Gaius-Lex (Kraków) | AI legal research and drafting over PL/CZ/AT/DE law | not found | not found | [Stanford CodeX TechIndex](https://techindex.law.stanford.edu/companies/gaius-lex) |
| LexAlpha, VeroLex, VOLARIA AI, Advocly | Small Polish startups: litigation-file organisation and pleading drafts (LexAlpha), Q&A and contracts (VeroLex, founded 2025), clause review (VOLARIA, Advocly; Advocly raised EUR 50k by 2025-04) | not found | not found | [TechIndex LexAlpha](https://techindex.law.stanford.edu/companies/16432); [TechIndex VeroLex](https://techindex.law.stanford.edu/companies/verolex); [TechIndex VOLARIA](https://techindex.law.stanford.edu/companies/16433); [Dealroom Advocly](https://app.dealroom.co/companies/advocly) |
| Custom builds | Sawaryn & Partners built an Azure OpenAI tool for court-document analysis with TTMS | project | 1 firm | [TTMS case study](https://ttms.com/pl/case-studies/ai-implementation-for-court-document-analysis-at-a-law-firm/) |

## 2. Does the Western leader already serve Poland?
- **Harvey:** firmwide at WKB Lawyers (160+ lawyers), June 2026 ([Harvey blog](https://www.harvey.ai/blog/wkb-lawyers-deploys-harvey-firmwide)). Autocomplete shows "harvey ai polska", "harvey ai cena", "harvey ai dla prawników".
- **Legora:** Wardyński & Partners, the first Polish firm with a strategic partnership, after a 2024 pilot with 70+ lawyers; announced 2025-08-28 ([Wardyński & Partners, codozasady.pl](https://codozasady.pl/en/p/as-the-first-law-firm-in-poland-we-have-started-strategic-partnership-with-legora--ai-platform-for-lawyers)). Site tried: English only, no prices, demo only ([legora.com](https://legora.com/)).
- **DeepJudge** (knowledge search over the firm's DMS) lists Schoenherr, a CEE firm with a Warsaw office, as a customer ([Legal IT Insider, 2025-11-04](https://legaltechnology.com/2025/11/04/in-brief-deepjudge-raises-41-2m-series-a-announces-freshfields-as-a-customer/)).
- Small firms use NotebookLM, ChatGPT and Microsoft 365 Copilot over their own files (listed for Polish firms in the [TTMS article](https://ttms.com/pl/najlepsze-narzedzia-ai-dla-kancelarii-prawnych/)).
- Could not check: Harvey/Legora product UI in Polish (demo-only, no signup attempted).

## 3. Polish demand signals
- Autocomplete (2026-11-05): "ai dla kancelarii" → "ai dla kancelarii prawnej"; "harvey ai" → 10 suggestions incl. "harvey ai polska", "harvey ai cena", "harvey ai dla prawników"; "legora polska" → echo only. Branded interest in Harvey from Polish searchers.
- Press/vendor content: ranking articles on legal AI for Polish firms (TTMS, techsy.io 2026) show a market being actively marketed to.

## 4. What adaptation needs
M52 Polish legal language and pleading templates; M29 SAOS, M31 ISAP/ELI for grounding; tajemnica adwokacka/radcowska and RODO push toward EU hosting (M-level, not unique); e-Doręczenia and Portal Informacyjny Sądów as document sources for litigation files. The firm's own documents are language-agnostic for retrieval, which is why Harvey and Legora work in Polish firms.

## 5. Demographic or social driver
None specific. DD7 (scarce staff) applies weakly: junior-lawyer hours are the line replaced.

## 6. CEE check
Gaius-Lex itself covers CZ/AT/DE law; Nexana (SK) lists Polish law (batch B TH20). No CZ/HU firm-knowledge workspace aimed at Poland found in the [R6 catalogue](../../catalogue/R6-cee-peers.csv).

## 7. Verdict: **taken**
Top Polish firms already run Harvey, Legora or DeepJudge, publishers bundle AI with LEX and Legalis, and small firms get "chat with my files" free or cheap from NotebookLM and Copilot. A firm-knowledge workspace is horizontal and multilingual by nature, so local knowledge adds little; the remaining small-firm litigation niche overlaps TH10 and TH11 in batches A and B.

**Seed idea:** — (residue belongs to TH10 law-practice operations and TH11 claim files).
