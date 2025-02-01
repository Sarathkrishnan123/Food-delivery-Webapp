# Generated by Django 5.1.1 on 2025-01-30 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodapp', '0057_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('preparing', 'Preparing'), ('prepared', 'Prepared'), ('cancelled', 'Cancelled')], default='pending', max_length=50),
        ),
    ]
