# Generated by Django 5.0.7 on 2024-10-08 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pinnacle_app', '0013_application_funding_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='commission',
            name='comission_paid',
            field=models.BooleanField(default=False),
        ),
    ]
