from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("competitions", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="tournament",
            name="ci_id",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="tournament",
            name="established_year",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="tournament",
            name="end_year",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="competition",
            name="ci_id",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="competition",
            name="established_year",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="competition",
            name="end_year",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="series",
            name="ci_id",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="series",
            name="established_year",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="series",
            name="end_year",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
