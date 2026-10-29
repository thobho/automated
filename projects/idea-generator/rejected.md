# Rejected ideas

Every dropped idea with a one-line reason. Never drop an idea silently.
Format: `- <id or name> · <task that dropped it> · <reason>`
- Allegro market-price index built from scraped or shared-key offer data · T11 · Allegro REST API terms from 23 Sep 2025 forbid this use ([L9-F17](research/09-unit-economics/platform-risk.md))
- Pooled no-show deposits or BNPL held by the platform for salons/clinics · T11 · holding clients' money needs a KNF licence or registration ([L7-F09](research/07-founder-fit/licensing-and-regulation.md)); kept only the Stripe Connect variant (I121, I203)
- Open-banking cash-flow app reading bank accounts directly · T11 · account-information access is a registered payment service ([L7-F11](research/07-founder-fit/licensing-and-regulation.md)); kept the KSeF-based variant (I005)
- Personalised tax-advice chatbot for JDG · T11 · individual tax advice for a fee is a reserved activity ([L7-F14](research/07-founder-fit/licensing-and-regulation.md)); kept generic calculators (I021, I045, I116)
- Peppol access point for Polish or German SMEs · T11 · sign-up and yearly membership costs plus certification ([L7-F04](research/07-founder-fit/api-access.md)) exceed budget and profile
- Hardware GPS tracker for mileage logs (Vimcar-style) · T11 · hardware and inventory are out of profile; kept the software-only variant (I007)
- Kindergarten parent-communication app (Twigsee-style) · T11 · several Polish equivalents exist ([L1-F23](research/01-proven-abroad/more-markets.md)) and no wedge was found
- Fitness/yoga studio pass and booking app · T11 · Polish fitness-booking products exist (lens 1 headline, [README](research/01-proven-abroad/README.md)); no wedge
- Medical triage or symptom-checker features in clinic booking · T11 · would fall under medical-device rules ([L7-F13](research/07-founder-fit/licensing-and-regulation.md)); clinic ideas kept strictly administrative

### T12 merges (near-duplicates folded into the kept idea; the kept ID carries both in shortlist.csv)
- I024 Multi-client KSeF archive · T12 · merged into I010: same payer (biura rachunkowe) and same KSeF receive-side data; archive and year-end export become I010 features
- I129 Language-school admin · T12 · merged into I128: same admin job (timetable, attendance, parent invoices); language schools become one segment of I128
- I026 White-label whistleblower channel · T12 · merged into I025: a reseller channel for the same product, not a separate product
- I164 Whistleblower procedure + training pack · T12 · merged into I025 as its one-off entry product
- I163 NIS2 policy template pack · T12 · merged into I027 as its one-off entry product
- I175 Accessibility quick-check extension · T12 · merged into I029 as its free lead-gen front end
- I172 Company card on hover · T12 · merged into I061 as its free front end (same data, same API)
- I084 VAT white-list bulk check and monitoring · T12 · merged into I013: the same supplier bank-account check, I013 adds the KSeF XML/PDF comparison
- I171 VAT white-list check on hover · T12 · merged into I013 as its free extension front end
- I073 Model-agnostic extraction API · T12 · merged into I018: same per-document extraction API; model-agnostic regression set becomes I018's reliability promise
- I174 Gmail add-on "send to my accountant" · T12 · merged into I074 as its delivery channel
- I078 Voice note → quote for renovation crews · T12 · merged into I090 as its input mode (voice) for the same quote generator
- I071 Allegro API change digest · T12 · merged into I059 as its lead-gen content (longlist already called it lead-gen for I059)
- I176 GPSR field checker extension · T12 · merged into I052 as its extension front end
- I104 Subsidy application status tracker · T12 · merged into I101: same installers, same Czyste Powietrze applications
- I173 KSeF number copier for transfers · T12 · merged into I014: same 2027 KSeF-number-in-transfer trigger; the extension is a front end
- Not merged, noted: I072/I139 (voice receptionist vs job cards are different products for the same workshops; scored separately), I191 kept apart from I029 (different payer: public bodies)

