# Generated by Django 5.0.7 on 2024-10-24 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pinnacle_app', '0015_adminnotification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='financialinformation',
            name='annual_revenue',
            field=models.DecimalField(decimal_places=2, max_digits=20),
        ),
        migrations.AlterField(
            model_name='financialinformation',
            name='net_profit',
            field=models.DecimalField(decimal_places=2, max_digits=20),
        ),
        migrations.AlterField(
            model_name='financialinformation',
            name='outstanding_debt',
            field=models.DecimalField(decimal_places=2, max_digits=20),
        ),
        migrations.AlterField(
            model_name='fundingrequirements',
            name='amount_required',
            field=models.DecimalField(decimal_places=2, max_digits=20),
        ),
    ]
