# Generated by Django 5.0.1 on 2024-01-19 18:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_user_role"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="role",
        ),
    ]
