from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0004_search_terms"),
    ]

    operations = [
        # Existing rows get 0 until `rebuild_catalog` (run after migrate) writes the real value.
        migrations.AddField(
            model_name="catalogentry",
            name="completeness_bucket",
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
