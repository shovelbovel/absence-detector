# Generated by Django 4.2.20 on 2025-05-21 11:10

from django.db import migrations, models
import presence.models


class Migration(migrations.Migration):

    dependencies = [
        ("presence", "0010_add_created_updated_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="absencereport",
            name="justification_file",
            field=models.FileField(
                blank=True,
                help_text="Téléversez un fichier PDF justifiant votre absence",
                null=True,
                upload_to=presence.models.user_justification_path,
                verbose_name="Justificatif (PDF)",
            ),
        ),
    ]
