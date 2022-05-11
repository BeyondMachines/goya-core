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
import mixpanel


from content.models import Advisory, RealLifeEvent
from main.models import SlackInstalledWorkspace
from communicator.models import Latest_Advisory, Latest_Event_Report, Advisories_Sent, Events_Sent

# Create your views here.

@login_required  # the message is protected. 
@require_http_methods(["GET"])
def send_advisories_view(request, *args, **kwargs):
    '''
    a view to send the individual advisory e-mail to take action because of a vulnerability or zero day attack.
    '''
    client_id, installation_store = get_slack_bot_installation_store()
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
            reminder_message = "\n Make sure that you have added the BeyondMachines App to the appropriate channel so we can send awareness and advisories that reach all team members. \n \
            Your workspace default channel is: "+workspace.workspace_default_channel
            for advisory in advisories:
                message_text = "*"+advisory.advisory_title+"*" + "\n" + spacer_line + "\n" + markdown(advisory.advisory_details) + "\n\n"
                try:
                    client.chat_postMessage(channel='#'+workspace.workspace_default_channel, text=message_text)
                    update_workspace_advisory(workspace,datetime.now())
                    update_workspace_advisory_list(workspace,advisory,datetime.now())
                except SlackApiError as error:
                    message_to_workspace_admin = "ERROR - We couldn't send an advisory. The error was:"+error.response['error']+reminder_message
                    # notify admin
                    notify_admin(installation.user_id, installation.bot_token, message_to_workspace_admin)
                    # notify superadmin
                    message_to_superadmin = message+" On workspace "+workspace.workspace_name+" with chosen default channel:"+workspace.workspace_default_channel
                    installation1 = installation_store.find_installation(enterprise_id="No_Ent_ID",team_id="TNMQGFG4F")
                    notify_admin(installation1.user_id, installation1.bot_token, message_to_superadmin)
    return HttpResponse("Advisories Sent! Result: ")


@login_required  # the message is protected. 
@require_http_methods(["GET"])
def send_event_report_view(request, *args, **kwargs):
    '''
    a view to send summary of real life events to all workspaces. Should be scheduled to run once per week. 
    '''
    client_id, installation_store = get_slack_bot_installation_store()
    all_workspaces = SlackInstalledWorkspace.objects.all()
    # 
    for workspace in all_workspaces:
        latest_event_report_time = Latest_Event_Report.objects.get(advised_workspace=workspace).latest_event_report_time
        event_reports = RealLifeEvent.objects.filter(event_published_time__gt=latest_event_report_time)
        print('Prepared for sending Events')
        if event_reports:
            print('Got into sending Events')
            installation = installation_store.find_installation(enterprise_id=workspace.enterprise_id,team_id=workspace.workspace_id)
            client = WebClient(token=installation.bot_token)
            intro_line = "*Latest Cybersecurity Events and lessons learned* \n ==================================== \n\n"
            spacer_line = "\n------------------------------------\n"
            delimiter_line = "\n++++++++++++++++++++++++++++++++++++\n"
            message_text= intro_line
            reminder_message = "\n Make sure that you have added the BeyondMachines App to the appropriate channel so we can send awareness and advisories that reach all team members. \n \
            Your workspace default channel is: "+workspace.workspace_default_channel
            for event_report in event_reports:
                message_text = message_text + "*"+event_report.event_title+"*" + spacer_line + markdown(event_report.event_details) + delimiter_line
            try:
                client.chat_postMessage(channel='#'+workspace.workspace_default_channel, text=message_text)
                update_workspace_event_report(workspace,datetime.now())
                for event_report in event_reports:
                    update_workspace_event_list(workspace, event_report, datetime.now())
            except SlackApiError as error:
                message_to_workspace_admin = "ERROR - We couldn't send an event report. The error was:"+error.response['error']+reminder_message
                # notify admin
                notify_admin(installation.user_id, installation.bot_token, message_to_workspace_admin)
                # notify superadmin
                message_to_superadmin = message+" On workspace "+workspace.workspace_name+" with chosen default channel:"+workspace.workspace_default_channel
                installation1 = installation_store.find_installation(enterprise_id="No_Ent_ID",team_id="TNMQGFG4F")
                notify_admin(installation1.user_id, installation1.bot_token, message_to_superadmin)
    return HttpResponse("Events Sent! Result: ")


def update_workspace_advisory(workspace,time):
    '''
    internal function for updating the latest time an advisory is sent to a workspace so we don't repeat advisories
    '''
    obj, created = Latest_Advisory.objects.update_or_create(advised_workspace=workspace, defaults={'latest_advisory_time' : time})
    return(obj)


def update_workspace_advisory_list(workspace,advisory,time):
    '''
    internal function for registering sent advisories to workspace for analytics
    '''
    obj = Advisories_Sent.objects.create(advised_workspace=workspace, advisory_sent=advisory, advisory_sent_time=time)
    return(obj)


def update_workspace_event_report(workspace,time):
    '''
    internal function for updating the latest time a summary of events is sent to a workspace so we don't repeat events
    '''
    obj, created = Latest_Event_Report.objects.update_or_create(advised_workspace=workspace, defaults={'latest_event_report_time' : time})
    return(obj)


def update_workspace_event_list(workspace,event,time):
    '''
    internal function for registering sent events to workspace for analytics
    '''
    obj = Events_Sent.objects.create(advised_workspace=workspace, event_sent=event, event_sent_time=time)
    return(obj)


def notify_admin(receiving_channel, receiving_token, receiving_message):
    '''
    internal function that sends a slack notification to the admin of the workspace based on different events (new workspace, error in sending notifications etc.)
    '''
    client = WebClient(token=receiving_token)
    status_result = client.chat_postMessage(channel=receiving_channel, text=receiving_message) 



def send_analytics(request, event):
    mp_eu = mixpanel.Mixpanel(
        settings.MIXPANEL_TOKEN,
        consumer=mixpanel.Consumer(api_host="api-eu.mixpanel.com"),
        )
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    mp_eu.track(ip, event)


def test_scheduler_advisory():
    '''
    internal function to test a schedule of advisory sending
    '''
    client_id, installation_store = get_slack_bot_installation_store()
    message_to_superadmin = "test scheduled message as advisory for 9AM mon-thursday"
    installation1 = installation_store.find_installation(enterprise_id="No_Ent_ID",team_id="TNMQGFG4F")
    notify_admin(installation1.user_id, installation1.bot_token, message_to_superadmin)


def test_scheduler_event():
    '''
    internal function to test a schedule of advisory sending
    '''
    client_id, installation_store = get_slack_bot_installation_store()
    message_to_superadmin = "test scheduled message as advisory for 10AM thursday"
    installation1 = installation_store.find_installation(enterprise_id="No_Ent_ID",team_id="TNMQGFG4F")
    notify_admin(installation1.user_id, installation1.bot_token, message_to_superadmin)


def get_slack_bot_installation_store():
    '''
    internal function to get the installation_store for getting individual events. Returns the BeyondMachines slack app id as well as the installation store.
    '''
    client_id=str(settings.SLACK_CLIENT_ID)
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
    return client_id, installation_store