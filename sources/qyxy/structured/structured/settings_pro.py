#encoding=utf-8

from settings import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'clawer',
        'USER': 'cacti',
        'PASSWORD': 'cacti',
        'HOST': '10.100.80.50',
        'PORT': '3306',
    }
}

