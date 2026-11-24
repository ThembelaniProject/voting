# Generated for the Pheli FM 95.0 Phase 2 competition manager.
import django.utils.timezone
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="DJ",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("bio", models.CharField(blank=True, max_length=240)),
                ("photo_url", models.URLField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["name"], "verbose_name": "DJ", "verbose_name_plural": "DJs"},
        ),
        migrations.CreateModel(
            name="Competition",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("week_number", models.PositiveIntegerField(unique=True)),
                ("title", models.CharField(default="Pheli FM DJ Survival Challenge", max_length=140)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("open", "Voting open"), ("closed", "Voting closed"), ("completed", "Completed")], default="draft", max_length=12)),
                ("starts_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("ends_at", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("dj_one", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="first_rounds", to="competition.dj")),
                ("dj_two", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="second_rounds", to="competition.dj")),
            ],
            options={"ordering": ["-week_number"], "verbose_name": "Weekly competition"},
        ),
    ]
