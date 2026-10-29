# Developer tools and Polish APIs

Lens 2 findings. All data from the GitHub search API (https://api.github.com/search/repositories), queried 2026-10-29; star counts and push dates are as returned that day. "Stale" = no push for more than 12 months before 2026-10-29. Library counts are search hits, not a census (name-matching only; forks and unrelated repos may be included). Stars are a weak proxy for demand.

## L2-F07 — Allegro REST API clients: few libraries, most unmaintained
- **Evidence:** https://api.github.com/search/repositories?q=allegro+api+client&sort=stars — 24 hits in total. Top results: `chawel/python-allegro` 27 stars, last push 2023-12-07; `ircykk/allegro-api` (PHP) 11 stars, 2024-12-21; `AshmaDev/node-allegro-client` (TypeScript) 4 stars, last push 2022-10-29; `wtx-labs/allegro-rest-api-client-java` 2 stars, 2025-06-23. No Allegro client hit with more than 27 stars.
- **Assessment:** there is no widely used, maintained Node/TS or Python SDK. Official API docs exist (https://developer.allegro.pl/) but were **not** read in this session, so whether an official SDK exists is unverified.
- **Caveat:** sellers mostly buy hosted integrators (see L2-F01..F03) instead of coding against the API, so the paying audience for an SDK is mainly agencies and in-house devs.

## L2-F08 — InPost ShipX API: SDKs are PHP-centric and mostly stale
- **Evidence:** https://api.github.com/search/repositories?q=inpost+api&sort=stars — 55 hits. Top: `imper86/php-inpost-api` 14 stars (last push 2021-11-23), `patryk-sawicki/inpost-laravel` 10 stars (2026-10-08), `michalbiarda/shipx-php-sdk` marked abandoned (2022-02-21). No TypeScript or Python SDK in the top 12; the TS items are an API emulator and a demo.
- **Assessment:** a typed Node/Python client and a webhook/tracking layer for InPost looks unserved in open source. The commercial alternatives (Furgonetka, BaseLinker shipping) bundle it, so the opening is for developers, not for sellers.

## L2-F09 — CEIDG and KRS company-data API clients: small, old, some are scrapers
- **Evidence:** https://api.github.com/search/repositories?q=ceidg+api — 22 hits; best has 10 stars (`sigrundev/ceidg-api`, PHP, last push 2022-02-08). The only recently active hit is `ContentWriterco/Compabase-API` (2 stars, pushed 2026-10-27), an OpenAPI spec for KRS/CEIDG/RDF data, which suggests at least one commercial wrapper exists (not verified).
- **Related:** GUS REGON (BIR1) is better covered: `johnzuk/GusApi` PHP 138 stars (pushed 2026-08-03), `pawel-id/bir1` TypeScript 31 stars (2026-04-12), plus an MCP server (`SmartMobileHouse/regon-mcp`, 1 star). Source: https://api.github.com/search/repositories?q=regon+gus+api
- **Assessment:** "Polish company lookup by NIP in one API with caching and a clean JSON schema" is a plausible API product, but the official feeds (CEIDG, KRS, REGON) are free, so the sellable value is convenience and uptime. Whether existing paid aggregators exist was **not** checked (gap).

## L2-F10 — KSeF libraries: already crowded, no gap in the basic client (counter-finding)
- **Evidence:** https://api.github.com/search/repositories?q=ksef — 709 hits. Official-looking repos from the Ministry-linked org `CIRFMF` (`ksef-client-csharp` 115 stars, `ksef-client-java` 49 stars, `ksef-pdf-generator` 81 stars; pushed 2026-09/10). Community: PHP (92 stars), Python (82 and 29 stars), Go (33), TypeScript (`Flopsstuff/ksef-client-ts` 18, `CodeFormers-it/ksefnik` 11 with an MCP server), at least two MCP servers, an invoice validator (`ksefuj/ksefuj`). TypeScript search: 94 hits, https://api.github.com/search/repositories?q=ksef+language:typescript.
- **Assessment:** a generic KSeF client is not a gap; effort has gone in since the 2026 rollout. What remains open source and thin is the layer on top (reconciliation, accounting-firm workflow), see the ~9-star "accounting AI agent" repos in the same results. Do not count KSeF-client libraries as weak competition.

## L2-F11 — Przelewy24 SDKs: PHP is fine, Node/TypeScript is thin and 2+ years stale
- **Evidence:** https://api.github.com/search/repositories?q=przelewy24 — 146 hits. PHP: `mnastalski/przelewy24-php` 53 stars (pushed 2026-05-04), `devpark/laravel-przelewy24` 39 stars (2023-10-23). Node: `ingameltd/node-przelewy24` 23 stars, last push 2023-12-11; a Medusa.js 2.0 provider (`gmi-software/przelewy24-medusa`, 13 stars) was pushed 2026-10-29.
- **Assessment:** the JavaScript/TypeScript side is fragmented. Weak evidence of pain: no issues or user quotes were read.
