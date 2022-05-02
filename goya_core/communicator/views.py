from django.shortcuts import render
from django.views.decorators.http import require_http_methods # To restrict access to views based on the request method 
from django.conf import settings
from slack_sdk.oauth.installation_store.sqlite3 import SQLite3InstallationStore
from slack_sdk.oauth.installation_store.amazon_s3 import AmazonS3InstallationStore
import boto3
import os
from slack_sdk.web import WebClient
from django.http import HttpResponseBadRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from markdownify import markdownify as markdown  # to convert html to markdown
from slack_sdk.errors import SlackApiError
from datetime import datetime    


from content.models import Advisory
from main.models import SlackInstalledWorkspace
from communicator.models import Latest_Advisory

# Create your views here.

@login_required  # the message is protected. 
@require_http_methods(["GET"])
def send_advisories_view(request, *args, **kwargs):

    client_id=str(settings.SLACK_CLIENT_ID)
    client_secret=str(settings.SLACK_CLIENT_SECRET)
    if str(settings.LOCAL_TEST) == 'True':  # preparing a place where the state store - Local is sqlite. Parameters are in settings, server is S3
        installation_store = SQLite3InstallationStore(
            database=settings.STATE_DB_NAME,
            client_id=client_id
        ) 
    else:
        s3_client = boto3.client("s3")
        installation_store=AmazonS3InstallationStore(
            s3_client=s3_client,
            bucket_name="goya-slack-installation-store",
            client_id=client_id
        )
    all_workspaces = SlackInstalledWorkspace.objects.all()
    # 
    for workspace in all_workspaces:
        latest_advisory_time = Latest_Advisory.objects.get(advised_workspace=workspace).latest_advisory_time
        advisories = Advisory.objects.filter(advisory_published_time__gt=latest_advisory_time)
        if advisories:
            installation = installation_store.find_installation(enterprise_id=workspace.enterprise_id,team_id=workspace.workspace_id)
            client = WebClient(token=installation.bot_token)
            spacer_line = "===================================="
            message_text=""
            for advisory in advisories:
                message_text = "*"+advisory.advisory_title+"*" + "\n" + spacer_line + "\n" + markdown(advisory.advisory_details) + "\n\n"
                try:
                    client.chat_postMessage(channel='#general', text=message_text)
                    update_workspace_advisory(workspace,datetime.now())
                except SlackApiError as error:
                    message = "ERROR - We couldn't send an advisory. The error was:"+error.response['error']
                    # notify admin
                    notify_admin(installation.user_id, installation.bot_token, message)
                    # notify superadmin
                    message = message+" On workspace "+workspace.workspace_name
                    installation1 = installation_store.find_installation(enterprise_id="No_Ent_ID",team_id="TNMQGFG4F")
                    notify_admin(installation1.user_id, installation1.bot_token, message)

    
    return HttpResponse("Test completed! Result: ")
    

def update_workspace_advisory(workspace,time):
    obj, created = Latest_Advisory.objects.update_or_create(advised_workspace=workspace, defaults={'latest_advisory_time' : time})
    return(obj)
    return(True)


def notify_admin(receiving_channel, receiving_token, receiving_message):
    client = WebClient(token=receiving_token)
    status_result = client.chat_postMessage(channel=receiving_channel, text=receiving_message) 