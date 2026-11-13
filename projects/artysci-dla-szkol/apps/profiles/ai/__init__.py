"""AI adapter (T07): one provider-independent, PII-safe, cost-capped way to call LLMs.

    from apps.profiles import ai

    result = ai.complete(
        [{"role": "user", "content": "..."}], purpose="profile_draft", max_cost_usd="0.01"
    )

`AI_CLIENT` picks the implementation: "fake" (default; deterministic, offline) or
"openrouter". See base.py for the checks every call goes through.
"""

from django.conf import settings

from .base import AIClient, AIResult, Reply, Request
from .errors import AICapExceeded, AIConfigError, AIDisabled, AIError, AIProviderError
from .fake import FakeClient
from .openrouter import OpenRouterClient

CLIENTS = {"fake": FakeClient, "openrouter": OpenRouterClient}

__all__ = [
    "AICapExceeded",
    "AIClient",
    "AIConfigError",
    "AIDisabled",
    "AIError",
    "AIProviderError",
    "AIResult",
    "FakeClient",
    "OpenRouterClient",
    "Reply",
    "Request",
    "complete",
    "get_client",
]


def get_client() -> AIClient:
    try:
        cls = CLIENTS[settings.AI_CLIENT]
    except KeyError:
        raise AIConfigError(f"Unknown AI_CLIENT {settings.AI_CLIENT!r}.") from None
    return cls()


def complete(messages, **kwargs) -> AIResult:
    """`get_client().complete(...)`; see `AIClient.complete` for the arguments."""
    return get_client().complete(messages, **kwargs)
