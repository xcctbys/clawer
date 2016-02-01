### Mysql's Configs

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
    mysql -uroot -p
    mysql> create database db_name;
    mysql> \q

    python manage.py makemigrations clawer_parse
    python manage.py migrate

### Deps

    pip install MySQL-python
    pip install requests

### Crontab

    # In Terminal
    crontab -e.

    # Press i to go into vim's insert mode.
    # Type the cron job, 01:00 every day import yesterday's data to db:
    00 01 * * * sh ~/projects/nice-clawer/sources/qyxy/structured/run.sh

    # Press Esc to exit vim's insert mode.
    # Type ZZ (must be capital letters).
    # Verify by using
    crontab -l.
