# -*- coding: utf-8 -*-
from settings import *
import logging


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'enterprise',
        'USER': 'cacti',
        'PASSWORD': 'cacti',
        'HOST': '10.100.80.50',
        'PORT': '3306',
    }
}

JSONS_URL = 'http://10.100.90.51:8080/media/clawer_result/enterprise/json'

LOG_LEVEL = logging.ERROR
LOG_FORMAT = '%(asctime)s %(name)s %(levelname)s %(pathname)s:%(lineno)d:: %(message)s'
LOG_FILE = 'structured.log'
logger = None

EMAIL_HOST = 'smtp.exmail.qq.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'robot@princetechs.com'
EMAIL_HOST_PASSWORD = 'Robot0023'

ADMINS = (
    ('admin', 'zhongyid@princetechs.com'),
    ('admin', 'yijiadw@princetechs.com'),
)
