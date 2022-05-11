"""
Django settings for goya_core project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import os  # needed to check for the AWS_REGION parameter.
import boto3  # needed to connect to AWS.
import botocore  # needed to connect to AWS.
from dotenv import load_dotenv  # needed to load content from .env files


# This function is used to pull the AWS SSM parameters needed to configure this program to run in AWS.
def get_ssm_key(name):
    '''
    This function gets an encrypted key from AWS Systems Manager Parameter Store
    '''
    ssm = boto3.client('ssm')
    try:
        key = ssm.get_parameter(Name=name, WithDecryption=True)
        return key['Parameter']['Value']
    except botocore.exceptions.ClientError as error:
        return error


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# The path to the local data store for sensitive information
LOCAL_DATA_STORE = Path(__file__).resolve().parent.parent.parent / 'local_data_store'

# Decide if the program is running in local copy or on AWS (looks for "AWS REGION" string) and set parameters for the rest of the setup.
if os.environ.get('AWS_REGION'):  # Check whether AWS_REGION variable exists to see if running in AWS or locally
    LOCAL_TEST = False
    DEBUG = os.environ.get('DJANGO_DEBUG', False)
    hosts = ['app.beyondmachines.net','beyondmachines.net','www.beyondmachines.net']  # the following code populates the ALLOWED_HOSTS starting from an empty list.
    api_gatway = get_ssm_key('GOYA_API_GATEWAY')
    hosts.append(api_gatway)
    ALLOWED_HOSTS = hosts
    USE_S3 = True  # tell the static file setup to look for the S3 version of static files
    SLACK_CLIENT_SECRET = get_ssm_key('GOYA_SLACK_CLIENT_SECRET')
    SLACK_CLIENT_ID = get_ssm_key('GOYA_SLACK_CLIENT_ID')
    SLACK_REDIRECT_URI = get_ssm_key('GOYA_SLACK_INSTALL_REDIRECT_URL')
    MIXPANEL_TOKEN= get_ssm_key('GOYA_MIXPANEL_TOKEN')
else:
    LOCAL_TEST = True
    DEBUG = os.getenv('DJANGO_DEBUG', True)
    env_path = LOCAL_DATA_STORE / '.env'  # define the path of the .env 
    load_dotenv(dotenv_path=env_path)  # load the environment file .env
    SLACK_CLIENT_SECRET = os.environ["SLACK_CLIENT_SECRET"]  # the secret issued to our App
    SLACK_CLIENT_ID = os.environ["SLACK_CLIENT_ID"]  # the ID issued to our app
    SLACK_REDIRECT_URI= os.environ["SLACK_REDIRECT_URL"]  # the redirect URL set up in our app that the user will be redirected after the initial setup.
    STATE_DB_NAME = LOCAL_DATA_STORE / 'state_store.sqlite3'  # the database which keeps the Oauth request states for a local installation
    MIXPANEL_TOKEN= os.environ["MIXPANEL_TOKEN"]
    ALLOWED_HOSTS = ['*']  # when running on localhost to allow extenal proxy connections
    USE_S3 = False  # tell the static file setup not to look for the S3 version of static files


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# Creation of SECRET_KEY - this key is needed to generate all CSRF protection codes. This code should never be visible and should be frequently rotated.
# SECURITY WARNING: keep the secret key used in production secret! The commented string version is most insecure
# SECRET_KEY = 'some-secret-string-s#37m%3#0=o%pvvj+mptv+2k&w_@8^o7vt-y$ef&5pvd%yhdgm'
# The code below loads the SECRET_KEY from the local data store or from AWS Parameter Store (depending on whether the environment is detected to be local or remote).

if str(LOCAL_TEST) == 'True':
    SECRET_FILE = os.path.join(LOCAL_DATA_STORE, 'secret_key.txt')
    with open(SECRET_FILE) as f:
        SECRET_KEY = f.read().strip()
else:
    SECRET_KEY = get_ssm_key('GOYA_DJANGO_SECRET_KEY')


# SECURITY WARNING: don't run with debug turned on in production!

# ALLOWED_HOSTS = [] the allowed hosts are in the setup above


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admindocs',  # used to generate automatic docs using docutils
    'django.contrib.sites',
    'django.contrib.flatpages',

    # goya apps
    'main',
    'content',
    'slack_app',
    'communicator',

    # third party tools
    'bootstrap5',
    'storages',  # needed for the django s3 static files
    'ckeditor',
    'taggit',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
]

ROOT_URLCONF = 'goya_core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'goya_core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
# modified to decide whether to run on a local Sqlite 3 or to pull the AWS DB Parameters from parameter store.

if str(LOCAL_TEST) == 'True':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': LOCAL_DATA_STORE / 'db.sqlite3',
        }
    }
else:  # read from AWS Parameter store environment variables
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': get_ssm_key('GOYA_DJANGO_POSTGRES_DB'),
            'USER': get_ssm_key('GOYA_DJANGO_POSTGRES_USER'),
            'PASSWORD': get_ssm_key('GOYA_DJANGO_POSTGRES_PASSWORD'),
            'HOST': get_ssm_key('GOYA_DJANGO_POSTGRES_HOST'),
            'PORT': '5432',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

# STATIC_URL = 'static/'


# STATIC_URL = '/static/'


if str(LOCAL_TEST) == 'True':
    STATIC_FILE_PATH = BASE_DIR
    STATIC_ROOT = os.path.join(STATIC_FILE_PATH, 'static_assets/')
    STATIC_URL = 'static/'
else:  # important, the below code is not finished yet!
    if str(USE_S3) == 'True':
        AWS_STORAGE_BUCKET_NAME = get_ssm_key('GOYA_S3_AWS_STORAGE_BUCKET_NAME')  # get the key for API access to S3
        # AWS_STORAGE_BUCKET_NAME = 'codeonion-static-test.s3.us-east-2.amazonaws.com'  # get the key for API access to S3
        AWS_DEFAULT_ACL = 'public-read'
        AWS_S3_CUSTOM_ROOT = f'{AWS_STORAGE_BUCKET_NAME}'
        AWS_S3_CUSTOM_DOMAIN = 'pubcdn.beyondmachines.net'  # to allow for cdn use
        AWS_S3_OBJECT_PARAMETERS = {
            'CacheControl': 'max-age=86400'
        }
        AWS_IS_GZIPPED = True

        # s3 static settings
        AWS_STATIC_LOCATION = '' 
        # STATIC_URL = 'https://%s/%s/' % (AWS_S3_ENDPOINT_URL, AWS_STATIC_LOCATION)
        # STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_STATIC_LOCATION}/'  # setting before the CDN - keeping this as backup to use for static root
        # STATIC_ROOT = STATIC_URL  # setting before the CDN - keeping this as backup
        STATIC_ROOT = f'https://{AWS_S3_CUSTOM_ROOT}/{AWS_STATIC_LOCATION}/'
        STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_STATIC_LOCATION}/'
        STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    else:  # this is a special case for cloud version where we need local file serving. Should not be used. 
        STATIC_FILE_PATH = os.getenv('DJANGO_STATIC_PATH')
        STATIC_ROOT = os.path.join(STATIC_FILE_PATH, 'static_assets/')
        STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static_data/')
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CKEDITOR RICH TEXT EDITOR SETTING
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': [["Format", "Bold", "Italic", "Underline", "Strike", "SpellChecker"],
                    ['NumberedList', 'BulletedList', "Indent", "Outdent", 'JustifyLeft', 'JustifyCenter',
                    'JustifyRight', 'JustifyBlock'],
                    #  ["Image"],
                    ["Table", "Link", "Unlink", "Anchor", "SectionLink", "Subscript", "Superscript"], ['Undo', 'Redo'],
                    ["Source"],
                    ],
        'width': 'auto',
    },
}

SITE_ID = 1

LOGIN_REDIRECT_URL = 'home'
ACCOUNT_LOGOUT_REDIRECT_URL = 'home'
ACCOUNT_PRESERVE_USERNAME_CASING = False

TAGGIT_CASE_INSENSITIVE = True