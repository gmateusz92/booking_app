# Generated by Django 5.0.2 on 2024-02-21 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reservations", "0023_delete_comment"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="rating",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
