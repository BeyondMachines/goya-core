from django.db import models
from datetime import datetime    


from main.models import SlackInstalledWorkspace
from content.models import Advisory, RealLifeEvent, EventSummary, AwarenessMessage
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


class Latest_Awareness(models.Model):
    '''
    model to store the latest time an awareness message was successfully sent per each workspace
    '''
    advised_workspace = models.ForeignKey(SlackInstalledWorkspace, blank=False, null=True, on_delete=models.CASCADE, related_name='awareness_advised_workspace')  # may want to validate proper challenge reference
    # latest_advisory_sent = models.ForeignKey(Advisory, blank=True, null=True, on_delete=models.SET_NULL, related_name='latest_advisory')  # may want to validate proper participant reference
    latest_awareness_time = models.DateTimeField(blank=True, null=False, default=datetime.now)


class Advisories_Sent(models.Model):
    advised_workspace = models.ForeignKey(SlackInstalledWorkspace, blank=False, null=True, on_delete=models.CASCADE, related_name='workspace_advisory_notified')  # may want to validate proper challenge reference
    advisory_sent = models.ForeignKey(Advisory, blank=False, null=True, on_delete=models.SET_NULL, related_name='advisory_sent_to_workspace')
    advisory_sent_time = models.DateTimeField(blank=True, null=False, default=datetime.now)


class Events_Sent(models.Model):
    advised_workspace = models.ForeignKey(SlackInstalledWorkspace, blank=False, null=True, on_delete=models.CASCADE, related_name='workspace_event_notified')  # may want to validate proper challenge reference
    event_sent = models.ForeignKey(RealLifeEvent, blank=False, null=True, on_delete=models.SET_NULL, related_name='event_sent_to_workspace')
    event_sent_time = models.DateTimeField(blank=True, null=False, default=datetime.now)


class EventSummary_Sent(models.Model):
    advised_workspace = models.ForeignKey(SlackInstalledWorkspace, blank=False, null=True, on_delete=models.CASCADE, related_name='workspace_event_summary_notified')  # may want to validate proper challenge reference
    event_summary_sent = models.ForeignKey(EventSummary, blank=False, null=True, on_delete=models.SET_NULL, related_name='event_summary_sent_to_workspace')
    event_summary_sent_time = models.DateTimeField(blank=True, null=False, default=datetime.now)


class Awareness_Sent(models.Model):
    advised_workspace = models.ForeignKey(SlackInstalledWorkspace, blank=False, null=True, on_delete=models.CASCADE, related_name='workspace_awareness_notified')  # may want to validate proper challenge reference
    awareness_message_sent = models.ForeignKey(AwarenessMessage, blank=False, null=True, on_delete=models.SET_NULL, related_name='awareness_message_sent_to_workspace')
    awareness_message_sent_time = models.DateTimeField(blank=True, null=False, default=datetime.now)