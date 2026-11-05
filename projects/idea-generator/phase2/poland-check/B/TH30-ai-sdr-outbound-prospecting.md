# TH30 — AI SDR and outbound prospecting (Poland check)

Theme: [THEMES.md#th30](../../themes/THEMES.md#th30) · rank 41, batch B · sources accessed **2026-11-05** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| Woodpecker (Woodpecker AI sp. z o.o., Wrocław, listed on NewConnect) | Cold email + LinkedIn sequences; AI email writer, AI reply interest detection, Lead Finder credits; MCP server and CLI for AI agents; "AI-native" new version announced | monthly plans by send volume (5k–1M emails), PLN among 12 currencies, 14-day trial; amounts not rendered on the page (unverified) | global SMBs; Q3 2025 revenue 4.6M PLN (−13% y/y), net loss 280k PLN | [woodpecker.co/pricing](https://woodpecker.co/pricing/); [strefainwestorow.pl Q3 2025](https://strefainwestorow.pl/wiadomosci/20251121/woodpeckerco-publikuje-wyniki-za-trzeci-kwartal); [biznesradar.pl](https://www.biznesradar.pl/a/141477,woodpecker-ponownie-ze-strata-ale-widzi-pierwsze-sygnaly-stabilizacji) |
| DMSales (Warsaw) | Polish B2B databases from several sources, AI email generator (0.1 point/email), DMSender campaigns (0.01 point/email) | points-based; plan amounts not shown | Polish B2B sales teams (unverified) | [dmsales.com/pl/cennik](https://dmsales.com/pl/cennik) |
| BizSpace (Warsaw) | Search over "almost a million" Polish firms, lookalike ICP modelling from CRM data, lead lists; no automated sending described | not shown | not shown | [bizspace.pl](https://bizspace.pl/) |
| Outbound agencies (Outbound Republic, Vanderbuild, Automatemeup, Leadpack and others) | Done-for-you lead generation "with AI"; RevenueBase lists 39 Polish firms under "AI SDR platforms" (descriptions unverified) | retainers (unverified) | Polish B2B firms | [revenuebase.ai list](https://revenuebase.ai/companies/ai-sdr-platforms/poland) |

## 2. Does the Western leader already serve Poland?
- **Artisan (Ava)**: reviews of its help centre say Ava writes in 40+ languages; no source names Polish explicitly; coverage of Polish firms in its lead data not checked. Usable in Polish in principle, no Polish sales or case studies found ([bitscale.ai review](https://bitscale.ai/blogs/artisan-ai-review); [appvizer](https://appvizer.com/customer/sales-intelligence/artisan)).
- **11x (Alice)**: e-mail and social agents that research accounts and write outreach; the site lists "Multi-Lingual Outreach" without naming languages; only a London office in Europe; no Polish presence found ([11x.ai](https://www.11x.ai/)).
- **AiSDR** (Ukrainian roots, Lviv IT Cluster 2023): its help centre was reported in search results as supporting 21+ languages for e-mail and LinkedIn; the article now returns 404, so unverified.
- **AInora** (LT): sells an AI SDR (voice callback, qualification, booking) with full Polish-language site and a Polish legal guide on cold calling ([ainora.lt/pl](https://ainora.lt/pl/asystent-sprzedazy-ai-sdr)).
- **ElevenLabs** markets AI SDR voice agents in Polish ([elevenlabs.io/pl](https://elevenlabs.io/pl/agents/ai-sales-agent)).
- Not checked (no accounts created): output quality of Polish emails, PLN invoicing for Artisan/11x.

## 3. Polish demand signals
- Autocomplete (2026-11-05): "ai sdr" → 10, all English ("meaning", "tools", "reddit", "linkedin"); "cold mailing" → 10 including "cold mailing co to", "cold mailing a rodo", "cold mailing b2b"; "cold mailing rodo" → only "cold mailing a rodo"; "baza firm ceidg" → 3 ("baza nowych firm ceidg", "baza firm i osób decyzyjnych ceidg krs regon"); "automatyzacja cold mailingu" → empty; "generowanie leadów b2b" → only itself. Interest exists but centres on legality and data lists, not on AI agents.
- Job posts for Polish-speaking human SDRs in Warsaw and abroad show the job still exists ([bluselection.com](https://www.bluselection.com/job/polish-speaking-sdr-5912651); [startup.jobs, Fonio](https://startup.jobs/sales-development-representative-polish-speaking-fonio-8348341)).

## 4. What adaptation needs
- **Law is the main local factor.** Prawo komunikacji elektronicznej (in force 2024-11-10), art. 398, requires prior consent for unsolicited commercial information and direct marketing through telecom terminal equipment and automated calling systems; commentators read it as covering business recipients too and as ruling out cold calls and, for most, cold e-mailing without consent; UKE can fine up to 3% of prior-year revenue (art. 444, 446). The B2B e-mail point is contested between commentators and no UKE decision on B2B cold mailing was found ([prawo.pl](https://www.prawo.pl/biznes/zgody-marketingowe-i-kontakty-handlowe-co-mowi-prawo-komunikacji-elektronicznej,530981.html); [Wolters Kluwer](https://www.wolterskluwer.com/pl-pl/expert-insights/jak-prowadzic-dzialania-marketingowe-zgodnie-z-rodo); [lexlege art. 398](https://lexlege.pl/komunik-elektr/art-398/); [Lege Artis](https://czasopismo.legeartis.org/2024/08/przesylanie-informacji-handlowych-prawo-komunikacji-elektronicznej-uprzednia-zgoda-marketing-bezposredni/)). A US-style autonomous SDR that blasts first-touch e-mails and calls is legally riskier in Poland than in the US.
- Lead data: KRS (M09), CEIDG (M10), GUS REGON (M11), CRBR (M13) give firm and board data; CEIDG e-mails and phones of sole traders are personal data under RODO.
- Polish B2B language register and formal address (Pan/Pani) (M52).

## 5. Demographic or social driver
DD7: labour is scarce and expensive (66% of firms cite labour costs), which favours replacing junior SDR hours, but this is a weak, generic driver.

## 6. CEE check
No CZ/SK/RO/HU AI SDR in the [R6 catalogue](../../catalogue/R6-cee-peers.csv). The nearby entrants are Baltic: AInora (LT) already sells in Polish, and Handhold (EE, `R4-EE-002`) and Zero (FI, `R4-FI-001`) are in the theme.

## 7. Verdict: **taken**
Sending, sequencing and AI-written e-mails are covered for Polish users by Woodpecker (a Polish company, PLN pricing) and DMSales (Polish data + AI e-mail), with multilingual Western agents and AInora already marketing in Polish. The remaining space is narrowed by PKE art. 398: the core US workflow (autonomous first-touch outreach to bought lists) is legally exposed in Poland, and search demand is about "is cold mailing legal" rather than about AI SDRs.

**Seed idea (weak):** consent-first prospecting assistant: builds account lists from KRS/CEIDG/REGON, writes research notes and first-touch drafts only for channels with a defensible legal basis (e.g. LinkedIn, public tender contacts, warm inbound), and keeps the RODO/PKE record of basis, source and opt-out per contact; 149–299 PLN/user/month. Legal reading of art. 398 for B2B e-mail must be confirmed first.
