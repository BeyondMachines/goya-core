from django.shortcuts import render
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



# Create your views here.

# First set up the environment from the .env file in the local_data_store

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
            bucket_name="your-own-s3-bucket-name-for-installations",
            expiration_seconds=300,  # the default value: 10 minutes
        ),
    authorize_url_generator = AuthorizeUrlGenerator(client_id=str(settings.SLACK_CLIENT_ID),scopes=["chat:write","team:read"],user_scopes=["identity.basic","identity.email"],)  # this version is not elegant, there is no central management of scopes but for MVP good enough. 
    state = state_store.issue()  # we issue a temporary state variable to be used in the request so the link can't be recycled 
    generated_url = authorize_url_generator.generate(state)
    print(generated_url)
    context = {
        'generated_url': generated_url,
    }
    return render(request, "slack_app/slack_install.html", context)


@require_http_methods(["GET"])
def slack_callback_view(request, *args, **kwargs):
    '''
    This is the view that completes the installation of the provides the install page where the users will click on the installation of the application. 
    this may need to be changed later to make it simpler for users to find and use this app (maybe put it on the home page
    '''
    # Retrieve the auth code and state from the request params
    if request.GET.get('code'):
        # Verify the state parameter
        state_store = SQLite3OAuthStateStore(
            expiration_seconds=300, database=settings.STATE_DB_NAME
        ) 
        if state_store.consume(request.GET.get('state')):
            client_id=str(settings.SLACK_CLIENT_ID)
            client_secret=str(settings.SLACK_CLIENT_SECRET)
            redirect_uri=str(settings.SLACK_REDIRECT_URI)
            client = WebClient()  # no prepared token needed for this
            # Complete the installation by calling oauth.v2.access API method
            print('client_id 2:',client_id,client_secret)
            oauth_response = client.oauth_v2_access(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                code=request.GET.get('code')
            )

            installed_enterprise = oauth_response.get("enterprise", {})
            is_enterprise_install = oauth_response.get("is_enterprise_install")
            installed_team = oauth_response.get("team", {})
            installer = oauth_response.get("authed_user", {})
            incoming_webhook = oauth_response.get("incoming_webhook", {})

            bot_token = oauth_response.get("access_token")
            client = WebClient(token=bot_token) #create

            # client.chat_postMessage(channel='#general', text='hello with Oauth access token authentication. second step towards token authentication. Now works only on install App action.')
            
            # NOTE: oauth.v2.access doesn't include bot_id in response
            bot_id = None
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
        
            if str(settings.LOCAL_TEST) == 'True':  # preparing a place where the state store - Local is sqlite. Parameters are in settings, server is S3
                installation_store = SQLite3InstallationStore(
                    database=settings.STATE_DB_NAME,
                    client_id=client_id
                ) 
            else:
                s3_client = boto3.client("s3")
                state_store=AmazonS3InstallationStore(
                    s3_client=s3_client,
                    bucket_name="your-own-s3-bucket-name-for-installations",
                    client_id=client_id
                ),
                
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
            # testing the identification of the details that are needed: Workspace ID, Workspace domain, Workspace Name, Installer user ID, installer user email, installer user name. 
            print(oauth_response)
            print('installed enterprise',installed_enterprise)
            print('installed enterprise',is_enterprise_install)
            print('url',oauth_response.get("url"))
            print('url 1', auth_test.get("url"))
            print('team',installed_team)
            print('installer',installer)
            print('installer_id',installer.get("id"))
            print('installer email', installer.get("email"))
            print('installer user', installer.get("user"))
            print('installer user from auth_test', auth_test.get("user"))

            ## This block is the one that exposes the installing user 
            client = WebClient(token=installer.get("access_token"))  # this requiest works only with the user access token, not the bot token.
            user = client.users_identity()
            user_details = user.get("user")
            team_details = user.get("team")
            print('slack workspace id',team_details.get("id"))
            print('user name',user_details.get("name"))
            print('user id',user_details.get("id"))
            print('user email',user_details.get("email"))



            # Store the installation
            installation_store.save(installation)
            print('installation_saved')

            return HttpResponse("Thanks for installing this app!")
        else:
            
            return HttpResponseBadRequest("Error: The state value is expired. Start the installation again and complete it within 5 minutes of starting.")
    else:
        error = args["error"] if "error" in args else "no error message available"
        return HttpResponseBadRequest("Something is wrong with the installation (Error message: "+error+")")

