# Generated by Django 5.0.7 on 2024-11-24 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pinnacle_app', '0021_user_is_superadmin'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='admin_name',
            field=models.CharField(default='Admin', max_length=255),
        ),
    ]
