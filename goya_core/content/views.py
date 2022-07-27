from logging import exception
from django.shortcuts import render
from django.http import HttpResponseBadRequest, HttpResponse
from django.db import IntegrityError
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods # To restrict access to views based on the request method 
import feedparser
from fuzzywuzzy import fuzz
import re
import datetime
import json
from datetime import timedelta
from django.utils import timezone
from content.models import CandidateEvent, InterestingEventCategory
import os

from content.models import CandidateEvent, AwarenessMessage
# Create your views here.

@staff_member_required  # the message is protected. 
@require_http_methods(["GET"])
def list_awareness_message(request):
    awareness_messages = AwarenessMessage.objects.all()
    # return HttpResponse("<h1>Home Page</h1>")
    context = {
        'awareness_messages': awareness_messages,
    }
    return render(request, "content/list_awareness.html", context)


@staff_member_required  # the message is protected. 
@require_http_methods(["GET"])
def get_event_candidates_from_rss(request):
    '''
    internal function to parse events from RSS feed into manageable information, remove duplicates and store data to db
    '''
    # this section collects data from RSS feeds and pools it into a single array.
    initial_data = []
    json_data = json.loads(settings.RSS_FEEDS)
    for key, value in json_data.items():  # loop through all the items of the json to collect information
        feed = feedparser.parse(value)
        for candidate in feed.entries:
            initial_data.append([key,candidate])

    # this section collects the titles of the articles from the candidate events db so we don't duplicate them
    seen = set()
    seen_db = CandidateEvent.objects.values('candidate_event_title')
    for i in seen_db:
        seen.add(i['candidate_event_title'])

    # this section passes all records of new collected data title into a comparison to find articles with similar title
    # those that aren't similar are moved to the final array for data extraction and storing to DB
    final_data=[]
    for item in initial_data:
        title = item[1].title
        similar = 0
        for i in seen:
            similarity = fuzz.token_set_ratio(title.lower(),i.lower())
            if similar < similarity:
                similar = similarity
        if similar < 75:
            final_data.append(item)
            seen.add(title)

    # this section parses the final data set, extracts the title, excerpt, link url and topic (from the RSS feed topic)
    # then stores data into db
    for candidate in final_data:
        title, content, link, published_date = parse_event_candidate(candidate[1])
        try:
            obj = CandidateEvent.objects.create(candidate_event_title=title[:199], candidate_event_details=content, candidate_event_source_url=link,candidate_event_published_time=published_date)
            obj.tags.add(candidate[0])
        except IntegrityError as error:
            pass
    return HttpResponse("Parsing complete")



def parse_event_candidate(candidate):
    '''
    internal function to parse events from RSS feed into manageable information
    '''
    start_substring= "https://www.google.com/url?rct=j&sa=t&url="
    link=candidate.link.replace(start_substring,'')
    end_substring = re.findall(r'\&ct\=ga\&cd=CAIyG.*', link)
    link=link.replace(end_substring[0],'')
    published_day=datetime.datetime.strptime(candidate.published, "%Y-%m-%dT%H:%M:%SZ")
    return(candidate.title, candidate.content[0]['value'], link, published_day)


def fetch_events_of_interest():
    '''
    Internal Function that retrieves events on interest in a certain time period
    '''
    # Fetch the tags of interested added to the Model
    TAGS_OF_INTEREST = InterestingEventCategory.objects.values('interesting_event_category')

    # Get all events from the last week knowing today's date
    today = timezone.now()
    lastweek = today - timedelta(weeks=1)

    # Filter for Events based on the publishing time and tags that have been added. 
    events = CandidateEvent.objects.filter(candidate_event_published_time__week=lastweek.isocalendar()[1], tags__name__in=TAGS_OF_INTEREST)

    # Storage for Tag Repetition
    references = {}

    # Events
    for event in events:
        # Fetch All the tags in one post
        found_tags = [tag['name'] for tag in event.tags.values()]
        # Store the Number of Mentions for each one.
        for tag in found_tags:
            references[tag] = references.setdefault(tag, 1) + 1 

    return references