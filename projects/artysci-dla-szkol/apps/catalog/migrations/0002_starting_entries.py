"""Starting entries of the closed dictionaries (US-4.2, US-4.6). Idempotent; never overwrites."""

from django.db import migrations

STARTING = {
    "topic": [
        ("uzależnienia", "uzaleznienia"),
        ("hejt", "hejt"),
        ("bezpieczeństwo", "bezpieczenstwo"),
        ("emocje", "emocje"),
        ("ekologia", "ekologia"),
    ],
    "form": [("spektakl", "spektakl"), ("warsztaty", "warsztaty"), ("pokaz", "pokaz")],
}


def add_entries(apps, schema_editor):
    Entry = apps.get_model("catalog", "DictionaryEntry")
    for kind, entries in STARTING.items():
        for position, (name, slug) in enumerate(entries):
            Entry.objects.get_or_create(
                kind=kind, slug=slug, defaults={"name": name, "position": position}
            )


class Migration(migrations.Migration):
    dependencies = [("catalog", "0001_dictionaries")]

    # Reverse keeps the rows: removing a dictionary the admin may have edited is not ours to do.
    operations = [migrations.RunPython(add_entries, migrations.RunPython.noop)]
