# Generated by Django 4.1 on 2024-04-08 05:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_remove_user_custom_id_directory_is_deleted_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directory',
            name='concept',
            field=models.CharField(max_length=2000, null=True),
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice_num', models.IntegerField()),
                ('choice_content', models.CharField(max_length=500)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choice', to='main.question')),
            ],
        ),
    ]
