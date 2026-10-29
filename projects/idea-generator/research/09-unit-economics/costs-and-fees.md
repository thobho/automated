# Lens 9 — Payment fees, store commissions and variable infrastructure costs

Part of [lens 9](README.md). All sources accessed 2026-10-29. Pages were read through a summarising fetch tool, so numbers are as returned; "unverified" marks what I could not confirm on a primary page. Prices are net of VAT unless stated. Platform fees from other lenses are referenced, not re-counted: Paddle merchant-of-record [L7-F18](../07-founder-fit/costs-and-ops.md), LLM price table and per-document cost [L7-F26, F27](../07-founder-fit/costs-and-ops.md), Shopify / Atlassian / DATEV / Allegro programmes [L8-F01–F07](../08-distribution/marketplaces-and-directories.md).

## L9-F01 — Stripe Poland: 1.5% + 1.00 zł on standard EEA cards, 1.6% + 1.00 zł BLIK, 1.9% + 1.00 zł Przelewy24; Billing adds 0.7%
Stripe's Polish pricing page: domestic standard EEA cards 1.5% + 1.00 zł, premium EEA cards 1.9% + 1.00 zł, UK/international cards 2.5–3.25% + 1.00 zł, +2% currency conversion where needed; BLIK 1.6% + 1.00 zł; Przelewy24 1.9% + 1.00 zł. Disputes cost 90.00 zł each (refunded only when won). Add-ons: Billing pay-as-you-go 0.7% of Billing volume, Invoicing 0.4% per paid invoice, Tax 0.5% per transaction (no-code) or 2.00 zł (API). Source: https://stripe.com/en-pl/pricing (accessed 2026-10-29).
- **Reading (estimate):** on a 49 PLN monthly subscription a standard card costs 0.735 + 1.00 = about 1.74 PLN (3.6%); on 99 PLN about 2.49 PLN (2.5%); with Billing 0.7% added about 3.2 PLN (3.2%) at 99 PLN. The fixed 1 zł is the main cost for low prices, so annual billing or ~99+ PLN plans dilute it. Without a merchant of record the founder owns VAT/OSS filing (L7-F18 shows the alternative at 5% + USD 0.50).
- **Confidence:** high (primary pricing page), perishable.

## L9-F02 — PayU Poland: 1.1% + 0.30 PLN for cards, BLIK and bank transfers; activation 29 PLN, no monthly fee shown
PayU Poland's pricing page lists electronic bank transfers, BLIK and payment cards (incl. Google Pay/Apple Pay) at 0.30 PLN + 1.1% per transaction, a 1.49% figure the page does not explain, and a 29 PLN activation fee (shown as reduced from 199 PLN). Monthly and minimum fees are not listed on the page; a price-list PDF exists but was not read. Source: https://poland.payu.com/en/pricing/ (accessed 2026-10-29).
- **Reading (estimate):** at 99 PLN this is about 1.39 PLN (1.4%), roughly 1.1 PLN cheaper than Stripe cards, but PayU is a gateway with no subscription billing: recurring charges need card-on-file tokens and your own dunning. Which rate a micro-merchant actually gets depends on onboarding (unverified).
- **Confidence:** medium (promo vs standard rate unclear).

## L9-F03 — Przelewy24: 1.9% standard (1.29% + 0.30 PLN new-client offer), no monthly fee, 0% on cards for 12 months under "Polska Bezgotówkowa"
Przelewy24's offer page lists cards, BLIK, online transfers and e-wallets at 1.9%, or 1.29% + 30 gr for a new-client offer; monthly subscription 0 zł; refunds free; foreign-currency cards 2% (EUR, CZK) and 3.6% (GBP, USD); account activation shown as 0 zł with a footnote of 59 zł refunded after 10 transactions in two months. A "Polska Bezgotówkowa" promotion gives 0% commission on card payments for 12 months to new online sellers. Source: https://www.przelewy24.pl/oferta (accessed 2026-10-29). The `/cennik` URL returned 404.
- **Reading:** all three Polish options sit between about 1.1% and 1.9% plus 0.30–1.00 zł; the choice moves margin by 1–2 percentage points, not by a category. The recurring-billing tooling (Stripe) matters more than the rate.
- **Confidence:** medium (page read via summary; promotion terms not read).

## L9-F04 — Apple: 15% commission in the Small Business Program (up to USD 1M proceeds); 10% for EU alternative terms and subscriptions after year one
Apple's programme page: commission falls to 15% on paid apps and in-app purchases for developers with up to USD 1 million in proceeds in the prior and current calendar year; a further reduced 10% applies for developers on the alternative terms in the EU and for subscriptions after the first year (as returned by the summariser; the page's wording on the 10% case should be re-read before relying on it). The page does not state the standard rate; it is widely known to be 30% (unverified here). Source: https://developer.apple.com/app-store/small-business-program/ (accessed 2026-10-29).
- **Reading:** a consumer/B2C mobile subscription loses 15% of revenue to Apple before VAT and tax effects, versus about 2–4% for a web checkout; B2B web SaaS avoids this. Native-mobile polish is already a negative in the brief (L7).
- **Confidence:** medium.

