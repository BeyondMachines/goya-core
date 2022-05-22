# Generated by Django 4.0.4 on 2022-05-22 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_alter_slackinstalledworkspace_workspace_advisory_shout_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slackinstalledworkspace',
            name='workspace_advisory_shout',
            field=models.CharField(choices=[('<!channel>', 'CHANNEL'), ('<!here>', 'PRESENT'), ('All', 'QUIET')], default='CHANNEL', max_length=10),
        ),
        migrations.AlterField(
            model_name='slackinstalledworkspace',
            name='workspace_awareness_shout',
            field=models.CharField(choices=[('<!channel>', 'CHANNEL'), ('<!here>', 'PRESENT'), ('All', 'QUIET')], default='PRESENT', max_length=10),
        ),
        migrations.AlterField(
            model_name='slackinstalledworkspace',
            name='workspace_event_shout',
            field=models.CharField(choices=[('<!channel>', 'CHANNEL'), ('<!here>', 'PRESENT'), ('All', 'QUIET')], default='QUIET', max_length=10),
        ),
    ]