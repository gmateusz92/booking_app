# Generated by Django 5.0.1 on 2024-01-27 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reservations", "0010_apartment_latitude"),
    ]

    operations = [
        migrations.AddField(
            model_name="apartment",
            name="address",
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
