# slack_app
The app that will run the Slack integration

It will provide the OAuth 2 endpoints for the slack app installation, and will send out the messages to the Slack workspaces where the app is installed. The information will be received from the content app. 

## Endpoints defined in this app
- `slack_install` - the endpoint that generates the request URL for the slack app installation. This is a dynamic URL that contains several important elements: slack app IT, app access scope and a randomized session that times out so the link can't be recycled.
- `slack_callback` - the endpoint that receives the callback from Slack after initiating the install of a slack app to workspace. It collects the access code granted by the user, validates the proper access grants through a test auth, and then collects the information about the workspace and the installer to create a workspace record in the main app for sending of notifications. 

## Models defined in this app
TBD.
Future improvement - to decouple this app into a microservice.

