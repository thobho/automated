# TH24 — Local-language voice and CS agents (Poland check)

Theme: [THEMES.md#th24](../../themes/THEMES.md#th24) · rank 15, batch A · sources accessed **2026-11-03** · method: [README](README.md#method). Overlaps [TH23](TH23-enterprise-customer-service-agents.md) (enterprise CS) and [TH26](TH26-ai-receptionist-smes.md) (SME receptionist); this file covers the "national-language voice stack sold to local enterprises" angle.

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| PKO Bank Polski in-house voicebots (and IKO voice assistant) | Inbound and outbound voicebots on the bank's hotline | internal | PKO reports 70 million conversations with "conversational AI" | [PKO BP press release](https://media.pkobp.pl/413115-rozmowna-sztuczna-inteligencja-w-pko-banku-polskim-juz-70-mln-konwersacji-z-klientami) |
| Lekta (Kraków) | Voicebots for banks; 12 voicebots in one large bank; subscription model for smaller firms | on request | banks, insurers approaching (vendor claim) | [Gazeta Prawna](https://www.gazetaprawna.pl/twoje-prawo/finanse-osobiste/artykuly/10930034,w-tych-bankach-obsluza-was-voiceboty-cyfrowych-doradcow-glosowych-bedzie-coraz-wiecej.html) |
| Alior "InfoNina", EFL outbound voicebot | Bank and leasing voicebots (100–200 calls/min at EFL, per the firm) | internal/vendor | Alior Bank, EFL | [Gazeta Prawna](https://www.gazetaprawna.pl/twoje-prawo/finanse-osobiste/artykuly/10930034,w-tych-bankach-obsluza-was-voiceboty-cyfrowych-doradcow-glosowych-bedzie-coraz-wiecej.html); [bank.pl](https://bank.pl/efl-wprowadzil-voicebota-ktory-dzwoni-do-klientow/) |
| Voicetel, Sovva, SentiOne, VoiceLab.ai, Thulium, InteliWISE | Polish voicebot vendors; Voicetel put the Polish voicebot market "near 100 million PLN" (older article, undated in snippet) | on request; Thulium 1,395 PLN/month for 5 licences (see TH23) | enterprise contact centres | [money.pl](https://www.money.pl/gielda/voicetel-wartosc-rynku-voicebotow-w-polsce-szybko-zmierza-do-100-mln-zl-6522746404939905a.html); [TH23](TH23-enterprise-customer-service-agents.md) |

## 2. Does the Western/foreign leader already serve Poland?
- **Wonderful** (IL, theme member `R8-IL-001`): has **entered Poland** with a Poland general manager (Marcin Motel), framing the offer as local tailoring rather than translation ([brandsit.pl](https://brandsit.pl/?p=1989765)); Globes lists Poland among its fastest-growing markets ([Globes, 2026-08](https://en.globes.co.il/en/article-1001552121)). **In PL.**
- **Born Digital** (CZ, `R6-CZ-004`): Netia (Polish telco) launched an AI voice assistant for business lines on Born Digital ([Born Digital case study](https://borndigital.ai/netia-launches-ai-voice-assistant-to-help-businesses-handle-calls-smarter/)). **In PL.**
- Other members (Fano Labs HK, WIZ.AI SG, Gulf players) are tied to their language markets; not in PL.
- Could not check: Polish-language demo calls (all demo-led, no self-serve).

## 3. Polish demand signals
- Autocomplete: "voicebot po polsku" → echo only; "bot głosowy" → none; "asystent głosowy ai" → "… po polsku", "najlepszy asystent glosowy ai". Low consumer search; enterprise buyers go through RFPs.
- PKO's running press series (10 → 15 → 20 → 25 → 50 → 70 million conversations) shows sustained enterprise adoption; critical press ("clients talk to bots because they have no choice", [gsmonline.pl](https://gsmonline.pl/artykuly/klienci-pko-gadaja-z-botami-bo-nie-maja-innego-wyjscia)).

## 4. What adaptation needs
M53 (no Polish voice assistants) is the moat item, but it is now eroded: global TTS/STT stacks (ElevenLabs, see TH26) and local vendors handle Polish. Remaining local needs: KNF outsourcing and cloud communication rules for banks, telco integration (Netia, Orange), RODO for call recordings, AI Act bot disclosure.

## 5. Demographic or social driver
DD7 labour scarcity raises contact-centre wages; DD1 ageing customers are the group most hostile to voicebots (press criticism above), a constraint rather than a driver.

## 6. CEE check
Born Digital (CZ) already sells in PL through Netia; Wonderful runs a Zagreb hub for South-East Europe ([R6 README](../../research/regions/R6-cee-peers/README.md)).

## 7. Verdict: **taken**
Polish banks run large in-house or vendor voicebots, a dozen Polish vendors compete, and two of the theme's foreign leaders (Wonderful, Born Digital) are already in Poland. Enterprise sales cycles and RFPs also do not fit a 40-hour/month solo founder.

**Seed idea:** none at enterprise level. Residue: a Polish **voicebot QA/test harness** (scripted synthetic callers in Polish dialects and accents, regression tests after prompt changes) sold to the vendors above, unverified demand.
