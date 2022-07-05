# Generated by Django 2.2 on 2022-07-02 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50, verbose_name='用户名')),
                ('phone_number', models.CharField(max_length=14, unique=True, verbose_name='手机号')),
                ('is_delete', models.BooleanField()),
            ],
            options={
                'verbose_name': '用户',
                'verbose_name_plural': '用户',
                'db_table': 'user',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.CharField(max_length=20, verbose_name='性别')),
                ('birthday', models.DateField(blank=True, null=True, verbose_name='生日')),
                ('city', models.CharField(blank=True, max_length=50, null=True, verbose_name='城市')),
                ('address', models.CharField(blank=True, max_length=215, null=True, verbose_name='地址')),
                ('ip', models.GenericIPAddressField(blank=True, null=True, verbose_name='注册时ip地址')),
            ],
            options={
                'verbose_name': '个人信息',
                'verbose_name_plural': '个人信息',
                'db_table': 'user_profile',
                'managed': False,
            },
        ),
    ]
