# Generated by Django 5.0.1 on 2024-01-27 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0012_alter_apartment_address_alter_apartment_latitude_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apartment',
            name='address',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]