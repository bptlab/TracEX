# Generated by Django 4.2.7 on 2024-03-19 10:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("extraction", "0012_alter_cohort_trace"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cohort",
            name="trace",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="cohort",
                to="extraction.trace",
            ),
        ),
    ]
