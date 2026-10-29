# Demand signals: search suggestions and attention curves

Google Trends and keyword-volume tools could not be used (Trends returned HTTP 429 to scripted access; paid keyword tools not available). Two free, scriptable proxies were used instead, both **qualitative**: Google autocomplete suggestions (what people type after a prefix; order reflects popularity but gives no volumes) and Wikimedia monthly pageviews (exact, but only for encyclopedic interest). All sources accessed 2026-10-29. IDs `L6-Fnn` are stable anchors.

### L6-F23 — Polish autocomplete: KSeF queries centre on "nie działa", corrections, notifications and bookkeeper permissions
- **Evidence:** `suggestqueries.google.com` (hl=pl, gl=pl), 2026-10-29, the first suggestions for each prefix:
  - "ksef program dla…": mikroprzedsiębiorców, JDG, rolników, małych firm.
  - "ksef nie działa…": dzisiaj, logowanie, profil zaufany, "forum".
  - "ksef korekta…": korekta faktury, danych nabywcy, do zera, daty sprzedaży, numeru faktury.
  - "ksef biuro rachunkowe…": uprawnienia, "jakie uprawnienia", certyfikat, plus vendor names (Optima, Symfonia, wFirma, Insert).
  - "ksef powiadomienia o fakturach": "czy ksef wysyła powiadomienia o fakturach" (matches [L6-F01](ksef-and-accounting-pain-pl.md)).
  - "program do kosztorysów…": budowlanych, elektrycznych, za darmo, Norma, Zuzia (matches [L6-F12](ecommerce-and-local-services-pl.md)).
  - "program dla salonu…": beauty, fryzjerskiego, kosmetycznego.
  - "allegro sprzedawca program": no suggestions returned.
- **Reading:** corroborates the forum themes (corrections, permissions for accounting offices, notifications), and shows an agriculture angle ("ksef program dla rolników") not seen in earlier lenses. Autocomplete is not a volume measure; the suggestions are not independent of each other.
- **Counter-evidence:** "za darmo/darmowy" appears next to kosztorysy.
- **Confidence:** medium for themes, none for sizes.

### L6-F24 — German autocomplete leans "kostenlos", "ohne Abo", "einmalig kaufen": a low-price-expectation signal for E-Rechnung tools
- **Evidence:** hl=de, gl=de: "e-rechnung software…" → kostenlos, kleinunternehmer kostenlos, datev, testsieger, **einmalig kaufen**, **ohne abo**, vergleich; "e-rechnung empfangen…" → kostenlos, kleinunternehmer, pflicht, datev; "e-rechnung kostenlos…" → erstellen, empfangen, prüfen, lesen; "xrechnung erstellen…" → kostenlos, aus pdf, open source, freeware; "handwerker software…" → kostenlos, vergleich, SHK, Elektro, **e rechnung**.
- **Reading:** German micro-business searchers expect free or one-off pricing for E-Rechnung basics. A paid product needs to sit above "convert/validate" (workflow, archiving, DATEV export) or use one-time licences. This is a demand signal **against** pure-validator ideas (see also [L6-F16](dev-and-api-pain.md) and [L3 pricing anchors](../03-monetization/README.md)).
- **Confidence:** medium (consistent across 5 prefixes, but a single tool).

### L6-F25 — Attention curves: German E-Rechnung topics are rising again toward the 2027 issuing deadline; Poland's KSeF peaked in March 2026
- **Evidence:** Wikimedia pageviews API (user traffic, monthly). de.wikipedia ZUGFeRD: Jan 2025 26,769; Sep 2025 4,726; Jan 2026 4,490; Jun 2026 4,702; Sep 2026 7,397. de.wikipedia XRechnung: Jan 2025 9,055; Sep 2025 1,829; Sep 2026 2,940. de.wikipedia Elektronische Rechnung: Jan 2025 6,490; Sep 2025 1,302; Sep 2026 1,278 (flat). pl.wikipedia KSeF article: Mar 2026 1,278, Sep 2026 200 ([L6-F07](ksef-and-accounting-pain-pl.md)). es.wikipedia Verifactu: Dec 2025 390, Sep 2026 170. pl.wikipedia Allegro: Jan 2025 794, Sep 2026 353 (no trend). Query URL pattern: https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/de.wikipedia/all-access/user/ZUGFeRD/monthly/20250101/20261001
- **Reading:** attention follows deadlines. German interest fell after 1 Jan 2025 and has been climbing since mid-2026 as the 1 Jan 2027 issuing duty for larger firms nears (see [L5-F04](../05-why-now/poland-and-eu-invoicing-tax.md#l5-f04--germany-e-rechnung-receiving-since-1-jan-2025-issuing-from-1-jan-2027-large-and-1-jan-2028-all)); a product aimed at the 2027–2028 wave would launch into rising, not peak, interest. Poland's KSeF curve is already past peak until the 1 Jan 2027 wave.
- **Confidence:** medium (Wikipedia is an indirect measure; dates of statutory deadlines come from lens 5).
