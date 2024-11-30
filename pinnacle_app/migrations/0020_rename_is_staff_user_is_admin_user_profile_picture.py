# Generated by Django 5.0.7 on 2024-11-24 06:28

import pinnacle_app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pinnacle_app', '0019_alter_documentupload_file'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='is_staff',
            new_name='is_admin',
        ),
        migrations.AddField(
            model_name='user',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to=pinnacle_app.models.profile_pic_upload_path),
        ),
    ]
