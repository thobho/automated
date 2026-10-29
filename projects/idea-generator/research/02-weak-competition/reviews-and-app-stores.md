# Low ratings and complaints: invoicing, KSeF, booking, parcels, DACH (Trustpilot, app stores)

Lens 2 findings. All pages accessed 2026-10-29. Review portals do not verify reviews, and Trustpilot samples are small and skew negative; each entry says what was actually read. Quotes are short and verbatim (Polish quotes with an English gist).

## L2-F12 — Official KSeF mobile app (Ministry of Finance): 2.9 on Google Play, 2.0 on the App Store
- **Evidence:** Google Play listing for `pl.gov.mf.ksef` ("KSeF 2.0"): 2.9 stars, about 1,020 reviews (listing page read via search, https://play.google.com/store/apps/details?id=pl.gov.mf.ksef&hl=en_US). App Store: 2.0 of 5, 645 ratings, https://apps.apple.com/pl/app/ksef-2-0/id6478391157?see-all=reviews&platform=iphone.
- **Quotes (App Store):** "Nawet po zalogowaniu do profilu zaufanego nie da się przejść dalej." (2025-07-28); "Faktury nie można wystawiać w innej walucie jak PL !" (1 April); a reviewer asks for notifications about new invoices (4 April; year not shown on the page).
- **Assessment:** a free official tool with repeatedly named gaps: login, foreign-currency invoices, notifications. Commercial invoicing apps with KSeF (inFakt, Fakturownia, iFirma) are separate Play/App Store listings (not rated in this session). The opening is a thin KSeF companion for people who only need to receive/issue a few invoices, not a full accounting package. Risk: the ministry can fix its app; its ratings are not a durable moat for a third party.

## L2-F13 — iFirma: 2.8 on Trustpilot while inFakt sits at 4.8 (invoicing is split, not empty)
- **Evidence:** https://www.trustpilot.com/review/ifirma.pl — 2.8, 125 reviews, 42% one- or two-star; quotes: "Zero helpfulness"; "Very quick to demand payment, very slow to repay deposits" (2025-10-17). https://www.trustpilot.com/review/infakt.pl — 4.8, 2,374 reviews; its low reviews cite support and accountant mistakes ("Customer support is a disaster", 2026-06-17).
- **Assessment:** one well-rated and heavily reviewed competitor (inFakt) and one weakly rated one (iFirma). The invoicing/accounting category is not a gap for a newcomer; use it only as proof that support and refund handling are the sore spots. Trustpilot's English sample may not represent Polish users.

## L2-F14 — Fakturownia: WooCommerce connection failures cited (very small sample)
- **Evidence:** https://www.trustpilot.com/review/fakturownia.pl — 3.3 from only 3 reviews, unclaimed profile. Quote (2025-05-01, 2-star): "Bardzo często blokowane jest połączenie z Woocommerce." (reviewer says outages over two years caused cancelled orders). Another (2026-03-16): "Tragiczna obsługa Klienta".
- **Assessment:** n=3, too small to rely on. It matches the thin WooCommerce–Allegro plugin market in L2-F04, so a reliable shop-to-invoice bridge for WooCommerce could be a niche, but it is a hypothesis only.

## L2-F15 — Booksy: 2.9 on Trustpilot (16,585 reviews), billing and cancellation complaints
- **Evidence:** https://www.trustpilot.com/review/booksy.com — 2.9, 16,585 reviews (262 in the last 12 months). Quotes: "Booksy charged me anyway." (2026-10-14); "They want piece of everything even tips." (2026-10-06); "awful customer service but quick to take your monthly fee" (2026-10-12). Reviews are mostly English-language, so mixed markets; Polish salons are not separable from this page.
- **Pricing context:** see L2-F05 in [allegro-and-ecommerce-tools.md](allegro-and-ecommerce-tools.md#l2-f05--booksy-145-złmonth-plus-45-first-visit-commission-a-recurring-salon-pain).
- **Assessment:** real, recurring complaints about fees and cancelling, from a funded incumbent. Challengers such as Versum have 0 Trustpilot reviews (https://www.trustpilot.com/review/versum.com), so no independent rating signal for them was found.

## L2-F16 — InPost: 4.2 overall, but business shippers complain about claims and support
- **Evidence:** https://www.trustpilot.com/review/inpost.pl — 4.2, 29,400 reviews, 18% one-star. Business sender (2026-07-30): they "refuse to reimburse it" (5 of 11 parcels damaged or lost). Another (2026-10-09): "It is almost impossible to get in touch with a live agent." InPost replied to 97% of negative reviews with templated messages (page).
- **Assessment:** the courier itself is well liked; the gap is tooling for sellers to track claims and compensation across carriers. Existing seller platforms bundle labels (see Apilo/Base), but a dedicated claim-handling layer was **not** found or searched for beyond this page (gap).

## L2-F17 — Vimcar (Germany): 4.0 on Trustpilot, 23% low ratings, support and contract complaints
- **Evidence:** https://www.trustpilot.com/review/www.vimcar.de — 4.0, 1,009 reviews, 23% one- or two-star. Quotes: "Zero customer service from VIMCAR." (2024-01-24); "When it comes to the contractual side, it's a disaster." (2025-05-20); "product is extremely unreliable, effectively useless." (2026-02-13; the English reviews seem to come from UK users, the DACH core market is not isolated).
- **Link to lens 1:** Vimcar is the foreign analogue in [L1-F04](../01-proven-abroad/dach-niche-software.md#l1-f04--vimcar-germany-automatic-digital-fahrtenbuch-and-fleet-logbook). Its contract and hardware lock-in are the complaints; a software-only log would avoid those.
- **Counter-evidence for Poland:** Google Play search "ewidencja przebiegu pojazdu" (https://play.google.com/store/search?q=ewidencja%20przebiegu%20pojazdu&c=apps&hl=pl) lists "Kilometrówka Automatyczna" (motolog.app) at 4.8 and "MyCarTracks: Kilometrówka" at 4.0, so Polish software-only logs already exist (installs not shown).

## L2-F18 — Polish Google Play search: low-rated apps in scheduling and clinic booking
- **Evidence (listing pages, ratings only, no review text read):** "Grafik Pracy" (GrafikiOnline.pl) 3.0 vs "Grafik pracy i czas pracy" (Trasco studio) 4.7: https://play.google.com/store/search?q=grafik%20pracy%20pracownik%C3%B3w&c=apps&hl=pl. "Wizyta Lekarska" (KAMSOFT S.A.) 2.7 vs DobryGabinet (Swifter Software) 4.2: https://play.google.com/store/search?q=rezerwacje%20wizyt%20gabinet&c=apps&hl=pl. The page truncates results, so more apps exist.
- **Assessment:** the KAMSOFT patient-side app is low-rated, but KAMSOFT builds reimbursement/clinical software, which is outside the "no licence" boundary; what matters is that a 4.2 competitor exists. Weak evidence; no ratings counts.

## L2-F19 — WISO MeinVerein Web (Germany): 3.3 on trusted.de, complaints about mail delivery (not verified by fetch)
- **Evidence:** a web-search summary of https://trusted.de/wiso-meinverein-web-bewertung reported 3.3/5 and a 2026-03 review saying e-mails reach only part of the members since mid-2025 and that receipt scanning in the app is unreliable. **The page itself returned HTTP 403 to fetch, so these details are unverified.** ClubDesk (https://trusted.de/clubdesk-bewertung) was reported at 3.9 from 17 reviews, same caveat. easyVerein has one Trustpilot review (1 star, "Der Support war kompliziert", 2026-06-18, https://www.trustpilot.com/review/easyverein.com).
- **Assessment:** German association software is crowded (MeinVerein, ClubDesk, easyVerein, campai, SEWOBE). Not a Polish gap; relevant only as a hint for associations (stowarzyszenia), see [L1-F05](../01-proven-abroad/dach-niche-software.md#l1-f05--campai--chapster-germany-club-and-association-management).
