# Generated by Django 5.0.1 on 2024-01-20 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reservations", "0002_booking_home_delete_room_booking_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="home",
            name="description",
            field=models.CharField(max_length=1000, null=True),
        ),
    ]
