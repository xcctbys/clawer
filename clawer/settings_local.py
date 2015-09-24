#encoding=utf-8

from settings import *

import djcelery
djcelery.setup_loader()


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'clawer',                      # Or path to database file if using sqlite3.
        'USER': 'cacti',                      # Not used with sqlite3.
        'PASSWORD': 'cacti',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'KEY_PREFIX': "crawler",
        'LOCATION': [
            '127.0.0.1:11211',
        ],
    }
}

PYTHON = "/Users/pengxt/Documents/pyenv/dj14/bin/python"
CRONTAB_USER = "pengxt"
CLAWER_SOURCE = "/Users/pengxt/Documents/clawer/source/"
CLAWER_RESULT = "/Users/pengxt/Documents/clawer/result/"

BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERYD_TIMER_PRECISION = 1
TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'
CELERY_RESULT_BACKEND='djcelery.backends.cache:CacheBackend'
CELERYD_MAX_TASKS_PER_CHILD = 1024
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']


MEDIA_URL = 'http://localhost:8000/media/'

REDIS = "redis://localhost:6379//0"
URL_REDIS = "redis://localhost:6379//1"


RAVEN_CONFIG = {
    'dsn': 'http://c63b0d71513f4569b661e81bcfe8f903:c16131fe0f8d4195b0ea8be642aaa419@coredump.51zhi.com//4',
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(pathname)s:%(lineno)d:: %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(os.path.dirname(__file__), "clawer.debug.log"),
            'backupCount': 1,
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
        'dbfile': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(os.path.dirname(__file__), "db.debug.log"),
            'backupCount': 1,
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        '': {
            'handlers':['file'],
            'propagate': True,
            'level':'DEBUG',
        },
        'django': {
            'handlers':['null'],
            'propagate': True,
            'level':'DEBUG',
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['dbfile'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}