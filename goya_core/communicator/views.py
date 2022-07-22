from django.views.decorators.http import require_http_methods # To restrict access to views based on the request method 
from django.conf import settings
from slack_sdk.oauth.installation_store.sqlite3 import SQLite3InstallationStore
from slack_sdk.oauth.installation_store.amazon_s3 import AmazonS3InstallationStore
import boto3
from slack_sdk.web import WebClient
from django.http import HttpResponseBadRequest, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from markdownify import markdownify as markdown  # to convert html to markdown
from slack_sdk.errors import SlackApiError
from datetime import datetime    
import mixpanel
from urllib.request import urlopen
from django.conf import settings



from content.models import Advisory, RealLifeEvent, EventSummary, AwarenessMessage, AwarenessCategory
from main.models import SlackInstalledWorkspace
from communicator.models import Latest_Advisory, Latest_Event_Report, Advisories_Sent, EventSummary_Sent, Latest_Awareness, Awareness_Sent

# Create your views here.

@staff_member_required  # the message is protected. 
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
            shout_signal = workspace.workspace_advisory_shout
            intro_line = ":warning: "+shout_signal+" *Cybersecurity Advisory - please read and take action!* \n====================================\n\n"
            spacer_line = "\n------------------------------------\n"
            takeaway_line = ":exclamation: *Take action now!*\n"
            message_text=""
            reminder_message = "\nMake sure that you have added the BeyondMachines App to the appropriate channel so we can send awareness and advisories that reach all team members. \n \
            Your workspace default channel is: "+workspace.workspace_default_channel
            for advisory in advisories:
                message_text = intro_line+"*"+advisory.advisory_title+"*"+ spacer_line + markdown(advisory.advisory_details) + spacer_line + takeaway_line + "```"+advisory.advisory_takeway +"```"
                try:
                    client.chat_postMessage(channel='#'+workspace.workspace_default_channel, text=message_text)
                    update_workspace_advisory(workspace,datetime.now())
                    update_workspace_advisory_list(workspace,advisory,datetime.now())
                except SlackApiError as error:
                    message = "ERROR - We couldn't send an advisory. The error was:"+error.response['error']
                    message_to_workspace_admin = message+reminder_message
                    # notify admin
                    notify_admin(installation.user_id, installation.bot_token, message_to_workspace_admin)
                    # notify superadmin
                    message_to_superadmin = message+" On workspace "+workspace.workspace_name+" with chosen default channel:"+workspace.workspace_default_channel
                    installation1 = installation_store.find_installation(enterprise_id="No_Ent_ID",team_id="TNMQGFG4F")
                    notify_admin(installation1.user_id, installation1.bot_token, message_to_superadmin)
    return HttpResponse("Advisories Sent! Result: ")


@staff_member_required  # the message is protected. 
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
        event_reports = EventSummary.objects.filter(summary_published_time__gt=latest_event_report_time)
        if event_reports:
            installation = installation_store.find_installation(enterprise_id=workspace.enterprise_id,team_id=workspace.workspace_id)
            client = WebClient(token=installation.bot_token)
            shout_signal = workspace.workspace_event_shout
            intro_line = ":loudspeaker: "+shout_signal+" *Latest Cybersecurity Events and lessons learned* \n====================================\n\n"
            spacer_line = "\n------------------------------------\n"
            message_text= intro_line
            takeaway_line = ":eyes: *One thing to keep in mind*\n"
            reminder_message = "\n Make sure that you have added the BeyondMachines App to the appropriate channel so we can send awareness and advisories that reach all team members. \n \
            Your workspace default channel is: "+workspace.workspace_default_channel
            for event_report in event_reports:
                message_text = message_text + "*"+event_report.summary_title+"*" + spacer_line + markdown(event_report.summary_details) + spacer_line + takeaway_line + "```"+event_report.summary_takeway +"```"
            try:
                client.chat_postMessage(channel='#'+workspace.workspace_default_channel, text=message_text)
                update_workspace_event_report(workspace,datetime.now())
                for event_report in event_reports:
                    update_workspace_event_summary_list(workspace, event_report, datetime.now())
            except SlackApiError as error:
                message = "ERROR - We couldn't send an event report. The error was:"+error.response['error']
                message_to_workspace_admin = message+reminder_message
                # notify admin
                notify_admin(installation.user_id, installation.bot_token, message_to_workspace_admin)
                # notify superadmin
                message_to_superadmin = message+" On workspace "+workspace.workspace_name+" with chosen default channel:"+workspace.workspace_default_channel
                installation1 = installation_store.find_installation(enterprise_id="No_Ent_ID",team_id="TNMQGFG4F")
                notify_admin(installation1.user_id, installation1.bot_token, message_to_superadmin)
    return HttpResponse("Events Sent! Result: ")



