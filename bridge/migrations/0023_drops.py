# Generated by Django 4.1.3 on 2023-05-02 05:09

import bridge.models
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bridge', '0022_wallet_password'),
    ]

    operations = [
        migrations.CreateModel(
            name='Drops',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=1000)),
                ('photo', models.ImageField(blank=True, null=True, upload_to=bridge.models.get_user_photo_file_path)),
                ('video', models.FileField(null=True, upload_to='videos', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])])),
                ('document', models.FileField(null=True, upload_to='documents')),
                ('receipients', models.ManyToManyField(blank=True, related_name='received_posts', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='creater', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
