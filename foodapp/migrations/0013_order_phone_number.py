# Generated by Django 5.1.1 on 2024-12-30 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodapp', '0012_address_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
