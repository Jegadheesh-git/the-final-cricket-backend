from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scoring", "0018_ballwicket_decision_given_by_umpire"),
    ]

    operations = [
        migrations.AddField(
            model_name="ballspatialoutcome",
            name="batter_stump_zone",
            field=models.CharField(
                blank=True,
                help_text="Batter stump zone selected from matrix",
                max_length=20,
                null=True,
            ),
        ),
    ]
