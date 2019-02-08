# Generated by Django 2.1.5 on 2019-02-02 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('nickname', models.TextField()),
                ('content', models.TextField()),
                ('likes', models.IntegerField(default=0)),
            ],
        ),
    ]
