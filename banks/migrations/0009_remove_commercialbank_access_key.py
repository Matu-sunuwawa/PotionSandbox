# Generated by Django 5.1.8 on 2025-05-23 21:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("banks", "0008_remove_accesskey_raw_secret_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="commercialbank",
            name="access_key",
        ),
    ]
