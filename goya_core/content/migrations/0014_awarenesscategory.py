# Generated by Django 4.0.4 on 2022-05-24 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0013_advisory_advisory_takeway'),
    ]

    operations = [
        migrations.CreateModel(
            name='AwarenessCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('awareness_category', models.CharField(max_length=200)),
                ('awareness_category_id', models.IntegerField(unique=True)),
            ],
        ),
    ]
