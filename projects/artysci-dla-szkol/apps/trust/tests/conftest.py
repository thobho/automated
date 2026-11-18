import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(
        email="osoba@example.invalid", password="x-Pass-123"
    )


@pytest.fixture
def staff(db):
    return get_user_model().objects.create_superuser(
        email="admin@example.invalid", password="x-Pass-123"
    )
