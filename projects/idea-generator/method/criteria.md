# Scoring criteria

How every idea is scored. Used by the shortlist (T12), the write-ups (T13–T15) and the review (T16).
Each of the 9 lenses in [BRIEF.md](../BRIEF.md) gets a score from 1 to 5. The anchors below describe 1, 3 and 5; 2 and 4 sit in between.

**Evidence rule.** A score of 4 or 5 needs at least one cited source (URL + access date) showing the evidence named in the anchor. Without a source the score is capped at 3. A score that rests on an estimate says so ("estimate"). When in doubt, score lower: most ideas land at 2–3.

## 1. Rubric (1 / 3 / 5)

### L1 — Proven abroad, missing in Poland (weight 8%)
- **1:** No foreign analogue found, or a good Polish-language product already covers the same job.
- **3:** A foreign analogue exists with visible traction (reviews, customer logos, funding or app-store ratings), and Polish alternatives exist but are weak (outdated, partial, English-only).
- **5:** At least one foreign analogue with public revenue or a large review base (e.g. 100+ reviews on G2/Capterra or an app store) in a comparable market, and a search in Polish (Google, Allegro, app stores) finds no product doing the job in Polish.

### L2 — Weak or no competition (weight 12%)
- **1:** Several well-reviewed, well-funded or free tools serve the target customer in Polish; switching to a newcomer has no clear reason.
- **3:** Competitors exist, but there is a documented gap: low ratings (≤3.5★) or recurring complaints in reviews, a missing feature, a price far above what small customers pay, or no Polish version.
- **5:** No direct competitor serving the customer in their language, or incumbents rated ≤3★ with repeated, quoted complaints about the exact job the idea does, plus "is there a tool that…" requests left unanswered.

### L3 — Clear monetization (weight 15%)
- **1:** No obvious payer, or the customer expects it free (consumer, ad-funded, "nice to have").
- **3:** A named payer (role and company type) and a price point that matches what they pay today for something similar, but recurring payment is uncertain (one-off or seasonal use).
- **5:** B2B recurring: a named payer with budget, a price point backed by 2+ competitor pricing pages, and usage that recurs every month (invoices, payroll, listings, compliance deadlines). Reaching 10,000 PLN MRR needs a customer count that the target market can plausibly supply (see section 3).

### L4 — Copy what already makes money (weight 8%)
- **1:** No product with public revenue uses this model.
- **3:** A product with the same model shows traction indirectly (install counts, review counts, a sale listing) but no revenue figure.
- **5:** Two or more products with the same or a very close model show public revenue (Indie Hackers, TrustMRR, Starter Story, an Acquire.com/Flippa listing, founder posts), at least one of them ≥ the equivalent of 10,000 PLN MRR.
- Don't reuse lens 1 evidence here: L1 is about the gap in Poland, L4 about proof that the model makes money.

### L5 — Why now (weight 8%)
- **1:** No trigger; the problem has been the same for years.
- **3:** A trend or technology shift makes the product cheaper or better now (e.g. LLMs make a manual task automatable), but nothing forces customers to act.
- **5:** A dated, binding trigger: a law, regulation or platform rule with a deadline that falls within ~18 months and affects the target customer (cited from the official text, e.g. EUR-Lex, ISAP, a ministry page), or a technology change that makes the core feature possible for the first time.

### L6 — Evidence of pain (weight 15%)
- **1:** No one is found complaining about the problem or asking for a solution.
- **3:** A handful (3–5) of independent complaints or requests (Reddit, Wykop, forums, Facebook groups, reviews, GitHub issues), or a modest but stable search interest.
- **5:** 10+ independent, recent (≤2 years) complaints or requests with links and short quotes, people describing workarounds or money spent on the problem, and search interest that is stable or rising (Google Trends / keyword tools).

### L7 — Founder fit and feasibility (weight 12%)
- **1:** Needs a licence, hardware, physical inventory, staff, partner certification, pixel-perfect design or native mobile polish, or heavy on-call; or the MVP is clearly >3 months of work.
- **3:** MVP in 6–10 weeks on a mainstream stack; one risky dependency (an API that needs approval, a hard-to-test integration, moderate support load).
- **5:** MVP in ≤6 weeks on the founder's stack (Java/Python/Node/React/AWS), easy to specify and test automatically, public or self-serve APIs only, little support, no regulatory exposure beyond normal GDPR.

