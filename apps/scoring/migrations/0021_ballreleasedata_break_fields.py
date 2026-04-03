from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scoring", "0020_ballfielding_difficulty"),
    ]

    operations = [
        migrations.AddField(
            model_name="ballreleasedata",
            name="break_type",
            field=models.CharField(
                blank=True,
                help_text="Type of break following this ball",
                max_length=50,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="ballreleasedata",
            name="is_break",
            field=models.BooleanField(
                default=False,
                help_text="Whether a break follows this ball",
            ),
        ),
    ]
