# Generated by Django 4.0.4 on 2022-06-17 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Membership', '0006_alter_user_date_of_birth'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='membership_duration',
            field=models.CharField(max_length=20),
        ),
    ]
