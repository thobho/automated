# 020 — Phone agent for private clinics that books into Polish clinic calendars

**One-liner:** A Polish-speaking voice agent that answers a private clinic's or dental practice's phone when reception is busy or closed, books, moves and cancels visits directly in the clinic's calendar (mMedica, Medfile, KS-SOMED, ZnanyLekarz), fills freed slots from a waiting list by calling or texting patients (merged L104 no-show recovery), and answers "czy przyjmujecie na NFZ / ile się czeka" from the NFZ Terminy leczenia data.
**Field:** health-care | **Type:** SaaS (voice) | **B2B** · shortlist id L103 (merges L104)

**Western analogues:**
- **Assort Health** (US): specialty-specific voice AI for patient calls; **US$26M Series A (2025-04)** and **US$76M Series B led by Lightspeed (2025-09), US$102M total** ([Fierce Healthcare](https://www.fiercehealthcare.com/ai-and-machine-learning/assort-health-brings-total-funding-102m-four-months), accessed 2026-11-06). TechCrunch's sources put ARR at "a little more than US$3M" at a ~US$750M valuation in 2025-08 ([TechCrunch](https://techcrunch.com/2025/08/26/assort-health-nabs-50m-to-automate-patient-phone-calls-sources-say), accessed 2026-11-06).
- **Docplanner Noa Booking** (PL-founded, 13 countries): voice booking agent on Twilio, announced 2026-03-24; 24/7 phone booking, FAQs, SMS/WhatsApp confirmation, human fallback; doctors using it "recorded twice as many bookings" as with call centres; 1,300 doctors onboarded in three days; cancellations and referrals listed as future features; launch markets not named ([Twilio press release](https://www.twilio.com/en-us/press/releases/docplanner-expands-patient-access-with-voice-ai-agent-powered-by), fetched 2026-11-06).
- TH02 theme rows: Hyro (IL), Tucuvi (ES), Vocca (FR) (TH02 check; not re-verified).

**Spread:** TH02: US, IL, ES, FR, PL-founded Docplanner across Europe and LatAm (R1, R3, R5, R8, R10), 2023–2026.

**Does the Western leader already work in Poland?** Yes for the voice part. **ElevenLabs** sells "AI answering for hospitals and clinics" on Polish pages and documents a Reception product in Polish (70+ languages; Google Calendar, Calendly, Cal.com; no Polish clinic software listed) (TH02 check, 2026-11-03). **fonio** (AT) sells a Polish clinic receptionist at 399–479 PLN/month; **AInora** (LT) has a Polish clinic page; 30+ Polish voicebot vendors (EasyCall from 0.40 PLN/min, InteliWISE from 899 PLN/month) (TH02 check). **Docplanner** owns ZnanyLekarz and now has Noa Booking; whether it is live in Poland was not confirmed (searched 2026-11-06). Not tried hands-on (no test call made).

**Polish adaptation, i.e. the edge:**
- Clinic calendars: mMedica (Asseco), Medfile, KS-SOMED; no public calendar API was found for Medfile or mMedica (a catalogue claims Medfile has an "open API", unverified; Asseco documents only a mobile-app integration module) ([mMedica integration doc](https://mmedica.asseco.pl/assets/Dokumentacja/mM-Modul-Integracji-Aplikacji-Mobilnych.pdf), accessed 2026-11-06).
- NFZ Terminy leczenia data for queue answers (M22), e-skierowanie numbers (M24), the private vs. NFZ split in one clinic, Polish health vocabulary, AI disclosure at call start.
- These are real but narrow; the voice layer itself is commodity.

**Target customer in Poland:** private multi-doctor clinics and dental practices. GUS counted **24,225 przychodnie, 532 praktyki lekarskie and 2,508 praktyki stomatologiczne** with public financing at end-2024 (GUS "Ambulatoryjna opieka zdrowotna w 2024 r.", search excerpt via [stat.gov.pl](https://stat.gov.pl/obszary-tematyczne/zdrowie/zdrowie/ambulatoryjna-opieka-zdrowotna-w-2018-roku,13,3.html) series page; 2024 release not opened); purely private practices are not in that count (unverified). Buyer: clinic owner or manager. CEE: the same vendors (fonio, AInora, ElevenLabs) sell across CEE already.

**Demand driver:** DD3 queues (4.2–4.3 months to a specialist) and DD1 older patients who phone rather than book online (a third of 60–74-year-olds offline) ([demography.md](../../research/poland/demography.md) D15, D24); DD7 receptionist shortage (indirect).

**Polish competition:**
| Who | What | Price | Gap |
|---|---|---|---|
| ElevenLabs Reception / Agents | Polish voice receptionist, generic calendars | agent minutes ~US$0.08/min + LLM + telephony ([Macha guide](https://www.getmacha.com/blog/elevenlabs-agents-pricing-explained), secondary, accessed 2026-11-06) | no mMedica/Medfile |
| fonio (AT) | Polish clinic receptionist | 399–479 PLN/month | integrations unclear |
| AInora (LT), EasyCall, InteliWISE, Talknbot, SentiOne | Polish voicebots | 0.40 PLN/min; from 899 PLN/month; quotes | generic |
| Docplanner (ZnanyLekarz Phone, Noa Booking) | call handling and booking for ZnanyLekarz doctors | not published | owns the calendar of private doctors |
| Centralna e-Rejestracja voicebot (CeZ, ElevenLabs + SoftBlue) | state NFZ registration and reminders | free to patients | public specialists only |

**Evidence of Polish demand:** autocomplete "voicebot" → "voicebot medyczny", "voicebot cez", "voicebot cena" (TH02); ZnanyLekarz runs a press survey on patients' attitudes to AI ([ZnanyLekarz biuro prasowe](https://biuroprasowe.znanylekarz.pl/350654-raport-nastawienie-pacjentow-wobec-ai), not read in full). No clinic-owner forum evidence of "I want an AI receptionist" was found in this pass.

**MVP scope (≤6 weeks):**
1. Voice agent on a hosted platform (ElevenLabs or a Deepgram + TTS stack) with a Polish clinic script, AI disclosure, transfer to a human.
2. One calendar integration: Google Calendar / ZnanyLekarz-independent clinics first; mMedica or Medfile only after API access is confirmed.
3. Booking, rescheduling, cancellation; waiting-list call-back for freed slots.
4. NFZ Terminy lookup for "how long is the wait" questions.
5. Tests: scripted call simulations (text-level) with expected calendar actions; 50 recorded test calls scored by a rubric.

**Monetization:** 599 PLN/month per location incl. 1,000 minutes, 0.60 PLN per extra minute. **Unit economics:** agent ~US$0.08/min + LLM ~US$0.001/min + Polish telephony (estimate ~US$0.01–0.02/min) ≈ US$0.10/min ≈ 0.40 PLN/min. 1,000 minutes ≈ 400 PLN, so gross margin at 599 PLN is ~30% before support; a cheaper self-assembled stack might halve the voice cost (estimate). Margin fails the L6 ≥60% bar unless the clinic only routes overflow and after-hours calls. **Customer count:** 10k PLN MRR ≈ 17 locations at 599 PLN; tens of thousands of clinics is ample.

**Distribution, first 10 customers:** dental and aesthetic clinics in two cities by phone and visit; dental-practice Facebook groups; resellers of Medfile/KS-SOMED (not checked).

**Regulation:** AI Act: a booking agent is not Annex III high-risk (it does not triage or decide access to essential services) ([Annex III](https://artificialintelligenceact.eu/annex/3/)); Art. 50 disclosure that the caller speaks to AI. RODO: health data (art. 9), call recordings, processor agreement with the clinic, EU hosting of audio; medical-secrecy rules. Avoid any triage advice (that would edge toward a medical device).

**Opportunities (szanse):**
| # | Opportunity | Likelihood | Impact | What would make it true |
|---|---|---|---|---|
| O1 | Phone stays the main booking channel for older patients, so missed calls are lost revenue the clinic can see | H | M | pilot clinic logs ≥20% missed calls before go-live |
| O2 | Waiting-list refill of cancelled slots is a value metric clinics already track | M | M | ≥5 refilled slots a week per pilot location |
| O3 | Dental and aesthetic clinics on their own calendars are outside the ZnanyLekarz booking flow, a niche the platform ignores | M | M | ≥50% of called dental clinics book outside ZnanyLekarz |
| O4 | Voice minute prices keep falling, lifting margins during year one | M | M | a provider cuts per-minute price by ≥30% |

**Risks (ryzyka):**
| # | Risk | Likelihood | Impact | Early warning sign |
|---|---|---|---|---|
| R1 | Docplanner rolls Noa Booking out to ZnanyLekarz clinics in Poland, bundled with the calendar they already pay for | H | H | Polish Noa Booking page or ZnanyLekarz sales calls offering it |
| R2 | Supply is crowded: ElevenLabs, fonio, AInora and 30+ Polish voicebots already pitch clinics | H | M | prospects already have a voicebot quote |
| R3 | Voice minutes (~0.40 PLN/min) leave a thin margin at PLN prices | H | M | pilot usage >1,500 min per location |
| R4 | No API access to mMedica/Medfile/KS-SOMED calendars, so the agent cannot book directly | M | H | vendors refuse or quote partner fees |
| R5 | Live-call failures with elderly patients create complaints and on-call support | M | M | >5% of calls transferred because the agent failed |

O sum 6+4+4+4 = 18; R sum 9+6+6+6+4 = 31. R − O = 13 and R1 is H×H without mitigation → **down one band**, already at the `<5%` floor.

**Success signals:**
- Western analogue durable signals: replaces receptionist/call-centre hours (signal 1), daily problem with an owner (signal 2), calendar and EHR integrations (signal 8), Docplanner's "twice as many bookings" (company claim) ([Twilio](https://www.twilio.com/en-us/press/releases/docplanner-expands-patient-access-with-voice-ai-agent-powered-by)). No retention data. Durability score ~3 → **unproven**.
- Hype warnings: Assort's valuation is described as far ahead of its ~US$3M ARR ([TechCrunch](https://techcrunch.com/2025/08/26/assort-health-nabs-50m-to-automate-patient-phone-calls-sources-say)); many thin voice-agent wrappers in the theme.
- Polish adaptation can reproduce: replaced spend = part of a receptionist's salary and missed-visit revenue; first channel = direct visits to dental clinics; retention driver = calendar integration, if access is obtained.

**Graveyard:** none confirmed in Poland. TH02/TH26 themes have many vendors; the TH26 check records generic voice receptionists consolidating (not re-checked).

**Scores (1–5):** L1 4 · L2 3 · L3 2 · L4 3 · L5 3 · L6 2 · L7 2 · L8 3 · L9 1 | **Weighted:** 2.7 / 5 | **Chance band:** **<5%** (score < 2.8; O 18, R 31, unmitigated H×H). The voice layer is already sold in Polish by ElevenLabs, fonio and dozens of local vendors, and the one platform that owns private doctors' calendars (Docplanner) has shipped its own voice booking agent; the remaining edge, direct writes into Polish clinic software, depends on API access that is not public.
Changes vs. quick score: L3 3 → 2 (ElevenLabs/fonio in Polish), L4 4 → 3 (integrations unconfirmed, NFZ data is one narrow piece), L6 3 → 2 (voice minute cost), L9 2 → 1 (Docplanner Noa Booking, 2026-03); weighted 3.1 → 2.7. Close to collapse; kept because the dental-clinic niche outside ZnanyLekarz is testable; T24 may move it to rejected.md.

**Cheapest validation test (≤1 week, ≤200 PLN):** call 20 private dental clinics and ask (a) share of missed calls, (b) calendar software, (c) whether ZnanyLekarz handles bookings, (d) what they would pay; ask Medfile and Asseco for calendar API terms.

**Kill criteria:** no calendar vendor grants API access within a month; or >50% of clinics already book via ZnanyLekarz; or Noa Booking appears in Poland.

**Confidence:** medium (competition and Western traction sourced; Polish rollout of Noa Booking, API access and clinic counts for private-only practices not confirmed).

**Sources** (accessed 2026-11-06 unless noted):
1. https://www.fiercehealthcare.com/ai-and-machine-learning/assort-health-brings-total-funding-102m-four-months
2. https://techcrunch.com/2025/08/26/assort-health-nabs-50m-to-automate-patient-phone-calls-sources-say
3. https://www.twilio.com/en-us/press/releases/docplanner-expands-patient-access-with-voice-ai-agent-powered-by
4. https://mmedica.asseco.pl/assets/Dokumentacja/mM-Modul-Integracji-Aplikacji-Mobilnych.pdf
5. https://stat.gov.pl/obszary-tematyczne/zdrowie/zdrowie/ambulatoryjna-opieka-zdrowotna-w-2018-roku,13,3.html (series page; 2024 figures from search excerpt)
6. https://www.getmacha.com/blog/elevenlabs-agents-pricing-explained
7. https://biuroprasowe.znanylekarz.pl/350654-raport-nastawienie-pacjentow-wobec-ai
8. https://artificialintelligenceact.eu/annex/3/
9. https://ainora.lt/pl/blog/najlepsi-asystenci-telefoniczni-ai-dla-firm-2026 (accessed 2026-11-03)
10. https://www.fonio.ai/pl/ki-telefonassistenten-archived/przychodnie (accessed 2026-11-03)
11. https://elevenlabs.io/pl/agents/healthcare-answering-service (accessed 2026-11-03)
12. Internal: [TH02 check](../../poland-check/A/TH02-patient-call-scheduling-agents.md), [demography.md](../../research/poland/demography.md)

Coverage: 5 web searches and 1 fetch for this write-up (Docplanner voice agent, Assort traction, clinic counts, clinic-software APIs, voice pricing). Not found: Noa Booking status in Poland, public calendar APIs of mMedica/Medfile/KS-SOMED, number of private-only practices, Polish clinic demand evidence.
