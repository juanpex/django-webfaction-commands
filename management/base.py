# -*- encoding: utf-8 -*-
import logging

from optparse import make_option
from django.core.management.base import CommandError, BaseCommand

from webfaction.models import WFMachine
from webfaction.conf import settings

class WFBaseCommand(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--hostname', '-H', action='store', dest='hostname', 
            help='WebFaction account hostname.'),
        make_option('--username', '-u', '-U', action='store', dest='username', 
            help='WebFaction account username.'),
        make_option('--password', '-p', '-P', action='store', dest='password', 
            help='WebFaction account password.'),
        make_option('--safemode', action='store_true', dest='safemode', 
            help='Run command in safe mode.'),
    )
    
    messages = {
        'command_fail': 'Command: %s',
        'login_fail': 'Login FAIL!',    
    }
    
    def __init__(self, *args, **kwargs):
        super(WFBaseCommand, self).__init__(*args, **kwargs)
        try:
            self.is_test = settings.WEBFACTION_TEST
        except:
            # For security default is testing
            self.is_test = True
            
    
    def handle(self, *args, **options):
        if 'machine' in options:
            machine = options.get('machine', None)
            if machine:
                try:
                    machine.check_connection()
                    self.machine = machine
                    return
                except:
                    pass
        
        machine = WFMachine()
        machine.is_test = self.is_test
        if machine.is_test:
            machine.raise_log('TESTING')
        else:
            machine.RAISE_ERROR = CommandError
            
        
        hostname = options.get('hostname', None)
        if hostname is None:
            try:
                hostname = settings.WEBFACTION_HOSTNAME
            except:
                return machine.raise_error('You need a hostname to connect.')
        self.hostname = hostname
        
        username = options.get('username', None)
        if username is None:
            try:
                username = settings.WEBFACTION_USERNAME
            except:
                return machine.raise_error('You need a username to connect.')
        self.username = username
        
        password = options.get('password', None)
        if password is None:
            try:
                password = settings.WEBFACTION_PASSWORD
            except:
                return machine.raise_error('You need a password to connect.')
        self.password = password                
                
        machine.safemode = options.get('safemode', False)
        if machine.safemode:
            machine.raise_log('SAFEMODE')
        if not machine.login(username, password, hostname):
            machine.safemode = False
            return machine.raise_error(messages['login_fail'])
        self.machine = machine
