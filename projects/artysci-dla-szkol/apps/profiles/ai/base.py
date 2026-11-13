"""The provider-independent adapter: `AIClient.complete()` and what it returns.

`complete()` does the same for every client, in this order, before anything is sent:
kill switch, message checks, PII scrubbing, per-call cap (sets `max_tokens`), daily cap (a
`pending` AICall row reserves the worst case). Then the client's `_send()` runs, and the AICall
row is settled with model, tokens, `usage.cost`, latency and status. No prompt or reply text is
stored or logged.
"""

import json
import logging
import time
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from django.conf import settings
from django.utils.crypto import salted_hmac

from . import budget
from .errors import AIError, AIProviderError
from .scrub import scrub_messages

logger = logging.getLogger("apps.profiles.ai")

ROLES = {"system", "user", "assistant"}
SYSTEM_USER = "system"


@dataclass(frozen=True)
class Request:
    """What a client sends: already scrubbed and capped."""

    messages: list[dict]
    schema: dict | None
    max_tokens: int
    user: str
    purpose: str


@dataclass(frozen=True)
class Reply:
    """What a client got back. `cost_usd` None means the provider did not report a cost."""

    text: str
    model: str
    provider: str = ""
    generation_id: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: Decimal | None = None


@dataclass(frozen=True)
class AIResult:
    text: str
    cost_usd: Decimal
    model: str
    call_id: int
    data: Any = field(default=None)  # parsed JSON when a schema was given


def pseudonymous_user(user_ref) -> str:
    """Stable id for the provider's `user` field; never the real user id or e-mail."""
    if user_ref is None:
        return SYSTEM_USER
    return "u-" + salted_hmac("ai.user", str(user_ref)).hexdigest()[:16]


def _checked(messages) -> list[dict]:
    if not messages:
        raise AIError("messages must not be empty.")
    checked = []
    for message in messages:
        role, content = message.get("role"), message.get("content")
        if role not in ROLES or not isinstance(content, str):
            # Only plain-text messages: anything else could bypass the scrubber.
            raise AIError("Each message needs a role (system/user/assistant) and text content.")
        checked.append({"role": role, "content": content})
    return checked


class AIClient:
    """Base class. Subclasses set `name` and implement `_send(request) -> Reply`."""

    name = "base"

    def __init__(self, *, model: str | None = None, prices: budget.Prices | None = None):
        self.model = model or settings.AI_MODEL
        self.prices = prices or budget.Prices.from_settings()

    def complete(
        self,
        messages: list[dict],
        *,
        schema: dict | None = None,
        purpose: str,
        max_cost_usd,
        user_ref=None,
        scrub_names=(),
    ) -> AIResult:
        """Send chat `messages` and return the reply.

        `purpose` labels the call in AICall (e.g. "profile_draft"). `max_cost_usd` is this
        call's ceiling (at most AI_PER_CALL_CAP_USD). `schema` (JSON Schema) asks for structured
        output; the parsed object is in `AIResult.data`. `user_ref` (e.g. the artist's pk) is
        sent only as an HMAC pseudonym. `scrub_names` adds names to remove for this call.

        Raises AIDisabled, AICapExceeded (nothing sent), AIProviderError or AIError.
        """
        if not purpose or len(purpose) > 50:
            raise AIError("purpose must be 1-50 characters.")
        try:
            budget.check_kill_switch()
            names = [*settings.AI_SCRUB_NAMES, *scrub_names]
            clean = scrub_messages(_checked(messages), names)
            max_cost = Decimal(str(max_cost_usd))
            plan = budget.plan_call(clean, max_cost, self.prices)
            call = budget.reserve(
                client=self.name, purpose=purpose, model=self.model, max_cost_usd=max_cost
            )
        except AIError as exc:
            logger.warning("AI call blocked purpose=%s: %s", purpose, exc)
            raise

        request = Request(clean, schema, plan.max_tokens, pseudonymous_user(user_ref), purpose)
        started = time.monotonic()
        try:
            reply = self._send(request)
        except AIProviderError as exc:
            # Timeouts may still be billed: keep the reservation; other errors cost nothing.
            cost = max_cost if exc.maybe_billed else Decimal(0)
            self._settle(call, started, status="error", error=exc.code, cost=cost)
            raise
        except Exception:
            self._settle(call, started, status="error", error="unexpected", cost=max_cost)
            raise

        cost = reply.cost_usd
        if cost is None:
            logger.warning("AI reply without usage.cost; keeping the reserved worst case.")
            cost = max_cost
        data, error = None, ""
        if schema is not None:
            try:
                data = json.loads(reply.text)
            except ValueError:
                error = "invalid_json"
        self._settle(
            call, started, status="error" if error else "ok", error=error, cost=cost, reply=reply
        )
        if error:
            raise AIProviderError("The reply is not valid JSON.", code=error)
        return AIResult(
            text=reply.text, data=data, cost_usd=cost, model=reply.model, call_id=call.pk
        )

    def _send(self, request: Request) -> Reply:  # pragma: no cover - abstract
        raise NotImplementedError

    @staticmethod
    def _settle(call, started, *, status, error, cost, reply: Reply | None = None):
        call.status = status
        call.error = error[:200]
        call.cost_usd = cost
        call.latency_ms = int((time.monotonic() - started) * 1000)
        if reply is not None:
            call.model = reply.model[:200] or call.model
            call.provider = reply.provider[:100]
            call.generation_id = reply.generation_id[:200]
            call.prompt_tokens = reply.prompt_tokens
            call.completion_tokens = reply.completion_tokens
        call.save()
        logger.info(
            "AI call %s purpose=%s model=%s status=%s cost_usd=%s latency_ms=%s",
            call.pk,
            call.purpose,
            call.model,
            status,
            cost,
            call.latency_ms,
        )
