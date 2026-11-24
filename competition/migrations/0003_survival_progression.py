from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("competition", "0002_vote")]

    operations = [
        migrations.AddField(
            model_name="dj",
            name="is_eliminated",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="dj",
            name="is_champion",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="competition",
            name="next_challenger",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                related_name="scheduled_challenges", to="competition.dj",
                help_text="Choose the fresh DJ who will challenge the winner next week.",
            ),
        ),
        migrations.AddField(
            model_name="competition",
            name="is_final",
            field=models.BooleanField(
                default=False, help_text="Tick this only when this is the final round of the season."
            ),
        ),
        migrations.AddField(
            model_name="competition",
            name="winner",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                related_name="competition_wins", to="competition.dj",
            ),
        ),
        migrations.AddField(
            model_name="competition",
            name="eliminated_dj",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                related_name="competition_eliminations", to="competition.dj",
            ),
        ),
    ]
