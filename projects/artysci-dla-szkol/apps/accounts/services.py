"""Account services. Seeding lives here until artists/institutions get their own models."""

from django.contrib.auth import get_user_model

SEED_DOMAIN = "example.invalid"
ARTIST_COUNT = 10
INSTITUTION_COUNT = 5


def seed_users() -> dict[str, int]:
    """Create synthetic artist and institution users (idempotent, no real data: D57).

    Every address is on the reserved ``example.invalid`` domain and the accounts have no usable
    password. Returns how many rows were created by this call.
    """
    user_model = get_user_model()
    created = {"artists": 0, "institutions": 0}
    specs = [
        ("artists", "artysta", "Artysta Testowy", ARTIST_COUNT),
        ("institutions", "szkola", "Szkoła Testowa", INSTITUTION_COUNT),
    ]
    for key, prefix, name, count in specs:
        for number in range(1, count + 1):
            user, was_created = user_model.objects.get_or_create(
                email=f"{prefix}{number:02d}@{SEED_DOMAIN}",
                defaults={"full_name": f"{name} {number:02d}"},
            )
            if was_created:
                user.set_unusable_password()
                user.save(update_fields=["password"])
                created[key] += 1
    return created
