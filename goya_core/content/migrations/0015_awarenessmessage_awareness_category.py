# Generated by Django 4.0.4 on 2022-05-24 09:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0014_awarenesscategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='awarenessmessage',
            name='awareness_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='content.awarenesscategory'),
        ),
    ]