# TH28 — Car-dealer agents (Poland check)

Theme: [THEMES.md#th28](../../themes/THEMES.md#th28) · rank 49, batch C · sources accessed **2026-11-05** · method: [README](README.md#method).

## 1. Polish players
A comparison dated 2026-10-11 by AInora (LT, a vendor itself) counts **at least ten** AI phone assistants sold to Polish car workshops; prices are net per month as read on that date ([AInora blog](https://ainora.lt/pl/blog/asystent-ai-warsztat-samochodowy-porownanie-2026)):

| Product | Price (PLN/month) | Integrations named |
|---|---|---|
| Zilo AI (DobryMechanik) | 199 (200 calls), AI+ 299 (500 calls); program without AI 149 | is itself a workshop program |
| PilotGo | 159 | Motowarsztat, Warsztat24, Google Calendar |
| Fonio / SekretarkaAI.pl | 479 (399 annual), 1,000 min | calendar |
| Heyheyo | 299–599 | calendar, SMS |
| home.pl | 169–369 | API on top plan |
| Smart Asystenci | 499–1,499 | own calendar |
| Maikon AI Recepcja | from 1,900 | none named |
| odbierze.ai | 990 + 2,990 setup; outbound from 1,490 + 4,990 setup | calendar or one system |
| AInora (LT) | quote | Motowarsztat, Integra, Zilo |
| YarMobile | not published | none named |

Fonio also markets a Polish-language assistant for car showrooms that routes calls or books callbacks ([Fonio PL: salony samochodowe](https://www.fonio.ai/pl/ki-telefonassistenten-archived/salony-samochodowe)). No customers are named in the comparison.

## 2. Does the Western leader already serve Poland?
- **Flai** (UY, for US dealers: 50k+ appointments/month) and **Toma** (US) sell only to US dealers with US DMS integrations (CDK, Reynolds); no European presence found ([LatamList on Flai](https://latamlist.com/flai-raises-27m-series-a-to-expand-ai-agents-for-us-car-dealerships/)).
- **Sandra AI** (FR, YC F24): site is JavaScript-only and returned no content on fetch, so languages and markets could not be checked ([sandra-ai.com](https://www.sandra-ai.com/)).
- The gap the Western leaders fill is already filled locally by horizontal Polish voice-receptionist vendors with workshop templates.

## 3. Polish demand signals
- Autocomplete (2026-11-05): "crm dla dealera", "umówienie serwisu samochodu online", "otomoto dla dealerów", "voicebot serwis" → none; "program dla komisu samochodowego" → echo only. **Low search volume**; supply is vendor-pushed.

## 4. What adaptation needs
Workshop programs (Motowarsztat, Warsztat24, Integra, Zilo), M40 OLX and Otomoto lead flows, M21 CEPiK/historiapojazdu for vehicle history, PKE consent rules for outbound reminder calls (batch B TH30), M53 Polish voice. Authorised dealers (ASO) run brand DMS mandated by the OEM, a channel a solo founder cannot reach.

## 5. Demographic or social driver
DD7 labour scarcity (mechanics, receptionists); no specific demographic driver.

## 6. CEE check
AInora (LT) already sells in Poland with Polish workshop integrations; no CZ/SK/RO/HU dealer agent in the [R6 catalogue](../../catalogue/R6-cee-peers.csv).

## 7. Verdict: **taken**
Call answering and service booking for workshops is sold by 10+ vendors at 159–499 PLN/month, including DobryMechanik's own workshop program, which owns the distribution. Dealer-group sales agents would need OEM DMS access and enterprise sales. This is a vertical of batch A TH26 (AI receptionist), already crowded.

**Seed idea:** (weak) Otomoto/OLX lead follow-up agent for independent used-car dealers (komisy): answers listing messages 24/7, checks CEPiK history and books viewings; 149–299 PLN/month. Demand unproven.
