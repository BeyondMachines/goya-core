import string
from datetime import date, datetime
from slugify import slugify
import random
import re
from ckeditor.fields import RichTextField

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

    def __str__(self):
        return self.advisory_title

    def title_no_spaces(self):
        return re.sub('[^a-zA-Z0-9]', '_', self.advisory_title)  # use regex to replace anything non alphanumeric with underscore
        #  return self.challenge_title.replace(" ", "_")

    def save(self, *args, **kwargs):  # the autogeneration of the slug for the challenge
        if not self.advisory_url:
            self.advisory_url = slugify(self.advisory_title + '-' + str(random.choices(string.ascii_uppercase + string.digits, k=4)))
        super(Advisory, self).save(*args, **kwargs)