### L8 — Cheap distribution (weight 12%)
- **1:** The only route to customers is paid ads or enterprise sales; the audience can't be listed or found in one place.
- **3:** A plausible route exists (SEO keywords with some volume, a community, a marketplace) but it is crowded or slow, or it needs more than ~10 h/week.
- **5:** A concrete, cheap route to the first 100 customers that fits ~10 h/week and 500 PLN/month: a marketplace or app store where buyers search (Allegro, Shopify, Chrome Web Store, WordPress), low-difficulty keywords with measured volume, a named community, a partner with reach, or a public list of target companies (KRS/CEIDG, registries) for outbound.

### L9 — Unit economics and defensibility (weight 10%)
- **1:** Margin below ~50% after infrastructure, LLM and payment costs, or high churn expected, or one platform can kill it at will.
- **3:** Margin 50–80%, monthly churn likely 3–6%, some switching cost (data, setup) but no moat; moderate platform dependency.
- **5:** Margin above 80% (show the cost estimate), sticky usage (data accumulates, workflows depend on it, annual plans common), and no single platform able to cut off the business.

## 2. Weights

| Lens | Weight |
|---|---|
| L3 Clear monetization | 15% |
| L6 Evidence of pain | 15% |
| L2 Weak or no competition | 12% |
| L7 Founder fit and feasibility | 12% |
| L8 Cheap distribution | 12% |
| L9 Unit economics and defensibility | 10% |
| L1 Proven abroad, missing in Poland | 8% |
| L5 Why now | 8% |
| L4 Copy what already makes money | 8% |
| **Total** | **100%** |

These are the default weights from BRIEF.md, unchanged. Change them only with a reason written here and a line in [CHANGELOG.md](../CHANGELOG.md); then rescore every shortlisted idea with the new weights.

**Weighted score** = Σ (score × weight), a number from 1.0 to 5.0, rounded to one decimal.
Example: L1 3, L2 3, L3 4, L4 2, L5 3, L6 3, L7 5, L8 3, L9 4 → 0.24 + 0.36 + 0.60 + 0.16 + 0.24 + 0.45 + 0.60 + 0.36 + 0.40 = **3.41 → 3.4**.

## 3. From weighted score to chance band

Success = **≥10,000 PLN MRR within 12 months of launch**. The base rate for solo products is low: most never reach it. So the default band is `<5%`, and the score has to earn its way up.

| Weighted score | Chance band | Extra conditions |
|---|---|---|
| < 2.8 | `<5%` | — |
| 2.8 – 3.4 | `5–15%` | — |
| 3.5 – 4.1 | `15–30%` | L3, L6 and L8 each ≥ 3, and at least two of them ≥ 4 with sources |
| ≥ 4.2 | `>30%` | All of the above, plus a written argument: who the first 10 paying customers are, why they pay, and why the 10,000 PLN MRR customer count is reachable |

**Knock-outs** (override the table):
- L7 = 1 (licence, inventory, staff, hardware, heavy on-call): drop the idea and record it in [rejected.md](../rejected.md).
- L3 = 1 or L6 = 1: band is `<5%` whatever the score.
- If a condition for a band isn't met, use the next band down.

**Sanity check on customer count.** Divide 10,000 PLN by the planned monthly price (e.g. at 99 PLN/month you need ~101 paying customers, at 29 PLN/month ~345). If the reachable market, with a source for its size (e.g. GUS/BDL or registry counts), is not at least ~20× that number, cap the band at `5–15%`.

Bands are judgments backed by evidence, not computed probabilities. Every band above `<5%` must point to the sources behind the scores that put it there.

## 4. Starting sources per lens

A starting list, not a limit. Prefer primary sources (the product's own pricing page, the law's official text, official statistics). Record URL + access date for anything you use.

### L1 — Proven abroad, missing in Poland
- https://www.producthunt.com/ — launches and upvotes by category
- https://www.g2.com/ and https://www.capterra.com/ — categories, review counts, top products per market
- https://www.indiehackers.com/ — products and founder interviews
- https://alternativeto.net/ — alternatives, to check whether a Polish equivalent exists
- Polish check: https://www.google.pl/, https://allegro.pl/, https://play.google.com/store, https://apps.apple.com/

