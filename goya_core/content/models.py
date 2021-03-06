import string
from datetime import date, datetime
from slugify import slugify
import random
import re
from ckeditor.fields import RichTextField
from taggit.managers import TaggableManager
from django.conf import settings


# import models
from django.db import models

# Create your models here.

class Advisory(models.Model):  
    '''
    The Advisory model contains the individual advisories that are created for sending as immediate messages.
    '''
    advisory_title = models.CharField(max_length=200, blank=False, null=False)
    advisory_details = RichTextField(blank=False, null=False)
    advisory_takeway = models.TextField(blank=False, null=False, default=" ")
    advisory_url = models.SlugField(max_length=220, blank=True, null=True)  # the slug text for the url
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


class RealLifeEvent(models.Model):  
    '''
    The RealLifeEvents model contains the individual events that happen during and are used for awareness examples. 
    '''
    event_title = models.CharField(max_length=200, blank=False, null=False)
    event_details = RichTextField(blank=False, null=False)
    event_url = models.SlugField(max_length=220, blank=True, null=True)  # the slug text for the url
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



class EventSummary(models.Model):  
    '''
    The EventSummary model contains the aggregation of the individual events that's sent to users as weekly awareness sessions. 
    '''
    summary_title = models.CharField(max_length=200, blank=False, null=False)
    summary_details = RichTextField(blank=False, null=False)
    summary_takeway = models.TextField(blank=False, null=False)
    summary_url = models.SlugField(max_length=220, blank=True, null=True)  # the slug text for the url
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



class CandidateEvent(models.Model):  
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



class AwarenessCategory(models.Model):  
    '''
    The AwarenessCategory model contains the events automatically parsed for filtering and review. 
    '''
    awareness_category = models.CharField(max_length=200, blank=False, null=False)
    awareness_category_id = models.IntegerField(blank=False, null=False, unique=True)

    def __str__(self):
        return self.awareness_category


class AwarenessMessage(models.Model):  
    '''
    The AwarenessMessage model contains the awareness messages. 
    '''
    awareness_category = models.ForeignKey(AwarenessCategory, blank=False, null=True, on_delete=models.SET_NULL)  # may want to validate proper challenge reference
    awareness_message_title = models.CharField(max_length=200, blank=False, null=False)
    awareness_message_details = RichTextField(blank=False, null=False)
    awareness_message_takeway = models.TextField(blank=False, null=False)
    awareness_message_url = models.SlugField(max_length=220, blank=True, null=True)  # the slug text for the url
    awareness_message_published_time = models.DateTimeField(blank=True, null=False, default=datetime.now)
    awareness_message_image = models.ImageField(blank=True, null=True,
                                     upload_to="media_upload/awareness/upload/%Y/%m/%d/", max_length=255)
    tags = TaggableManager()  # the adding of tags to the challenge

    def __str__(self):
        return self.awareness_message_title

    def title_no_spaces(self):
        return re.sub('[^a-zA-Z0-9]', '_', self.awareness_message_title)  # use regex to replace anything non alphanumeric with underscore

    def save(self, *args, **kwargs):  # the autogeneration of the slug for the challenge
        if not self.awareness_message_url:
            self.awareness_message_url = slugify(self.awareness_message_title + '-' + str(random.choices(string.ascii_uppercase + string.digits, k=4)))
        super(AwarenessMessage, self).save(*args, **kwargs)


class InterestingEventCategory(models.Model):
    '''
    The InterestingEventCategory model contains the tags used to search events that are in the interest of the superadmin.
    '''
    interesting_event_category = models.CharField(max_length=200, blank=False, null=False)
    interesting_event_category_category_id = models.IntegerField(blank=False, null=False, unique=True)

    def __str__(self):
        return self.interesting_event_category


class ScrapedEvent(models.Model):
    '''
    The ScrapedEvent model containts events scraped from the internet
    '''
    event_custom_id = models.CharField(max_length=20, blank=False, null=False)
    event_title = models.TextField(blank=False, null=False)
    event_details = RichTextField(blank=True, null=True)
    event_url = models.SlugField(max_length=220, blank=True, null=True)  # the slug text for the url
    event_source_url = models.URLField(max_length=400, blank=False, null=False, default='https://localhost')
    event_published_time = models.DateTimeField(blank=True, null=False, default=datetime.now)
    event_additional_data = models.URLField(max_length=500, blank=True, null=True)
    event_source = models.CharField(max_length=50, blank=False, null=False)
    tags = TaggableManager()

    def __str__(self):
        return self.event_title

    def title_no_spaces(self):
        return re.sub('[^a-zA-Z0-9]', '_', self.event_title)  # use regex to replace anything non alphanumeric with underscore

    def save(self, *args, **kwargs):  # the autogeneration of the slug for the challenge
        if not self.event_url:
            self.event_url = slugify(self.event_title + '-' + str(random.choices(string.ascii_uppercase + string.digits, k=4)))
        super(ScrapedEvent, self).save(*args, **kwargs)

