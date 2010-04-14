# -*- encoding: utf-8 -*-
from optparse import make_option

from webfaction.utils import get_projectname
from webfaction.conf import settings
from webfaction.management.base import WFBaseCommand


class Command(WFBaseCommand):
    custom_option_list = (
        make_option('--dbengine', action='store', dest='dbengine', 
            help='WebFaction database engine.'),
        make_option('--dbname', action='store', dest='dbname', 
            help='WebFaction database name.'),
        make_option('--dbpass', action='store', dest='dbpass', 
            help='WebFaction database password.'),
    )
    option_list = WFBaseCommand.option_list + custom_option_list
    
    WFBaseCommand.messages.update({
        'dbengine_empty': 'No database engine was suplied.',
        'dbname_empty': 'No database name was suplied.',
        'dbpass_empty': 'No database password was suplied.',
        },)
    
    def create_database(self,dbname, dbpass, dbengine):
        try:
            wfdb = self.machine.create_database(dbname, dbpass, dbengine.split("_")[0])
        except:
            self.machine.raise_error(self.messages['command_fail'] % 'Unknown')
            return None
        return wfdb
    
    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)
        self.run(*args, **options)
    
    def get_default_dbname(self):
        return self.machine.user.username + '_' + get_projectname()
    
    def run(self, *args, **options):
        try:
            dbengine = options.get('dbengine', None)
            if not dbengine:
                try:
                    dbengine = settings.DATABASE_ENGINE
                except:
                    dbengine = settings.DEFAULT_DJANGO_DATABASE_ENGINE
                    self.machine.raise_error(self.messages['dbengine_empty'])
            if dbengine is None or len(dbengine) <= 0:
                dbengine = settings.DEFAULT_DJANGO_DATABASE_ENGINE

            dbname = options.get('dbname', None)
            if not dbname:
                try:
                    dbname = settings.DATABASE_NAME
                except:
                    dbname = self.get_default_dbname()
                    self.machine.raise_error(self.messages['dbname_empty'])
            if dbname is None or len(dbname) <= 0:
                dbname = self.get_default_dbname()

            dbpass = options.get('dbpass', None)
            if not dbpass:
                try:
                    dbpass = settings.DATABASE_PASSWORD.replace(" ","")
                except:
                    dbpass = settings.DEFAULT_DJANGO_DATABASE_PASSWORD
                    self.machine.raise_error(self.messages['dbpass_empty'])
            if len(dbpass) <= 0:
                dbpass = settings.DEFAULT_DJANGO_DATABASE_PASSWORD
                
            return self.create_database(dbname, dbpass, dbengine.split("_")[0])
        except Exception, error:
            self.machine.raise_error(self.messages['command_fail'] % str(error))

