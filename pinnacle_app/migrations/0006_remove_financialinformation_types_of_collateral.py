# Generated by Django 5.0.7 on 2024-10-01 21:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pinnacle_app', '0005_alter_basiccontactinformation_phone_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='financialinformation',
            name='types_of_collateral',
        ),
    ]
