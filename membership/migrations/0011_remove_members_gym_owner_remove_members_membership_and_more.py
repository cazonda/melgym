# Generated by Django 4.0.4 on 2023-08-29 17:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0010_remove_members_password'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='Members',
            name='gym_owner',
        ),
        migrations.RemoveField(
            model_name='Members',
            name='membership',
        ),
        migrations.RemoveField(
            model_name='Members',
            name='validity',
        ),
        migrations.RemoveField(
            model_name='Membership',
            name='user',
        ),
        migrations.RemoveField(
            model_name='user',
            name='gender',
        ),
        migrations.RemoveField(
            model_name='user',
            name='gym_location',
        ),
        migrations.RemoveField(
            model_name='user',
            name='gym_name',
        ),
        migrations.RemoveField(
            model_name='user',
            name='gym_phone',
        ),
        migrations.CreateModel(
            name='MemberMemberships',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purchase_date', models.DateField()),
                ('expiry_date', models.DateField()),
                ('status', models.CharField(max_length=2)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='membership.Members')),
                ('membership', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='membership.Membership')),
            ],
        ),
    ]
