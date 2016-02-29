结构化程序线上环境部署
=====================

### Mysql's Configs

    # edit structured/settings.py
    # change `db_name` `db_user` and `db_password` for yours.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'db_name',
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
    python manage.py syncdb
    python manage.py schemamigration enterprise --initial
    python manage_pro.py migrate

### Deps

    cd /home/webapps/nice-clawer/clawer/
    /home/virtualenvs/py27/bin/pip install -r requirements.txt

### Crontab

    # In Terminal
    crontab -e.

    # Press i to go into vim's insert mode.
    # Type the cron job, 01:00 every day import yesterday's data to db:
    */50 * * * * cd /home/webapps/nice-clawer/confs/production/; sh run.sh import_data_from_json

    # Press Esc to exit vim's insert mode.
    # Type ZZ (must be capital letters).
    # Verify by using
    crontab -l.
