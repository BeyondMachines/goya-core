# Generated by Django 4.0.4 on 2022-07-27 11:01

import ckeditor.fields
import datetime
from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0005_auto_20220424_2025'),
        ('content', '0020_alter_awarenessmessage_awareness_message_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScrapedEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_title', models.TextField()),
                ('event_details', ckeditor.fields.RichTextField(blank=True, null=True)),
                ('event_url', models.SlugField(blank=True, max_length=220, null=True)),
                ('event_source_url', models.URLField(default='https://localhost', max_length=400)),
                ('event_published_time', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('event_additional_data', models.URLField(blank=True, max_length=500, null=True)),
                ('event_source', models.CharField(max_length=50)),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
        ),
    ]
