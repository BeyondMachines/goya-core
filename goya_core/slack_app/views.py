from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods # To restrict access to views based on the request method 
from django.conf import settings
from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.oauth.state_store.sqlite3 import SQLite3OAuthStateStore
from slack_sdk.oauth.state_store.amazon_s3 import AmazonS3OAuthStateStore
from slack_sdk.oauth.installation_store import Installation
from slack_sdk.oauth.installation_store.sqlite3 import SQLite3InstallationStore
from slack_sdk.oauth.installation_store.amazon_s3 import AmazonS3InstallationStore
import boto3
import os
from slack_sdk.web import WebClient
from django.http import HttpResponseBadRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime


from communicator.views import update_workspace_advisory, update_workspace_event_report, send_analytics, notify_admin
from main.models import SlackInstalledWorkspace, Additional_Admin
from content.models import Advisory
from communicator import messages

# Create your views here.

@require_http_methods(["GET"])
def slack_install_view(request, *args, **kwargs):
    '''
    This is the view that provides the install page where the users will click on the installation of the application. 
    this may need to be changed later to make it simpler for users to find and use this app (maybe put it on the home page
    '''
    state_st = prepare_state_store()
    authorize_url_generator = AuthorizeUrlGenerator(client_id=str(settings.SLACK_CLIENT_ID),scopes=["chat:write","team:read","files:write"],user_scopes=["identity.basic","identity.email"],)  # this version is not elegant, there is no central management of scopes but for MVP good enough. 
    state = state_st.issue()  # we issue a temporary state variable to be used in the request so the link can't be recycled 
    generated_url = authorize_url_generator.generate(state)
    send_analytics(request, "Install Slack App")
    context = {
        'generated_url': generated_url,
    }
    # return render(request, "slack_app/slack_install.html", context)
    return redirect(generated_url)

