# Generated by Django 5.1.1 on 2025-01-08 05:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodapp', '0021_orderissuereport'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderissuereport',
            name='is_sent_to_restaurant',
            field=models.BooleanField(default=False),
        ),
    ]
