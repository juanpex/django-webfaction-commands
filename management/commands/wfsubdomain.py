# -*- encoding: utf-8 -*-
from optparse import make_option

from webfaction.utils import get_projectname
from webfaction.management.base import WFBaseCommand


class Command(WFBaseCommand):
    
    custom_option_list = (
        make_option('--domain', action='store', dest='domain',
            help='Domain for subdomain. (optional)'),
        make_option('--subdomain', action='store', dest='subdomain',
            help='Subdomain name. (optional)'),
    )
    option_list = WFBaseCommand.option_list + custom_option_list
    
    WFBaseCommand.messages.update({
        'domain_empty': 'No domain was suplied.',
        'subdomain_empty': 'No subdomain was suplied.',
        'domain_invalid': 'Domain "%s" is not valid.',
        'subdomain_invalid': 'Subdomain "%s" is not valid.',
        },)
    
    def create_subdomain(self, subdomain, domain):
        if not self.machine.create_subdomain(subdomain, domain):
            self.machine.raise_error(self.messages['command_fail'] % 'Unknown')
            return False
        return True            

    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)
        self.run(*args, **options)
    
    def run(self, *args, **options):
        try:
            self.fullurl = None
            try:
                self.fullurl = self.settings.WEBFACTION_URL
            except:
                domain = options.get('domain', None)
                if not domain is None:
                    subdomain = options.get('subdomain', None)
                    if subdomain is None:
                        try:
                            subdomain = self.settings.WEBFACTION_APPNAME    
                        except:
                            subdomain = get_projectname()
                    self.fullurl = "%s.%s" % (subdomain, domain)
                else:
                    self.machine.raise_error(self.messages['domain_empty'])
            
            if self.fullurl is None:
                return self.machine.raise_error('Invalid url to create subdomain (%s)' & self.fullurl)
            
            auxurl = self.fullurl.split("//")
            auxurl.reverse()
            fullurl = auxurl[0]
            subdomain = fullurl.split(".")[0]
            domain = ".".join(fullurl.split(".")[1:])
            self.fullurl = "%s.%s" % (subdomain, domain)
            self.create_subdomain(subdomain, domain)
        except Exception, error:
            self.machine.raise_error(self.messages['command_fail'] % str(error))
    

