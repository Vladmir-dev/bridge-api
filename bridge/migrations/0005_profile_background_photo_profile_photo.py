# Generated by Django 4.1.3 on 2022-12-06 07:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bridge', '0004_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='background_photo',
            field=models.ImageField(blank=True, null=True, upload_to='media'),
        ),
        migrations.AddField(
            model_name='profile',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='media'),
        ),
    ]