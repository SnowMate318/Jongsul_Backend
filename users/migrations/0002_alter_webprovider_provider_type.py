# Generated by Django 5.0.6 on 2024-06-23 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webprovider',
            name='provider_type',
            field=models.CharField(max_length=30),
        ),
    ]