# TH02 — Patient call and scheduling agents (Poland check)

Theme: [THEMES.md#th02](../../themes/THEMES.md#th02) · rank 7, batch A · sources accessed **2026-11-03** · method: [README](README.md#method). Overlaps [TH26 AI receptionist](TH26-ai-receptionist-smes.md) (same vendors).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| SoftBlue + ElevenLabs voicebot for **Centralna e-Rejestracja** (Centrum e-Zdrowia) | State voicebot for central NFZ registration; will call NFZ patients to remind and reschedule | public contract (value not found) | national | [ITwiz](https://itwiz.pl/voicebot-od-elevenlabs-usprawni-centralna-e-rejestracje-i-zadzwoni-do-pacjentow-nfz/); [Bank.pl](https://bank.pl/?p=549049) |
| EasyCall (Bydgoszcz), InteliWISE, SentiOne, Talknbot, Maikon and others | Polish voicebot vendors also pitching clinics | EasyCall from 0.40 PLN/min + setup; InteliWISE from 899 PLN/month net (1,000 min); others on request | not stated | vendor comparison by AInora (a competitor, 2026-10-11): [ainora.lt](https://ainora.lt/pl/blog/najlepsi-asystenci-telefoniczni-ai-dla-firm-2026) |
| Talkie.ai (Warsaw/US) | Voice AI for patient calls | — | sells mainly in the US | ai-landscape S27 |
| AInora (LT), fonio (AT) | Polish-language clinic/dental receptionist pages | AInora quote-based; fonio from 399–479 PLN/month | not stated | [AInora clinics](https://ainora.lt/pl/recepcjonista-ai-przychodnie); [fonio PL clinics](https://www.fonio.ai/pl/ki-telefonassistenten-archived/przychodnie) |

## 2. Does the Western leader already serve Poland?
- **ElevenLabs** (Polish-founded, global): Polish pages for "AI answering for hospitals and clinics" and a Polish-documented Reception.ai product (70+ languages, auto-detect, Google Calendar/Calendly/Cal.com; Booksy and ZnanyLekarz not listed) ([elevenlabs.io/pl healthcare](https://elevenlabs.io/pl/agents/healthcare-answering-service); [Reception docs PL](https://elevenlabs.io/docs/pl/reception-ai)). **Serves PL.**
- **Tucuvi** (ES), **Vocca** (FR), **Hyro** (IL): no Polish presence found (not searched individually in Polish beyond one query).
- Could not check: integrations with Polish clinic software (mMedica, Medfile, KS-SOMED) for any vendor; Polish number provisioning.

## 3. Polish demand signals
- Autocomplete: "automatyczna rejestracja pacjentów" → none; "voicebot" → "voicebot medyczny", "voicebot cez" (= Centrum e-Zdrowia), "voicebot cena". The public e-Rejestracja voicebot is what people search for.
- 30+ vendors publish Polish voicebot offers (AInora list above): supply side is crowded.

## 4. What adaptation needs
M49 ZnanyLekarz calendars (owns booking for private doctors), M22 NFZ waiting-time API (for "when is the earliest slot" answers), M24 P1 e-skierowanie numbers (patients quote them), Polish clinic-software calendars, RODO health-data processing agreements, AI Act disclosure at call start (A22).

## 5. Demographic or social driver
DD3 queues (4.2–4.3 months for a specialist) and DD1 older patients who phone rather than book online (D15, D24: a third of 60–74-year-olds still offline).

## 6. CEE check
Born Digital (CZ) is in PL via Netia (enterprise); Linca (CZ) receptionist app; no CEE clinic-specific entrant found ([R6 README](../../research/regions/R6-cee-peers/README.md)).

## 7. Verdict: **partial**
Generic Polish-speaking voice receptionists are plentiful and ElevenLabs sells them in Polish, so voice itself is no gap. The open part is depth of integration: none of the vendors seen lists ZnanyLekarz or Polish clinic-software calendars, and NFZ-specific questions (queues, referrals, kolejka oczekujących) need Polish data.

**Seed idea:** phone agent for **private multi-doctor clinics and dental practices** that books straight into mMedica/Medfile/ZnanyLekarz calendars, handles cancellations and fills gaps from the waiting list, and answers "czy przyjmujecie na NFZ / ile czekam" from the NFZ Terminy API; priced per location (e.g. 399–699 PLN/month).
