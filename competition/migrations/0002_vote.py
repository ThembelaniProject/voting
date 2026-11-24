# Phase 3: persist public votes and enforce one vote per session per round.
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("competition", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="Vote",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("voter_hash", models.CharField(max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("competition", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="votes", to="competition.competition")),
                ("dj", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="votes", to="competition.dj")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddConstraint(
            model_name="vote",
            constraint=models.UniqueConstraint(fields=("competition", "voter_hash"), name="one_vote_per_session_per_competition"),
        ),
        migrations.AddIndex(
            model_name="vote",
            index=models.Index(fields=["competition", "dj"], name="vote_comp_dj_idx"),
        ),
    ]
