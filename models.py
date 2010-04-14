# -*- coding: utf-8 -*-
import xmlrpclib
import logging
import socket

from webfaction.utils import *
from webfaction.conf import settings

from django.db import models
from django.core.management.base import CommandError, BaseCommand



class WFSession(object):
    
    def __init__(self, *args, **kwargs):
        self.session = kwargs.get('session', None)
        self.username = kwargs.get('username', None)
        self.home = '%s/%s' % (kwargs.get('home', None), self.username)
        self.web_server = kwargs.get('web_server', None)
        self.mail_server = kwargs.get('mail_server', None)

    def __call__(self):
        return self.session

    def __str__(self):
        data = {}
        for field in ('session', 'username', 'home', 'web_server', 'mail_server'):
            data[field] = getattr(self, field)
        return str(data)


class WFApp(object):
    
    def __init__(self, machine, name, type, extradata='', url='/'):
        self.machine = machine
        self.name = name
        self.type = type
        self.extradata = extradata
        self.url = url

    def get_app_path(self):
        return '%s/webapps/%s' % (self.machine.user.home, self.name)


class WFWebSite(object):
    
    def __init__(self, name, domines, apps):
        self.name = name
        self.domines = domines
        self.apps = apps

class WFDatabase(object):
    
    def __init__(self, engine, name, password):
        self.engine = engine
        self.name = name
        self.password = password


