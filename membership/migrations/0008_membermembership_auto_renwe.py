# Generated by Django 4.0.4 on 2025-05-04 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0007_alter_attendance_entrance_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='membermembership',
            name='auto_renwe',
            field=models.BooleanField(default=True),
        ),
    ]
