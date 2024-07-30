# Generated by Django 4.1.13 on 2024-07-01 22:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0003_photo_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]