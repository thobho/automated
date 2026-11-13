"""Cost cap (D63): kill switch, per-call cap and global daily cap, checked before sending.

Per call: the caller's `max_cost_usd` may not exceed `AI_PER_CALL_CAP_USD`. The prompt cost is
estimated from its length (pessimistic: 3 characters per token) at the configured price, and
`max_tokens` is limited so that prompt + longest possible reply stay within `max_cost_usd`.
OpenRouter also gets `provider.max_price`, so no endpoint above the configured price is used.

Daily: today's (Europe/Warsaw) recorded cost plus this call's `max_cost_usd` may not exceed
`AI_DAILY_CAP_USD`. `reserve()` checks and inserts a `pending` AICall row holding the worst
case in one short transaction under a PostgreSQL advisory lock, so concurrent workers cannot
both pass the check; the row is settled with the real cost after the call.
"""

import math
from dataclasses import dataclass
from datetime import datetime, time
from decimal import Decimal

from django.conf import settings
from django.db import connection, transaction
from django.db.models import Sum
from django.utils import timezone

from .errors import AICapExceeded, AIConfigError, AIDisabled

BUDGET_LOCK_ID = 0x41494341  # "AICA": advisory lock key for daily-cap reservations
CHARS_PER_TOKEN = 3  # pessimistic for Polish text: more tokens means a higher estimate
PER_MESSAGE_OVERHEAD_TOKENS = 8
MILLION = Decimal(1_000_000)


@dataclass(frozen=True)
class Prices:
    """USD per one million tokens."""

    prompt: Decimal
    completion: Decimal

    @classmethod
    def from_settings(cls) -> "Prices":
        prompt = Decimal(str(settings.AI_PRICE_PROMPT_USD_PER_MTOK))
        completion = Decimal(str(settings.AI_PRICE_COMPLETION_USD_PER_MTOK))
        if prompt < 0 or completion <= 0:
            raise AIConfigError("AI prices must be >= 0 (prompt) and > 0 (completion).")
        return cls(prompt=prompt, completion=completion)


@dataclass(frozen=True)
class Plan:
    max_tokens: int
    estimated_prompt_tokens: int
    estimated_max_cost_usd: Decimal


def check_kill_switch() -> None:
    if settings.AI_KILL_SWITCH:
        raise AIDisabled("AI calls are switched off (AI_KILL_SWITCH).")


def estimate_prompt_tokens(messages: list[dict]) -> int:
    chars = sum(len(m.get("content", "")) for m in messages)
    return math.ceil(chars / CHARS_PER_TOKEN) + PER_MESSAGE_OVERHEAD_TOKENS * len(messages)


def plan_call(messages: list[dict], max_cost_usd: Decimal, prices: Prices) -> Plan:
    """Check the per-call cap and work out `max_tokens`. Raises AICapExceeded."""
    per_call_cap = Decimal(str(settings.AI_PER_CALL_CAP_USD))
    if max_cost_usd <= 0:
        raise AICapExceeded("max_cost_usd must be positive.")
    if max_cost_usd > per_call_cap:
        raise AICapExceeded(
            f"max_cost_usd {max_cost_usd} is above the per-call cap {per_call_cap} USD."
        )
    prompt_tokens = estimate_prompt_tokens(messages)
    prompt_cost = prompt_tokens * prices.prompt / MILLION
    room = max_cost_usd - prompt_cost
    affordable = int(room * MILLION / prices.completion) if room > 0 else 0
    max_tokens = min(int(settings.AI_MAX_TOKENS), affordable)
    if max_tokens < 1:
        raise AICapExceeded(
            f"The prompt alone (~{prompt_tokens} tokens) does not fit in {max_cost_usd} USD."
        )
    estimate = prompt_cost + max_tokens * prices.completion / MILLION
    return Plan(max_tokens, prompt_tokens, estimate)


def start_of_today():
    today = timezone.localdate()
    return timezone.make_aware(datetime.combine(today, time.min))


def spent_today() -> Decimal:
    from apps.profiles.models import AICall

    total = AICall.objects.filter(created_at__gte=start_of_today()).aggregate(s=Sum("cost_usd"))
    return total["s"] or Decimal(0)


def check_daily_cap(max_cost_usd: Decimal) -> None:
    """Raise AICapExceeded when today's spend plus this call's worst case is above the cap."""
    cap = Decimal(str(settings.AI_DAILY_CAP_USD))
    spent = spent_today()
    if spent + max_cost_usd > cap:
        raise AICapExceeded(
            f"Daily AI cap reached: spent {spent} of {cap} USD today, this call may cost up "
            f"to {max_cost_usd} USD."
        )


def _lock_budget() -> None:
    """Serialise reservations across processes (PostgreSQL; SQLite serialises writes itself)."""
    if connection.vendor == "postgresql":
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_xact_lock(%s)", [BUDGET_LOCK_ID])


def reserve(*, client: str, purpose: str, model: str, max_cost_usd: Decimal):
    """Check the daily cap and record a `pending` AICall holding `max_cost_usd`."""
    from apps.profiles.models import AICall

    with transaction.atomic():
        _lock_budget()
        check_daily_cap(max_cost_usd)
        return AICall.objects.create(
            client=client,
            purpose=purpose,
            model=model,
            status=AICall.Status.PENDING,
            cost_usd=max_cost_usd,
        )
