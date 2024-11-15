# Generated by Django 5.0.1 on 2024-01-27 18:58

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reservations", "0011_apartment_address"),
    ]

    operations = [
        migrations.AlterField(
            model_name="apartment",
            name="address",
            field=models.CharField(default=django.utils.timezone.now, max_length=250),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="apartment",
            name="latitude",
            field=models.FloatField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name="apartment",
            name="longitude",
            field=models.FloatField(blank=True, max_length=20, null=True),
        ),
    ]
