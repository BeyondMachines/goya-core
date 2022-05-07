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


from communicator.views import update_workspace_advisory
from main.models import SlackInstalledWorkspace
from content.models import Advisory

# Create your views here.

@require_http_methods(["GET"])
def slack_install_view(request, *args, **kwargs):
    '''
    This is the view that provides the install page where the users will click on the installation of the application. 
    this may need to be changed later to make it simpler for users to find and use this app (maybe put it on the home page
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
        ),
    authorize_url_generator = AuthorizeUrlGenerator(client_id=str(settings.SLACK_CLIENT_ID),scopes=["chat:write","team:read"],user_scopes=["identity.basic","identity.email"],)  # this version is not elegant, there is no central management of scopes but for MVP good enough. 
    if type(state_store) is tuple:  # this piece of code is needed because the AmazonS3OAuthStateStore returns a tuple.
        state_st = state_store[0]
    else:
        state_st = state_store
    state = state_st.issue()  # we issue a temporary state variable to be used in the request so the link can't be recycled 
    generated_url = authorize_url_generator.generate(state)
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
    # First let's set up whether we are in local or AWS environment. 
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
    # Then let's get the auth code for the workspace
    if request.GET.get('code'):  # Retrieve the auth code and state from the request params
        if state_st.consume(request.GET.get('state')):  # Verify the state parameter and prepare for getting the access token.
            client_id=str(settings.SLACK_CLIENT_ID)
            client_secret=str(settings.SLACK_CLIENT_SECRET)
            redirect_uri=str(settings.SLACK_REDIRECT_URI)
            client = WebClient()  # no prepared token needed for this
            # Complete the installation by calling oauth.v2.access API method
            oauth_response = client.oauth_v2_access(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                code=request.GET.get('code')
            )

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

            # we check in the currently installed workspaces for duplicates...
            workspace = SlackInstalledWorkspace.objects.filter(enterprise_id=enterprise_id,workspace_id=installed_workspace_id)

            if not workspace:
                # save a new workspace to the installed workspace model
                new_workspace = SlackInstalledWorkspace()
                new_workspace.workspace_name = installed_workspace_name
                new_workspace.enterprise_id = enterprise_id
                new_workspace.is_enterprise_install = is_enterprise_install
                new_workspace.workspace_id = installed_workspace_id
                new_workspace.workspace_slack_url = auth_test.get("url")
                new_workspace.admin_user_id = user_details.get("id")
                new_workspace.admin_user_name = user_details.get("name")
                new_workspace.admin_user_email = user_details.get("email")
                new_workspace.save()

                # continue saving the installation
                
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
                    ),
                    if type(installation_store) is tuple:  # this piece of code is needed because the AmazonS3InstallationStore returns a tuple.
                        installation_st = installation_store[0]
                    else:
                        installation_st = installation_store
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
                update_workspace_advisory(new_workspace,datetime.now())
                # client.chat_postMessage(channel='#general', text='hello with Oauth access token authentication. second step towards token authentication. Now works only on install App action.')
                

                # now we send notification to Slack to the admin that installed the application
                client = WebClient(token=installation.bot_token)
                status_result = client.chat_postMessage(channel=installation.user_id, text="<@"+installation.user_id+">"+":wave: BeyondMachines Slack bot successfully installed")  # this line sends the status message to the admin user to remind him if everything is OK.


                # now we send a notification to the overall Slack admin to the beyondmachines app.
                installation = installation_st.find_installation(enterprise_id="No_Ent_ID",team_id="TNMQGFG4F")
                print(installation)
                client = WebClient(token=installation.bot_token)
                status_result = client.chat_postMessage(channel=installation.user_id, text="<@"+installation.user_id+">"+":wave: We have a new registered workspace "+installed_workspace_name)  # this line sends the status message to the admin user to remind him if everything is OK.
        
                context = {
                }
                return render(request, "slack_app/install_success.html", context)
            else:
                context = {
                }
                return render(request, "slack_app/install_exists.html", context)
        else:
            return HttpResponseBadRequest("Error: The state value is expired. Start the installation again and complete it within 5 minutes of starting.")
    else:
        error = args["error"] if "error" in args else "no error message available"
        return HttpResponseBadRequest("Something is wrong with the installation (Error message: "+error+")")


def design_page_view(request, *args, **kwargs):
    context = {
    }
    return render(request, "slack_app/install_exists.html", context)


