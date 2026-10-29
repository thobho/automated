# Germany, Czechia and other markets

Lens 6 findings outside Poland. Reddit (r/de, r/selbststaendig), gutefrage, finanzfrage, Trustpilot, Capterra and Indie Hackers all returned HTTP 403 or were blocked for the tools (README Coverage), so the German and Czech evidence comes from App Store reviews, search-result summaries of vendor and press pages (weak), and Wikipedia traffic. All sources accessed 2026-10-29. IDs `L6-Fnn` are stable anchors.

### L6-F19 — Germany: sevDesk's iOS app: 292 of 350 sampled reviews are 1–2★; missing Abschlagsrechnung, Lieferschein and offer drafts, login failures, subscription traps
- **Evidence:** App Store listing https://apps.apple.com/de/app/id731738076 — 4.39/5 from 8,020 ratings (iTunes lookup). The 350 most recent German-store reviews (RSS feed, 2023-05-15 to 2026-10-23): 1★ 261, 2★ 31, 3★ 20, 4★ 7, 5★ 31. My regex counts: "Angebot" 46, login/Anmeldung 26, Abo/Kündigung 40, Lieferschein 6.
- **Quotes (DE, short):** "Software erlaubt Abschlagsrechnungen an ausländische Kunden zu erstellen – unterstützt die Funktion aber nicht" (1★, 2026-05-18; wrong VAT pre-return); "Lieferscheine können nicht mehr über die App erstellt werden" (1★, 2026-07-03, paraphrased from a longer review); "Angebotsentwürfe nicht verfügbar" (1★, 2026-07-21); "Abo Falle Vorsicht" (1★, 2026-08-07, says a 14-day notice is needed to avoid auto-renewal).
- **Workarounds:** users fall back to the web version or other tools; one reviewer says accounting costs rose by 440 euros for 2025.
- **Repeated or one-off:** repeated, but the sample is recency-weighted and the full-store rating is 4.39, so the app is probably worse than average in the last 6 months rather than disliked overall. Mixed with the search-result summary (selbststaendigkeit.de, Capterra 3.6/5 from 39 reviews, OMR 4.3/5 from 277, both unverified secondary figures): https://selbststaendigkeit.de/buchhaltung-fuer-gruender/sevdesk-erfahrungen .
- **Product category:** mobile-first quote → deposit invoice (Abschlag) → delivery note flow for tradespeople; overlaps lens 1/2 trades seeds.
- **Confidence:** medium.

### L6-F20 — Germany: a "reader" for received E-Rechnungen is the named small-business gap (vendor-written sources, weak)
- **Evidence (search-result summaries; pages not fetched in full):** since 1 Jan 2025 all German businesses must be able to receive e-invoices, including Kleinunternehmer; guides say an email address is not enough and a tool that can read XRechnung is needed, with ZUGFeRD named as the format readable as a PDF https://selbststaendigkeit.de/buchhaltung-fuer-gruender/e-rechnung-kleinunternehmer/ , https://www.fuer-gruender.de/wissen/unternehmen-fuehren/buchhaltung/rechnung/e-rechnungspflicht-kleinunternehmer/ , https://www.cleartax.com/de/e-rechnungpflicht-fur-kleinunternehmer . Sources disagree on when small issuers must send e-invoices (2027 vs about 2028), consistent with [L5-F04](../05-why-now/poland-and-eu-invoicing-tax.md#l5-f04--germany-e-rechnung-receiving-since-1-jan-2025-issuing-from-1-jan-2027-large-and-1-jan-2028-all).
- **Reading:** vendor SEO, not complaints by buyers. The best demand signal is in [demand-signals.md](demand-signals.md): Google suggestions like "e-rechnung kostenlos empfangen" and "ohne abo", plus Wikipedia traffic rising again (L6-F25).
- **Counter-evidence:** mainstream bookkeeping vendors (sevDesk, Lexware, DATEV) already include the feature, and 8 small tools failed to get HN traction (L6-F16).
- **Repeated or one-off:** pattern across many vendor pages, no direct customer voice.
- **Confidence:** low.

### L6-F21 — Czechia: the government eDoklady app is rated 1★ in 306 of 450 sampled reviews; iDoklad's iOS app gets 1★ for slowness and a subscription surprise
- **Evidence:** eDoklady https://apps.apple.com/cz/app/id6470912982 — 2.65/5 from 1,845 ratings; sample 450 reviews (RSS, 2024-01-21 to 2026-10-12): 1★ 306, 2★ 34, 3★ 32, 4★ 17, 5★ 61. Quotes: "Zas a opět nefunguje přihlašování" (1★, 2026-10-09); "U voleb 9.10.2026 nefunguje" (1★, 2026-10-09). iDoklad (invoicing, Czech market leader by ratings) https://apps.apple.com/cz/app/id1407259199 — 4.75/5 from 3,262 ratings; sample 109 reviews (2019–2026): 1★ 49, 2★ 13, 5★ 28; quotes: "Idoklad je extrémně pomalý" (2★, 2026-06-30); "po mně chtěla abych si ji přeplatil na měsíc za 500kč" (1★, 2026-08-26, user report).
- **Reading:** an e-government app (like the KSeF app in [L6-F01](ksef-and-accounting-pain-pl.md)) gets mass 1★ ratings when login fails, so "official app is bad" is a cross-country pattern, not a Polish quirk. iDoklad shows the same mobile gap as sevDesk (F19): web strong, iOS weak.
- **Counter-evidence:** eDoklady is a citizen ID app and not a business tool; iDoklad's overall rating is high.
- **Confidence:** medium for the pattern, low for any product implication.

### L6-F22 — France and Spain: e-invoicing deadlines drive search interest but no complaint data was reachable
- **Evidence:** Google suggestions (autocomplete, 2026-10-29): "facturation électronique 2026 auto-entrepreneur / plateforme agréée / report / ou 2027" and "verifactu cuando entra en vigor / es obligatorio / gratis / 2027 / autónomos"; Wikipedia es "Verifactu" views peaked at 390 in Dec 2025 and fell to 62–91 in spring 2026, up to 170 in Sep 2026 (Wikimedia pageviews API). Details in [demand-signals.md](demand-signals.md).
- **Reading:** both markets show "when is it mandatory / is there a free option" questions, which hints at low willingness to pay; there is no direct complaint text here. Not a finding of pain, a pointer for the gap pass (README Gaps).
- **Confidence:** low.
