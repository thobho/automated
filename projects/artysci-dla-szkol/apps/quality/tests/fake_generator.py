"""Test-only fake generator: the shape a real generator (US-2.5a) takes, wired through the
registry services and the fake AI client. It sends no artist material, only a fixed prompt."""

import json

from apps.profiles.ai import FakeClient
from apps.quality import services
from apps.quality.models import Generation
from apps.quality.registry import Component, Registry

SCHEMA_TEXT = '{"type": "object", "properties": {"title": {"type": "string"}}}'


def fake_components(instructions_version="1", instructions_text="Napisz krótki opis.") -> list:
    reg = Registry()
    return [
        reg.register(Component("instructions", "fake_draft", instructions_version,
                               content=instructions_text)),
        reg.register(Component("schema", "fake_profile", "1", content=SCHEMA_TEXT)),
        reg.register(Component("validator", "fake_check", "1",
                               files=("apps/quality/tests/fake_generator.py",))),
        reg.register(Component("template", "fake_page", "1", content="<h1>{{ title }}</h1>")),
    ]  # fmt: skip


def run(artist, *, components=None, client=None, trigger="manual") -> Generation:
    """Two AI calls: a draft, then one repair round. Both are linked to the generation, the
    first through the adapter, the second through `record_ai_call`."""
    client = client or FakeClient(cost_usd="0.0012", model="fake/model-1")
    components = components or fake_components()
    generation = services.start_generation(artist, trigger, components)
    schema = json.loads(SCHEMA_TEXT)
    messages = [{"role": "user", "content": "Opis profilu testowego."}]
    draft = client.complete(
        messages, schema=schema, purpose="fake_draft", max_cost_usd="0.01", generation=generation
    )
    repair = client.complete(messages, schema=schema, purpose="fake_repair", max_cost_usd="0.01")
    services.record_ai_call(generation, repair.call_id)
    return services.finish_generation(
        generation,
        result={"draft": draft.data, "final": repair.data},
        warnings=["brak zdjęć"],
        repair_rounds=1,
        status=Generation.Status.REVIEW,
    )
