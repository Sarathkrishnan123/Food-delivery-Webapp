# Generated by Django 5.1.1 on 2025-01-17 05:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodapp', '0037_reward'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='has_issue',
            field=models.BooleanField(default=False),
        ),
    ]
