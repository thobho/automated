# KSeF and accounting pain in Poland

Lens 6 findings from the official app's store reviews, the GOFIN accountants' forum, Wykop, GitHub and Wikipedia traffic. All sources accessed 2026-10-29. Reddit blocks the research tools (see README Coverage), so Polish evidence here comes from Wykop, forums, app stores and GitHub. IDs `L6-Fnn` are stable anchors. Each finding says whether it is **repeated pain** (many independent posters) or a **one-off**.

### L6-F01 — Official KSeF 2.0 app: 2.03/5 from 645 iOS ratings; 12 of 51 sampled reviews ask for push notifications of new purchase invoices
- **Evidence:** App Store listing (rating and count from the iTunes lookup API) https://apps.apple.com/pl/app/ksef-2-0/id6478391157 — average 2.03 from 645 ratings, publisher Izba Administracji Skarbowej we Wrocławiu, updated 2026-10-29. Google Play shows the same app (`pl.gov.mf.ksef`) at 2.9 from about 1,020 reviews (WebFetch of https://play.google.com/store/search?q=ksef&c=apps&hl=pl ).
- **Sample read:** 51 reviews from Apple's public RSS feed (2024-07 to 2026-04). Rating split 1★ 23, 2★ 6, 3★ 8, 4★ 3, 5★ 10. Keyword counts in the sample (my regex, ±): notifications 12, login problems 9, purchase-invoice lists 6, foreign currency 2.
- **Quotes:** "Dlaczego twórca aplikacji nie pomyślał o powiadomieniach o otrzymaniu faktury zakupowej?" (2★, 2026-04-09); "Dodajcie możliwość włączenia powiadomień o nowych fakturach" (1★, 2026-04-04); "Faktury nie można wystawiać w innej walucie jak PL !" (1★, 2026-03-31); "aplikacja pokazuje domyślnie tylko faktury wystawione w PLN" (2★, 2026-03-10).
- **Repeated or one-off:** repeated. Notifications, foreign-currency invoices, missing invoices in the list and login failures recur across months and users.
- **Counter-evidence:** a part of the 1★ reviews are pure venting ("Dziadostwo"), and the ministry may add push features; the app is free, so the pain does not prove willingness to pay.
- **Product category:** companion to KSeF (alerts, mailbox, foreign-currency view). Overlaps [L2-F12](../02-weak-competition/reviews-and-app-stores.md#l2-f12--official-ksef-mobile-app-ministry-of-finance-29-on-google-play-20-on-the-app-store).
- **Confidence:** medium (small sample, vendor-neutral source).

### L6-F02 — GOFIN KSeF forum: 22 new threads in 11 weeks on page 1, mostly "how do I handle this case" questions
- **Evidence:** forum section https://forum.gofin.pl/dzialy-forum/ksef (fetched). Page 1 lists 22 threads created between 2026-08-07 and 2026-10-22 (my count from the list), 0–13 comments each, newest thread numbered 1560545 (2026-10-28). Titles include "Korekta do korekty jak wystawić w Aplikacji Podatnika" (13 comments), "Jakie daty w programie" (10), "Faktura z numerem KSeF, której nie mam w KSeF" (8), "Jak wystawić fakturę przez Aplikację Podatnika w imieniu klienta" (3), "Zapomniałam wystawić faktury w ksef..." (2).
- **Reading:** the forum audience is bookkeepers and small firms, and the questions are about corrections, dates, foreign or NIP-less buyers and issuing on behalf of clients. These are knowledge gaps, not tooling gaps; the answers come from other readers within hours.
- **Repeated or one-off:** repeated (about 2 new threads per week in the KSeF section), low volume per thread.
- **Counter-evidence:** the activity is modest for a mandate that reached all VAT payers; many answers say "ask your program's support".
- **Product category:** Q&A/knowledge product, correction wizard, checklist for biura rachunkowe.
- **Confidence:** medium.

### L6-F03 — GOFIN: "my client rejected the KSeF invoice" — a missing buyer-side accept/reject step causes disputes
- **Evidence:** thread https://forum.gofin.pl/1555659/wystawilam-fv-w-ksef-klient-nie-zaplacil-napisal-mail-ze (2026-06-24; fetched, 5+ comments). Poster: invoice issued and declared for VAT, client did not pay and "rejected" it. Answers: KSeF has no accept/reject step for the buyer, only technical rejection of malformed XML; "Ustal o co chodzi, co nie pasuje, wystaw korektę."
- **Related:** Symfonia's blog says accountant liability for KSeF errors mostly stems from unclear rules with the client https://symfonia.pl/blog/rozwoj-firmy/biura-rachunkowe-rozwoj-firmy/ksiegowy-czy-przedsiebiorca-kto-odpowiada-za-bledy-w-ksef/ (search result, not fully read), and LEX (prawo.pl) recommends client approval of imported invoices before posting https://www.prawo.pl/podatki/ksef-a-biura-rachunkowe,1540703.html (search result).
- **Takeaway:** a client-side "approve / dispute / comment" workflow on top of imported KSeF invoices for bookkeeping offices, with an audit trail. One thread plus two vendor/legal-press pages: pain is plausible, volume unproven.
- **Repeated or one-off:** one-off thread, but a recurring theme in practitioner press.
- **Confidence:** low-medium.

### L6-F04 — GOFIN: PDF visualisation differs from the KSeF XML (amount, bank account, address)
- **Evidence:** thread https://forum.gofin.pl/1546989/archiwum/co-innego-w-ksef-i-na-pdf-ie-faktury (2026-02-18; fetched first comments) plus a search summary of the same thread: a buyer found a different bank account and building number on the supplier's KSeF invoice than on the emailed PDF, and the supplier would not correct it in KSeF. Related Wykop thread: "Godzinne spotkanie dotyczące poprawienia faktury w ksef zrobiło mi dzień" (about 4 months before Oct 2026, 3 upvotes) https://wykop.pl/wpis/86657889/godzinne-spotkanie-dotyczace-poprawienia-faktury-w
- **Takeaway:** reconciliation of purchase invoice XML against PDF/email/payment details, e.g. a "bank-account changed" fraud alert for accounts-payable. No payment evidence.
- **Repeated or one-off:** two independent threads on two sites.
- **Confidence:** low-medium.

### L6-F05 — Wykop #ksef: low-volume tag (43 followers), practical gripes and open scepticism that the feared chaos arrived
- **Evidence:** tag page https://wykop.pl/tag/ksef (fetched; 43 followers). Posts in the last ~4 months mostly link to bezprawnik.pl and pikip.pl articles (1–44 upvotes). Pain quotes: "fajnie by było, gdyby KSEF miał aplikację... powiadomienie, że jest nowa faktura" (9 replies, https://wykop.pl/wpis/87792659/fajnie-by-bylo-gdyby-ksef-mial-aplikacje-i-np-kupu); the answer is "korzystasz z aplikacji do księgowości... przy wykonanej prawidłowo integracji z reguły te powiadomienia są" (inFakt user). A promoter post lists a free local invoice app, KsefInvoice https://ksefinvoice.pl/ (1 upvote; same thread). A user asks "Działa wam wysyłka FV do KSEF? W mBanku od 1,5h wisi" https://wykop.pl/wpis/86941879/dziala-wam-wysylka-fv-do-ksef-w-mbanku-od-1-5h-wis
- **Counter-evidence:** a popular sceptic post "JAK TAM KSeF? Czy paraliż gospodarki już nastąpił?" (5 upvotes, https://wykop.pl/wpis/87270543/e-wykopowi-doktorzy-ekonomii-doradcy-podatkowi-pre) and a comment "jedyny problem z prawidłową obsługą FV w KSeF mają instytucje publiczne" (https://wykop.pl/wpis/87492813/z-mojego-doswiadczenia-jedyny-problem-z-prawidlowa) say the mass failure did not happen.
- **Repeated or one-off:** notification wish repeats (also L6-F01); the rest is isolated.
- **Confidence:** medium. Wykop is a general-audience site, not a bookkeeper channel.

### L6-F06 — GitHub CIRFMF/ksef-api: 824 issues, 120 open; integrators fight over tokens, duplicates and change-sync
- **Evidence:** repo https://github.com/CIRFMF/ksef-api (stars 230, open issues 120 per the GitHub API, 2026-10-29). Issue #565 "Bezsensowność rezygnacji z tokenów" has 73 comments (opened 2026-01-16): "biura księgowe wymagają od przedsiębiorców tego certyfikatu tylko po to, żeby móc w jego imieniu wysyłać i odbierać faktury" https://github.com/CIRFMF/ksef-api/issues/565 . #794 (ministry consultation on an event/webhook model for invoice changes) has 103 comments https://github.com/CIRFMF/ksef-api/issues/794 ; #786 "Awaria KSeF? masowe duplikaty" 72 comments (2026-04-17) https://github.com/CIRFMF/ksef-api/issues/786 . Tokens were later kept (Wykop link, 2026-09-09: https://wykop.pl/link/8010969/tokeny-w-ksef-pozostaja , announcement in a handbook, not law).
- **Reading:** software vendors and integrators raise the issues, not end users. The wish list shows where the official API leaves gaps for third-party tools: change notifications, delegated access for accounting offices, duplicate detection.
- **Repeated or one-off:** repeated, high engagement (three issues ≥70 comments).
- **Counter-evidence:** the ministry is responsive (token reversal, consultation), so gaps may close.
- **Product category:** delegated-access, polling/notification and dedup layers for KSeF; developer libraries (see [dev-and-api-pain.md](dev-and-api-pain.md)).
- **Confidence:** high on the activity, medium on what it means commercially.

### L6-F07 — Attention is decaying: pl.wikipedia "Krajowy System e-Faktur" monthly views peaked at 1,278 in Mar 2026 and fell to about 200 by Aug–Sep
- **Evidence:** Wikimedia pageviews API (user agent, all access) for pl.wikipedia article Krajowy_System_e-Faktur: Feb 553, Mar 1,278, Apr 643, May 356, Jun 216, Jul 166, Aug 199, Sep 200 (Oct partial). https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/pl.wikipedia/all-access/user/Krajowy_System_e-Faktur/monthly/20240101/20261001 (accessed 2026-10-29). Wikipedia is a weak proxy for commercial search interest. Google Trends returned HTTP 429 to scripted access, so no Trends numbers (README Gaps).
- **Takeaway (counter-evidence):** the panic peak around the 1 Feb / 1 Apr 2026 waves has passed. The next wave on 1 Jan 2027 (see [L5-F01](../05-why-now/poland-and-eu-invoicing-tax.md#l5-f01--ksef-is-mandatory-in-three-waves-1-feb-2026-1-apr-2026-1-jan-2027)) may lift it again, but pain tools sold now compete with free bundles and a calmer audience.
- **Confidence:** medium (data is exact, interpretation is a proxy).

### L6-F26 — Counter-evidence: free single-purpose KSeF notification apps already exist, with almost no users
- **Evidence:** App Store lookups (iTunes API, 2026-10-29): "KSeF Mobile – powiadomienia" (released 2026-10-01, 5.0 from 2 ratings, free) https://apps.apple.com/pl/app/ksef-mobile-powiadomienia/id6817448137 ; "Monitor KSeF" (released 2026-03-13, 5.0 from 3 ratings, free) https://apps.apple.com/pl/app/monitor-ksef/id6759834557 . Accounting apps already push the alert: Wykop user "przy wykonanej prawidłowo integracji z reguły te powiadomienia są" (inFakt user, see F05); inFakt 4.81/5 from 9,348 and Fakturownia 4.63/5 from 2,818 ratings.
- **Reading:** the loudest single complaint in F01 (no push for new purchase invoices) is being solved by free hobby apps and by the commercial invoicing apps. A paid "notification" product has no room; the pain pays only as part of an accounting-office workflow.
- **Confidence:** medium.
