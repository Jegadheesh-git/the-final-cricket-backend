from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("coredata", "0003_stadium_umpire_player_team_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="stadium",
            name="floodlights",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
