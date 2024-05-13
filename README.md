# Geoportal INSPIRE

Geoportal INSPIRE - backend project

## Requirements

- Python 3.8+
- requirements.txt

## Features

- Custom-style admin site
- Translation (en, hr)
- Django REST framework
- GeoDjango
- PostgreSQL database with PostGIS extension

## Installation

#### Step 1: Clone the repo

```sh
git clone gitea@git.li-st.net:LI-ST/geoportal-inspire-backend-django.git
```

#### Step 2: Create python virtualenv (virtualenvwrapper)

```sh
mkvirtualenv venv
workon venv
```

#### Step 3: Install python requirements

```sh
pip install -r requirements.txt
```

#### Step 4: Create postgis db that will be used for dev env

```sh
sudo -u postgres createdb <db_name>
sudo -u postgres psql <db-name>
> CREATE EXTENSION postgis;
> CREATE EXTENSION postgis_topology;
```

#### Step 5: Create .env file in django project dir (setup) with environment settings according to env.sample file

```sh
vim .env
```

#### Step 6: Create all DB tables using migrations file

```sh
python manage.py migrate
```

#### Step 7 (optional): Run management commands to create DB entries

##### Make sure to prepare required files in resources dir and to run the commands in proper order as below

```sh
python manage.py create_zupanije
python manage.py create_jls
python manage.py create_naselja
python manage.py import_gospodarske_jedinice
python manage.py import_granice_lovista
python manage.py import_ribolovne_zone
python manage.py import_sume
python manage.py create_materialized_views
python manage.py import_minp_download_service
python manage.py import_odsjek_suma_dataset
python manage.py import_ribolovne_podzone_dataset
python manage.py import import_granice_lovista_dataset
python manage.py import import_gospodarske_jedinice_dataset

```

#### Step 8: Run written tests

```sh
python manage.py test
```

#### Step 9: Start development server (debug only)

```sh
python manage.py runserver
```

## Author

[LIST LABS](https://www.listlabs.net/)