# Generated by Django 4.0.4 on 2022-05-02 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0002_alter_advisory_advisory_details'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advisory',
            name='advisory_published_date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
