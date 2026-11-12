import pytest
from django.contrib.auth import authenticate, get_user_model

pytestmark = pytest.mark.django_db

User = get_user_model()


def test_auth_user_model_is_custom():
    assert User._meta.label == "accounts.User"
    assert User.USERNAME_FIELD == "email"
    assert not hasattr(User, "username")


def test_create_user_by_email():
    user = User.objects.create_user(email="  Anna.Nowak@Example.PL ", password="s3cret-pass")
    assert user.email == "anna.nowak@example.pl"
    assert user.check_password("s3cret-pass")
    assert user.is_active
    assert not user.is_staff
    assert not user.is_superuser
    assert str(user) == "anna.nowak@example.pl"


def test_create_user_without_password_is_unusable():
    user = User.objects.create_user(email="a@example.pl")
    assert not user.has_usable_password()


def test_create_user_requires_email():
    with pytest.raises(ValueError, match="email"):
        User.objects.create_user(email="", password="x")


def test_create_superuser_by_email():
    admin = User.objects.create_superuser(email="Admin@Example.pl", password="s3cret-pass")
    assert admin.email == "admin@example.pl"
    assert admin.is_staff
    assert admin.is_superuser


@pytest.mark.parametrize("flag", ["is_staff", "is_superuser"])
def test_create_superuser_rejects_false_flags(flag):
    with pytest.raises(ValueError, match=flag):
        User.objects.create_superuser(email="x@example.pl", password="p", **{flag: False})


def test_email_is_unique_case_insensitive():
    User.objects.create_user(email="dup@example.pl", password="p")
    from django.db import IntegrityError, transaction

    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.create_user(email="DUP@example.pl", password="p")


def test_login_with_any_email_case():
    User.objects.create_user(email="login@example.pl", password="s3cret-pass")
    assert authenticate(username="LOGIN@Example.pl", password="s3cret-pass") is not None
    assert authenticate(username="login@example.pl", password="wrong") is None


def test_clean_normalizes_email():
    user = User(email=" Mixed@Case.PL ")
    user.clean()
    assert user.email == "mixed@case.pl"
