from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("matches", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="match",
            name="ci_id",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="match",
            name="drs_count",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="match",
            name="floodlights_count",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
