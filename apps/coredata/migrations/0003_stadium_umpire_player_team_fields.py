from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("coredata", "0002_player_ci_player_id_player_jersey_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="stadium",
            name="ci_id",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="stadium",
            name="specific_area",
            field=models.CharField(blank=True, default="", max_length=150),
        ),
        migrations.AddField(
            model_name="stadium",
            name="established_year",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="stadium",
            name="floodlights",
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="stadium",
            name="time_zone",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AddField(
            model_name="stadium",
            name="home_teams",
            field=models.ManyToManyField(blank=True, related_name="home_grounds", to="coredata.team"),
        ),
        migrations.AddField(
            model_name="umpire",
            name="last_name",
            field=models.CharField(blank=True, default="", max_length=150),
        ),
        migrations.AddField(
            model_name="umpire",
            name="short_name",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AddField(
            model_name="umpire",
            name="ci_id",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="umpire",
            name="date_of_birth",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="player",
            name="debut_year_intl",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="player",
            name="retirement_year_intl",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="player",
            name="bowling_types",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="team",
            name="ci_id",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="team",
            name="team_category",
            field=models.CharField(blank=True, choices=[("MEN", "Men"), ("WOMEN", "Women"), ("U19", "Under 19"), ("U16", "Under 16"), ("MIXED", "Mixed")], max_length=10, null=True),
        ),
        migrations.AddField(
            model_name="team",
            name="established_year",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="team",
            name="master_squad",
            field=models.ManyToManyField(blank=True, related_name="master_teams", to="coredata.player"),
        ),
    ]
