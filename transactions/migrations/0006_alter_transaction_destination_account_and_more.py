# Generated by Django 5.1.8 on 2025-05-23 22:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_bankaccount_webhook_url"),
        ("transactions", "0005_transaction_remarks"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transaction",
            name="destination_account",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="received_transactions",
                to="accounts.bankaccount",
            ),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="source_account",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sent_transactions",
                to="accounts.bankaccount",
            ),
        ),
    ]
