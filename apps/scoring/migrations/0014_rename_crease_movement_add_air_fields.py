from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scoring", "0013_rename_scoring_bal_action_0c52c6_idx_scoring_bal_action_c79d75_idx_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="ballanalytics",
            old_name="crease_movement",
            new_name="foot_movement",
        ),
        migrations.AlterField(
            model_name="ballanalytics",
            name="foot_movement",
            field=models.CharField(
                blank=True,
                help_text="Batter foot movement",
                max_length=30,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="ballanalytics",
            name="air_movement",
            field=models.CharField(
                blank=True,
                help_text="Ball air movement profile",
                max_length=30,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="ballanalytics",
            name="control",
            field=models.CharField(
                blank=True,
                help_text="Whether the air movement was controlled",
                max_length=30,
                null=True,
            ),
        ),
    ]
