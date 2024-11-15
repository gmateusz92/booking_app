# Generated by Django 5.0.1 on 2024-02-18 18:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0020_comment_delete_booking_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='apartment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='reservations.apartment'),
        ),
    ]