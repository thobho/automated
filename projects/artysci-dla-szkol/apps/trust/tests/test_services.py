import pytest
from django.core.management import call_command
from django.utils import timezone

from apps.trust import services
from apps.trust.errors import DocumentImmutable, NoPublishedVersion, UnknownKind
from apps.trust.models import LegalAcceptance, LegalDocument

pytestmark = pytest.mark.django_db


def test_current_is_none_without_versions():
    assert services.current("terms") is None


def test_publish_numbers_versions_per_kind():
    t1 = services.publish("terms", "Regulamin 1", material=False)
    p1 = services.publish("privacy", "Polityka 1", material=False)
    t2 = services.publish("terms", "Regulamin 2", material=False)
    assert (t1.version, p1.version, t2.version) == (1, 1, 2)
    assert services.current("terms") == t2
    assert services.current("privacy") == p1
    assert timezone.is_aware(t2.published_at)


def test_first_version_is_always_material():
    assert services.publish("terms", "v1", material=False).material is True
    assert services.publish("terms", "v2", material=False).material is False


def test_publish_rejects_empty_body_and_unknown_kind():
    with pytest.raises(ValueError):
        services.publish("terms", "   ", material=True)
    with pytest.raises(UnknownKind):
        services.publish("contract", "x", material=True)
    with pytest.raises(UnknownKind):
        services.current("contract")


def test_correction_is_new_version_and_old_one_is_unchanged():
    v1 = services.publish("terms", "Pierwotna treść", material=True)
    snapshot = LegalDocument.objects.values().get(pk=v1.pk)
    v2 = services.publish("terms", "Poprawiona treść", material=False)
    assert services.current("terms") == v2
    assert v2.version == 2
    assert LegalDocument.objects.values().get(pk=v1.pk) == snapshot


def test_published_version_cannot_be_edited_or_deleted():
    v1 = services.publish("terms", "Treść", material=True)
    v1.body = "Zmieniona"
    with pytest.raises(DocumentImmutable):
        v1.save()
    with pytest.raises(DocumentImmutable):
        LegalDocument.objects.filter(pk=v1.pk).update(body="Zmieniona")
    with pytest.raises(DocumentImmutable):
        v1.delete()
    with pytest.raises(DocumentImmutable):
        LegalDocument.objects.all().delete()
    assert LegalDocument.objects.get(pk=v1.pk).body == "Treść"


def test_record_acceptance_stores_current_versions_now(user):
    services.publish("terms", "t1", material=True)
    terms = services.publish("terms", "t2", material=False)
    privacy = services.publish("privacy", "p1", material=True)
    before = timezone.now()
    rows = services.record_acceptance(user, ["terms", "privacy"])
    after = timezone.now()
    assert LegalAcceptance.objects.filter(user=user).count() == 2
    assert {r.document for r in rows} == {terms, privacy}
    for row in rows:
        assert timezone.is_aware(row.accepted_at)
        assert before <= row.accepted_at <= after


def test_record_acceptance_is_idempotent_per_version(user):
    services.publish("terms", "t1", material=True)
    first = services.record_acceptance(user, ["terms", "terms"])
    again = services.record_acceptance(user, ["terms"])
    assert len(first) == 1
    assert first[0].pk == again[0].pk
    assert LegalAcceptance.objects.count() == 1


def test_record_acceptance_without_version_raises_and_stores_nothing(user):
    services.publish("terms", "t1", material=True)
    with pytest.raises(NoPublishedVersion) as exc:
        services.record_acceptance(user, ["terms", "privacy"])
    assert exc.value.kind == "privacy"
    assert not LegalAcceptance.objects.exists()


def test_pending_for_anonymous_is_empty():
    from django.contrib.auth.models import AnonymousUser

    services.publish("terms", "t1", material=True)
    assert services.pending_acceptances(AnonymousUser()) == []


def test_pending_never_accepted(user):
    terms = services.publish("terms", "t1", material=True)
    assert services.pending_acceptances(user) == [terms]
    assert services.pending(user)[0].accepted_version is None


def test_pending_after_material_change(user):
    services.publish("terms", "t1", material=True)
    services.publish("privacy", "p1", material=True)
    services.record_acceptance(user, ["terms", "privacy"])
    assert services.pending_acceptances(user) == []
    v2 = services.publish("terms", "t2", material=True)
    assert services.pending_acceptances(user) == [v2]
    assert services.pending(user)[0].accepted_version == 1


def test_non_material_change_is_not_pending(user):
    services.publish("terms", "t1", material=True)
    services.record_acceptance(user, ["terms"])
    services.publish("terms", "t2 literówka", material=False)
    assert services.pending_acceptances(user) == []


def test_non_material_after_material_asks_for_newest(user):
    services.publish("terms", "t1", material=True)
    services.record_acceptance(user, ["terms"])
    services.publish("terms", "t2", material=True)
    v3 = services.publish("terms", "t3", material=False)
    assert services.pending_acceptances(user) == [v3]
    services.record_acceptance(user, ["terms"])
    assert services.pending_acceptances(user) == []


def test_cookies_never_pending(user):
    services.publish("cookies", "c1", material=True)
    assert services.pending_acceptances(user) == []


def test_accept_pending_requires_what_was_shown(user):
    v1 = services.publish("terms", "t1", material=True)
    assert services.accept_pending(user, []) is False
    v2 = services.publish("terms", "t2", material=True)  # published after the page was shown
    assert services.accept_pending(user, [v1.pk]) is False
    assert not LegalAcceptance.objects.exists()
    assert services.accept_pending(user, [v2.pk]) is True
    assert LegalAcceptance.objects.get(user=user).document == v2
    assert services.accept_pending(user, [v2.pk]) is False  # nothing pending any more


def test_seed_placeholders_idempotent():
    assert services.seed_placeholders() == 3
    assert services.seed_placeholders() == 0
    assert LegalDocument.objects.count() == 3
    for kind in LegalDocument.Kind.values:
        document = services.current(kind)
        assert document.body.startswith(services.PLACEHOLDER_PREFIX)
        assert document.version == 1


def test_seed_placeholders_keep_real_versions():
    real = services.publish("terms", "Prawdziwy regulamin", material=True)
    services.seed_placeholders()
    assert services.current("terms") == real


def test_seed_command_adds_placeholders_once(capsys):
    call_command("seed")
    assert "3 placeholder legal documents" in capsys.readouterr().out
    call_command("seed")
    assert "0 placeholder legal documents" in capsys.readouterr().out
    assert LegalDocument.objects.count() == 3


def test_str_representations(user):
    document = services.publish("terms", "t1", material=True)
    row = services.record_acceptance(user, ["terms"])[0]
    assert str(document) == "Regulamin v1"
    assert str(row).startswith("Regulamin v1 @ ")
