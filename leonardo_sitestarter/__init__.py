
from django.apps import AppConfig

default_app_config = 'leonardo_sitestarter.Config'


LEONARDO_APPS = ['leonardo_sitestarter']

LEONARDO_MIDDLEWARES = [
    'leonardo_sitestarter.middleware.QuickStartMiddleware'
]


class Config(AppConfig):
    name = 'leonardo_sitestarter'
    verbose_name = "leonardo-sitestarter"
