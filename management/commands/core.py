# -*- encoding: utf-8 -*-
import xmlrpclib
import logging
import socket

DEFAULT_DJANGO_APPNAME = 'django_database'
DEFAULT_DJANGO_DATABASE_ENGINE = 'sqlite'
DEFAULT_DJANGO_DATABASE_PASSWORD = ''


DJANGO_APP_MAIN_TYPE = 'djangotrunk_mw25_25'
DJANGO_APP_MEDIA_TYPE = 'symlink_static_only'


def logginginfo(text):
    print text

class WebFactionUser(object):

    def __init__(self, *args, **kwargs):
        self.username = kwargs.get('username', None)
        self.home = '%s/%s' % (kwargs.get('home', None), self.username)
        self.web_server = kwargs.get('web_server', None)
        self.mail_server = kwargs.get('mail_server', None)

class WebFactionApp(object):

    def __init__(self, machine, name, type, extradata='', url='/'):
        self.machine = machine
        self.name = name
        self.type = type
        self.extradata = extradata
        self.url = url

    def get_app_path(self):
        return "%s/webapps/%s" % (self.machine.user.home, self.name)

class WebFactionWebSite(object):

    def __init__(self, name, domines, apps):
        self.name = name
        self.domines = domines
        self.apps = apps

class WebFactionMachine(object):

    session = None

    def __init__(self, username=None, password=None, machinename=None):
        self.username = username
        self.password = password
        self.machinename = machinename

    def check_connection(self):
        if self.session is None:
            raise ValueError('No connected')
        return True

    def login(self, username=None, password=None, machinename=None):
        if username:
            self.username = username
        if password:
            self.password = password
        if machinename:
            self.machinename = machinename
        if not self.username:
            raise ValueError('No username')
        if not self.password:
            raise ValueError('No username')
        self.server = xmlrpclib.ServerProxy('https://api.webfaction.com/')
        data = self.server.login(self.username, self.password, self.machinename)
        self.session = data[0]
        self.user = WebFactionUser(**data[1])
        self.server_ip = socket.gethostbyaddr('%s.webfaction.com' % self.user.web_server)[2][0]
        logginginfo("Logged on %s.webfaction.com as %s" % (self.user.web_server, self.username))
        return True

    def create_app(self, name, type='static', extradata='', url='/', get_or_add=False):
        self.check_connection()
        if not name or len(name)<=0:
            raise ValueError("Application need a name")
        try:
            wf_app = [x for x in self.server.list_apps(self.session) if x['name'] == name][0]
        except IndexError:
            wf_app = None
        if wf_app:
            if get_or_add:
                new_app = WebFactionApp(self, name, type, extradata, url)
                logginginfo("Application %s was load." % name)
            else:
                raise ValueError('ERROR: The appname %s already exists.' % name)
        else:
            self.server.create_app(self.session, name, type, False, extradata)
            new_app = WebFactionApp(self, name, type, extradata, url)
            logginginfo("Application %s was created." % name)
        return new_app

    def get_or_create_app(self, name, type='static', extradata='', url='/'):
        return self.create_app(name, type, extradata, url, get_or_add=True)

    def create_website(self, name, domains, apps=[], get_or_add=False):
        self.check_connection()
        if not name or len(name)<=0:
            raise ValueError("Website need a name")
        if not apps or len(apps)<=0:
            raise ValueError("Webbsite needs almost one app")
        if not domains or len(domains)<=0:
            raise ValueError("Webbsite needs apps with some domain")
        try:
            wf_website =  [x for x in self.server.list_websites(self.session) if x['name'] == name][0]
        except IndexError:
            wf_website = None
        if wf_website:
            if get_or_add:
                new_website = WebFactionWebSite(name, domains, apps)
                logginginfo("Website %s was load." % name)
            else:
                raise ValueError('ERROR: The website %s already exists.' % name)
        else:
            kwapps = tuple([(a.name, a.url) for a in apps])
            self.server.create_website(self.session, name, self.server_ip, False, domains, *kwapps)
            logginginfo("Website %s was created." % name)
            new_website = WebFactionWebSite(name, domains, apps)
        return new_website

    def create_database(self, name, password, engine=None):
        self.check_connection()
        if not name or len(name)<=0:
            raise ValueError("Database need a name")
        if not name.startswith(self.user.username):
            name = self.user.username + '_' + name
        if name in [x['name'] for x in self.server.list_dbs(self.session)]:
             logginginfo('WARNING: The database %s already exists.' % (name))
        else:
            if not engine or len(engine.replace(" ",""))<=0:
                engine = 'sqlite3'
            self.server.create_db(self.session, name, engine , password)
            logginginfo("(%s) Database %s was created with password: %s" % (engine, name, password))
        return (engine, name, password)

    def create_subdomain(self, name, domainname):
        self.check_connection()
        if not name or len(name)<=0:
            raise ValueError("Subdomain need a name")
        if not domainname or len(domainname)<=0:
            raise ValueError("Subdomain need a domain")
        try:
            domain = [k for k in self.server.list_domains(self.session) if k['domain'] == domainname][0]
        except IndexError:
            raise ValueError('The domain %s does not exists.' % domainname)
        if name in domain['subdomains']:
            logginginfo('WARNING: The subdomain %s.%s already exists.' % (name, domainname))
        else:
            self.server.create_domain(self.session, domainname, name)
            logginginfo("Subdomain %s.%s was created." % (name, domainname))
        return True



        """
        create_email(
            session_id,
            email_address,
            targets, # "pepe@pepe.com.uy, lala@lala.net"
            autoresponder_on=False, # Opcional
            autoresponder_subject='', # Requerido si autoresponder_on=True
            autoresponder_message='', # Requerido si autoresponder_on=True
            autoresponder_from='' # Requerido si autoresponder_on=True
            )

        Create an email address which delivers to the specified mailboxes.

        If autoresponder_on is True, then an autoresponder subject, message, and from address may be specified.
        Parameters:

            * session_id – session ID returned by login()
            * email_address – an email address (for example, name@mydomain.tld)
            * targets (string) – names of destination mailboxes, addresses, or scripts, separated by commas
            * autoresponder_on (boolean) – whether an autoresponder is enabled for the address
            * autoresponder_subject – subject line of the autoresponder message
            * autoresponder_message – body of the autoresponder message
            * autoresponder_from – originating address of the autoresponder message
        """
    def create_email(self, email_address):
        self.check_connection()
        if not email_address or len(email_address)<=0:
            raise ValueError("Email need a address")
        if email_address in [x['email_address'] for x in self.server.list_emails(self.session)]:
             logginginfo('WARNING: The email address %s already exists.' % (email_address))
        else:
            self.server.create_email(self.session, email_address)
            logginginfo("Email address %s was created." % (email_address))
        return True



    def system(self, cmd):
        self.check_connection()
        logginginfo(cmd)
        self.server.system(self.session, cmd)

    def write_file(self, path, filename, data, mode='a'):
        self.check_connection()
        self.server.write_file(self.session, path + filename , data, mode)

    def replace_in_file(self, filename, antes, despues):
        self.check_connection()
        self.server.replace_in_file(self.session, filename, (antes, despues))
