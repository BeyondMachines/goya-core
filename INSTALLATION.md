# Installation and running goya-core 

<!-- vscode-markdown-toc -->
* [How to install goya-core app locally (without Docker)](#Howtoinstallgoya-coreapplocallywithoutDocker)
	* [Local installation](#Localinstallation)
	* [Local running](#Localrunning)
* [How to run goya-core app in a Docker container](#Howtorungoya-coreappinaDockercontainer)
* [How to update your local copy of goya-core](#Howtoupdateyourlocalcopyofgoya-core)
* [How to install production grade goya-core in AWS.](#Howtoinstallproductiongradegoya-coreinAWS.)
	* [Components and ingredients](#Componentsandingredients)
	* [Details on the ingredients](#Detailsontheingredients)
	* [AWS Installation](#AWSInstallation)
		* [Create deployoment and running credentials](#Createdeployomentandrunningcredentials)
		* [Create a VPC](#CreateaVPC)
		* [Create needed S3 buckets](#CreateneededS3buckets)
		* [Create RDS DB](#CreateRDSDB)
		* [Insert parameters in AWS Systems Manager Parameter Store.](#InsertparametersinAWSSystemsManagerParameterStore.)
	* [Configure the zappa_settings.json](#Configurethezappa_settings.json)
		* [Set up VPC](#SetupVPC)
		* [Set up Role](#SetupRole)
	* [Deploy, update and manage the application](#Deployupdateandmanagetheapplication)

<!-- vscode-markdown-toc-config
	numbering=false
	autoSave=true
	/vscode-markdown-toc-config -->
<!-- /vscode-markdown-toc -->

## <a name='Howtoinstallgoya-coreapplocallywithoutDocker'></a>How to install goya-core app locally (without Docker)
### <a name='Localinstallation'></a>Local installation
1. Install latest Python 3 version and virtualenv.
2. Create a folder `goya` on your computer. 
3. Create a virtualenv within that folder. 
```
virtualenv -p python3 .
```
4. Activate the virtualenv within the `goya` folder.
```
source bin/activate
```
5. While in the `goya` folder, clone the repository
```
git clone https://github.com/BeyondMachines/goya-core
```
6. Enter the folder `goya-core/goya_core` and install the required dependencies
```
pip install -r requirements.txt
```
7. In the `goya-core` folder create a new folder named `local_data_store`. This folder will keep all sensitive information for the local install (databases, environment files etc)
```
mkdir local_data_store
```
8. In the `local_data_store` generate a secret key.
```
LC_ALL=C </dev/urandom tr -dc 'A-Za-z0-9!"#$%&()*+,-./:;<=>?@[\]^_`{|}~' | head -c 50 > secret.txt
echo DJANGO_SECRET_KEY='"'`cat secret.txt`'"' > secret_key.txt
rm secret.txt
```
9. Go to the `goya_core` folder (example: `Initial path/goya/goya-core/goya_core`) and run the migrations to populate the database.
```
python manage.py makemigrations
python manage.py migrate
```
10. Create your own superuser for the local installation. 
```
python manage.py createsuperuser
```
11. Run the Django server
```
python manage.py runserver
```

### <a name='Localrunning'></a>Local running
Go to the `goya_core` folder (example: `Initial path/goya/goya-core/goya_core`) and run the server
```
python manage.py runserver
```

## <a name='Howtorungoya-coreappinaDockercontainer'></a>How to run goya-core app in a Docker container
1. Go to the `goya_core` folder (example: `Initial path/goya/goya-core/`) and build the image using the command docker build
```
docker build .
```
2. Run the Docker container using the command docker-compose up

```
docker-compose up
```

That's it. 

To create a superuser account instead of typing python manage.py createsuperuser the updated command would now look like 
```
docker-compose exec web python manage.py createsuperuser
```

## <a name='Howtoupdateyourlocalcopyofgoya-core'></a>How to update your local copy of goya-core
1. Pull new version of the code while in the goya folder `goya-core`
```
git pull
```

2. Reinstall the dependencies in the folder `goya-core` 
```
pip install -r requirements.txt
```

## <a name='Howtoinstallproductiongradegoya-coreinAWS.'></a>How to install production grade goya-core in AWS. 
### <a name='Componentsandingredients'></a>Components and ingredients 
- The Django application (folder `goya_core`)
- AWS Account with credentials that can run VPC, RDS, S3, API Gateway, Lambda, Route53, Nat Gateway, Internet Gateway, IAM. 
- Appropriate credentials set up on the AWS Account (see recipe below)
- Appropriate components activated in AWS (see recipe below)
- [Zappa](https://github.com/Zappa/Zappa) to run the deployment.

### <a name='Detailsontheingredients'></a>Details on the ingredients
We are using [Zappa](https://github.com/Zappa/Zappa) to quickly deploy stuff in production on AWS and to optimize the runtime costs. It's installed as part of the `requirements.txt`
Zappa enables implementation of server-less, event-driven Python applications on AWS with AWS Lambda + AWS API Gateway.
[Here's a small tutorial on how things are deployed with Zappa](https://cloudacademy.com/blog/zappa-or-how-to-go-serverless-with-django/)

The Zappa configuration is set up in `zappa_settings.json` file in the folder of goya_core. The Github repo has a template version of the file, but not the real live setup (obviously).

The architecture concept is available in the `ARCHITECTURE.md` file in this folder.

The proper implementation of Zappa deployment is within AWS VPC so the traffic is private, and the proper roles are also essential. 
Some tutorials on implementing Zappa in AWS VPC can be found here:
- [How to Deploy a Serverless WSGI App using Zappa, CloudFront, RDS, and VPC](https://jinwright.net/how-deploy-serverless-wsgi-app-using-zappa/)
- [A Brief Primer on AWS VPC Networking](https://romandc.com/zappa-django-guide/aws_network_primer/)
- [Running tasks in VPC](https://github.com/Zappa/Zappa#running-tasks-in-a-vpc)

The Zappa deployment can build an IAM role in which the deployed AWS Lambda function that executes the Django application will run. But that's not really secure since you don't control the permission stack. 
A better approach is implementing the role yourself and declaring the role in the `zappa_settings.json`.
See more details here 
- [Prepare AWS IAM User, Role, and Policies for Zappa and Serverless Python](https://www.codingforentrepreneurs.com/blog/aws-iam-user-role-policies-zappa-serverless-python)

### <a name='AWSInstallation'></a>AWS Installation
This installation describes all steps needed. It doesn't prescribe whether the installation is manual (through AWS console) or scripted (through CloudFormation/Terraform/etc...).
Naturally, a scripted installation is far better, but for the initial setup a manual installation is possibly easier.
#### <a name='Createdeployomentandrunningcredentials'></a>Create deployoment and running credentials
- Create One user account for execution of zappa commands to deploy the application.
- Create One Zappa role for running of the Lambda function (execution of the deployed application).

For the deployment of Zappa you should have a user with appropriate deployment permissions. Ideally it's not an admin role but for manual deployment an admin role username is ok (as long as you are the only one controlling that user). 
For running of Zappa Lambda function you should have a specific role with attached specific policy which limits the access and permissions of the role only to the resources that are needed to execute the application. 
The setup of the Zappa role policy requires some experimenting to set up properly since different applications will need different AWS resources. 


#### <a name='CreateaVPC'></a>Create a VPC
Create AWS VPC in the selected region. Configure the VPC wizard to create:
- One VPC
- One public subnet and one private subnet in two availability zones
- Three route tables - one for public access and two for private access
- Four network connections - one for internet gateway, one for S3 access and two NAT gateways - one for each availability zone.

#### <a name='CreateneededS3buckets'></a>Create needed S3 buckets
Create S3 buckets for the: 
- static files of Django
- Zappa scripted deployment
- Slack workspaces repository
- Slack session repository.
All S3 buckets should have blocked public access and all should be encrypted at rest. 

#### <a name='CreateRDSDB'></a>Create RDS DB
- Create a Postgres RDS instance within the VPC (no external access). Encrypt the database, and set backups of at least 7 days retention. 
- Create a separate security group for the database.
- Edit the security group rules for the RDS to add the two private subnets from the two availability zones of the VPC. 

##### RDS remote access
- Create an internet facing NLB in the vpc to connecto to the Database attached to a public subnet of the VPC (put in the same AZ as the primary location of the db and map to the private IP of the RDS)
- **Don't forget to create a permission rule** to the  from the RDS database security group to add the public subnet of the VPC where you attached the NLB subnet to the RDS, otherwise it can't connect.
- **Don't keep the NLB active past the initial creation of the DB**. This will create a security risk and big costs. You can disable the rule in the security group above if you don't want to disable the NLB. 

##### Configure the django db
Set up the database for Django within the RDS
```
CREATE DATABASE db_name;
CREATE USER db_user WITH PASSWORD 'db_password';
ALTER ROLE db_user SET client_encoding TO 'utf8';
ALTER ROLE db_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE db_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE db_name TO db_user;
```
#### <a name='InsertparametersinAWSSystemsManagerParameterStore.'></a>Insert parameters in AWS Systems Manager Parameter Store.
Important information needs to be well protected. The Django app looks for the important information (credentials and URLs) in the AWS SSM Parameter Store. Create encrypted string records for:
- RDS DB Name
- RDS Hostname
- RDS DB Username
- RDS DB Password
- Django Secret
- Slack Bot ID
- Slack Bot Access Code
- Slack Bot Secret Code

Then grant the Zappa role proper permissions to access that information by updating the policy. 
```
{
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "ssm:GetParameter"
            ],
            "Resource": [
                "arn:aws:ssm:aws_region:aws_account:parameter/Parameter_Name",
            ]
        },
```

### <a name='Configurethezappa_settings.json'></a>Configure the zappa_settings.json
#### <a name='SetupVPC'></a>Set up VPC
Configure the `zappa_settings.json` file to place the AWS Lambda in the private subnets of the VPC. 
```
        "vpc_config": {
            "SubnetIds": [ "VPC_private_subnet-1", "VPC_private_subnet-2" ], 
            "SecurityGroupIds": [ "VPC_default_security_group" ]
        },
```
#### <a name='SetupRole'></a>Set up Role
Configure the `zappa_settings.json` file with Zappa role to be assigned to the AWS Lambda function. Also, tell zappa that it won't be managing roles directly.
```
        "manage_roles": false,
        "role_name": "production_role",
```

### <a name='Deployupdateandmanagetheapplication'></a>Deploy, update and manage the application
To _deploy_ the application (assuming the name is `production`) from the `goya-core/goya_core` folder (where the `manage.py` program sits), run:
```
zappa deploy production
```

To _update_ the code of the application with new code, (assuming the name is `production`) run:
```
zappa update production
```

To execute _migrations_, it's a three step process:
- prepare migrations locally: `python manage.py makemigrations`
- update instance: `zappa update production`
- execute migrations: `zappa manage production migrate`

To _debug_ issues on the deployed instance use `zappa tail`
```
zappa tail production
```
To remove the application and it's components provisioned by zappa, run:
```
zappa undeploy production
```
**Please note that the AWS VPC, RDS, S3 and roles will not be removed with this command, you have to do that yourself.**

# Notes / ToDo
- Zappa deploy has a problem if the default region is different than the configured region. I made a temp fix by changing the ~./aws/config for the default user to be the same region as the zappa user. 
- We need to deploy continuous integration
https://medium.com/@vladimirnani/continuous-delivery-with-zappa-61518bd9b1a7
