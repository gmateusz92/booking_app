# Generated by Django 5.0.1 on 2024-02-11 17:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("reservations", "0018_booking_notification"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="message",
            name="apartment",
        ),
    ]
