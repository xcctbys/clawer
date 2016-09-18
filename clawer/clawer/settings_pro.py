# encoding=utf-8

from settings import *  # noqa


DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',                   # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'clawer',                                       # Or path to database file if using sqlite3.
        'USER': 'dachengmysqlserver%%dacheng',                  # Not used with sqlite3.
        'PASSWORD': 'daCheng!0527',                             # Not used with sqlite3.
        'HOST': 'dachengmysqlserver.mysqldb.chinacloudapi.cn',  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                                             # Set to empty string for default. Not used with sqlite3.
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

EMAIL_BACKEND = 'django_smtp_ssl.SSLEmailBackend'
EMAIL_HOST = 'smtp.exmail.qq.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'robot@princetechs.com'
EMAIL_HOST_PASSWORD = 'Robot0023'
USE_TLS = True


MEDIA_ROOT = "/data/media/"
MEDIA_URL = "http://clawer.princetechs.com/media/"

PYTHON = "/home/virtualenvs/py27/bin/python"
CRONTAB_USER = "nginx"
CLAWER_SOURCE = "/data/clawer/"
CLAWER_RESULT = "/data/clawer_result/"
CLAWER_RESULT_URL = "http://clawer.princetechs.com/media/clawer_result/"


REDIS = "redis://:uwKQJUC1RJxoKGtcP69oGLhyY2XumrfYp4WYtxgT9vU=@dacheng-redis.redis.cache.chinacloudapi.cn/0"
URL_REDIS = "redis://:uwKQJUC1RJxoKGtcP69oGLhyY2XumrfYp4WYtxgT9vU=@dacheng-redis.redis.cache.chinacloudapi.cn/1"
MONITOR_REDIS = "redis://:uwKQJUC1RJxoKGtcP69oGLhyY2XumrfYp4WYtxgT9vU=@dacheng-redis.redis.cache.chinacloudapi.cn/2"


CRONTAB_HOME = "/home/webapps/nice-clawer/confs/production"

CAPTCHA_STORE = "/data/media/captcha"


RAVEN_CONFIG = {
    'dsn': 'http://917b2f66b96f46b785f8a1e635712e45:556a6614fe28410dbf074552bd566750@sentry.princetechs.com//2',
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
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
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
            'handlers': ['file'],
            'propagate': True,
            'level': 'ERROR',
        },
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'ERROR',
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
