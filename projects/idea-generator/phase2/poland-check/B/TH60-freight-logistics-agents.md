# TH60 — Freight and logistics agents (Poland check)

Theme: [THEMES.md#th60](../../themes/THEMES.md#th60) · rank 34, batch B · sources accessed **2026-11-04** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| TSL Assistant | AI reads orders from e-mails and messengers, highlights extracted fields, automates data entry, publishes offers on exchanges, pulls carrier data from Trans.eu into the TMS | not published; 14-day trial after a meeting | forwarders and carriers (vendor claims thousands of orders/day) | [trans.info (sponsored)](https://trans.info/pl/tsl-assistant-upraszcza-zarzadzanie-zleceniami-spedycyjnymi-399956) |
| Trans.eu Automation Suite | Exchange-native automation, "Produkt Innowacyjny 2025"; plans to move to predictive and generative-AI decision support; partnerships with CargoCrush (automatic spot matching) and Soloplan CarLo TMS announced for TransLogistica 2026 (2026-11-03/05) | part of Trans.eu subscriptions | Trans.eu's carrier/forwarder base | [trans.info award](https://trans.info/pl/trans-eu-nagrodzone-za-automatyzacje-procesow-spedycyjnych-447346); [trans.info CargoCrush](https://trans.info/pl/trans-eu-i-cargocrush-lacza-sily-inteligentna-optymalizacja-transportu-z-dostepem-do-ladunkow-trans-eu-511998) |
| Polish TMS vendors and AI service sellers | TMS for carriers/forwarders; agencies selling "AI agents for order entry into TMS" (Polish landing pages) | various | not checked | [virtualworkforce.ai PL page](https://virtualworkforce.ai/pl/agenci-ai-do-wprowadzania-zlecen-w-tms/) |
| Transmetrics (BG) and other EU vendors | AI forecasting/pricing for logistics, publish in Polish trade media | enterprise | not checked | [trans.info op-ed](https://trans.info/pl/sama-skala-nie-wystarczy-jak-ai-zmienia-przewage-w-europejskiej-spedycji-505002) |

## 2. Does the Western leader already serve Poland?
- **HappyRobot** and **FleetWorks** (US): voice/e-mail agents for US brokers and carriers (load booking calls, MC numbers, US load boards). **Not in PL**; the European equivalent of their integration point is Trans.eu/Timocom, which Trans.eu itself is automating.
- **Nuvocargo** (MX) and **ShipBee** (QA): home-market digital forwarders.
- Could not check: HappyRobot EU availability (demo-led).

## 3. Polish demand signals
- Autocomplete (2026-11-04): "ai w spedycji" → 3 incl. "**agent ai w spedycji**"; "program dla firmy transportowej" → 5 (księgowy, jaki, najlepszy, do faktur); "giełda transportowa" → 10 incl. "bez rejestracji", "darmowa", "clicktrans"; "program dla spedytora" → echo only.
- Trade press runs a steady stream of AI-in-TSL pieces (sponsored and editorial); one large carrier said it will consider AI tools only in later years ([trans.info](https://trans.info/pl/sztuczna-inteligencja-weszla-do-transportu-481783)).

## 4. What adaptation needs
Trans.eu and Timocom exchanges (Trans.eu is Polish), CMR and zlecenie formats, Polish TMS integrations, M01 KSeF invoices for domestic legs, Mobility Package rules (posting of drivers, tachograph), PL/UA/BY drivers by phone in Polish, Ukrainian and Russian, payment-term disputes (see [TH14](TH14-debt-recovery-agents.md)). Poland's role as the EU's largest road-haulage country (theme note) makes the market large but fragmented.

## 5. Demographic or social driver
DD7: transport is on the shortage list and labour costs bite; DD6: many drivers are Ukrainian or other foreigners, so multilingual phone and message handling matters.

## 6. CEE check
No CZ/SK/RO/HU freight agent in R6 ([R6 catalogue](../../catalogue/R6-cee-peers.csv)); Transmetrics (BG, outside R6 catalogue) sells logistics AI regionally.

## 7. Verdict: **partial**
Order-entry and exchange automation for forwarders is already offered by TSL Assistant and by Trans.eu itself, the platform owner, which limits a newcomer. Not covered in this check: a **multilingual voice/messenger agent for small carriers** (1–20 trucks) that answers forwarders' and drivers' status calls, chases CMR/documents and prepares invoices, the HappyRobot pattern on the carrier side.

**Seed idea:** "Dyspozytor AI" for small carriers: one phone/WhatsApp/Viber number that answers forwarders' "where is the truck" calls from GPS, collects CMR photos from drivers in PL/UA/RU, checks them and issues the KSeF invoice with the right payment term; 199–399 PLN/month per fleet. Platform risk from Trans.eu remains.
