# Generated by Django 4.2.6 on 2023-10-22 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("qa", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="answer",
            field=models.TextField(blank=True, null=True),
        ),
    ]
