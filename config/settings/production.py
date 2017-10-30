from .base import *

ALLOWED_HOSTS = ['*']
SECRET_KEY = env('DJANGO_SECRET_KEY')

MIDDLEWARE = [MIDDLEWARE[0]] + ['whitenoise.middleware.WhiteNoiseMiddleware'] + MIDDLEWARE[1:]
