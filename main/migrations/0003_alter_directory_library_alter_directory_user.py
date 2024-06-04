# Generated by Django 5.0.6 on 2024-06-02 11:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_webprovider_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directory',
            name='library',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='directories', to='main.library'),
        ),
        migrations.AlterField(
            model_name='directory',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='directories', to=settings.AUTH_USER_MODEL),
        ),
    ]
