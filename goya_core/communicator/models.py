from django.db import models
from datetime import datetime    


from main.models import SlackInstalledWorkspace
from content.models import Advisory
# Create your models here.


class Latest_Advisory(models.Model):
    '''
    model to store the latest time an advisory was successfully sent per each workspace
    '''
    advised_workspace = models.ForeignKey(SlackInstalledWorkspace, blank=False, null=True, on_delete=models.CASCADE, related_name='advisory_informed_workspace')  # may want to validate proper challenge reference
    # latest_advisory_sent = models.ForeignKey(Advisory, blank=True, null=True, on_delete=models.SET_NULL, related_name='latest_advisory')  # may want to validate proper participant reference
    latest_advisory_time = models.DateTimeField(blank=True, null=False, default=datetime.now)


class Latest_Event_Report(models.Model):
    '''
    model to store the latest time an event summary was successfully sent per each workspace
    '''
    advised_workspace = models.ForeignKey(SlackInstalledWorkspace, blank=False, null=True, on_delete=models.CASCADE, related_name='event_advised_workspace')  # may want to validate proper challenge reference
    # latest_advisory_sent = models.ForeignKey(Advisory, blank=True, null=True, on_delete=models.SET_NULL, related_name='latest_advisory')  # may want to validate proper participant reference
    latest_event_report_time = models.DateTimeField(blank=True, null=False, default=datetime.now)