# Generated by Django 2.1.5 on 2019-02-08 09:15

import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import re


class Migration(migrations.Migration):

    dependencies = [
        ('gugugu', '0003_merge_20190202_2157'),
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(max_length=255, verbose_name='Session Key')),
                ('name', models.CharField(max_length=32, null=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator])),
                ('date_updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_sent', models.DateTimeField(auto_now_add=True, verbose_name='Date Sent')),
                ('text', models.TextField()),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gugugu.Member')),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='Date Created')),
                ('date_polled', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date Last Polled')),
                ('date_updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date Updated')),
                ('date_deactivated', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Date Deactivated')),
                ('active', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=255, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')])),
                ('deactivate_delta_sec', models.IntegerField(default=43200)),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gugugu.Room'),
        ),
        migrations.AddField(
            model_name='member',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gugugu.Room'),
        ),
        migrations.AlterUniqueTogether(
            name='member',
            unique_together={('room', 'name')},
        ),
    ]