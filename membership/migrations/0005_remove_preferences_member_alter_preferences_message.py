# Generated by Django 5.0.3 on 2024-04-20 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0004_rename_user_preferences_member'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='preferences',
            name='member',
        ),
        migrations.AlterField(
            model_name='preferences',
            name='message',
            field=models.TextField(),
        ),
    ]