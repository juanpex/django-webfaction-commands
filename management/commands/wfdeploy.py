# -*- encoding: utf-8 -*-
from optparse import make_option

from webfaction.conf import settings
from webfaction.utils import email_valid, append_to_option_list
from webfaction.management.base import WFBaseCommand

from webfaction.management.commands.wfemail import Command as WFEmail
from webfaction.management.commands.wfmailbox import Command as WFMailBox
from webfaction.management.commands.wfdjangoapp import Command as WFDjangoApp
from webfaction.management.commands.wfsubdomain import Command as WFSubDomain
from webfaction.management.commands.wfdatabase import Command as WFDatabase
from webfaction.management.commands.wfsetup import Command as WFSetup

class Command(WFBaseCommand):
    custom_option_list = (
        make_option('-u', action='store_true', dest='dosubdomain',
            help='WebFaction subdomain.'),
        make_option('-e', action='store_true', dest='doemail',
            help='WebFaction email.'),
        make_option('-a', action='store_true', dest='dodjangoapp',
            help='WebFaction django app.'),
        make_option('-d', action='store_true', dest='dodatabase',
            help='WebFaction database.'),
        make_option('-s', action='store_true', dest='dosetup',
            help='WebFaction setup.'),
        make_option('--all', action='store_true', dest='doall', default=False,
            help='WebFaction all options true.'),
    )
    option_list = append_to_option_list(WFBaseCommand.option_list, custom_option_list)
    option_list = append_to_option_list(option_list, WFEmail.custom_option_list)
    option_list = append_to_option_list(option_list, WFDjangoApp.custom_option_list)
    option_list = append_to_option_list(option_list, WFSubDomain.custom_option_list)

    washandle = False
    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)
        self.washandle = True
        self.run(*args, **options)

    def run(self, *args, **options):
        conf = {}
        if 'machine' in options:
            self.machine = options['machine']
        elif hasattr(self, 'machine'):
            m = getattr(self, 'machine')
            if m:
                options['machine'] = m


        task = WFSubDomain()
        if self.washandle and (options.get('dosubdomain', False) or options.get('doall')):
            task.handle(*args, **options)
            options.update({'machine': task.machine})
        conf.update(task.get_related_options(**options))

        task = WFEmail()
        if self.washandle and (options.get('doemail', False) or options.get('doall')):
            task.handle(*args, **options)
            options.update({'machine': task.machine})
        conf.update(task.get_related_options(**options))

        task = WFDjangoApp()
        if self.washandle and (options.get('dodjangoapp', False) or options.get('doall')):
            apps = task.handle(*args, **options)
            options.update(apps)
            options.update({'machine': task.machine})
        conf.update(task.get_related_options(**options))

        task = WFDatabase()
        if self.washandle and (options.get('dodatabase', False) or options.get('doall')):
            task.handle(*args, **options)
            options.update({'machine': task.machine})
        conf.update(task.get_related_options(**options))
        task = WFSetup()
        if self.washandle and (options.get('dosetup', False) or options.get('doall')):
            if 'djangosite' not in options:
                task_apps = WFDjangoApp()
                temp_options = dict(options)
                temp_options['safemode'] = True
                apps = task_apps.handle(*args, **options)

                options.update(apps)
            options.update(conf)
            task.handle(*args, **options)
            options.update({'machine': task.machine})
        if self.washandle:
            conf.update(task.get_related_options(**options))
        return conf
