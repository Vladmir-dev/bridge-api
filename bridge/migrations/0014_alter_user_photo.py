# Generated by Django 4.1.3 on 2023-04-15 08:42

import bridge.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bridge', '0013_user_interests_user_occupation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='photo',
            field=models.ImageField(blank=True, default='media/user/photo/default/default.jpeg', null=True, upload_to=bridge.models.get_user_photo_file_path),
        ),
    ]
