# Generated by Django 4.1.13 on 2024-09-15 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0007_photo_editor_photo_photos_editor_e6fbaf_idx'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
    ]
