# Generated by Django 5.0.1 on 2024-02-20 18:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0022_booking_comment'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Comment',
        ),
    ]