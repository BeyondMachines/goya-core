# slack_app
The app that will run the Slack integration

It will provide the OAuth 2 endpoints for the slack app installation, and will send out the messages to the Slack workspaces where the app is installed. The information will be received from the content app. 

Endpoints defined in this app
- `slack_install` - the endpoint that generates the request URL for the slack app installation. This is a dynamic URL that contains several important elements: slack app IT, app access scope and a randomized session that times out so the link can't be recycled.


Future improvement - to decouple this app into a microservice.

