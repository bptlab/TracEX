# Generated by Django 4.2.7 on 2024-02-27 10:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("extraction", "0003_alter_patientjourney_managers_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="patientjourney",
            name="patient_journey",
            field=models.FileField(upload_to="patient_journeys/"),
        ),
    ]
