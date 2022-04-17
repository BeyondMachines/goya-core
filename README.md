# goya-core 
## Information Security Awareness Platform

This project is the core underpinning of the Information Security awareness platform.

The project name is inspired by the Urdu word **"Goya"** - a momentary suspension of disbelief associated with a story very well told.

This is important for us since too many people don't believe that they can be a target of cyber attack. This platform aims to suspend this disbeleif.

# Documentation Structure
Each folder contains it's own README file that describes the function of the folder.
## Local installation 
The instructions to install and run the app locally are in the file `INSTALLATION.md` in this folder.
## Coding Standard
The coding standard of this project is defined in the file `CODING.md` in this folder.
## Architecture 
The architecture of this project is defined in the file `ARCHITECTURE.md` in this folder.
## Security 
The security concepts of this project is defined in the file `SECURITY.md` in this folder.

# Contributing to the project
Read the architecture, coding standard and security concepts first. Install the application and start adding features. In order to push to the code you have to be added to the project first. 

# Project Structure
## goya_core 
The **goya_core** folder is the project source code
The project is based on Django.
More details of the content of the `goya_core` in the README file in the folder.

## local_data_store
The **local_data_store** folder contains all local data stores, that shouldn't be included in the source code. Anything stored in this folder is ignored via the _.gitignore_ and _.dockerignore_ files.
### .env file
You need to create your own .env file in the `local_data_store` that will contain your apps config (example below)
```
SLACK_TOKEN=your_app_token_secret
SLACK_CLIENT_ID=your_app_id
SLACK_CLIENT_SECRET=your_app_secret
SLACK_SIGNING_SECRET=your_app_signing_secret
SLACK_REDIRECT_URL=https://some_url_you_chose/slack/oauth/callback
```
# Roadmap
- Implement a content server (django)
    - Backend entry of content
- Implement delivery of content
    - Slack App for multiple workspaces
    - Teams App for multiple workspaces
- Implement long form content
- Implement authentication and access

