from django.shortcuts import render
from django.views.decorators.http import require_http_methods # To restrict access to views based on the request method 
from django.conf import settings
from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.oauth.state_store.sqlite3 import SQLite3OAuthStateStore
from slack_sdk.oauth.state_store.amazon_s3 import AmazonS3OAuthStateStore
import boto3
import os

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