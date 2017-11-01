from .base import *

DEBUG = env.bool('DJANGO_DEBUG', default=True)
SECRET_KEY = env('DJANGO_SECRET_KEY', default='development_key')

BROKER_URL = env('CLOUDAMQP_URL', default='amqp://guest:guest@localhost//')
CELERY_RESULT_BACKEND = env('CLOUDAMQP_URL', default='amqp://guest:guest@localhost//')
