# Phase 2 scoring criteria

How Phase 2 products, themes and ideas are recorded and scored. Used by the regional scans (T04–T14, catalogue columns), theme ranking (T15), the Poland checks (T16–T18), the shortlist (T20), the write-ups (T21–T23) and the review (T24).

Each of the 9 lenses in [BRIEF.md](../BRIEF.md) gets a score from 1 to 5. The anchors below describe 1, 3 and 5; 2 and 4 sit in between.

**Evidence rule.** A score of 4 or 5 needs at least one cited source (URL + access date) showing the evidence named in the anchor. Without a source the score is capped at 3. A score that rests on an estimate says so ("estimate"). When in doubt, score lower: most ideas should land at 2–3. (Kept from Phase 1's [criteria](../../method/criteria.md).)

## 1. Rubric (1 / 3 / 5)

### L1 — Innovation / LLM-native (weight 12%)
- **1:** Classic software or a service that worked the same way before 2023; the LLM part is a chat box or a text-polishing button bolted on, removable without changing the product.
- **3:** An LLM does one real job step (reads a document, drafts an output, classifies, transcribes), but the workflow around it is familiar and a pre-2023 product could do ~70% of the job with templates or rules.
- **5:** The product only became practical with LLMs since 2023 (agents acting across tools, real-time voice, vision, document understanding at scale, generation), and it replaces a person's job step, a service or an agency end to end. Meets at least three of the brief's four "innovative" conditions.

### L2 — Durable traction abroad (weight 12%)
Scored with the durable-vs-hype rubric in section 6. Growth alone is not enough.
- **1:** No traction evidence, or only hype evidence (launch upvotes, traffic spike, a viral post) and one country.
- **3:** Visible traction (funding round, revenue claim, chart rank, customer logos) in 1–3 of the 51 countries, with 2–3 durable signals evidenced, and no serious hype warning.
- **5:** Public revenue or ARR, retention or NRR evidence, and the theme appears in ≥5 countries across ≥3 regions, with ≥5 durable signals evidenced and no unresolved hype warning.
- **Cap:** an idea whose Western analogue shows only hype warnings can't score above 3 (brief rule); with 2+ hype warnings and ≤1 durable signal, cap at 2.

### L3 — Poland gap (weight 12%)
- **1:** A Polish product, or the Western leader itself, already does the job well in Polish (Polish UI, Polish documents, Polish integrations, PLN pricing, Polish VAT invoices). Gap verdict "taken".
- **3:** Polish or Western alternatives exist but serve Poland partly: English-only UI, no Polish integrations, no PLN/VAT invoice, weak Polish-language output, or only a generic tool (ChatGPT, Copilot) used today. Gap verdict "partial".
- **5:** Search in Polish (Google, app stores, local media, Polish startup lists) finds no product doing the job, **and** the Western leader was actually tried and fails on Polish documents, integrations or language. Gap verdict "open".

### L4 — Localization moat (weight 15%)
- **1:** Translation is the only adaptation; any foreign entrant can serve Poland by switching the UI language.
- **3:** Needs one or two Polish-specific pieces that take weeks to learn and build (a Polish registry or form, a local payment method, Polish industry vocabulary, a local integration such as InPost or Allegro).
- **5:** Needs several Polish-specific pieces from the [local-moats inventory](../research/poland/local-moats.md) that take months to learn and that a foreign team would struggle with: Polish law and forms (ZUS, KSeF, JPK, KRS, CEIDG, ePUAP, mObywatel, NFZ/IKP, e-Dziennik, księgi wieczyste, Geoportal, SAOS, ISAP), industry structure, and how Polish customers buy (phone, trust, VAT invoices, BLIK/Przelewy24).

### L5 — Polish demand, including demographic and social drivers (weight 15%)
- **1:** No evidence that Polish customers have the problem, or the problem is rare in Poland (e.g. driven by a US-only rule or habit).
- **3:** The problem exists in Poland with indirect evidence (forum threads, job posts for the job step, search autocomplete) and a plausible driver, but no data on its size.
- **5:** Sourced data for both the size of the target group (GUS/BDL, registry counts, Eurostat) and a driver making demand grow (demographic, social, regulatory or technological, e.g. ageing, migrants, labour shortages, a dated 2026–2028 regulatory trigger), plus direct demand evidence (people asking for or paying for a workaround).

### L6 — Monetization and willingness to pay in PLN (weight 10%)
- **1:** No obvious payer, or customers expect it free; or the unit economics fail at a realistic PLN price once token costs are counted.
- **3:** A clear payer and a PLN price grounded in comparable Polish tools; gross margin after token, infrastructure and payment costs ≥60% on an estimate.
- **5:** The customer already pays for the job (salary hours, an agency, a freelancer, a penalty) and the PLN price is a fraction of that spend; computed gross margin ≥75% with real token prices (cite [OpenRouter](https://openrouter.ai/models) or the provider page) at the planned usage per customer; value-based pricing (per client, per document, per outcome).

### L7 — Founder fit and buildability (weight 8%)
- **1:** Needs a financial or medical licence, large upfront capital, staff, physical inventory or heavy on-call operations (knock-out), or an MVP far beyond 6 weeks.
- **3:** Buildable by the founder with the agentic stack in ~6 weeks, but with one hard dependency (API approval, certification, a data source with uncertain access) or behaviour that is hard to test automatically (open-ended voice, subjective outputs).
- **5:** MVP in ≤4 weeks on known tech (Java/Python/Node, React, AWS), all integrations publicly documented and open, outputs testable automatically (fixtures, golden files, schema checks), ≤40 h/month of non-code work after launch.

### L8 — Distribution in Poland, first 100 customers (weight 8%)
- **1:** No identifiable channel except paid ads into a broad audience; customers are hard to list or reach.
- **3:** A plausible channel exists (an industry Facebook group, an association, a marketplace, outbound to a registry list) but nobody has shown it works for this kind of product.
- **5:** A concrete, cheap channel with evidence it works in Poland: a marketplace or app store with Polish demand, partners such as accounting offices with a referral programme, purchase-intent search phrases with volume, or a named community where the target customer asks for this.

### L9 — Defensibility (weight 8%)
- **1:** The Western leader can enter Poland with a translation, or ChatGPT/Copilot/the platform owner absorbs the feature in one update, or a local copycat can clone it in a month.
- **3:** Some protection: Polish integrations, a niche the leader ignores, or workflow lock-in, but no data or regulatory advantage.
- **5:** Value lives in proprietary or local data, Polish integrations, regulation or distribution that compounds with each customer (switching cost, network effect, partner channel), and the Western leader has shown no sign of entering CEE.

## 2. Weights

| Lens | Weight |
|---|---|
| L1 Innovation / LLM-native | 12% |
| L2 Durable traction abroad | 12% |
| L3 Poland gap | 12% |
| L4 Localization moat | 15% |
| L5 Polish demand | 15% |
| L6 Monetization and WTP in PLN | 10% |
| L7 Founder fit and buildability | 8% |
| L8 Distribution in Poland | 8% |
| L9 Defensibility | 8% |
| **Total** | **100%** |

These are the default weights from the brief, unchanged (they sum to 100% and match the Phase 2 goal: local edge L4 and L5 weigh most). Change them only with a reason written here and a line in [CHANGELOG.md](../CHANGELOG.md); then rescore every shortlisted idea with the new weights.

**Weighted score** = Σ (score × weight), a number from 1.0 to 5.0, rounded to one decimal.
Example: L1 4, L2 3, L3 4, L4 4, L5 3, L6 3, L7 4, L8 3, L9 3 → 0.48 + 0.36 + 0.48 + 0.60 + 0.45 + 0.30 + 0.32 + 0.24 + 0.24 = **3.47 → 3.5**.

**Quick score (T20 shortlist).** Same lenses and weights, scored from the Poland-check file and the catalogue only; mark it "quick". Write-ups rescore with full evidence.

## 3. From weighted score to chance band

Success = **≥10,000 PLN MRR within 12 months of launch**. The base rate for solo products is low, so the default band is `<5%` and the score has to earn its way up.

| Weighted score | Chance band | Extra conditions |
|---|---|---|
| < 2.8 | `<5%` | — |
| 2.8 – 3.4 | `5–15%` | — |
| 3.5 – 4.1 | `15–30%` | L5, L6 and L8 each ≥ 3, and at least two of them ≥ 4 with sources; L3 ≥ 3 |
| ≥ 4.2 | `>30%` | All of the above, plus a written argument: who the first 10 paying customers are, why they pay, and why the customer count for 10,000 PLN MRR is reachable |

**Knock-outs** (override the table):
- L7 = 1 (licence, capital, staff, inventory, heavy on-call): drop the idea and record it in [rejected.md](../rejected.md).
- L3 = 1 (gap "taken") or L5 = 1 or L6 = 1: band is `<5%` whatever the score.
- If a condition for a band isn't met, use the next band down.

**Sanity check on customer count.** Divide 10,000 PLN by the planned monthly price (at 99 PLN/month ~101 paying customers, at 29 PLN/month ~345). If the reachable Polish market, with a source for its size (GUS/BDL, registry counts), is not at least ~20× that number, cap the band at `5–15%`.

Bands are judgments backed by evidence, not computed probabilities. Every band above `<5%` points to the sources behind the scores that put it there.

## 4. Opportunities (szanse) and risks (ryzyka)

Write the two lists independently: list opportunities first without looking at risks, then risks without looking at opportunities. Don't write a risk as the negation of an opportunity ("demand may not exist" next to "demand exists"). Aim for 3–6 items in each list.

**Each item** gets:
- **Likelihood** H / M / L: H = more likely than not within 12 months, with evidence; M = plausible, some evidence; L = possible but no evidence yet.
- **Impact** H / M / L on reaching 10,000 PLN MRR: H = changes whether the idea reaches the goal at all; M = changes the time or size noticeably (±30% of MRR or ±3 months); L = minor.
- **What would make it true** (for an opportunity) or **early warning sign** (for a risk): something observable within the first 3 months.

**Points:** H = 3, M = 2, L = 1; item weight = likelihood × impact (1–9). An item with weight ≥ 6 is **major**.

**How they move the band** (after the score table and knock-outs):
1. Sum opportunity weights (O) and risk weights (R).
2. **Up one band** only if O − R ≥ 6 **and** at least one major opportunity has a source, **and** the extra conditions of the higher band are met. Never more than one band up; never into `>30%` by this rule alone.
3. **Down one band** if R − O ≥ 6, or if any risk is H likelihood × H impact (weight 9) with no mitigation in the MVP plan.
4. **Down two bands** (floor `<5%`) if two or more risks have weight 9.
5. Otherwise the band stays where the score put it. Record the sums and the rule applied, e.g. "O 14, R 11, no H×H risk → band unchanged".

Typical risk sources to consider (from the brief): "already works in Polish", ChatGPT/Copilot absorption, token cost vs. PLN price, Polish-language model quality, AI Act high-risk category, Western leader entering CEE, a German/Czech adaptation moving in, graveyard lessons, slow Polish sales cycle.

## 5. Catalogue CSV columns

One row per product in `catalogue/RN-<name>.csv`, UTF-8, comma-separated, header row exactly as below, fields with commas in double quotes. `unknown` when not found; never leave a cell blank except `theme` before T15.

| Column | Content | Example |
|---|---|---|
| `id` | `RN-CC-NNN`: region number, ISO 3166-1 alpha-2 country code, running number | `R1-US-014` |
| `name` | Product name as on its site | `Abridge` |
| `country` | Country where the company is based or the product first grew (English name from the brief) | `United States` |
| `region` | `R1`–`R10` | `R1` |
| `url` | Product home page (checked) | `https://…` |
| `launched` | Year (or year-month) of launch or breakout, with "launch"/"breakout"; `unknown` | `2023 launch` |
| `category` | Short field label, reused across rows (e.g. healthcare-admin, legal, hr, accounting, sales, real-estate, education, consumer-health) | `healthcare-admin` |
| `b2b_b2c` | `B2B`, `B2C` or `B2B2C` | `B2B` |
| `llm_role` | What the LLM does, a few words (agent, voice, vision, document understanding, generation, classification) | `voice: transcribes visits, drafts notes` |
| `traction` | Number + what it measures + date | `"ARR 100M USD, 2025-06"` |
| `traction_source` | URL of the source for `traction` (+ access date in `YYYY-MM-DD`) | `https://… 2026-11-02` |
| `country_specific` | `y`/`n` + why (does it depend on that country's laws, systems or habits?) | `"y: built on US Medicare billing codes"` |
| `works_in_polish` | `unknown` / `no` / `partly` / `yes`, from trying it or its docs | `partly` |
| `first_channel` | How its first customers came (marketplace, SEO, community, partners, viral loop, outbound, paid ads), or `unknown` | `"partners: health-system pilots"` |
| `durable_signals` | Signal numbers from the brief's Success signals (1–10) with evidence, each with a source | `"1 replaces scribe salary (url); 3 NRR 130% (url)"` |
| `hype_warnings` | Hype warnings found, or `none found` | `"lifetime deals on AppSumo (url)"` |
| `pl_adaptation_angle` | One line: what a Polish adaptation would need (local systems, laws, data) | `"NFZ e-recepta/IKP, Polish medical vocabulary"` |
| `theme` | Theme id from `themes/THEMES.md` (filled in T15) | `` |

## 6. Durable vs. hype rubric (used by L2)

For each Western product, check the brief's 10 durable signals and the hype warnings. A signal counts only with a source (URL + date); "probably" doesn't count.

**Durable signals** (numbers as in the brief): 1 replaces an existing spend · 2 frequent, painful problem with an owner · 3 retention · 4 expansion · 5 owned distribution · 6 time to value in minutes · 7 value-based pricing from day one · 8 hard to absorb · 9 pull from customers · 10 timing window.

Signals 3 (retention) and 4 (expansion) are the strongest evidence: count each of them double.

**Hype warnings:** traffic spike without retention · revenue mostly from one-off or lifetime deals · growth from paid ads or influencers only · a novelty use case (avatars, one-time generators) · a thin wrapper around one model's API · rapid price cuts · heavy layoffs or a pivot after funding.

**Durability score** = durable points (signals, with 3 and 4 double) − 2 × hype warnings.

| Durability score | Label | Effect on L2 |
|---|---|---|
| ≤ 0, or only hype evidence | **hype** | L2 ≤ 2 (≤ 3 if spread is wide, per the brief cap) |
| 1 – 3 | **unproven** | L2 ≤ 3 |
| 4 – 6 | **promising** | L2 ≤ 4 |
| ≥ 7, including signal 3 or 4 | **durable** | L2 can reach 5 if spread across countries also qualifies |

Then set L2 within the cap using spread: theme in 1 country → at most 3; 2–4 countries → at most 4; ≥5 countries across ≥3 regions → 5 possible.

For a theme (T15), take the best-evidenced product per country and report how many products are **durable**, **promising**, **unproven** and **hype**; rank themes by spread and the count of durable/promising products, not by headline growth.

For a Polish idea (write-ups), list which durable signals the Polish adaptation can realistically reproduce: the budget line it replaces (signal 1), the first channel (signal 5) and the retention driver (signals 3, 8).