@require_http_methods(["GET"])
def slack_callback_view(request, *args, **kwargs):
    '''
    This is the view that completes the installation of the provides the install page where the users will click on the installation of the application. 
    this may need to be changed later to make it simpler for users to find and use this app (maybe put it on the home page
    '''
    # First let's set up the state store based on our environment (local or AWS). 
    state_st = prepare_state_store()
    # Then let's get the auth code for the workspace
    if request.GET.get('code'):  # Retrieve the auth code and state from the request params
        if state_st.consume(request.GET.get('state')):  # Verify the state parameter and prepare for getting the access token.
            client_id=str(settings.SLACK_CLIENT_ID)

            oauth_response = call_oauth_v2_access(request.GET.get('code'))  # Complete the installation by calling oauth.v2.access API method

            # Now we collect some basic information from the oauth_token
            is_enterprise_install = oauth_response.get("is_enterprise_install")

            # now we have to get the information. First from the bot auth request
            installed_enterprise = oauth_response.get("enterprise", {})
            installer = oauth_response.get("authed_user", {})  # this is an interim block to get the subarray
            installed_team = oauth_response.get("team", {})  # this is a interim block to get the subarray
            installed_workspace_name = installed_team.get("name")
            installed_workspace_id = installed_team.get("id")
            incoming_webhook = oauth_response.get("incoming_webhook", {})

            # Now we prepare the auth_test to confirm the proper authentication
            bot_token = oauth_response.get("access_token")
            client = WebClient(token=bot_token) #create an OAuth client with a bot taccess token
            bot_id = None  # NOTE: oauth.v2.access doesn't include bot_id in response
            enterprise_url = None
            if bot_token is not None:
                auth_test = client.auth_test(token=bot_token)
                bot_id = auth_test["bot_id"]
                if is_enterprise_install is True:
                    enterprise_url = auth_test.get("url")
                    enterprise_id=installed_enterprise.get("id")
                    enterprise_name=installed_enterprise.get("name")
                else:
                    enterprise_url = 'No_Ent_Url'
                    enterprise_id = 'No_Ent_ID'
                    enterprise_name = 'No_Ent_Name'


            # now we get the information from the user access token, to get the user details
            client = WebClient(token=installer.get("access_token"))
            user = client.users_identity()
            user_details = user.get("user", {})

            # get the current workspace, and then pass it to the function for saving of workspace
            workspace = SlackInstalledWorkspace.objects.filter(enterprise_id=enterprise_id,workspace_id=installed_workspace_id).first()
            new_workspace = save_workspace_details(workspace, oauth_response, enterprise_id, user_details, auth_test.get("url"))

            # prepare installation store for the new installation
            installation_st = prepare_installation_store(client_id) 
            
            installation = Installation(
                app_id=oauth_response.get("app_id"),
                enterprise_id=enterprise_id,
                enterprise_name=enterprise_name,
                enterprise_url=enterprise_url,
                team_id=installed_team.get("id"),
                team_name=installed_team.get("name"),
                bot_token=bot_token,
                bot_id=bot_id,
                bot_user_id=oauth_response.get("bot_user_id"),
                bot_scopes=oauth_response.get("scope"),  # comma-separated string
                user_id=installer.get("id"),
                user_token=installer.get("access_token"),
                user_scopes=installer.get("scope"),  # comma-separated string
                incoming_webhook_url=incoming_webhook.get("url"),
                incoming_webhook_channel=incoming_webhook.get("channel"),
                incoming_webhook_channel_id=incoming_webhook.get("channel_id"),
                incoming_webhook_configuration_url=incoming_webhook.get("configuration_url"),
                is_enterprise_install=is_enterprise_install,
                token_type=oauth_response.get("token_type"),
            )

            # Store the installation
            installation_st.save(installation)

            #Updating advisories timers only for new workspaces, not for updated workspaces
            if workspace:
                
                user_welcome_message = messages.USER_UPDATE_MESSAGE
                notify_admin(installation.user_id, installation.bot_token, "<@"+installation.user_id+">"+user_welcome_message) # this line sends the status message to the admin user to remind him if everything is OK.

                # now we send a notification to the overall Slack admin to the beyondmachines app.
                installation = installation_st.find_installation(enterprise_id="No_Ent_ID",team_id="TNMQGFG4F") #the superadmin team
                notify_admin(installation.user_id, installation.bot_token, "<@"+installation.user_id+">"+":wave: We have an updated installation workspace "+installed_workspace_name) # this line sends the status message to the admin user to remind him if everything is OK.

                send_analytics(request, "Updated Install Slack App - Success")
            else:
                update_workspace_advisory(new_workspace,datetime.now())
                update_workspace_event_report(new_workspace,datetime.now())              
                # now we send notification to Slack to the admin that installed the application
                user_welcome_message = messages.USER_WELCOME_MESSAGE
                notify_admin(installation.user_id, installation.bot_token, "<@"+installation.user_id+">"+user_welcome_message) # this line sends the status message to the admin user to remind him if everything is OK.

                # now we send a notification to the overall Slack admin to the beyondmachines app.
                installation = installation_st.find_installation(enterprise_id="No_Ent_ID",team_id="TNMQGFG4F") #the superadmin team
                notify_admin(installation.user_id, installation.bot_token, "<@"+installation.user_id+">"+":wave: We have a new registered workspace "+installed_workspace_name) # this line sends the status message to the admin user to remind him if everything is OK.

                send_analytics(request, "First Install Slack App - Success")
            context = {
            }
            return render(request, "slack_app/install_success.html", context)
        else:
            send_analytics(request, "Install Slack App - Error Expired")
            return HttpResponseBadRequest("Session Error: The state value is expired. Start the installation again and complete it within 5 minutes of starting.")
    else:
        send_analytics(request, "Install Slack App - Error Message")
        error = args["error"] if "error" in args else "no error message available"
        return HttpResponseBadRequest("Something is wrong with the installation (Error message: "+error+")")


def design_page_view(request, *args, **kwargs):
    context = {
    }
    return render(request, "slack_app/install_exists.html", context)


@require_http_methods(["GET"])
def slack_sandbox_invite_view(request, *args, **kwargs):
    '''
    This is the view that provides the install page where the users will click on the installation of the application. 
    this may need to be changed later to make it simpler for users to find and use this app (maybe put it on the home page
    '''
    generated_url = settings.SANDBOX_SLACK_INVITE
    context = {
        'generated_url': generated_url
    }
    # return render(request, "slack_app/slack_install.html", context)
    return redirect(generated_url)


