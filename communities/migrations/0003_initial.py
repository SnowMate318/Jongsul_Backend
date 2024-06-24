# Generated by Django 5.0.6 on 2024-06-21 15:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('communities', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='shared',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shareds', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='sharedtag',
            name='shared',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shared_tags', to='communities.shared'),
        ),
        migrations.AddConstraint(
            model_name='sharedtag',
            constraint=models.UniqueConstraint(fields=('shared', 'name'), name='unique shared tag name'),
        ),
    ]