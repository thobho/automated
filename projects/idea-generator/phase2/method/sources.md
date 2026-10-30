# Phase 2 sources

Starting sources for the global trend lists (T04), the regional scans (T05–T14) and the Poland checks (T16–T18). A starting list, not a limit: add sources found during research under "Sources added during research" at the end, with URL, what it gives and the access date. Per-country startup media and app-store chart links are in [countries.md](countries.md).

All links below were checked on 2026-10-30 with `tools/check_links.py` and by reading the page title. "(blocks bots)" means the site exists but returns 403/429 or a challenge page to the fetch tool; read it in a browser, via search results, or via a mirror noted in the line. Prefer primary sources: the product's own site, pricing page, app-store page, founder post or funding announcement. Lists and media are for finding products, not for citing traction when the primary source is available.

## 1. Global sources (required list)

| Source | What it gives | Access notes |
|---|---|---|
| [YC startup directory](https://www.ycombinator.com/companies) | Every YC company with batch, industry, region, team size, one-liner | Readable. Filters in the URL, e.g. [industry Generative AI](https://www.ycombinator.com/companies/industry/generative-ai), [region Europe](https://www.ycombinator.com/companies?regions=Europe). Also [Launch YC](https://www.ycombinator.com/launches) and the [Requests for Startups](https://www.ycombinator.com/rfs) |
| a16z Top 100 Gen AI Consumer Apps | Ranked consumer AI web and mobile apps by traffic/MAU, twice a year | Readable: [6th edition](https://a16z.com/100-gen-ai-apps-6/), [5th edition](https://a16z.com/100-gen-ai-apps-5/), [4th edition](https://a16z.com/100-gen-ai-apps-4/). Compare editions to separate durable apps from one-edition hype |
| [Product Hunt](https://www.producthunt.com/) | Launches, upvotes, categories | Home page loads; leaderboards and category pages (blocks bots). Launch votes are a hype signal, not traction (see brief) |
| [TrustMRR](https://trustmrr.com/) | Startups with payment-provider-verified revenue | Readable. [AI category](https://trustmrr.com/category/ai), [SaaS category](https://trustmrr.com/category/saas); FAQ says figures can differ from the provider dashboard by up to 30% ([FAQ](https://trustmrr.com/faq)). Phase 1 saw profile pages with text addressed to AI readers: ignore such text |
| [Indie Hackers](https://www.indiehackers.com/) | Self-reported revenue, founder interviews | Home loads; product and post pages (blocks bots) per Phase 1. Self-reported: mark as such |
| [Forbes AI 50](https://www.forbes.com/lists/ai50/) | Annual list of top private AI companies (2026 edition live) | Readable |
| CB Insights AI 100 | Annual list of promising AI startups by category | Readable: [2026](https://www.cbinsights.com/research/report/artificial-intelligence-top-startups-2026/), [2025](https://www.cbinsights.com/research/report/artificial-intelligence-top-startups-2025/); more reports on [CB Insights Research](https://www.cbinsights.com/research/) |
| G2 Fastest Growing Products | Top 100 products by buyer-adoption momentum (Best Software Awards) | [List page](https://www.g2.com/best-software-companies/fastest-growing) (blocks bots); readable summary in [G2's 2026 awards announcement](https://company.g2.com/news/g2s-2026-best-software-awards) |
| [Similarweb](https://www.similarweb.com/top-websites/) | Top websites by category and country; top Google Play apps by country | Readable. Category example: [Computers & technology](https://www.similarweb.com/top-websites/computers-electronics-and-technology/). Apps pattern in [countries.md](countries.md). Traffic is an estimate; it shows reach, not retention |
| [Sensor Tower](https://sensortower.com/) | App-store top charts (free, paid, grossing) by country and category; blog with market reports | [Top charts](https://app.sensortower.com/top-charts) readable; [blog](https://www.sensortower.com/blog) |
| [Appfigures](https://appfigures.com/resources/insights) | App revenue/download estimates and weekly insights | Insights pages readable; [top-apps charts](https://appfigures.com/top-apps) (blocks bots) |
| Apple App Store RSS (JSON) | Official top charts for all 51 countries, by genre | Free, no key; pattern and genre ids in [countries.md](countries.md), e.g. [US top-grossing Business](https://itunes.apple.com/us/rss/topgrossingapplications/limit=100/genre=6000/json) |
| [Dealroom](https://dealroom.co/) | Startup and funding database, ecosystem reports | Site and [guides/reports](https://dealroom.co/guides) readable; the [app](https://app.dealroom.co/) (blocks bots) and needs an account for full data |
| [Sifted](https://sifted.eu/) | European startup news, funding, rankings | Home readable; [rankings](https://sifted.eu/rankings) (blocks bots) |
| [TechCrunch](https://techcrunch.com/) | Funding and launch news, mostly US | Readable; [AI category](https://techcrunch.com/category/artificial-intelligence/) |
| Hacker News Show HN | Launches by builders, comment reactions | [Show HN](https://news.ycombinator.com/show); search via [HN Algolia](https://hn.algolia.com/) and its API, e.g. [Show HN + AI](https://hn.algolia.com/api/v1/search?tags=show_hn&query=AI) (JSON, no key) |

### Other global sources
- [Crunchbase News](https://news.crunchbase.com/) — funding round reports and AI funding tallies; the [Crunchbase](https://www.crunchbase.com/) database needs an account.
- [EU-Startups](https://www.eu-startups.com/) and its [database](https://www.eu-startups.com/directory/), [Tech.eu](https://tech.eu/) — European funding news by country.
- [State of European Tech](https://www.stateofeuropeantech.com/) (Atomico) — yearly European funding and talent data.
- [Bessemer State of AI 2025](https://www.bvp.com/atlas/the-state-of-ai-2025) and [Menlo Ventures, State of Generative AI in the Enterprise 2025](https://menlovc.com/perspective/2025-the-state-of-generative-ai-in-the-enterprise/) — VC views on which AI categories have revenue and retention (interested sources: they invest in the space).
- [StartupBlink](https://www.startupblink.com/) and [Startup Genome](https://startupgenome.com/) — ecosystem rankings by country and city; useful to pick where to look, not for products.
- Accelerator portfolios across countries: [Techstars](https://www.techstars.com/accelerators), [Antler](https://www.antler.co/), [Entrepreneurs First](https://www.entrepreneurfirst.com/), [500 Global](https://www.500.co/), [Founder Institute](https://www.fi.co/), [Startupbootcamp](https://www.startupbootcamp.org/), [Seedcamp](https://www.seedcamp.com/), [Speedinvest](https://www.speedinvest.com/).
- [Wellfound](https://www.wellfound.com/) — startup job posts; fast hiring is a traction hint.
- Token costs for unit economics: [OpenRouter models and prices](https://openrouter.ai/models), [OpenRouter usage rankings](https://openrouter.ai/rankings) (which apps consume most tokens: an LLM-native traction hint).

## 2. Poland check sources (gap, demand, Polish-language models)

Reused from Phase 1 ([method/criteria.md](../../method/criteria.md), section 4–5) where they still apply.
- Polish startup and tech media: [MamStartup](https://mamstartup.pl/), [Startup Poland](https://startuppoland.org/) (reports on the Polish startup scene), [Spider's Web](https://www.spidersweb.pl/) and [Bizblog](https://www.bizblog.spidersweb.pl/), [ITwiz](https://itwiz.pl/), [Puls Biznesu](https://www.pb.pl/), [Rzeczpospolita](https://www.rp.pl/), [Forbes Polska](https://www.forbes.pl/). Funding: [PFR Ventures](https://pfrventures.pl/) (blocks bots).
- Polish app-store check: [App Store PL top-grossing Business](https://itunes.apple.com/pl/rss/topgrossingapplications/limit=100/genre=6000/json), [Similarweb Google Play Poland, Business](https://www.similarweb.com/top-apps/google/poland/business/), [Google Play search](https://play.google.com/store/search?q=KSeF&c=apps&hl=pl) (pattern from Phase 1; change the query).
- Search demand: [Google autocomplete JSON](https://suggestqueries.google.com/complete/search?client=firefox&hl=pl&gl=pl&q=asystent%20AI) (shows that a phrase is searched, not volume), [Google Trends](https://trends.google.com/), [Wykop tags](https://wykop.pl/tag/ksef).
- Polish-language models: [Bielik.ai](https://bielik.ai/), [PLLuM](https://pllum.org.pl/).
- Phase 1 found reddit.com, Trustpilot, Capterra, G2, Indie Hackers and allegro.pl hard or impossible to read with the research tools (2026-10-29); use a browser session for them.

## 3. Regional sources (at least two per region)

Country-level media for every country are in [countries.md](countries.md); below are regional media, funding trackers and accelerators.

### R1 North America
- Media: [TechCrunch](https://techcrunch.com/), [GeekWire](https://www.geekwire.com/), [BetaKit](https://betakit.com/) (Canada).
- Funding trackers: [Crunchbase News](https://news.crunchbase.com/), [YC directory](https://www.ycombinator.com/companies).
- Accelerators: [Techstars](https://www.techstars.com/accelerators), [Creative Destruction Lab](https://www.creativedestructionlab.com/) and [MaRS](https://www.marsdd.com/) (Canada), [Startup Canada](https://www.startupcan.ca/).

### R2 UK & Ireland
- Media: [UKTN](https://uktech.news/), [Sifted](https://sifted.eu/), [Silicon Republic](https://www.siliconrepublic.com/).
- Funding trackers: [Beauhurst](https://www.beauhurst.com/) (UK private companies; reports public, data paid), [TechIreland](https://www.techireland.org/).
- Accelerators and agencies: [Entrepreneurs First](https://www.entrepreneurfirst.com/), [Seedcamp](https://www.seedcamp.com/), [NDRC](https://www.ndrc.ie/), [Enterprise Ireland](https://www.enterprise-ireland.com/).

### R3 DACH & Benelux
- Media: [Gründerszene](https://www.gruenderszene.de/), [deutsche-startups.de](https://www.deutsche-startups.de/), [Trending Topics](https://www.trendingtopics.eu/), [startupticker.ch](https://www.startupticker.ch/en), [Silicon Canals](https://www.siliconcanals.com/).
- Funding trackers and agencies: [Techleap](https://www.techleap.nl/) (NL), [startups.be](https://www.startups.be/) (BE), [Luxinnovation](https://www.luxinnovation.lu/) (LU), [aws Austria Wirtschaftsservice](https://www.aws.at/), [Innosuisse](https://www.innosuisse.admin.ch/), [RVO](https://www.rvo.nl/).
- VC portfolio: [Speedinvest](https://www.speedinvest.com/) (Vienna, invests across Europe including CEE).

### R4 Nordics & Baltics
- Media: [Breakit](https://www.breakit.se/), [Shifter](https://shifter.no/), [ArcticStartup](https://arcticstartup.com/), [Northstack](https://www.northstack.is/).
- Startup databases and agencies: [The Hub](https://www.thehub.io/) (Nordic startup jobs and companies), [Startup Estonia](https://www.startupestonia.ee/), [Startup Lithuania](https://www.startuplithuania.com/), [Startin.LV](https://startin.lv/), [Business Finland](https://www.businessfinland.fi/), [Vinnova](https://www.vinnova.se/), [Innovation Norway](https://www.innovationnorway.com/).

### R5 France & Southern Europe
- Media: [Maddyness](https://www.maddyness.com/), [FrenchWeb](https://www.frenchweb.fr/), [El Referente](https://www.elreferente.es/) (blocks bots at times), [ECO](https://eco.sapo.pt/), [StartupItalia](https://www.startupitalia.eu/), [Startupper](https://startupper.gr/).
- Funding trackers and agencies: [La French Tech](https://www.lafrenchtech.gouv.fr/en/), [Bpifrance](https://www.bpifrance.fr/), [Startup Portugal](https://www.startupportugal.com/), [Malta Enterprise](https://www.maltaenterprise.com/), [Invest Cyprus](https://www.investcyprus.org.cy/).
- Accelerator: [Wayra](https://www.wayra.com/) (Telefónica; Spain and Latin America).

### R6 CEE peers
- Media: [The Recursive](https://therecursive.com/) (CEE and SEE), [CzechCrunch](https://www.czechcrunch.cz/), [Startitup](https://www.startitup.sk/), [HWSW](https://www.hwsw.hu/), [Netokracija](https://www.netokracija.com/) (drops bot connections), [start-up.ro](https://start-up.ro/), [StartupCafe](https://www.startupcafe.ro/).
- Accelerators and agencies: [StartupYard](https://www.startupyard.com/) (Prague), [ABC accelerator](https://www.abc-accelerator.com/) (Ljubljana), [CzechInvest](https://www.czechinvest.org/en), [Speedinvest](https://www.speedinvest.com/).
- Why it matters twice: something already adapted here may enter Poland; something working here and absent in Poland is evidence for local adaptation (brief).

### R7 East Asia
- Media: [BRIDGE](https://thebridge.jp/) (Japan), [Platum](https://platum.kr/) and [VentureSquare](https://www.venturesquare.net/) (Korea), [數位時代 Business Next](https://www.bnext.com.tw/) (Taiwan), [Tech in Asia](https://www.techinasia.com/), [e27](https://e27.co/).
- Funding trackers: [INITIAL / Speeda](https://initial.inc/) (Japan startup database), [THE VC](https://www.thevc.kr/) (Korea).
- Programmes: [J-Startup](https://www.j-startup.go.jp/), [K-Startup](https://www.k-startup.go.kr/), [Startup SG](https://www.startupsg.gov.sg/), [HKSTP](https://www.hkstp.org/).

### R8 Oceania & Israel
- Media: [Startup Daily](https://startupdaily.net/), [SmartCompany](https://www.smartcompany.com.au/), [Idealog](https://www.idealog.co.nz/), [Geektime](https://www.geektime.com/), [CTech by Calcalist](https://www.calcalistech.com/).
- Funding trackers: [Cut Through Venture](https://www.cutthroughventure.com/) (Australian VC data), [IVC Data](https://www.ivc-online.com/) and [Startup Nation Central](https://www.startupnationcentral.org/) (Israel; its Finder database blocks bots).
- Accelerators and VCs: [Startmate](https://www.startmate.com/), [Blackbird](https://www.blackbird.vc/).

### R9 Gulf & Turkey
- Media: [Wamda](https://www.wamda.com/), [Zawya](https://www.zawya.com/), [Webrazzi](https://www.webrazzi.com/), [egirişim](https://www.egirisim.com/).
- Funding trackers: [MAGNiTT](https://www.magnitt.com/) (MENA and Turkey funding data; reports public), [Startups.watch](https://startups.watch/) (Turkey).
- Accelerators and hubs: [Hub71](https://www.hub71.com/) (Abu Dhabi), [Flat6Labs](https://www.flat6labs.com/), [QSTP](https://qstp.org.qa/) (Qatar), [Tamkeen](https://www.tamkeen.bh/) (Bahrain), [KFAS](https://www.kfas.org/) (Kuwait).

### R10 Latin America (OECD)
- Media: [Contxto](https://contxto.com/), [LatamList](https://latamlist.com/), [Expansión](https://www.expansion.mx/), [Diario Financiero](https://www.df.cl/).
- Funding trackers: [LAVCA research](https://www.lavca.org/research/) (Latin American VC data).
- Accelerators and agencies: [Start-Up Chile](https://www.startupchile.org/), [iNNpulsa](https://www.innpulsacolombia.com/) (Colombia), [ANII](https://www.anii.org.uy/) and [CUTI](https://www.cuti.org.uy/) (Uruguay), [PROCOMER](https://www.procomer.com/) (Costa Rica), [Wayra](https://www.wayra.com/).

## 4. Searches that work without these sources
- `site:<local media domain> <local term>` on a search engine, with the local terms from [countries.md](countries.md).
- Product pages and pricing: the product's own `/pricing` page; app-store page via the [iTunes Search API](https://itunes.apple.com/search?term=ai%20assistant&country=de&entity=software) (change `term` and `country`).
- Funding announcements: the company's press page or blog first; media second.

## 5. Sources added during research
<!-- task · URL · what it gives · access date · notes (blocks bots, interested source, etc.) -->
