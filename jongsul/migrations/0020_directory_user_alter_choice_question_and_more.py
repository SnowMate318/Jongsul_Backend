# Generated by Django 4.1 on 2024-05-12 13:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_alter_choice_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='directory',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='directory', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='choice',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='main.question'),
        ),
        migrations.AlterField(
            model_name='directory',
            name='library',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='directory', to='main.library'),
        ),
        migrations.AlterField(
            model_name='question',
            name='directory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='main.directory'),
        ),
        migrations.AlterField(
            model_name='shared',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shareds', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='sharedtag',
            name='shared',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shared_tags', to='main.shared'),
        ),
    ]