### L2 — Weak or no competition
- https://www.g2.com/, https://www.capterra.com/, https://www.trustpilot.com/ — 1–2 star reviews
- https://apps.shopify.com/, https://chromewebstore.google.com/, https://wordpress.org/plugins/ — ratings, last-update dates, review text
- https://play.google.com/store and https://apps.apple.com/ — app reviews
- https://www.reddit.com/ — "is there a tool that…" posts

### L3 — Clear monetization
- Competitor pricing pages (cite each one), e.g. Polish invoicing tools https://www.wfirma.pl/, https://www.ifirma.pl/, https://fakturownia.pl/
- Business counts for market size: https://stat.gov.pl/ and https://bdl.stat.gov.pl/
- EU business statistics: https://ec.europa.eu/eurostat

### L4 — Copy what already makes money
- https://trustmrr.com/ — verified revenue
- https://www.indiehackers.com/ — self-reported revenue
- https://www.starterstory.com/ — founder revenue case studies
- https://acquire.com/ and https://flippa.com/ — listings with revenue and asking price
- https://www.producthunt.com/, https://chromewebstore.google.com/, https://apps.shopify.com/, https://wordpress.org/plugins/ — top lists, install counts
- https://gumroad.com/ — digital product bestsellers

### L5 — Why now
- https://eur-lex.europa.eu/ — EU regulations and directives (AI Act, European Accessibility Act, NIS2, CSRD, DAC7, PSD3)
- https://isap.sejm.gov.pl/ — Polish legal acts
- https://legislacja.gov.pl/ — Polish draft legislation
- https://ksef.podatki.gov.pl/ — KSeF e-invoicing
- https://www.podatki.gov.pl/ and https://www.gov.pl/ — ministry guidance and deadlines
- https://uodo.gov.pl/ — GDPR enforcement in Poland
- https://modelcontextprotocol.io/ — MCP and agent tooling

### L6 — Evidence of pain
- https://www.reddit.com/ (e.g. r/Polska, r/SaaS, r/smallbusiness, niche subreddits)
- https://wykop.pl/
- https://www.elektroda.pl/ and other Polish forums; Polish Facebook groups (cite the group URL)
- https://github.com/ issues for developer tools
- https://news.ycombinator.com/
- https://trends.google.com/ — search interest in PL and abroad

### L7 — Founder fit and feasibility
- Founder profile in [BRIEF.md](../BRIEF.md)
- API documentation of each integration the idea needs (cite it; note approval or certification steps)
- https://openrouter.ai/ — model availability and prices for LLM features

### L8 — Cheap distribution
- Marketplaces: https://allegro.pl/, https://apps.shopify.com/, https://chromewebstore.google.com/, https://wordpress.org/plugins/
- Keyword volume: https://ads.google.com/home/tools/keyword-planner/ and https://trends.google.com/
- Communities: https://wykop.pl/, https://www.reddit.com/, https://www.producthunt.com/, https://www.linkedin.com/
- Lists of target companies for outbound: https://wyszukiwarka-krs.ms.gov.pl/ (KRS), https://www.biznes.gov.pl/ (CEIDG search), https://dane.gov.pl/ (Polish open data)

### L9 — Unit economics and defensibility
- Infrastructure prices: https://aws.amazon.com/pricing/
- LLM prices: https://openrouter.ai/models
- Payment fees: https://stripe.com/pricing and https://www.przelewy24.pl/
- Platform risk: the marketplace's developer terms (cite the specific page per idea)

## 5. Sources added during research

### L1 (added by T02, accessed 2026-10-29)
- https://www.gramwzielone.pl/ — Polish renewable-energy trade news; lists Polish PV design tools
- https://www.capterra.pl/ — Polish Capterra, category pages for PL-market software
- https://itwiz.pl/ and https://www.infor.pl/ — Polish news on NIS2 (KSC amendment) and the whistleblower act; confirm in ISAP
- https://useme.com/pl/blog/ — Polish freelancer-marketplace data (vendor's own figures)
- https://base.com/ — BaseLinker (renamed Base), reverse-direction proof that Polish SaaS sells abroad

