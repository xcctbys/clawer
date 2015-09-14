#encoding=utf-8

from settings import *

import djcelery
djcelery.setup_loader()

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'clawer',                      # Or path to database file if using sqlite3.
        'USER': 'dev',                      # Not used with sqlite3.
        'PASSWORD': 'dev012131',                  # Not used with sqlite3.
        'HOST': 'rds023qjrzl93g2hjq61.mysql.rds.aliyuncs.com',                      # Set to empty string for localhost. Not used with sqlite3.
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

MEDIA_ROOT = "/data/media/"
MEDIA_URL = "http://clawer.princetechs.com/media/"

PYTHON = "/home/virtualenvs/py27/bin/python"
CRONTAB_USER = "nginx"
CLAWER_SOURCE = "/data/clawer/"
CLAWER_RESULT = "/data/clawer_result/"

#for celeryd
BROKER_URL = 'redis://10.171.34.147:6379/0'
CELERY_RESULT_BACKEND='djcelery.backends.cache:CacheBackend'
CELERYD_TIMER_PRECISION = 1
TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'
CELERYD_MAX_TASKS_PER_CHILD = 1024
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']


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
            'filename': os.path.join("/home/web_log/nice-clawer/", "clawer.pro.log"),
            'backupCount': 24,
            'formatter': 'verbose',
            'level': 'ERROR',
        },
    },
    'loggers': {
        '': {
            'handlers':['file'],
            'propagate': True,
            'level':'ERROR',
        },
        'django': {
            'handlers':['null'],
            'propagate': True,
            'level':'ERROR',
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}