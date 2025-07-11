# Generated by Django 4.2.20 on 2025-05-04 22:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("presence", "0002_employee_role"),
    ]

    operations = [
        migrations.CreateModel(
            name="Presence",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("present", "Présent"),
                            ("pause", "Pause"),
                            ("meeting", "Réunion"),
                            ("absent", "Absent"),
                            ("inactive", "Inactif"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="presence.employee",
                    ),
                ),
            ],
        ),
    ]
