from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("coredata", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="player",
            name="ci_player_id",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="player",
            name="jersey_number",
            field=models.CharField(blank=True, default="", max_length=20),
        ),
    ]
