import string
from datetime import date, datetime
from slugify import slugify
from django.db import models
import random

# Create your models here.

MESSAGE_CHOICES = [
    ('FR', 'Freshman'),
    ('SO', 'Sophomore'),
    ('JR', 'Junior'),
    ('SR', 'Senior'),
    ('GR', 'Graduate'),
]

class SlackInstalledWorkspace(models.Model):  # this is a generic challenge model where all challenges are picked up from.
    '''
    The SlackInstalledWorkspace model contains the register of workspaces where the App is successfully installed.
    '''
    MESSAGE_CHOICES = [
    ('<!channel>', 'CHANNEL'),
    ('<!here>', 'PRESENT'),
    ('All', 'QUIET'),
    ]
    workspace_name = models.CharField(max_length=100, blank=False, null=False)
    enterprise_id = models.CharField(max_length=50, blank=False, null=False)
    is_enterprise_install = models.BooleanField(blank=True, null=True)  # the slug text for the url
    workspace_id = models.CharField(max_length=50, blank=False, null=False)
    workspace_slack_url = models.URLField(max_length=200, blank=False, null=False)
    admin_user_id = models.CharField(max_length=50, blank=False, null=False)
    admin_user_name = models.CharField(max_length=200, blank=False, null=False)
    admin_user_email = models.EmailField(blank=True, null=False)
    workspace_url = models.SlugField(max_length=200, blank=True, null=True)  # the slug text for the url
    workspace_joined_time = models.DateTimeField(blank=True, null=False, default=datetime.now)
    workspace_default_channel = models.CharField(max_length=50, blank=True, null=False, default="general")
    workspace_advisory_shout = models.CharField(
        max_length=10,
        choices=MESSAGE_CHOICES,
        default='<!channel>'
    )
    workspace_awareness_shout = models.CharField(
        max_length=10,
        choices=MESSAGE_CHOICES,
        default='<!here>'
    )
    workspace_event_shout = models.CharField(
        max_length=10,
        choices=MESSAGE_CHOICES,
        default='All'
    )

    class Meta:
        unique_together = ('enterprise_id', 'workspace_id')  # block duplicating of workspace records

    def __str__(self):
        return self.workspace_name

    def title_no_spaces(self):
        return re.sub('[^a-zA-Z0-9]', '_', self.workspace_name)  # use regex to replace anything non alphanumeric with underscore

    def save(self, *args, **kwargs):  # the autogeneration of the slug for the challenge
        if not self.workspace_url:
            self.workspace_url = slugify(self.workspace_name + '-' + str(random.choices(string.ascii_uppercase + string.digits, k=4)))
        super(SlackInstalledWorkspace, self).save(*args, **kwargs)


class MailingList(models.Model):  # this is a generic challenge model where all challenges are picked up from.
    '''
    The SlackInstalledWorkspace model contains the register of workspaces where the App is successfully installed.
    '''
    mailing_list_user_email = models.EmailField(blank=True, null=False, unique=True)
    mailing_list_joined_time = models.DateTimeField(blank=True, null=False, default=datetime.now)

    def __str__(self):
        return self.mailing_list_user_email

