# Generated by Django 4.2.7 on 2024-03-19 10:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("extraction", "0014_remove_cohort_trace"),
    ]

    operations = [
        migrations.AddField(
            model_name="trace",
            name="cohort",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="trace",
                to="extraction.cohort",
            ),
        ),
    ]
