# Generated by Django 4.1.3 on 2023-04-19 11:36

from django.db import migrations, models
import django_mysql.models


class Migration(migrations.Migration):

    dependencies = [
        ('bridge', '0017_alter_user_interests'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='interests',
            field=django_mysql.models.ListCharField(models.CharField(max_length=100), blank=True, max_length=101000, null=True, size=1000),
        ),
    ]