class WFMachine(object):

    session = None
    safemode = False
    is_test = True
    RAISE_ERROR = ValueError


    def __init__(self, username=None, password=None, machinename=None, *args, **kwargs):
        self.username = username
        self.password = password
        self.machinename = machinename
        self.style = custom_color_style()
            
    def raise_error(self, err_msg):
        if self.safemode:
            logginginfo(self.style.WARNING(str(u'*** WARGING *** %s\n' % err_msg)))
            return False
        else:
            raise self.RAISE_ERROR(err_msg)
        
    def raise_success(self, msg):
        logginginfo(self.style.SUCCESS(str(u'%s\n' % msg)))

    def raise_log(self, msg):
        logginginfo(str(u'%s\n' % msg))

    def check_connection(self):
        if self.user is None or self.user() is None:
            return self.raise_error('Not connected')
        return True
    
    def login(self, username=None, password=None, machinename=None):
        if username: 
            self.username = username
        if password:
            self.password = password
        if machinename:
            self.machinename = machinename
        
        if not self.username:
            return self.raise_error('No username')
        if not self.password:
            return self.raise_error('No password')
        if not self.machinename:
            return self.raise_error('No machine name')
        
        self.server = xmlrpclib.ServerProxy('https://api.webfaction.com/')
        try:
            if not self.is_test:
                data = self.server.login(self.username, self.password, self.machinename)
                kwargs = {'session': data[0], }
                kwargs.update(data[1])
                self.user = WFSession(**kwargs)
                self.server_ip = socket.gethostbyaddr('%s.webfaction.com' % self.user.web_server)[2][0]
            else:
                kwargs = {'session': 'sessing_id_test', 'username': 'test', 'home': '/home', 'web_server': self.machinename, 'mail_server': 'test'}
                self.user = WFSession(**kwargs)
                self.server_ip = '127.0.0.1'
        except xmlrpclib.Fault, error:
            return self.raise_error('WebFaction Error >>> "%s".' % (error))
        
        self.raise_success('Logged on %s.webfaction.com as %s' % (self.user.web_server, self.username))
        return True

    def create_app(self, name, type='static', extradata='', url='/'):
        self.check_connection()
        
        if not name or len(name) <= 0:
            return self.raise_error('Application need a name')
            
        if self.exists('application', name):
            if self.safemode:
                self.raise_log('Application "%s" was load.' % name)
                return WFApp(self, name, type, extradata, url)
            else:
                return self.raise_error('The appname "%s" already exists.' % name)

        if not self.is_test:
            try:
                self.server.create_app(self.user(), name, type, False, extradata)
            except xmlrpclib.Fault, error:
                return self.raise_error('WebFaction Error >>> "%s".' % (error))
        self.raise_success('Application "%s" was created.' % name)
        return WFApp(self, name, type, extradata, url)

    def create_website(self, name, domains, apps=[]):
        self.check_connection()
        
        if not name or len(name) <= 0:
            self.raise_error('Website need a name')
            return
            
        if not apps or len(apps) <= 0:
            return self.raise_error('Website needs almost one app')
            
        if not domains or len(domains) <= 0:
            return self.raise_error('Website needs apps with some domain')
            
        if self.exists('website', name):
            if self.safemode:
                self.raise_log('Website "%s" was load.' % name)
                return WFWebSite(name, domains, apps)
            else:
                return self.raise_error('The website "%s" already exists.' % name)

        kwapps = tuple([(a.name, a.url) for a in apps])
        if not self.is_test:
            try:
                self.server.create_website(self.user(), name, self.server_ip, False, domains, *kwapps)
            except xmlrpclib.Fault, error:
                return self.raise_error('WebFaction Error >>> "%s".' % (error))
        self.raise_success('Website "%s" was created.' % name)
        return WFWebSite(name, domains, apps)

    def create_database(self, name, password, engine=None):
        self.check_connection()
        
        if not name or len(name) <= 0:
            return self.raise_error('Database need a name')
        name = self.get_webfaction_name(name)
        
        dbdata = self.exists('database', name)
        if dbdata:
            if self.safemode:
                self.raise_log('Database "%s" was load.' % name)
                return WFDatabase(dbdata.db_type, dbdata.name, None)
            else:
                return self.raise_error('The database "%s" already exists.' % name)
        if not engine or len(engine.replace(" ","")) <= 0:
            engine = settings.DEFAULT_DJANGO_DATABASE_ENGINE
        if not self.is_test:
            try:
                self.server.create_db(self.user(), name, engine , password)
            except xmlrpclib.Fault, error:
                return self.raise_error('WebFaction Error >>> "%s".' % (error))
        self.raise_success('(%s) Database "%s" was created with password: "%s"' % (engine, name, password))
        return WFDatabase(engine, name, password)

    def create_subdomain(self, name, domainname):
        self.check_connection()
        
        if not name or len(name) <= 0:
            return self.raise_error('Subdomain need a name')
            
        if not domainname or len(domainname) <= 0:
            return self.raise_error('Subdomain need a domain')

        domain = self.exists('domain', domainname)
        if domain is None:
            return self.raise_error('The domain "%s" does not exists.' % domainname)
            
        if name in domain['subdomains']:
            return self.raise_error('The subdomain "%s.%s" already exists.' % (name, domainname))
            
        if not self.is_test:
            try:
                self.server.create_domain(self.user(), domainname, name)
            except xmlrpclib.Fault, error:
                return self.raise_error('WebFaction Error >>> "%s".' % (error))
        self.raise_success('Subdomain "%s.%s" was created.' % (name, domainname))
        return True

    def create_email(self, email_address, mailbox):
        self.check_connection()
        
        if not mailbox or len(mailbox) <= 0:
            return self.raise_error('Mailbox need a name')
        mailbox = self.get_webfaction_name(mailbox)
        
        if self.exists('mailbox', mailbox) is None:
            return self.raise_error('The mailbox "%s" does not exists.' % mailbox)
 
        if not email_address or len(email_address)<=0:
            return self.raise_error('Email need a address')
            
        if self.exists('email', email_address):
            return self.raise_error('The email "%s" already exists.' % (email_address))
            
        self.raise_log('Creating email "%s"...' % (email_address))
        if not self.is_test:
            try:
                self.server.create_email(self.user(), email_address, mailbox)
            except xmlrpclib.Fault, error:
                return self.raise_error('WebFaction Error >>> "%s".' % (error))
        self.raise_success('Email address "%s" was created.' % (email_address))
        return True

    def get_webfaction_name(self, name):
        if not name.startswith(self.user.username + '_'):
            name = self.user.username + '_' + name
        return name
        
    def create_mailbox(self, name):
        #FIX: Bug of python2.4 on rpc response allow_null
        return self.create_mailbox_python24(name)
        #################################################
        self.check_connection()
        
        if not name or len(name) <= 0:
            return self.raise_error('Mailbox need a name')
        name = self.get_webfaction_name(name)
        
        if self.exists('mailbox', name):
             return self.raise_error('The mailbox "%s" already exists.' % (name))

        self.raise_log('Creating mailbox "%s"...' % (name))
        if not self.is_test:
            try:
                self.server.create_mailbox(self.user(), name, enable_spam_protection=True, discard_spam=False, spam_redirect_folder='Spam')
            except xmlrpclib.Fault, error:
                return self.raise_error('WebFaction Error >>> "%s".' % (error))
        self.raise_success('Mailbox "%s" was created.' % (name))
        return True

    def system(self, cmd):
        self.check_connection()
        if not self.is_test:
            try:
                self.server.system(self.user(), cmd)
            except xmlrpclib.Fault, error:
                return self.raise_error('WebFaction Error >>> "%s".' % (error))
        self.raise_log('Executing "%s"' % cmd)

    def write_file(self, path, filename, data, mode='a'):
        self.check_connection()
        if not self.is_test:
            try:
                self.server.write_file(self.user(), path + filename, data, mode)
            except xmlrpclib.Fault, error:
                return self.raise_error('WebFaction Error >>> "%s".' % (error))
        self.raise_log('Editing "%s"' % path + filename)
        return True
        
    def replace_in_file(self, filename, antes, despues):
        self.check_connection()
        if not self.is_test:
            try:
                self.server.replace_in_file(self.user(), filename, (antes, despues))
            except xmlrpclib.Fault, error:
                return self.raise_error('WebFaction Error >>> "%s".' % (error))
        self.raise_log('Replacing on "%s" ' % filename)
        return True
    
    def exists(self, object_key, value):
        OBJECT_KEYS = {
        'mailbox': {'function': 'list_mailboxes', 'attrname': 'name'},
        'email': {'function': 'list_emails', 'attrname': 'email_address'},
        'domain': {'function': 'list_domains', 'attrname': 'domain'},
        'database': {'function': 'list_dbs', 'attrname': 'name'},
        'website': {'function': 'list_websites', 'attrname': 'name'},
        'application': {'function': 'list_apps', 'attrname': 'name'},
        }
        #FIX: Bug of python2.4 on rpc response allow_null
        if object_key == 'mailbox': 
            return value
        if object_key == 'email':
            return None
        #################################################
        self.check_connection()
        
        if not value or len(value) <= 0:
            return self.raise_log('%s needs a value' % object_key.title())
            
        self.raise_log('Checking %s on server...' % object_key)
        func = getattr(self.server, OBJECT_KEYS[object_key]['function'])
        field = OBJECT_KEYS[object_key]['attrname']
        try:
            if self.is_test:
                data = {}
                data[field] = ''
                if object_key == 'domain':
                    data[field] = value
                    data['subdomains'] = ['',]
                data = [data,]
            else:
                data = func(self.user())
        except xmlrpclib.Fault, error:
            return self.raise_error('WebFaction Error >>> "%s".' % (error))
        try:
            return [x for x in data if x[field] == value][0]
        except IndexError:
            return None

    def create_mailbox_python24(self, name):
        self.check_connection()
        
        if not name or len(name) <= 0:
            self.raise_log('Mailbox need a name')
        name = self.get_webfaction_name(name)
        
        self.raise_log('Creating mailbox "%s"...' % (name))
        try:
            if not self.is_test:
                self.server.create_mailbox(self.user(), name, True, False, 'Spam')
            self.raise_success('Mailbox "%s" was created.' % (name))
        except xmlrpclib.Fault, error:
            return self.raise_error('WebFaction Error >>> "%s".' % (error))
        return True

