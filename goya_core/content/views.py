from logging import exception
import traceback
from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponseBadRequest, HttpResponse
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
import requests
from fake_useragent import UserAgent

from content.models import CandidateEvent, AwarenessMessage, ScrapedEvent
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


@staff_member_required  # the message is protected.
@require_http_methods(["GET"])
def get_reddit_events(request) -> HttpResponse:
    '''
    Gets latest x num of posts on selected subreddit containing the accepted flairs
    '''
    try:
        # Options
        subreddit = "r/cybersecurity"
        timespan = "day"    # Options: "day", "week", "month", "all"
        accepted_flairs = [
            "News - General",
            "News - Breaches & Ransoms",
            "New Vulnerability Disclosure",
            "Threat Actor TTPs & Alerts",
        ]

        # URL encoding
        URL = f"https://www.reddit.com/{subreddit}/search.json?q="
        for i, flair in enumerate(accepted_flairs):
            if i == 0:
                URL += f'flair%3A%22{flair.replace(" ", "%20").replace("&", "%26")}'
            else:
                URL += f'%22%20OR%20flair%3A%22{flair.replace(" ", "%20").replace("&", "%26")}'
        URL += f'%22&restrict_sr=1&sr_nsfw=&sort=top&t={timespan}'

        # Getting data from Reddit
        ua = UserAgent()
        response = requests.get(URL, headers={"User-Agent": ua.chrome})
        response_data = response.json()

        if response.status_code < 200 or response.status_code > 299:
            print(f"Bad response!\nResponse code:{response.status_code}\nResponse message: {response_data['message']}")
            return HttpResponse(
                f"""<h1>Bad response!</h1>
                Response code: <b>{response.status_code}</b><br>
                Response message: <b>{response_data['message']}</b>"""
            )

        posts = [post["data"] for post in response_data["data"]["children"]]

        cnt = 0
        for post in posts:
            # Extract data from posts
            content_id = post["id"]
            content_title = post["title"]
            content_flair = post["link_flair_text"].replace("&amp;", "&")
            content_details = post["selftext"]
            content_url = f"https://www.reddit.com{post['permalink']}"
            content_published_time = datetime.datetime.fromtimestamp(post["created_utc"])
            try:
                content_additional_data = post["url_overridden_by_dest"]
            except KeyError:
                content_additional_data = None

            # Check if post is already in the database
            try:
                reddit_event_obj = get_object_or_404(ScrapedEvent, event_custom_id=content_id)
            except Http404:
                # Create it if it's not
                reddit_event_obj = ScrapedEvent.objects.create(event_custom_id=content_id)
                reddit_event_obj.event_title = content_title
                reddit_event_obj.event_details = content_details
                reddit_event_obj.event_url = reddit_event_obj.title_no_spaces()
                reddit_event_obj.event_source_url = content_url
                reddit_event_obj.event_published_time = content_published_time
                reddit_event_obj.event_additional_data = content_additional_data
                reddit_event_obj.event_source = "Reddit"
                reddit_event_obj.tags.add(content_flair)
                reddit_event_obj.save()
                cnt += 1

    except Exception:
        tb = traceback.format_exc()
        print(tb)
        return HttpResponse(f"<h1>Error!</h1><pre>{tb}</pre>")

    return HttpResponse(f"Getting content from reddit complete<br>Found <b>{cnt}</b> new events")
