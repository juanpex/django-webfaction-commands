# -*- encoding: utf-8 -*-
from optparse import make_option


from webfaction.utils import ( email_valid, get_projectname,
    get_django_media_path, get_django_admin_media_path, append_to_option_list)

from webfaction.management.base import WFBaseCommand
from webfaction.conf import settings


class Command(WFBaseCommand):
    custom_option_list = (
        make_option('--appname', '-A', action='store', dest='appname',
            help='WebFaction project name.'),
        make_option('--fullurl', action='store', dest='fullurl',
            help='Url asociated to website.'),
    )
    option_list = append_to_option_list(WFBaseCommand.option_list, custom_option_list)

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

        djangomedia = self.machine.create_app(appname + '_django' + '_media',
            settings.DJANGO_APP_MEDIA_TYPE, get_django_media_path(self.machine.user.username, appname), '/media')
        if not djangomedia:
            self.machine.raise_error(self.messages['command_fail'] % 'Unknown on djangomedia')

        djangoadminmedia = self.machine.create_app(appname + '_django' + '_admin_media',
            settings.DJANGO_APP_MEDIA_TYPE, get_django_admin_media_path(self.machine.user.username, appname), '/admin_media')
        if not djangoadminmedia:
            self.machine.raise_error(self.messages['command_fail'] % 'Unknown on djangoadminmedia')

        fullurl = fullurl.replace("http://","")
        fullurl = fullurl.replace("https://","")
        if not self.machine.create_website(appname, [fullurl,], [djangosite, djangomedia, djangoadminmedia]):
            self.machine.raise_error(self.messages['command_fail'] % 'Unknown on website')

        return {'djangosite': djangosite,'djangomedia': djangomedia,'djangoadminmedia': djangoadminmedia}

    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)
        return self.run(*args, **options)

    def get_related_options(self, **options):
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
            return {'appname':appname,'fullurl':fullurl}
        except Exception, error:
            self.machine.raise_error(self.messages['command_fail'] % error)

    def run(self, *args, **options):
        try:
            conf = self.get_related_options(**options)
            return self.create_djangoapp(conf['appname'], conf['fullurl'])
        except Exception, error:
            self.machine.raise_error(self.messages['command_fail'] % error)
