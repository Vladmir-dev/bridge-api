# Generated by Django 4.1.3 on 2023-01-25 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bridge', '0009_likes_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='anonymous',
            field=models.BooleanField(default=False),
        ),
    ]
