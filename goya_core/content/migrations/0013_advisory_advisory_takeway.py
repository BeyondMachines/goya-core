# Generated by Django 4.0.4 on 2022-05-22 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0012_alter_advisory_advisory_url_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='advisory',
            name='advisory_takeway',
            field=models.TextField(default=' '),
        ),
    ]
