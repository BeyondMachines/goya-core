# Generated by Django 4.0.3 on 2022-04-17 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SlackInstalledWorkspace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('workspace_name', models.CharField(max_length=100)),
                ('enterprise_id', models.CharField(max_length=50)),
                ('is_enterprise_install', models.BooleanField(blank=True, null=True)),
                ('workspace_id', models.CharField(max_length=50)),
                ('admin_user_id', models.CharField(max_length=50)),
                ('admin_user_name', models.CharField(max_length=200)),
                ('admin_user_email', models.EmailField(blank=True, max_length=254)),
                ('workspace_url', models.SlugField(blank=True, max_length=200, null=True)),
            ],
        ),
    ]
