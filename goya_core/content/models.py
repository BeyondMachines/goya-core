import string
from datetime import date, datetime
from slugify import slugify
import random
import re
from ckeditor.fields import RichTextField
from taggit.managers import TaggableManager


# import models
from django.db import models

# Create your models here.

class Advisory(models.Model):  # this is a generic challenge model where all challenges are picked up from.
    '''
    The Advisory model contains the individual advisories that are created for sending as immediate messages.
    '''
    advisory_title = models.CharField(max_length=200, blank=False, null=False)
    advisory_details = RichTextField(blank=False, null=False)
    advisory_url = models.SlugField(max_length=100, blank=True, null=True)  # the slug text for the url
    advisory_published_time = models.DateTimeField(blank=True, null=False, default=datetime.now)
    tags = TaggableManager()  # the adding of tags to the challenge


    def __str__(self):
        return self.advisory_title

    def title_no_spaces(self):
        return re.sub('[^a-zA-Z0-9]', '_', self.advisory_title)  # use regex to replace anything non alphanumeric with underscore
        #  return self.challenge_title.replace(" ", "_")

    def save(self, *args, **kwargs):  # the autogeneration of the slug for the challenge
        if not self.advisory_url:
            self.advisory_url = slugify(self.advisory_title + '-' + str(random.choices(string.ascii_uppercase + string.digits, k=4)))
        super(Advisory, self).save(*args, **kwargs)


class RealLifeEvent(models.Model):  # this is a generic challenge model where all challenges are picked up from.
    '''
    The RealLifeEvents model contains the individual events that happen during and are used for awareness examples. 
    '''
    event_title = models.CharField(max_length=200, blank=False, null=False)
    event_details = RichTextField(blank=False, null=False)
    event_url = models.SlugField(max_length=100, blank=True, null=True)  # the slug text for the url
    event_source_url = models.URLField(max_length=400, blank=False, null=False, default='https://localhost')
    event_published_time = models.DateTimeField(blank=True, null=False, default=datetime.now)
    tags = TaggableManager()  # the adding of tags to the challenge

    def __str__(self):
        return self.event_title

    def title_no_spaces(self):
        return re.sub('[^a-zA-Z0-9]', '_', self.event_title)  # use regex to replace anything non alphanumeric with underscore
        #  return self.challenge_title.replace(" ", "_")

    def save(self, *args, **kwargs):  # the autogeneration of the slug for the challenge
        if not self.event_url:
            self.event_url = slugify(self.event_title + '-' + str(random.choices(string.ascii_uppercase + string.digits, k=4)))
        super(RealLifeEvent, self).save(*args, **kwargs)



class EventSummary(models.Model):  # this is a generic challenge model where all challenges are picked up from.
    '''
    The EventSummary model contains the aggregation of the individual events that's sent to users as weekly awareness sessions. 
    '''
    summary_title = models.CharField(max_length=200, blank=False, null=False)
    summary_details = RichTextField(blank=False, null=False)
    summary_takeway = models.TextField(blank=False, null=False)
    summary_url = models.SlugField(max_length=100, blank=True, null=True)  # the slug text for the url
    summary_published_time = models.DateTimeField(blank=True, null=False, default=datetime.now)
    tags = TaggableManager()  # the adding of tags to the challenge

    def __str__(self):
        return self.summary_title

    def title_no_spaces(self):
        return re.sub('[^a-zA-Z0-9]', '_', self.summary_title)  # use regex to replace anything non alphanumeric with underscore

    def save(self, *args, **kwargs):  # the autogeneration of the slug for the challenge
        if not self.summary_url:
            self.summary_url = slugify(self.summary_title + '-' + str(random.choices(string.ascii_uppercase + string.digits, k=4)))
        super(EventSummary, self).save(*args, **kwargs)



class CandidateEvent(models.Model):  # this is a generic challenge model where all challenges are picked up from.
    '''
    The CandidateEvent model contains the events automatically parsed for filtering and review. 
    '''
    candidate_event_title = models.CharField(max_length=200, blank=False, null=False)
    candidate_event_details = RichTextField(blank=False, null=False)
    candidate_event_source_url = models.URLField(max_length=400, blank=False, null=False, default='https://localhost')
    candidate_event_published_time = models.DateTimeField(blank=True, null=False, default=datetime.now)
    tags = TaggableManager()  # the adding of tags to the challenge

    class Meta:
        unique_together = ('candidate_event_title', 'candidate_event_source_url')  # block duplicating of candidate records

    def __str__(self):
        return self.candidate_event_title



class AwarenessMessage(models.Model):  # this is a generic challenge model where all challenges are picked up from.
    '''
    The AwarenessMessage model contains the awareness messages. 
    '''
    awareness_message_title = models.CharField(max_length=200, blank=False, null=False)
    awareness_message_details = RichTextField(blank=False, null=False)
    awareness_message_takeway = models.TextField(blank=False, null=False)
    awareness_message_url = models.SlugField(max_length=100, blank=True, null=True)  # the slug text for the url
    awareness_message_published_time = models.DateTimeField(blank=True, null=False, default=datetime.now)
    tags = TaggableManager()  # the adding of tags to the challenge

    def __str__(self):
        return self.awareness_message_title

    def title_no_spaces(self):
        return re.sub('[^a-zA-Z0-9]', '_', self.awareness_message_title)  # use regex to replace anything non alphanumeric with underscore

    def save(self, *args, **kwargs):  # the autogeneration of the slug for the challenge
        if not self.awareness_message_url:
            self.awareness_message_url = slugify(self.awareness_message_title + '-' + str(random.choices(string.ascii_uppercase + string.digits, k=4)))
        super(AwarenessMessage, self).save(*args, **kwargs)
