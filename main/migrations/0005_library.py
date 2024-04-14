# Generated by Django 4.1 on 2024-03-24 14:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_shared_is_activated_shared_is_deleted_sharedtag'),
    ]

    operations = [
        migrations.CreateModel(
            name='Library',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30, null=True)),
                ('library_last_access', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='library', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'library',
                'unique_together': {('user', 'title')},
            },
        ),
    ]