### T12 drops (unrealistic or outside the profile)
- I185 School-message digest for parents · T12 · no legitimate access route to e-dziennik messages (would need parents' credentials and scraping); consumer payer; unrealistic
- I177 Reseller cross-poster for OLX/Vinted · T12 · the longlist itself rates ToS risk high; automating posting on both platforms without an API is the core of the product, so one platform can end it (L9=1) and the build depends on unofficial UI automation
- I037 e-Doręczenia mailbox watcher · T12 · lens 5 found the deadline already passed and creates no paid need ([L5-F08](research/05-why-now/poland-and-eu-invoicing-tax.md)); API access unverified; unrealistic as a paid product

### T12 below the shortlist cut (rounded weighted score < 2.4; scores per lens L1..L9 in brackets, weights in method/criteria.md)
- I089 Address and TERYT normalisation API · T12 · below shortlist cut, weighted 2.3 [2 2 3 3 1 1 4 2 3]; No pain found; public TERYT data limits price.
- I099 Buyer change requests (zmiany lokatorskie) portal for small developers · T12 · below shortlist cut, weighted 2.3 [1 3 3 1 1 1 4 3 3]; Unverified complaint; small developers are listable.
- I140 Photographer client galleries with BLIK print orders · T12 · below shortlist cut, weighted 2.3 [3 2 3 2 1 1 3 3 3]; Pixieset has no Polish equivalent found (L1-F03) but global gallery tools are crowded.
- I204 Sworn-translator repertory and invoicing · T12 · below shortlist cut, weighted 2.3 [1 3 3 1 1 1 4 3 3]; Duty details and demand unverified.
- I096 Apartment handover (odbiór mieszkania) defect report app · T12 · below shortlist cut, weighted 2.3 [2 3 3 1 1 1 4 3 2]; Narrow listable audience but no demand evidence.
- I202 Optician recall reminders · T12 · below shortlist cut, weighted 2.3 [2 3 3 1 1 1 4 3 2]; SMS-heavy and no demand evidence.
- I008 Official WhatsApp shared inbox for Polish SMBs · T12 · below shortlist cut, weighted 2.3 [3 2 3 2 3 2 2 2 2]; Z-API shows demand abroad (L1-F26) but Meta's pricing changes (L9-F21) and approval make it platform-bound with no Polish pain found.
- I199 Client intake and conflict check for small law firms · T12 · below shortlist cut, weighted 2.3 [2 2 3 1 1 1 4 3 3]; Law-firm suites likely cover intake (L3-F36).
- I208 Report workflow for property appraisers · T12 · below shortlist cut, weighted 2.3 [2 3 3 1 1 1 3 3 3]; No demand evidence.
- I030 AI Act art. 50 transparency kit · T12 · below shortlist cut, weighted 2.3 [2 3 2 1 4 1 4 2 2]; Art. 50 duties apply since 2 Aug 2026 (L7-F12) but nobody was found asking and it is a one-off kit.
- I184 Polish CV builder · T12 · below shortlist cut, weighted 2.3 [1 2 2 4 2 1 5 2 2]; Rezi proves CV builders earn (L4-F02) but Polish builders exist.
- I079 Messaging-app marketing automation for Polish SMBs (L-Step pattern) · T12 · below shortlist cut, weighted 2.3 [3 3 3 2 3 1 2 2 2]; L-Step shows the pattern on LINE (L1-F21) but WhatsApp pricing and approval are Meta's call (L9-F21) and no Polish demand was found.
- I083 New-company feed by PKD and region · T12 · below shortlist cut, weighted 2.3 [2 2 3 2 1 1 4 3 2]; PKE art. 398 limits using the feed for e-mail outreach (L8-F13).
- I075 AI reply drafts for Allegro buyer messages · T12 · below shortlist cut, weighted 2.3 [1 3 3 2 3 2 2 2 2]; Needs an Allegro API key that can be refused (L7-F01) and a ToS check.
- I189 OSP (volunteer fire brigade) admin · T12 · below shortlist cut, weighted 2.3 [2 3 2 1 1 1 4 3 3]; Listable but low budgets and no demand found.
- I191 Accessibility statement generator + monitor for public bodies · T12 · below shortlist cut, weighted 2.3 [1 3 2 1 2 1 4 3 3]; Public-body rules date from 2019; small direct purchases only.
- I040 Foreign-worker document expiry tracker · T12 · below shortlist cut, weighted 2.3 [2 2 3 1 2 1 4 2 3]; Demand is an unverified complaint; no source found.
- I054 Returns portal with InPost return labels · T12 · below shortlist cut, weighted 2.3 [2 2 3 2 1 1 4 2 3]; No demand evidence; Sellasist-style tools may cover returns (L3-F04).
- I097 QR tool and equipment check-out for crews · T12 · below shortlist cut, weighted 2.3 [2 2 3 2 1 1 4 2 3]; No demand evidence; generic asset trackers exist.
- I120 Route planning for small delivery rounds · T12 · below shortlist cut, weighted 2.3 [2 2 3 2 1 1 4 2 3]; No demand evidence; global route planners exist.
- I190 Fee collection for children's sports clubs · T12 · below shortlist cut, weighted 2.3 [2 2 3 2 1 1 3 3 3]; Spond-type team apps exist in Poland (L1-F24).
- I203 Tattoo studio deposits and consents · T12 · below shortlist cut, weighted 2.3 [2 3 3 2 1 1 3 2 3]; Stripe Connect effect unverified (L7-F10); no demand found.
- I137 "Leaving Booksy" importer and migration service · T12 · below shortlist cut, weighted 2.3 [1 3 2 1 2 3 4 2 1]; The Versum migration is a loud pocket (L6-F09) but revenue is one-off.
- I188 Association and club manager · T12 · below shortlist cut, weighted 2.2 [2 2 2 2 1 1 4 3 3]; campai and AssoConnect show the model (L1-F05, F20) but Polish equivalents exist and budgets are low.
- I127 Occupational-medicine referral exchange · T12 · below shortlist cut, weighted 2.2 [1 3 3 1 1 1 3 3 3]; Two-sided network with no demand evidence.
- I032 GDPR processor pack generator for small SaaS and accountants · T12 · below shortlist cut, weighted 2.2 [2 2 2 2 2 1 5 2 2]; Art. 28 duties are real (L7-F28) but no demand evidence and template sellers abound.
- I088 Grants and subsidy call alerts for SMEs · T12 · below shortlist cut, weighted 2.2 [2 2 2 1 3 1 4 3 2]; Consultants already track calls; no demand found.
- I095 Landlord kit for private landlords · T12 · below shortlist cut, weighted 2.2 [3 3 2 2 1 1 4 2 2]; Small landlords are a low-budget consumer-like payer; no demand found.
- I187 Paid AI chat in Polish for seniors · T12 · below shortlist cut, weighted 2.2 [2 3 2 3 4 1 3 1 2]; Hard-to-reach payer and consumer support load.
- I116 Per-diem and foreign-trip settlement for international drivers · T12 · below shortlist cut, weighted 2.2 [1 2 3 1 2 1 3 3 3]; Complex rules, existing transport accounting tools unchecked, no demand found.
- I017 Invoice-history migrator between Polish invoicing tools · T12 · below shortlist cut, weighted 2.2 [1 3 2 1 3 2 3 3 1]; Imports skip invoice history (L9-F15) but revenue is one-off per migration.
- I058 OSS threshold monitor for Polish sellers shipping to EU consumers · T12 · below shortlist cut, weighted 2.2 [2 3 2 1 1 1 5 2 2]; Unverified complaint; marketplaces and invoicing tools may already warn.
- I141 Handyman instant-quote widget · T12 · below shortlist cut, weighted 2.2 [2 3 2 1 1 1 5 2 2]; No demand evidence.
- I142 Repair ticket tracker for tailors, shoe and phone repair · T12 · below shortlist cut, weighted 2.2 [2 3 2 1 1 1 5 2 2]; No demand evidence.
- I134 Professional-exam question bank (doradca podatkowy, aplikacje prawnicze, biegły rewident) · T12 · below shortlist cut, weighted 2.2 [2 2 3 2 1 1 3 3 2]; Unverified; course vendors dominate.
- I126 Digital pre-visit forms for private clinics · T12 · below shortlist cut, weighted 2.1 [2 2 3 2 1 1 3 2 3]; Health data and the MDR boundary (L7-F13) raise risk; no demand found.
- I034 Data Act switching pack for small SaaS vendors · T12 · below shortlist cut, weighted 2.1 [1 3 2 1 3 1 4 2 2]; Data Act switching rules apply Jan 2027 but small-SaaS scope is unverified (L9-F16) and no demand was found.
- I056 Packaging (PPWR/BDO) data helper for small e-shops · T12 · below shortlist cut, weighted 2.1 [1 3 2 1 3 1 4 2 2]; PPWR evidence is weak (L5-F19) and no demand was found.
- I057 Deposit (kaucja) line items for online beverage sellers · T12 · below shortlist cut, weighted 2.1 [1 3 2 1 3 1 4 2 2]; Whether online sellers must charge the deposit is unverified (L5-F20); no demand found.
- I110 Plant-protection treatment log · T12 · below shortlist cut, weighted 2.1 [2 3 2 1 2 1 4 2 2]; Record duty and demand unverified.
- I132 Lesson reports for private music schools · T12 · below shortlist cut, weighted 2.1 [2 3 2 2 1 1 4 2 2]; No demand evidence.
- I148 Hourly equipment rental booking (kayaks, bikes, SUP) · T12 · below shortlist cut, weighted 2.1 [2 3 2 2 1 1 4 2 2]; Seasonal and no demand evidence.
- I149 Allergen and menu QR for restaurants · T12 · below shortlist cut, weighted 2.1 [2 2 2 1 2 1 5 2 2]; QR menu tools abound; legal duty unverified.
- I158 Brand-deal CRM for influencers · T12 · below shortlist cut, weighted 2.1 [2 3 2 2 1 1 4 2 2]; No demand evidence.
- I155 Local media monitoring for small businesses and gminy · T12 · below shortlist cut, weighted 2.1 [2 2 3 3 1 1 3 2 2]; Brand24 is Polish (L3-F23) and Facebook data access is limited.
- I156 Polish social post scheduler for local businesses · T12 · below shortlist cut, weighted 2.1 [1 1 3 4 1 1 4 2 2]; Postiz proves schedulers earn (L4-F01) but the category is crowded.
- I067 MCP servers for Polish public registers · T12 · below shortlist cut, weighted 2.1 [1 3 1 1 3 1 5 3 1]; Free official data and no payer; a lead-gen asset at best.
- I105 ETS2 fuel-cost calculator · T12 · below shortlist cut, weighted 2.1 [1 3 1 1 3 1 5 3 1]; A free calculator with no payer.
- I192 1.5% campaign toolkit for small OPP · T12 · below shortlist cut, weighted 2.1 [1 3 2 1 1 1 5 3 1]; Seasonal, low budget.
- I044 Umowa zlecenie / o dzieło flow for event and promo agencies · T12 · below shortlist cut, weighted 2.1 [1 3 3 1 1 1 3 2 3]; Unverified complaint; payroll-adjacent rules raise support load.
- I087 Financial-statement database from KRS filings · T12 · below shortlist cut, weighted 2.1 [2 2 3 3 1 1 2 2 3]; Bulk access to KRS filings is unverified and paid registries exist.
- I106 Heat-cost allocation for small landlords and wspólnoty · T12 · below shortlist cut, weighted 2.1 [1 3 3 1 1 1 3 2 3]; Allocation methods are regulated and meter-service firms own the job.
- I045 Business-trip (delegacja) and per-diem calculator · T12 · below shortlist cut, weighted 2.1 [1 2 2 1 1 1 5 3 2]; Easy calculator with SEO potential, but free calculators exist and no pain was found.
- I150 Rooming lists for group organisers and hotels · T12 · below shortlist cut, weighted 2.1 [1 3 2 1 1 1 5 2 2]; No demand evidence.
- I154 Link-in-bio with BLIK tips and invoices · T12 · below shortlist cut, weighted 2.1 [2 2 2 3 1 1 4 2 2]; Link-in-bio revenue proof is stale (L4-F14); crowded.
- I042 Phone check-in time records for construction crews · T12 · below shortlist cut, weighted 2.1 [2 2 3 1 1 1 3 2 3]; Kadromierz already does time tracking (L3-F03); no construction-specific pain found.
- I117 Proof-of-delivery photo app · T12 · below shortlist cut, weighted 2.1 [2 2 3 1 1 1 3 2 3]; No demand evidence; mobile work.
- I009 Survey + NPS add-on bundled into invoices · T12 · below shortlist cut, weighted 2.1 [2 3 2 1 1 1 4 2 2]; An add-on nobody was found asking for; low price and no revenue proof.
- I114 Machine-sharing booking between farmers · T12 · below shortlist cut, weighted 2.1 [2 3 2 1 1 1 4 2 2]; No demand evidence; low budgets.
- I135 School trip and camp organiser admin · T12 · below shortlist cut, weighted 2.1 [2 3 2 1 1 1 4 2 2]; No demand evidence.
- I159 Ad-label checker for sponsored posts · T12 · below shortlist cut, weighted 2.1 [1 3 2 1 2 1 4 2 2]; Guidance details unverified; no demand found.
- I194 Grant-report workspace for small NGOs · T12 · below shortlist cut, weighted 2.1 [2 3 2 1 1 1 4 2 2]; No demand evidence.
- I206 Florist event-order intake · T12 · below shortlist cut, weighted 2.1 [2 3 2 1 1 1 4 2 2]; No demand evidence.
- I178 B2B-vs-employment salary converter on job boards · T12 · below shortlist cut, weighted 2.0 [1 3 1 2 1 1 5 3 1]; No payer.
- I162 Contract template pack for Polish freelancers · T12 · below shortlist cut, weighted 2.0 [2 2 2 2 1 1 4 3 1]; One-off templates with no demand evidence.
- I043 Anonymous pulse surveys on whistleblower infrastructure · T12 · below shortlist cut, weighted 2.0 [2 2 2 2 1 1 4 2 2]; Engagement surveys are crowded and no demand evidence was found.
- I086 Law-change alerts per industry · T12 · below shortlist cut, weighted 2.0 [2 2 2 1 2 1 4 2 2]; Legal databases and law-firm newsletters cover it; no demand found.
- I113 Farm shop page with BLIK pre-orders · T12 · below shortlist cut, weighted 2.0 [2 2 2 2 1 1 4 2 2]; Shop platforms already do pre-orders; no demand found.
- I157 Paid newsletter with BLIK and VAT invoices · T12 · below shortlist cut, weighted 2.0 [2 2 2 2 1 1 4 2 2]; Unverified whether BLIK is missing; no demand found.
- I167 Allegro seller starter course · T12 · below shortlist cut, weighted 2.0 [1 2 2 2 1 2 3 3 1]; Weak Wykop signal (L6-F11); one-off.
- I193 Fundusz sołecki voting and consultation tool · T12 · below shortlist cut, weighted 2.0 [1 3 2 1 1 1 4 2 2]; No demand evidence; gmina purchasing is slow.
- I119 Multi-carrier label tool for offices that are not shops · T12 · below shortlist cut, weighted 2.0 [2 2 2 1 1 2 3 2 2]; Courier brokers likely cover it; weak evidence (L2-F16).
- I196 KGW bookkeeping · T12 · below shortlist cut, weighted 1.9 [1 3 1 1 1 1 4 3 2]; Very low budgets.
- I182 Receipt and warranty keeper · T12 · below shortlist cut, weighted 1.9 [2 2 1 2 3 1 3 2 2]; Consumers expect it free.
- I195 Volunteer shift scheduling · T12 · below shortlist cut, weighted 1.9 [2 2 1 1 1 1 5 2 2]; Free tools exist; no payer.
- I183 Photo calorie tracker for Polish dishes · T12 · below shortlist cut, weighted 1.9 [2 1 2 3 3 1 2 2 2]; Crowded, native mobile, stale proof (L4-F15).
- I107 Prosumer bill analyser · T12 · below shortlist cut, weighted 1.9 [2 3 1 1 2 1 3 3 1]; Households expect it free and data formats are unverified.
- I166 Canva template packs for Polish beauty salons · T12 · below shortlist cut, weighted 1.8 [1 2 1 2 1 1 4 3 1]; No demand evidence; low price.
- I169 Polish wedding planner and budget template · T12 · below shortlist cut, weighted 1.8 [1 1 1 2 1 1 5 3 1]; Consumer one-off; crowded.
- I179 Total-cost view for Allegro buyers · T12 · below shortlist cut, weighted 1.7 [1 3 1 1 1 1 3 3 1]; Consumers expect it free; no demand found.
- I186 Car cost and deadline tracker · T12 · below shortlist cut, weighted 1.6 [1 2 1 1 1 1 3 2 2]; Consumers expect it free.

## T13 research rejections
- I062 KSeF XML → PDF rendering API and Docker image · T13 · collapsed in write-up research (2026-10-29), est. weighted 2.7 [1 1 2 2 4 3 5 3 3] `<5%`; the job is already served free: the ministry's CIRFMF/ksef-pdf-generator (81 stars, MIT), ksef4dev/ksef-fop (Apache-2.0), LeMobi-Software/ksef-pdf-generator ("REST API i usługa Docker", MIT) and several others (GitHub API search, accessed 2026-10-29); the law does not require the seller to supply a PDF (podatki.biz); no paying buyer found, only developers asking the ministry for a better library (L6-F14). Replaced by I070 (next `write_up=n` idea with a free field slot, developer-tools-apis; I023 skipped because accounting already has 3 write-ups).
- I061 Polish company-data API (NIP/KRS/REGON/VIES → JSON) (with merged I172) · T13 · collapsed in write-up research (2026-10-29), est. weighted 2.3 [2 1 2 3 2 2 4 3 2] `<5%`; the exact wedge is taken: CompanyData sells a unified KRS+CEIDG+REGON REST API (about 6.3M records, credits from 0.02 EUR, 500-lookup trial, named KYC customers), Apify actors sell NIP/KRS lookups at 4–8 USD per 1,000, NIPRegon.pl offers a free MCP endpoint (100 calls/day), and the official sources are free; 10,000 PLN MRR would need roughly 500,000 lookups per month at those prices (estimate). Replaced by I059 (Typed Allegro SDK + MCP server; next `write_up=n` developer-tools-apis idea, skipping I068 which duplicates the send queue in write-up 003).

### T16 review (write-ups dropped after the critical review; files kept with a "rejected" note)
- I070 XRechnung/ZUGFeRD validator and generator API (write-up 002) · T16 · no wedge left: hosted validation with plain-language fix hints (Rechnungslotse), free-tier hosted generate/validate (normbill) and paid generation from 49 EUR/month (Factora) already exist next to free KoSIT/Mustang; German-only market, no Polish moat ([write-up](ideas/developer-tools-apis/002-xrechnung-zugferd-validator-api.md))
- I012 Delegated KSeF access and token/certificate manager (write-up 007) · T16 · merged into I010 (write-up 001) as its permissions screen: same payer and certificate, incumbents show per-client KSeF status as a by-product, need peaks only during onboarding, no standalone price ([write-up](ideas/accounting-invoicing-tax/007-delegated-ksef-access-and-token-manager.md))
- I050 WooCommerce → KSeF bridge (write-up 008) · T16 · own kill criterion met: WP Desk's free KSeF add-on shipped OSS, foreign-currency and foreign-buyer handling May–Oct 2026 (v2.4.0–2.5.4), its PRO invoicing plugin costs 229 PLN/year, B2Brouter sells KSeF for WooCommerce from 15 EUR/month, and 19 KSeF plugins are listed; no gap left for a 29–59 PLN/month bridge ([write-up](ideas/ecommerce-sellers/008-woocommerce-ksef-bridge.md))
- I059 Typed Allegro SDK + MCP server (write-up 009, with merged I071) · T16 · at least nine free Allegro MCP servers published Jun–Oct 2026 (some generated from the official OpenAPI spec), no paid demand or price anchor, hosted proxy exposed to Allegro API terms; recommended for rejection by T13 ([write-up](ideas/developer-tools-apis/009-typed-allegro-sdk-and-mcp.md))
- I128 Tutoring-centre and language-school manager (write-up 010, with merged I129) · T16 · at least eleven Polish-language tools already ship lecturer-pay settlement, fee reminders and parent payments (Vibeclass from 49 PLN/month, LingoDesk, ActiveNow claiming 2,500+ institutions, LangLion, Teach 'n Go, Optimate, Anolla, others); no gap, no trigger (L5 = 1), no pain heard ([write-up](ideas/education-exams/010-tutoring-centre-manager.md))
- I074 E-mail-to-accountant agent for JDG (write-up 012, with merged I174) · T16 · the claimed gap does not exist: inFakt has offered a per-client forwarding address (imię.nazwisko@infaktpliki.pl) and photo upload straight to the accountant since 2015, SaldeoSMART/wFirma/Fakturownia/Comarch bundle intake and OCR, and KSeF now delivers B2B purchase invoices automatically, leaving only receipts and foreign invoices ([write-up](ideas/ai-agents-automation/012-email-to-accountant-agent-for-jdg.md))
- I076 Bank-statement categoriser for offices (write-up 013) · T16 · no segment left: SaldeoSMART reads PDF statements, pulls transactions from integrated banks and AI-matches them to documents; a Polish any-bank converter has 50 free pages a month with categorisation rules; wFirma, Optima and Fakturownia import MT940/CSV from all large banks ([write-up](ideas/ai-agents-automation/013-bank-statement-categoriser-for-offices.md))
- I031 CRA vulnerability-reporting and SBOM tracker (write-up 016) · T16 · free OpenCRA (Apache-2.0 GitHub Action, Sep 2026) and Dependency-Track already do SBOM, KEV matching and evidence export; what is left is a 24h timer and form checklist for events most small vendors rarely have, which ENISA or the free tools can add; one promotional forum post as pain evidence ([write-up](ideas/legal-compliance/016-cra-vulnerability-reporting-and-sbom-tracker.md))
- I136 Flat-fee salon booking with no first-visit commission (write-up 018) · T16 · rejected per the write-up's own verdict: at least nine Polish commission-free booking tools (Estetify, BeSkiz, Rezobo, Saloner, Reservis, GdzieKiedy, meetergo, Calendesk, Fresha from 29 PLN), Booksy takes no commission without Boost, and salons that complain stay for the marketplace a newcomer cannot offer ([write-up](ideas/local-services-booking/018-flat-fee-salon-booking.md))
