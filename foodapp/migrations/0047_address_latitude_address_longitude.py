# Generated by Django 5.1.1 on 2025-01-23 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodapp', '0046_delete_orderitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='address',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