@staff_member_required  # the message is protected. 
@require_http_methods(["GET"])
def send_awareness_message_view(request, *args, **kwargs):
    '''
    a view to send summary of awareness messages to all workspaces. Should be scheduled to run once per week. 
    '''
    client_id, installation_store = get_slack_bot_installation_store()
    all_workspaces = SlackInstalledWorkspace.objects.all()
    category_counter = AwarenessCategory.objects.count()  # get the max number of category IDs to loop though for each workspace to find next post to be sent
    for workspace in all_workspaces:
        latest_awareness_message = Latest_Awareness.objects.filter(advised_workspace=workspace).first()  # get the latest awareness message for the workspace
        if latest_awareness_message:  # if there was a message sent before, filter the rest of the available awareness posts to find the next post
            next_category = latest_awareness_message.latest_awareness_message.awareness_category_id
            next_message = None
            attempted_categories = 0  # a counter to stop an infinite loop in case of no new posts. 
            while next_message == None:
                attempted_categories = attempted_categories+1
                next_category = (next_category+1) % category_counter  # use modulo to loop through the 
                next_message = AwarenessMessage.objects.exclude(awareness_message_sent_to_workspace__advised_workspace=workspace).filter(awareness_category=next_category).first()
                if attempted_categories > category_counter+1: 
                    break
        else:
            next_category = -1
            next_message = None
            while next_message == None:
                next_category = (next_category+1) % category_counter  # use modulo to loop through the 
                next_message = AwarenessMessage.objects.filter(awareness_category=next_category).first()

        if next_message != None:
            installation = installation_store.find_installation(enterprise_id=workspace.enterprise_id,team_id=workspace.workspace_id)
            client = WebClient(token=installation.bot_token)
            shout_signal = workspace.workspace_awareness_shout
            intro_line = ":seedling: "+shout_signal+" *Regular Cybersecurity Awareness reminder* \n====================================\n\n"
            spacer_line = "\n------------------------------------\n"
            message_text= intro_line
            takeaway_line = ":eyes: *One thing to keep in mind*\n"
            reminder_message = "\n Make sure that you have added the BeyondMachines App to the appropriate channel so we can send awareness and advisories that reach all team members. \n \
            Your workspace default channel is: "+workspace.workspace_default_channel
            message_text = message_text + "*"+next_message.awareness_message_title+"*" + spacer_line + markdown(next_message.awareness_message_details) + spacer_line + takeaway_line + "```"+next_message.awareness_message_takeway +"```"
            try:
                if next_message.awareness_message_image:
                    image_url = settings.CUSTOM_DOMAIN+next_message.awareness_message_image.url
                    f = urlopen(image_url)
                    file_name = f.read()
                    client.files_upload(channels='#'+workspace.workspace_default_channel, initial_comment=message_text, file=file_name)
                else:
                    client.chat_postMessage(channel='#'+workspace.workspace_default_channel, text=message_text)
                update_workspace_awareness(workspace, next_message, datetime.now())
                update_workspace_awareness_list(workspace, next_message, datetime.now())
            except SlackApiError as error:
                message = "ERROR - We couldn't send an event report. The error was:"+error.response['error']
                message_to_workspace_admin = message+reminder_message
                # notify admin
                notify_admin(installation.user_id, installation.bot_token, message_to_workspace_admin)
                # notify superadmin
                message_to_superadmin = message+" On workspace "+workspace.workspace_name+" with chosen default channel:"+workspace.workspace_default_channel
                installation1 = installation_store.find_installation(enterprise_id="No_Ent_ID",team_id="TNMQGFG4F")
                notify_admin(installation1.user_id, installation1.bot_token, message_to_superadmin)
        else:
            message_to_superadmin = "No new messages to send for workspace: "+ workspace.workspace_name
            installation1 = installation_store.find_installation(enterprise_id="No_Ent_ID",team_id="TNMQGFG4F")
            notify_admin(installation1.user_id, installation1.bot_token, message_to_superadmin)
    return HttpResponse("Awareness Sent! Result: ")


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


def update_workspace_awareness(workspace,message,time):
    '''
    internal function for updating the latest time an awareness message is sent to a workspace so we don't repeat awareness messages
    '''
    obj, created = Latest_Awareness.objects.update_or_create(advised_workspace=workspace, defaults={'latest_awareness_message' : message, 'latest_awareness_time' : time})
    return(obj)


def update_workspace_awareness_list(workspace,message,time):
    '''
    internal function for updating the latest time a summary of events is sent to a workspace so we don't repeat events
    '''
    obj = Awareness_Sent.objects.create(advised_workspace=workspace, awareness_message_sent=message, awareness_message_sent_time=time)
    return(obj)


def update_workspace_event_summary_list(workspace,event,time):
    '''
    internal function for registering sent events to workspace for analytics
    '''
    obj = EventSummary_Sent.objects.create(advised_workspace=workspace, event_summary_sent=event, event_summary_sent_time=time)
    return(obj)


def notify_admin(receiving_channel, receiving_token, receiving_message):
    '''
    internal function that sends a slack notification to the admin of the workspace based on different events (new workspace, error in sending notifications etc.)
    '''
    client = WebClient(token=receiving_token)
    status_result = client.chat_postMessage(channel=receiving_channel, text=receiving_message) 
    return(status_result)



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


def generic_notify_workspace_admins(message):
    '''
    a view to send a generic notification to workspace admins - used for policy changes or service info
    '''
    client_id, installation_store = get_slack_bot_installation_store()
    all_workspaces = SlackInstalledWorkspace.objects.all()
    # 
    for workspace in all_workspaces:
        installation = installation_store.find_installation(enterprise_id=workspace.enterprise_id,team_id=workspace.workspace_id)
        message_to_workspace_admin = message
        # notify admin
        result = notify_admin(installation.user_id, installation.bot_token, message_to_workspace_admin)
        if result['ok'] != True:
            # notify superadmin
            message_to_superadmin = "ERROR on sending " + message+ " to user " + installation.user_id + " On workspace "+workspace.workspace_name
            installation1 = installation_store.find_installation(enterprise_id="No_Ent_ID",team_id="TNMQGFG4F")
            notify_admin(installation1.user_id, installation1.bot_token, message_to_superadmin)