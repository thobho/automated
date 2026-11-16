import io
import json

import pytest
from django.core.management import CommandError, call_command
from django.test import override_settings

from apps.profiles.ai import openrouter
from apps.profiles.management.commands.ai_smoke import key_from_file
from apps.profiles.models import AICall

pytestmark = pytest.mark.django_db

KEY = "sk-or-smoke-key-never-printed"
REPLY = {
    "id": "gen-smoke",
    "model": "anthropic/claude-haiku-5.5",
    "provider": "Google",
    "choices": [{"message": {"role": "assistant", "content": "Dzień dobry!"}}],
    "usage": {"prompt_tokens": 50, "completion_tokens": 5, "cost": 0.0000081},
}


@pytest.fixture
def sent(monkeypatch):
    calls = []

    def transport(url, headers, body, timeout):
        calls.append({"headers": headers, "body": json.loads(body)})
        return 200, json.dumps(REPLY).encode()

    monkeypatch.setattr(openrouter, "urllib_transport", transport)
    return calls


def run(*args):
    out = io.StringIO()
    call_command("ai_smoke", *args, stdout=out)
    return out.getvalue()


@pytest.mark.parametrize(
    "content",
    [
        f"OPENROUTER_API_KEY={KEY}\n",
        f"# comment\nOTHER=1\nexport OPENROUTER_API_KEY='{KEY}'\n",
        f'OPENROUTER_API_KEY = "{KEY}"\n',
    ],
)
def test_key_from_file(tmp_path, content):
    path = tmp_path / "secrets.env"
    path.write_text(content)
    assert key_from_file(path) == KEY


def test_key_from_file_errors(tmp_path):
    with pytest.raises(CommandError, match="not in"):
        (tmp_path / "s.env").write_text("OTHER=1\n")
        key_from_file(tmp_path / "s.env")
    with pytest.raises(CommandError, match="Cannot read"):
        key_from_file(tmp_path / "missing.env")


def test_smoke_call_uses_openrouter_and_prints_row_without_key(tmp_path, sent):
    (tmp_path / "s.env").write_text(f"OPENROUTER_API_KEY={KEY}\n")
    out = run("--key-file", str(tmp_path / "s.env"))

    assert sent[0]["headers"]["Authorization"] == f"Bearer {KEY}"
    assert sent[0]["body"]["provider"]["data_collection"] == "deny"
    assert "test@example.invalid" not in json.dumps(sent[0]["body"])  # scrubbed
    row = AICall.objects.get()
    assert (row.client, row.purpose, row.status) == ("openrouter", "ai_smoke", "ok")
    assert f"cost_usd: {row.cost_usd}" in out
    assert KEY not in out


@override_settings(OPENROUTER_API_KEY=KEY)
def test_smoke_call_falls_back_to_settings_key(sent):
    assert "status: ok" in run()


def test_smoke_errors_become_command_errors(sent):
    with pytest.raises(CommandError, match="AIConfigError"):
        run()  # test settings: no key
    with (
        override_settings(OPENROUTER_API_KEY=KEY, AI_KILL_SWITCH=True),
        pytest.raises(CommandError, match="AIDisabled"),
    ):
        run()
    assert sent == []
