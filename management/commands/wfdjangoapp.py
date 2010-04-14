# -*- encoding: utf-8 -*-
from optparse import make_option


from webfaction.utils import ( email_valid, get_projectname, 
    get_django_media_path, get_django_admin_media_path)

from webfaction.management.base import WFBaseCommand
from webfaction.conf import settings


class Command(WFBaseCommand):
    custom_option_list = (
        make_option('--appname', '-a', '-A', action='store', dest='appname', 
            help='WebFaction project name.'),
        make_option('--fullurl', action='store', dest='fullurl', 
            help='Url asociated to website.'),
    )
    option_list = WFBaseCommand.option_list + custom_option_list
    
    WFBaseCommand.messages.update({
        'appname_empty': 'No application name was suplied.',
        'appname_invalid': 'Application name "%s" already exist.',
        'fullurl_empty': 'No URL was suplied.',
        'fullurl_invalid': 'URL "%s" does not exist.',
        },)
    
    def create_djangoapp(self, appname, fullurl):
        djangosite = self.machine.create_app(appname + '_django', 
            settings.DJANGO_APP_MAIN_TYPE)
        if not djangosite:
            self.machine.raise_error(self.messages['command_fail'] % 'Unknown on djangosite')
            return False
        djangomedia = self.machine.create_app(appname + '_django' + '_media', 
            settings.DJANGO_APP_MEDIA_TYPE, get_django_media_path(self.machine.user.username, appname), '/media')
        if not djangomedia:
            self.machine.raise_error(self.messages['command_fail'] % 'Unknown on djangomedia')
            return False
        djangoadminmedia = self.machine.create_app(appname + '_django' + '_admin_media', 
            settings.DJANGO_APP_MEDIA_TYPE, get_django_admin_media_path(self.machine.user.username, appname), '/admin_media')
        if not djangoadminmedia:
            self.machine.raise_error(self.messages['command_fail'] % 'Unknown on djangoadminmedia')
            return False
        if not self.machine.create_website(appname, [fullurl,], [djangosite, djangomedia, djangoadminmedia]):
            self.machine.raise_error(self.messages['command_fail'] % 'Unknown on website')
            return False
        return True            
    
    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)
        self.run(*args, **options)
    
    def run(self, *args, **options):
        try:
            appname = options.get('appname', None)
            if appname is None:
                try:
                    appname = settings.WEBFACTION_APPNAME
                except:
                    appname = get_projectname()

            fullurl = options.get('fullurl', None)
            if fullurl is None:
                try:
                    fullurl = settings.WEBFACTION_URL
                except:
                    return self.machine.raise_error(self.messages['fullurl_empty'])
            self.create_djangoapp(appname, fullurl)
        except Exception, error:
            self.machine.raise_error(self.messages['command_fail'] % error)

