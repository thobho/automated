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
