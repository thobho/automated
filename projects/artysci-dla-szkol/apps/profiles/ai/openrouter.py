"""OpenRouter chat completions, pinned model, privacy-first routing (D46, D60).

Every request asks OpenRouter to route only to endpoints that do not collect data
(`data_collection: "deny"`) and keep zero data retention (`zdr: true`), only to providers in
`AI_PROVIDERS` (fallbacks stay inside that list), and never above the configured price.
The HTTP call uses the standard library: no extra dependency. The API key comes from the
`OPENROUTER_API_KEY` env var and never appears in logs, errors or `repr()`.
"""

import json
import urllib.error
import urllib.request
from collections.abc import Callable
from decimal import Decimal

from django.conf import settings

from .base import AIClient, Reply, Request
from .errors import AIConfigError, AIProviderError

API_URL = "https://openrouter.ai/api/v1/chat/completions"

# (url, headers, body, timeout) -> (HTTP status, response body)
Transport = Callable[[str, dict, bytes, float], tuple[int, bytes]]


def urllib_transport(url: str, headers: dict, body: bytes, timeout: float) -> tuple[int, bytes]:
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")  # noqa: S310
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, TimeoutError):
            raise _timeout() from exc
        raise AIProviderError("OpenRouter is unreachable.", code="network") from exc
    except TimeoutError as exc:
        raise _timeout() from exc


def _timeout() -> AIProviderError:
    # The request may have been processed (and billed) before the timeout.
    return AIProviderError("OpenRouter timed out.", code="timeout", maybe_billed=True)


class OpenRouterClient(AIClient):
    name = "openrouter"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        providers: list[str] | None = None,
        transport: Transport | None = None,
        timeout: float | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._api_key = api_key or settings.OPENROUTER_API_KEY
        if not self._api_key:
            raise AIConfigError("OPENROUTER_API_KEY is not set.")
        self.providers = list(providers if providers is not None else settings.AI_PROVIDERS)
        if not self.providers:
            raise AIConfigError("AI_PROVIDERS must list at least one provider.")
        self.transport = transport or urllib_transport
        self.timeout = timeout if timeout is not None else settings.AI_TIMEOUT_SECONDS

    def __repr__(self):
        return f"OpenRouterClient(model={self.model!r}, providers={self.providers!r})"

    def build_body(self, request: Request) -> dict:
        body = {
            "model": self.model,  # pinned: no `models` fallback list
            "messages": request.messages,
            "max_tokens": request.max_tokens,
            "user": request.user,
            "usage": {"include": True},
            "provider": {
                "data_collection": "deny",
                "zdr": True,
                "only": self.providers,
                "order": self.providers,
                "allow_fallbacks": True,  # only between the providers in `only`
                "require_parameters": request.schema is not None,
                "max_price": {
                    "prompt": float(self.prices.prompt),
                    "completion": float(self.prices.completion),
                },
            },
        }
        if request.schema is not None:
            body["response_format"] = {
                "type": "json_schema",
                "json_schema": {"name": "result", "strict": True, "schema": request.schema},
            }
        return body

    def _send(self, request: Request) -> Reply:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = json.dumps(self.build_body(request), ensure_ascii=False).encode()
        status, raw = self.transport(API_URL, headers, payload, self.timeout)
        try:
            data = json.loads(raw, parse_float=Decimal)
        except ValueError as exc:
            raise AIProviderError(f"OpenRouter HTTP {status}: not JSON.", code="bad_json") from exc
        if status != 200 or "error" in data:
            error = data.get("error") or {}
            code = str(error.get("code") or status)
            raise AIProviderError(f"OpenRouter error {code}.", code=f"http_{code}"[:200])
        try:
            choice = data["choices"][0]
            text = choice["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as exc:
            raise AIProviderError("OpenRouter reply has no choices.", code="no_choices") from exc
        usage = data.get("usage") or {}
        cost = usage.get("cost")
        return Reply(
            text=text,
            model=str(data.get("model") or self.model),
            provider=str(data.get("provider") or ""),
            generation_id=str(data.get("id") or ""),
            prompt_tokens=int(usage.get("prompt_tokens") or 0),
            completion_tokens=int(usage.get("completion_tokens") or 0),
            cost_usd=Decimal(str(cost)) if cost is not None else None,
        )
