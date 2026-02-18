from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scoring", "0011_fielding_runs"),
    ]

    operations = [
        migrations.AddField(
            model_name="ballspatialoutcome",
            name="structured_region_id",
            field=models.CharField(blank=True, help_text="Structured field engine region id", max_length=20, null=True),
        ),
        migrations.AddField(
            model_name="ballspatialoutcome",
            name="structured_slice_index",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="ballspatialoutcome",
            name="structured_band_index",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="ballspatialoutcome",
            name="structured_position",
            field=models.CharField(blank=True, help_text="Resolved fielding position from structured engine", max_length=50, null=True),
        ),
    ]
