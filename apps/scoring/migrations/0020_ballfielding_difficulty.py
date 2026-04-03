from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scoring", "0019_ballspatialoutcome_batter_stump_zone"),
    ]

    operations = [
        migrations.AddField(
            model_name="ballfielding",
            name="difficulty",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
