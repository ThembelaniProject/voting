from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("competition", "0003_survival_progression"),
    ]

    operations = [
        migrations.AddField(
            model_name="dj",
            name="photo",
            field=models.ImageField(blank=True, upload_to="dj_photos/"),
        ),
    ]
