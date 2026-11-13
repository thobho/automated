"""FakeClient: deterministic, offline. Used in tests, CI and local development.

Same input, same output: the reply is derived from a hash of the (scrubbed) messages and the
schema. With a schema it returns a minimal object matching it. Every Request it receives is
kept in `requests`, so tests can check exactly what would have been sent.
"""

import hashlib
import json
import math
from collections.abc import Callable
from decimal import Decimal

from .base import AIClient, Reply, Request


def example_for(schema: dict, seed: str = "fake"):
    """A small value matching a JSON Schema (object/array/string/number/integer/boolean)."""
    if "enum" in schema:
        return schema["enum"][0]
    kind = schema.get("type", "object")
    if isinstance(kind, list):
        kind = next((k for k in kind if k != "null"), "null")
    if kind == "object":
        props = schema.get("properties", {})
        return {name: example_for(sub, seed) for name, sub in props.items()}
    if kind == "array":
        return []
    if kind == "string":
        return seed
    if kind in ("number", "integer"):
        return 0
    if kind == "boolean":
        return False
    return None


class FakeClient(AIClient):
    name = "fake"

    def __init__(
        self,
        *,
        reply: str | Callable[[Request], str] | None = None,
        cost_usd="0",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.reply = reply
        self.cost_usd = Decimal(str(cost_usd))
        self.requests: list[Request] = []

    def _send(self, request: Request) -> Reply:
        self.requests.append(request)
        canonical = json.dumps([request.messages, request.schema], sort_keys=True)
        digest = hashlib.sha256(canonical.encode()).hexdigest()[:12]
        if callable(self.reply):
            text = self.reply(request)
        elif self.reply is not None:
            text = self.reply
        elif request.schema is not None:
            text = json.dumps(example_for(request.schema, f"fake-{digest}"), ensure_ascii=False)
        else:
            text = f"[fake reply {digest}]"
        return Reply(
            text=text,
            model=self.model,
            provider="fake",
            generation_id=f"fake-{digest}",
            prompt_tokens=sum(math.ceil(len(m["content"]) / 4) for m in request.messages),
            completion_tokens=math.ceil(len(text) / 4),
            cost_usd=self.cost_usd,
        )