## L9-F05 — Google Play: 15% on the first USD 1M a year, 30% above; 15% on auto-renewing subscriptions regardless of revenue (outside EEA/US/UK/Japan/Australia)
Google Play Console help, "remaining markets" section: the 15% tier pays 15% on the first USD 1M annual revenue and 30% above; 15% for auto-renewing subscriptions regardless of revenue. EEA, UK, US, Japan and Australia follow separate fee structures that I did not read. Source: https://support.google.com/googleplay/android-developer/answer/112622 (accessed 2026-10-29).
- **Reading:** the store tax (15%) is much higher than payment-processor fees (1.1–1.9%); apps sold in stores must price it in. Poland/EEA-specific fee schedule: unverified.
- **Confidence:** medium.

## L9-F06 — SMS is a real variable cost: SMSAPI prepaid 0.17 PLN per SMS at 49–499 PLN top-ups, postpaid 0.14–0.16 PLN in the 1–1,000/month tier
SMSAPI's price list (net): prepaid 0.17 PLN (49–499.99 PLN top-up), 0.16 (500–1,999.99), 0.15, 0.13, 0.11 above 10,000 PLN; postpaid 0.16 / 0.14 PLN for 1–1,000 messages a month (the page does not say what the second value is); a subscription fee of 49 PLN net per month (page does not say which model it applies to). Source: https://www.smsapi.pl/cennik (accessed 2026-10-29).
- **Reading (estimate):** a salon-booking tool sending two reminder SMS per appointment at ~0.16 PLN costs 0.32 PLN per booking; a salon with 300 bookings a month spends about 96 PLN on SMS, which already exceeds many ~49–99 PLN subscription prices. SMS must be passed through, capped or replaced by e-mail/push, otherwise margin goes negative for heavy users. Booksy-style commission/Boost complaints are in lens 6.
- **Confidence:** high for list prices; the margin reading is my estimate (assumes 2 SMS per booking, 300 bookings).

## L9-F07 — E-mail and hosting are close to free at micro scale: AWS SES USD 0.10 per 1,000 e-mails, Hetzner Cloud from EUR 6.49/month
AWS SES à-la-carte outbound is USD 0.10 per 1,000 e-mails; dedicated IP USD 24.95/month; new accounts get up to USD 200 credits for 6 months. Source: https://aws.amazon.com/ses/pricing/ (accessed 2026-10-29). Hetzner Cloud lists Regular Performance from EUR 6.49/month and General Purpose (dedicated vCPU) from EUR 43.49/month, excl. VAT (specs and traffic allowance not shown on the page): https://www.hetzner.com/cloud/ (accessed 2026-10-29).
- **Reading (estimate):** 500 customers each receiving 20 e-mails a month = 10,000 e-mails = USD 1; a single server in the EUR 6–43 range hosts the product for dozens to hundreds of paying small customers. Infra is below 5% of revenue for typical SaaS at 10k PLN MRR (estimate, not measured). The cost risks are SMS (F06), LLM loops with many calls (L7-F27 bounded per-document only), and the founder's own AWS/accounting time.
- **Confidence:** high for list prices; scale estimate is mine.

## L9-F08 — Worked margin estimate for three price points (assumptions marked)
Combining F01, F06, F07 and L7-F27 (not re-sourced): **estimate**, 1 EUR ≈ 4.3 PLN and 1 USD ≈ 3.7 PLN assumed (not looked up today).
| Price/month (net) | Stripe card + Billing | LLM (500 docs, Haiku) | SMS (100 msgs) | Infra share (assumed) | Gross margin (approx.) |
|---|---|---|---|---|---|
| 49 PLN | ~2.1 PLN | ~1.7 PLN | 16 PLN | ~1 PLN | ~80% with SMS, ~90% without |
| 99 PLN | ~3.2 PLN | ~1.7 PLN | 16 PLN | ~1 PLN | ~78% with SMS, ~94% without |
| 299 PLN | ~7.3 PLN | ~1.7 PLN | 16 PLN | ~1 PLN | ~91% with SMS, ~96% without |

Reading: for B2B text/data products gross margin is above 90% even on 49 PLN; only SMS-heavy, store-distributed or agent-loop products fall to 50–80%. LLM line uses L7-F27 (Haiku about USD 0.0009 per document × 500 × 3.7 ≈ 1.7 PLN). What destroys margin is **founder time per customer**, not cloud cost (lens 7, 40 h/month).
- **Confidence:** low-medium (arithmetic on sourced prices, assumed volumes).
