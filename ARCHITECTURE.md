# Architecture concepts of goya-core

The final architecture is not yet built up.
## General concepts
- MVP to be a single application.
- The application to be broken up into microservices for easier maintenance and management.
- The application should be built to be easily restartable and to survive unavailability. 
- The application should be built to protect the data - especially content with customers.

## Platform to run the application
The platform to run the application is AWS.

## AWS Architecture
VPC in two availability zones
RDS in VPC in one availability zone (to scale to standby copy in second AZ)
Lambda in VPC in two availability zones.
RDS and S3 are encrypted at rest
Application role to run Lambda and to access the S3
All secrets and parameters in Parameter Store
No servers to maintain
RDS is centrally managed. Backups are 7 days retention.


## To be defined
- CI/CD
- AWS architecture in detail - VPC, Availability Zones, Database setup...
- User access to the platform (slack based authentication for the workspace admin)