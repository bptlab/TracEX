# Generated by Django 4.2.7 on 2024-04-19 16:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("extraction", "0018_prompt_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="prompt",
            name="category",
            field=models.CharField(default="zero-shot", max_length=100),
        ),
        migrations.AlterField(
            model_name="prompt",
            name="name",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AlterField(
            model_name="prompt",
            name="text",
            field=models.JSONField(),
        ),
    ]