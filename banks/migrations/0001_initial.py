# Generated by Django 5.1.8 on 2025-04-21 13:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CommercialBank",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("license_number", models.CharField(max_length=20, unique=True)),
                ("swift_code", models.CharField(max_length=11, unique=True)),
                ("established_date", models.DateField()),
                (
                    "reserve_balance",
                    models.DecimalField(decimal_places=2, default=0, max_digits=20),
                ),
                (
                    "bank_type",
                    models.CharField(
                        choices=[
                            ("CBE", "Commercial Bank of Ethiopia"),
                            ("AWASH", "Awash Bank"),
                            ("DASHEN", "Dashen Bank"),
                            ("MELA", "Mela Wallet"),
                        ],
                        max_length=20,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="NBECentralBank",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "total_reserves",
                    models.DecimalField(decimal_places=2, default=0, max_digits=20),
                ),
                (
                    "base_interest_rate",
                    models.DecimalField(decimal_places=2, max_digits=5),
                ),
                ("last_policy_update", models.DateField(auto_now=True)),
            ],
            options={
                "verbose_name": "National Bank of Ethiopia",
            },
        ),
        migrations.CreateModel(
            name="Branch",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("branch_code", models.CharField(max_length=10, unique=True)),
                ("location", models.CharField(max_length=200)),
                ("contact_number", models.CharField(max_length=20)),
                ("opened_date", models.DateField(auto_now_add=True)),
                (
                    "commercial_bank",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="branches",
                        to="banks.commercialbank",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="commercialbank",
            name="nbe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="commercial_banks",
                to="banks.nbecentralbank",
            ),
        ),
    ]
