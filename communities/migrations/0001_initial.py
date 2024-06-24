# Generated by Django 5.0.6 on 2024-06-21 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Shared',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shared_title', models.CharField(max_length=30)),
                ('shared_content', models.CharField(max_length=500)),
                ('shared_upload_datetime', models.DateTimeField(auto_now_add=True)),
                ('is_activated', models.BooleanField(default=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('download_count', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'shared',
            },
        ),
        migrations.CreateModel(
            name='SharedTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'shared_tag',
            },
        ),
    ]