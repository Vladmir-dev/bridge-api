# Generated by Django 4.1.3 on 2023-03-09 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bridge', '0007_chatmessage_document_chatmessage_photo_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='token',
            field=models.CharField(blank=True, max_length=550, null=True, unique=True),
        ),
    ]
