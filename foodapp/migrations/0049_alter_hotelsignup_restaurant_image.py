# Generated by Django 5.1.1 on 2025-01-24 06:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodapp', '0048_hotelsignup_latitude_hotelsignup_longitude'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hotelsignup',
            name='restaurant_image',
            field=models.ImageField(blank=True, null=True, upload_to='hotel_images/'),
        ),
    ]
