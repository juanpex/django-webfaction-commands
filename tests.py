# -*- encoding: utf-8 -*-
import unittest

from django.core.management import call_command


class WFMachineTestCase(unittest.TestCase):
    
    def setUp(self):
        self.kwargs = {}
        self.kwargs['hostname'] = 'test'
        self.kwargs['username'] = 'test'
        self.kwargs['password'] = 'test'
        self.kwargs['appname'] = 'test'
        self.kwargs['dbname'] = 'test'
        self.kwargs['domain'] = 'domain.com'
        self.kwargs['subdomain'] = 'site'
        self.kwargs['mailbox'] = 'mailbox_test'
        self.kwargs['email'] = 'test@domain.com'
        self.kwargs['fullurl'] = 'site.domain.com'
    
    def testSubDomain(self):
        call_command('wfsubdomain', **self.kwargs)

    def testMailbox(self):
        call_command('wfmailbox', **self.kwargs)

    def testEmail(self):
        call_command('wfemail', **self.kwargs)

    def testDjangoApp(self):
        call_command('wfdjangoapp', **self.kwargs)

    def testDatabase(self):
        call_command('wfdatabase', **self.kwargs)

    def testDeploy(self):
        call_command('wfdeploy', **self.kwargs)

