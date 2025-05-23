# Generated by Django 5.1.8 on 2025-04-23 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("banks", "0002_alter_commercialbank_bank_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="commercialbank",
            name="bank_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Commercial", "Commercial Bank of Ethiopia"),
                    ("Awash", "Awash Bank"),
                    ("Dashen", "Dashen Bank"),
                    ("Mela", "Mela Wallet"),
                ],
                max_length=20,
                null=True,
            ),
        ),
    ]
