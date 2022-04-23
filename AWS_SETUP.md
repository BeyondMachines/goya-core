# AWS Environment to run Goya

This is the documentation that willl enable you to build an environment on AWS that will run Goya. 
While automatic configuration through Infrastructure as a Code is desired, the first phase will be a manual configuration that can then be reworked in a programmatic way.

## Basic naming standards
All resources start with `goya-service_name-service_specifics`
All resources are tagged with tag name `function` and tag value `goya-production`

## Manual configuration
### VPC
Create AWS VPC in the selected region. Configure the VPC wizard to create:
- One VPC
- One public subnet and one private subnet in two availability zones
- Three route tables - one for public access and two for private access
- Four network connections - one for internet gateway, one for S3 access and two NAT gateways - one for each availability zone.

### S3 buckets
Create S3 buckets for the static files `django-static` and for the zappa deployment `zappa-files`

Create a S3 bucket policy to allow communication from the VPC. I need to check the conditions, so the role of the zappa service sees these S3 buckets...

### Database

Create a database within the VPC (no external access). Encrypt the database, and set backups of at least 7 days retention 

core admin 
postgres_admin
f3UuvNVLt$kP%&zLfq

# ToDo
Test the S3 bucket policy and fix it so it runs with authenticated services only.
