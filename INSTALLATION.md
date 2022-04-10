# Installation and running goya-core 

## How to install goya-core app locally
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
6. Enter the folder `goya-core` and install the required dependencies
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

## How to run goya-core app locally
Go to the `goya_core` folder (example: `Initial path/goya/goya-core/goya_core`) and run the server
```
python manage.py runserver
```

## How to update your local copy of goya-core
1. Pull new version of the code while in the goya folder `goya-core`
```
git pull
```

2. Reinstall the dependencies in the folder `goya-core` 
```
pip install -r requirements.txt
```