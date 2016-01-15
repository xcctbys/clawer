### Mysql's Configs

    create database clawer
    # edit structured/settings.py
    # change `db_user` and `db_password` for yours.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'clawer',
            'USER': 'db_user',
            'PASSWORD': 'db_password',
            'HOST': '127.0.0.1',
            'PORT': '3306',
        }
    }

### Create Mysql Tables

    python manage.py makemigrations
    python manage.py migrate

### Import Data to Database
    python manage.py structured
