# Generated by Django 2.2 on 2022-08-01 18:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0003_auto_20220724_2149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='to_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='to_user', to='users.User'),
        ),
    ]
