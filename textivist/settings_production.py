import os

try:
    from settings import *
except ImportError:
    pass

# Celery Settings
CELERY_BROKER_URL = 'redis://redis-dev.4nnstd.0001.euw2.cache.amazonaws.com:6379/0'

ALLOWED_HOSTS = [
    '127.0.0.1',
    'www.textivist.net',
    'ec2-52-56-202-26.eu-west-2.compute.amazonaws.com'
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'textivist',
        'USER': os.environ['POSTGRES_DB_USER'],
        'PASSWORD': os.environ['POSTGRES_DB_PASS'],
        'HOST': 'testdb.cetagxa0mogt.eu-west-2.rds.amazonaws.com',
        'PORT': '',  # Set to empty string for default.
    }
}

