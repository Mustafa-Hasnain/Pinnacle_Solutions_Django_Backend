# Generated by Django 5.0.7 on 2024-10-02 20:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pinnacle_app', '0008_alter_applicationstatus_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basiccontactinformation',
            name='application',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='basiccontactinformation', to='pinnacle_app.application'),
        ),
    ]