def prepare_state_store():
    '''
    This is an internal function to generate a proper state_store depending on whether the system is local test (SQLite) or on S3 which returns a tuple so the first object has to be extracted
    '''
    if str(settings.LOCAL_TEST) == 'True':  # preparing a place where the state store - Local is sqlite. Parameters are in settings, server is S3
        state_store = SQLite3OAuthStateStore(
            expiration_seconds=300, database=settings.STATE_DB_NAME
        ) 
    else:
        s3_client = boto3.client("s3")
        state_store=AmazonS3OAuthStateStore(
            s3_client=s3_client,
            bucket_name="goya-slack-state-store",
            expiration_seconds=300,  # the default value: 10 minutes
        )
    if type(state_store) is tuple:  # this piece of code is needed because the AmazonS3OAuthStateStore returns a tuple.
        state_st = state_store[0]
    else:
        state_st = state_store
    return(state_st)



def prepare_installation_store(sent_client_id):
    '''
    This is an internal function to generate a proper installation_store for the workspace depending on whether the system is local test (SQLite) or on S3 which returns a tuple so the first object has to be extracted
    '''
    if str(settings.LOCAL_TEST) == 'True':  # preparing a place where the state store - Local is sqlite. Parameters are in settings, server is S3
        installation_store = SQLite3InstallationStore(
            database=settings.STATE_DB_NAME,
            client_id=sent_client_id
        )
        installation_st = installation_store
    else:
        s3_client = boto3.client("s3")
        installation_store=AmazonS3InstallationStore(
            s3_client=s3_client,
            bucket_name="goya-slack-installation-store",
            client_id=sent_client_id
        ),
    if type(installation_store) is tuple:  # this piece of code is needed because the AmazonS3InstallationStore returns a tuple.
        installation_st = installation_store[0]
    else:
        installation_st = installation_store
    return(installation_st)


def call_oauth_v2_access(sent_code):
    '''
    This is an internal function to complete the second phase of installation of bot to workspace by calling oauth.v2.access API method

    '''
    client_id=str(settings.SLACK_CLIENT_ID)
    client_secret=str(settings.SLACK_CLIENT_SECRET)
    redirect_uri=str(settings.SLACK_REDIRECT_URI)
    client = WebClient()  # no prepared token needed for this
    # Complete the installation by calling oauth.v2.access API method
    oauth_response = client.oauth_v2_access(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        code=sent_code
    )
    return(oauth_response)

def save_workspace_details(sent_workspace, sent_oauth_response, sent_enterprise_id, sent_user_details, sent_url):
    '''
    This is an internal function to save the workspace details for an installed workspace
    to save a new workspace send null as sent_workspace. If the workspace exists and the same person saves the data, then we don't do anything. Otherwise we save or update (depending on situation)
    '''
    installed_team = sent_oauth_response.get("team", {})
    
    if sent_workspace:  # if it's a new workspace, save it.
        if sent_user_details.get("id") != sent_workspace.admin_user_id:
            additional_admin = Additional_Admin()
            additional_admin.workspace = sent_workspace
            additional_admin.admin_user_id = sent_user_details.get("id")
            additional_admin.admin_user_name = sent_user_details.get("name")
            additional_admin.admin_user_email = sent_user_details.get("email")
            additional_admin.save()
        return(sent_workspace)
    else:  # if it's an existing workspace but the admin is different, save additional admin in a separate table.
        new_workspace = SlackInstalledWorkspace()
        new_workspace.workspace_name = installed_team.get("name")
        new_workspace.enterprise_id = sent_enterprise_id
        new_workspace.is_enterprise_install = sent_oauth_response.get("is_enterprise_install")
        new_workspace.workspace_id = installed_team.get("id")
        new_workspace.workspace_slack_url = sent_url
        new_workspace.admin_user_id = sent_user_details.get("id")
        new_workspace.admin_user_name = sent_user_details.get("name")
        new_workspace.admin_user_email = sent_user_details.get("email")
        new_workspace.save()
        return(new_workspace)
