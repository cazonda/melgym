# Generated by Django 4.0.4 on 2022-06-18 06:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0009_members_gym_owner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='Members',
            name='password',
        ),
    ]