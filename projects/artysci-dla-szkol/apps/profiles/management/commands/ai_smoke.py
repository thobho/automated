"""Make one real, tiny AI call through the adapter and print the stored AICall row.

For checking a new OpenRouter key or provider setup by hand. It always uses OpenRouterClient,
whatever AI_CLIENT says, so it spends real money (well under $0.001 with the pinned model).
The prompt is fixed and synthetic. The key is never printed.

    uv run python manage.py ai_smoke [--key-file ~/.config/automated/secrets.env]
"""

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.profiles import ai
from apps.profiles.models import AICall

PROMPT = [
    {"role": "system", "content": "Odpowiadaj jednym krótkim zdaniem po polsku."},
    {"role": "user", "content": "Przywitaj się ze szkołą. Kontakt: test@example.invalid"},
]
ROW_FIELDS = (
    "id",
    "created_at",
    "client",
    "purpose",
    "model",
    "provider",
    "generation_id",
    "prompt_tokens",
    "completion_tokens",
    "cost_usd",
    "latency_ms",
    "status",
    "error",
)


def key_from_file(path: Path) -> str:
    """Read OPENROUTER_API_KEY from a dotenv-style file (`KEY=value`, optional `export`)."""
    try:
        lines = path.expanduser().read_text().splitlines()
    except OSError as exc:
        raise CommandError(f"Cannot read {path}: {exc.strerror}") from None
    for line in lines:
        line = line.strip().removeprefix("export ").strip()
        name, sep, value = line.partition("=")
        if sep and name.strip() == "OPENROUTER_API_KEY":
            return value.strip().strip("'\"")
    raise CommandError(f"OPENROUTER_API_KEY is not in {path}.")


class Command(BaseCommand):
    help = "Make one real tiny OpenRouter call and print the AICall row (costs real money)."

    def add_arguments(self, parser):
        parser.add_argument("--key-file", type=Path, help="dotenv file with OPENROUTER_API_KEY")
        parser.add_argument("--max-cost", default="0.01", help="per-call ceiling in USD")

    def handle(self, *args, key_file=None, max_cost="0.01", **options):
        key = key_from_file(key_file) if key_file else None
        try:
            client = ai.OpenRouterClient(api_key=key)
            result = client.complete(PROMPT, purpose="ai_smoke", max_cost_usd=max_cost)
        except ai.AIError as exc:
            raise CommandError(f"{type(exc).__name__}: {exc}") from None
        self.stdout.write(f"{client!r}")
        self.stdout.write(f"reply: {result.text}")
        row = AICall.objects.values(*ROW_FIELDS).get(pk=result.call_id)
        for name in ROW_FIELDS:
            self.stdout.write(f"  {name}: {row[name]}")
