# -*- encoding: utf-8 -*-
from optparse import make_option

from webfaction.conf import settings
from webfaction.utils import email_valid
from webfaction.management.base import WFBaseCommand

from webfaction.management.commands.wfemail import Command as WFEmail
from webfaction.management.commands.wfmailbox import Command as WFMailBox
from webfaction.management.commands.wfdjangoapp import Command as WFDjangoApp
from webfaction.management.commands.wfsubdomain import Command as WFSubDomain
from webfaction.management.commands.wfdatabase import Command as WFDatabase

class Command(WFBaseCommand):

    option_list = WFBaseCommand.option_list + \
        WFEmail.custom_option_list + \
        WFDjangoApp.custom_option_list + WFSubDomain.custom_option_list



    def handle(self, *args, **options):
        task = WFSubDomain()
        task.handle(*args, **options)
        options.update({'fullurl': task.fullurl, 'machine': task.machine})
        task = WFEmail()
        task.handle(*args, **options)
        task = WFDjangoApp()
        task.handle(*args, **options)
        task = WFDatabase()
        task.handle(*args, **options)
        
