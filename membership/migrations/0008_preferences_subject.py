# Generated by Django 5.0.3 on 2024-04-20 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0007_alter_preferences_messagetype'),
    ]

    operations = [
        migrations.AddField(
            model_name='preferences',
            name='subject',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]
