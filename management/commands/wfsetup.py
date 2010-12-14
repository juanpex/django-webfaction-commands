# -*- encoding: utf-8 -*-
from optparse import make_option

from webfaction.utils import get_projectname, append_to_option_list
from webfaction.conf import settings
from webfaction.management.base import WFBaseCommand


class Command(WFBaseCommand):
    custom_option_list = (
        make_option('--djangoversion', action='store', dest='djangoversion',
            help='WebFaction django version.'),
        make_option('--checkout', action='store', dest='checkout',
            help='WebFaction checkout command.'),
    )
    option_list = append_to_option_list(WFBaseCommand.option_list, custom_option_list)

    WFBaseCommand.messages.update({
        'djangoversion_empty': 'No DJANGO VERSION was suplied.',
        'checkout_empty': 'No COMMAND CHECKOUT was suplied.',
    },)

    def setup_project(self, djangosite, appname, checkout, dbengine, dbname, dbusername, dbpass, djangoversion):
        app_path = djangosite.get_app_path()
        project_path = "%s/%s/" % (app_path, appname)
        djangosite.machine.replace_in_file('%s/myproject.wsgi' % app_path,'myproject', appname)
        try:
            djangosite.machine.replace_in_file('%s/myproject.wsgi' % app_path,'myproject', appname)
        except:
            pass
        djangosite.machine.system("cd %s && rm -rf myproject" % app_path)
        cmd = 'cd %s && %s' % (app_path, checkout)
        djangosite.machine.raise_success('Executing command: %s' % cmd)
        djangosite.machine.system(cmd)
        dbengine = "postgresql_psycopg2" if "postgresql" in dbengine else dbengine
        ls_data = djangosite.machine.get_localsettings()
        djangosite.machine.system('rm %s%s' % (project_path, 'local_settings.py*'), False, showerror=False)
        djangosite.machine.raise_success('Editing file local_settings.py')
        djangosite.machine.system('touch %s%s' % (project_path, 'local_settings.py'))
        djangosite.machine.write_file(project_path, '/local_settings.py', ls_data % (dbengine, dbname, dbusername, dbpass))
        djangosite.machine.raise_success('Creating links...')
        djangosite.machine.system('cd %s && ln -s ../apache2/bin/restart r' % (project_path), False)
        djangosite.machine.system('cd && ln -s %s %s' % (project_path, appname), False)
        djangosite.machine.system('cd && touch %s/.pgpass' % djangosite.machine.user.home)
        djangosite.machine.clear_pgpassfile(dbusername)
        djangosite.machine.write_file(djangosite.machine.user.home, '/.pgpass', 'localhost:*:%s:%s:%s\n' % (dbusername, dbname, dbpass))
        djangosite.machine.system('cd && chmod 600 %s/.pgpass' % djangosite.machine.user.home)
        djangosite.machine.raise_success('Installing django')
        djangosite.machine.system('cd %s/lib/python2.5/ && rm -rf django' % (app_path))
        djangosite.machine.system('cd %s/lib/python2.5/ && wget http://www.djangoproject.com/download/%s/tarball/' % (app_path, djangoversion),showerror=False)
        djangosite.machine.system('cd %s/lib/python2.5/ && tar xzvf Django-%s.tar.gz' % (app_path, djangoversion))
        djangosite.machine.system('cd %s/lib/python2.5/ && rm Django-%s.tar.gz' % (app_path, djangoversion))
        djangosite.machine.system('cd %s/lib/python2.5/ && mv Django-%s/django/ .' % (app_path, djangoversion))
        djangosite.machine.system('cd %s/lib/python2.5/ && rm -rf Django-%s' % (app_path, djangoversion))
        djangosite.machine.system('cd && ln -s %s %s' % (project_path, appname))
        djangosite.machine.system("cd %s && python2.5 manage.py syncdb" % project_path, showerror=False)
        djangosite.machine.raise_success('Setup Done')



    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)
        self.run(*args, **options)

    def get_related_options(self, **options):
        try:
            djangoversion = options.get('djangoversion', None)
            if not djangoversion:
                try:
                    djangoversion = settings.WEBFACTION_DJANGO_VERSION
                except:
                    pass
            if djangoversion is None or len(djangoversion) <= 0:
                djangoversion = settings.DEFAULT_WEBFACTION_DJANGO_VERSION
            if djangoversion is None or len(djangoversion) <= 0:
                self.machine.raise_error(self.messages['dbengine_empty'])

            checkout = options.get('checkout', None)
            if not checkout:
                try:
                    checkout = settings.WEBFACTION_COMMAND_CHECKOUT
                except:
                    self.machine.raise_error(self.messages['checkout_empty'])

            return {'djangoversion':djangoversion,'checkout':checkout}
        except Exception, error:
            self.machine.raise_error(self.messages['command_fail'] % str(error))

    def run(self, *args, **options):
        try:
            conf = self.get_related_options(**options)
            options.update(conf)
            kwlist = ('djangosite', 'appname', 'checkout', 'dbengine', 'dbname', 'dbusername', 'dbpass', 'djangoversion')
            kw = {}
            for k in kwlist:
                kw[k] = options[k]
            return self.setup_project(**kw)
        except Exception, error:
            self.machine.raise_error(self.messages['command_fail'] % str(error))
