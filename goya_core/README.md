# goya_core 
This is the root folder of the **goya_core** Django project.

## Subfolders/apps
- _goya_core_ - The project settings and configuration folders including the generic URLs configuration
- _templates_ - The folder where each app will store it's html templates that are sent back to the frontend with the information from the views.
- _main_ - The main app of the project. Will contain only the public pages/content interface. The UI is Bootrap 5 based.
- _content_ - The app that will contain the final content and advisories sent to the consumers.
- _slack_app_ - The app that will run the Slack integration


## Technologies/libraries used
- `bootstrap 5` for UI (via the django-bootstrap-v5 library)
- `Slack SDK` (via the python slack_sdk library)
- `AWS` (via the boto3/botocore library)
- `flatpages` from Django to build the simple static part of the application, like FAQ and Privacy pages. 