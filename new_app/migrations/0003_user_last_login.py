# Generated by Django 2.2.2 on 2021-09-05 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('new_app', '0002_user_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
    ]
