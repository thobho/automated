import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

pytestmark = pytest.mark.django_db


def test_seed_creates_expected_counts_and_is_idempotent(capsys):
    call_command("seed")
    first = get_user_model().objects.count()
    capsys.readouterr()
    call_command("seed")
    assert first == 15
    assert get_user_model().objects.count() == first
    assert "created 0 artists, 0 institutions" in capsys.readouterr().out


def test_seed_uses_only_reserved_domain_and_no_password():
    call_command("seed")
    for user in get_user_model().objects.all():
        assert user.email.endswith("@example.invalid")
        assert not user.has_usable_password()
