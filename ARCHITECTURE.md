# Architecture concepts of goya-core

The final architecture is not yet built up.
## General concepts
- MVP to be a single application.
- The application to be broken up into microservices for easier maintenance and management.
- The application should be built to be easily restartable and to survive unavailability. 
- The application should be built to protect the data - especially content with customers.

## Platform to run the application
The platform to run the application is AWS.

## To be defined
- CI/CD
- AWS architecture in detail - VPC, Availability Zones, Database setup...
- User access to the platform (slack based authentication for the workspace admin)