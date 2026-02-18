from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scoring", "0002_ball_completed_runs"),
    ]

    operations = [
        migrations.AddField(
            model_name="ball",
            name="is_quick_running",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="ball",
            name="is_free_hit",
            field=models.BooleanField(default=False),
        ),
    ]