### L2 (added by T03, accessed 2026-10-29)
- https://api.github.com/search/repositories?q=ksef&sort=stars — GitHub search API; works with the fetch tool (stars, last push, language) and is good for gauging maintained SDKs and open-source competitors
- https://www.trustpilot.com/review/ifirma.pl (pattern: /review/<domain>) — readable by the fetch tool (score, review counts, recent complaints); small and skewed samples, unclaimed profiles are unrepresentative
- https://play.google.com/store/search?q=KSeF&c=apps&hl=pl — Polish Play Store results with ratings (fetchable; truncated list); app-detail pages by package id can be resolved the same way
- https://wordpress.org/plugins/search/allegro/ — plugin ratings counts and active installs (fetchable)
- https://spolecznosc.allegro.pl/t5/zaawansowani-sprzedawcy/alternatywa-dla-baselinker/m-p/987268 — Allegro Community seller board example: "alternatywa dla BaseLinker" type threads with quotes and prices
- Not fetchable in this setup: Capterra and G2 (403), Reddit, trusted.de (403), Shopify App Store search (fails to load)

### L3 (added by T04, accessed 2026-10-29)
- Vendor pricing pages that the fetch tool reads as text: https://www.ifirma.pl/cennik, https://www.kadromierz.pl/cennik, https://www.sellasist.pl/cennik, https://www.shoper.pl/cennik/, https://www.smsapi.pl/cennik, https://landingi.com/pl/cennik, https://www.lexware.de/preise/, https://sevdesk.de/preise/, https://www.craftboxx.de/preise, https://www.papershift.com/de/preise, https://www.moneybird.nl/prijzen/, https://www.cookiebot.com/en/pricing/, https://www.iubenda.com/en/pricing, https://www.getjobber.com/pricing/, https://www.housecallpro.com/pricing/, https://www.shepherd.vet/pricing, https://www.timetopet.com/pricing, https://www.buildium.com/pricing/, https://www.tidio.com/pricing/, https://brand24.com/prices/
- Pricing pages that do not extract (prices in images or scripts, redirects to home, 404): wFirma /cennik, inFakt /cennik/, Fakturownia paid tiers, Plancraft /de/preise, Fakturoid /cenik (ambiguous), Holded, Fortnox, Klippa. Use a browser or Wayback for these.
- https://www.fuer-gruender.de/wissen/unternehmen-fuehren/buchhaltung/handwerker-software-vergleich/ — independent German trades-software comparison (13 vendors, prices conflict inside the article)
- https://www.vatax.pl/blog/obsluga-ksef-porownanie-cen — Polish KSeF price comparison across invoicing tools and ERPs (published by a vendor of one compared product)
- https://cenauslug.pl/ — Polish price-comparison guides, bookkeeping office fees (commercial)
- https://www.zdh.de/daten-und-fakten/kennzahlen-des-handwerks/wirtschaftlicher-stellenwert-des-handwerks-2025/ — German craft business counts (primary)
- https://xyz.pl/ — Polish business news citing GUS counts; read the GUS release for the primary figure
- Caution: hagel-it.de contained text addressed to AI assistants (ignored); treat as low-reliability. See L3-F14.

### L4 (added by T05, accessed 2026-10-29)
- https://trustmrr.com/country/pl — Polish-based startups with Stripe/Paddle/RevenueCat-verified revenue (partial page, ~100 of 182 visible); profile pages `https://trustmrr.com/startup/<slug>` read as text. `/category/<name>` pages work for `saas` and `developer-tools`; `/country/poland` and `/category/e-commerce` returned 404. FAQ notes figures can differ from the provider dashboard by up to 30%: https://trustmrr.com/faq
- https://flippa.com/search?filter%5Bproperty_type%5D=saas — Flippa SaaS listings with revenue, profit, age and asking price in the search table (partial, ~24 of 675); individual listing pages like https://flippa.com/12164346 are readable
- https://app.acquire.com/public/<listing-slug> — public Acquire.com listing pages are readable (the acquire.com/startups/ index returned 404)
- https://dashboard.simpleanalytics.com/open — example of a founder-published live revenue page
- https://extensionpay.com/articles/browser-extensions-make-money and https://freemius.com/blog/codecanyon-wordpress-plugins-analysis/ — extension and plugin revenue roundups (self-reported / dated 2016)
- https://revenuehunt.com/state-of-the-shopify-app-economy/ — Shopify App Store revenue concentration (estimated)
- https://www.starterstory.com/data — founder-revenue database, no stated verification; lead generator only
- Not fetchable in this setup: Indie Hackers (403 on product, interview and post pages), BigIdeasDB (429), Microns listings (404)
- Caution: several TrustMRR profile pages (Image-Charts, ConvertLabs, OpenAlternative, TrackAI) contained text addressed to AI readers (ignored). See L4-F04.
