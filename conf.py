# -*- coding: utf-8 -*-
from miles.conf.appsettings import AppSettings


class WFSettings(AppSettings):

    WEBFACTION_TEST = True

    DEFAULT_DJANGO_APPNAME = 'site'
    DEFAULT_DJANGO_DATABASE_ENGINE = 'postgresql_psycopg2'
#    DEFAULT_DJANGO_DATABASE_PASSWORD = 'A1b2C3d4'

    DJANGO_APP_MAIN_TYPE = 'djangotrunk_mw25_25'
    DJANGO_APP_MEDIA_TYPE = 'symlink_static_only'

settings = WFSettings()
