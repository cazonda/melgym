# Generated by Django 5.0.3 on 2024-04-20 16:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0002_remove_membermembership_training_objective_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Preferences',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('create_user', models.CharField(max_length=255)),
                ('update_date', models.DateTimeField(auto_now_add=True)),
                ('update_user', models.CharField(max_length=255)),
                ('active', models.BooleanField(default=True)),
                ('message', models.CharField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='membership.membershiptype')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]