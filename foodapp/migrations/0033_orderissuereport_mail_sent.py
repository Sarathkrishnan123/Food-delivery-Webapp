# Generated by Django 5.1.1 on 2025-01-15 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodapp', '0032_orderissuereport_is_resolved_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderissuereport',
            name='mail_sent',
            field=models.BooleanField(default=False),
        ),
    ]
