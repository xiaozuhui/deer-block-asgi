# Generated by Django 2.2 on 2022-07-09 15:32

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='message_content',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True, verbose_name='消息内容'),
        ),
        migrations.AlterField(
            model_name='messagegroup',
            name='group_name',
            field=models.CharField(max_length=225, unique=True, verbose_name='组名称'),
        ),
        migrations.AlterField(
            model_name='messagegroup',
            name='users',
            field=models.ManyToManyField(null=True, to='users.User'),
        ),
    ]