# TH29 — Conversational commerce on messaging apps (Poland check)

Theme: [THEMES.md#th29](../../themes/THEMES.md#th29) · rank 19, batch A · sources accessed **2026-11-03** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| **Tidio** (Szczecin), Lyro AI | Multichannel inbox: WhatsApp, Messenger, Instagram, email, live chat; Lyro replies on WhatsApp count toward a free 1,000 messages/month per number | WhatsApp integration free on every plan; extra messages at Meta's local rate | 300k+ businesses (see TH23) | [Tidio WhatsApp page](https://www.tidio.com/whatsapp-integration/); [TH23](TH23-enterprise-customer-service-agents.md) |
| PerfectBot (Warsaw, 1–10 staff) | "AI agent for online stores" | not found | not found | [Chopping Block listing](https://www.choppingblock.ai/companies/perfectbot) |
| Zowie (Polish-founded, US HQ) | AI CS agent for e-commerce | on request | e-commerce brands | [ain.ua](https://ain.ua/en/2022/01/19/polish-zowie-raises-5m-seed/) |
| Allegro chat (platform-owned) | Buyer–seller messaging inside Allegro (M36) | part of Allegro | Allegro sellers | autocomplete below |

## 2. Does the Western leader already serve Poland?
- **ManyChat** (US): Instagram/Messenger/WhatsApp automation with AI; works in any language; pricing page returned 403 to the checker; Polish autocomplete "manychat ile kosztuje", "manychat cennik", "manychat instagram" shows Polish users. **Serves Polish (English UI).**
- Shopify apps (CraftChat, FlashDM and others) sell DM automation to Polish Shopify stores in Polish-language listings ([CraftChat](https://apps.shopify.com/chatbook?locale=pl)).
- Theme leaders (Omnichat HK, Vambe CL, Yavendió MX, qeen.ai AE) are tied to WhatsApp/LINE-first markets; not in PL.
- Could not check: ManyChat signup flow (needs a Meta account).

## 3. Polish demand signals
- Autocomplete: "whatsapp dla firm" → "whatsapp platforma dla firm", "whatsapp firmowy"; "messenger bot sklep" → none; "chatbot do sklepu" → none; "chatbot shoper" → echo only; "automatyzacja instagram dm" → echo only; "czat allegro" → "… dla sprzedających", "… z konsultantem".
- No reliable Polish statistic on WhatsApp/Messenger shopping found (Statista chart paywalled: [Statista](https://www.statista.com/statistics/1624839/poland-consumers-using-ai-when-shopping-online)). Polish buying runs through Allegro, shop sites, phone and email, not WhatsApp threads (theme note; unverified by survey).

## 4. What adaptation needs
M36 Allegro messaging API (seller–buyer chat), M39 BaseLinker order data, M37 InPost tracking, M32 BLIK/M33 Przelewy24 payment links, Shoper/IdoSell shop platforms (Polish SaaS shop builders); consumer-law rules (14-day returns) in answers.

## 5. Demographic or social driver
None specific; DD6 Ukrainian customers may favour Telegram/Viber (unverified).

## 6. CEE check
No CZ/SK/RO/HU conversational-commerce product in R6 ([R6 catalogue](../../catalogue/R6-cee-peers.csv)).

## 7. Verdict: **taken**
The WhatsApp-centred selling behaviour that drives the theme in Latin America and Asia does not exist at scale in Poland, and the channels Polish shops do use (Messenger, Instagram, WhatsApp, web chat) are already covered by Tidio (Polish) and ManyChat in Polish. The one Polish-specific channel, Allegro chat, is owned by Allegro.

**Seed idea (weak, adjacent):** AI reply agent for **Allegro seller messages** (order status from BaseLinker, InPost tracking, returns policy, dispute tone), priced per seller account per month; overlaps TH23 CS tools and depends on Allegro API terms.
