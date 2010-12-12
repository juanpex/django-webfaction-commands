# -*- encoding: utf-8 -*-
from optparse import make_option
from webfaction.conf import settings
from webfaction.utils import get_projectname, append_to_option_list
from webfaction.management.base import WFBaseCommand


class Command(WFBaseCommand):

    custom_option_list = (
        make_option('--fullurl', action='store', dest='fullurl',
            help='Full URL. (optional)'),
        make_option('--domain', action='store', dest='domain',
            help='Domain for subdomain. (optional)'),
        make_option('--subdomain', action='store', dest='subdomain',
            help='Subdomain name. (optional)'),
    )
    option_list = append_to_option_list(WFBaseCommand.option_list, custom_option_list)

    WFBaseCommand.messages.update({
        'domain_empty': 'No domain was suplied.',
        'subdomain_empty': 'No subdomain was suplied.',
        'domain_invalid': 'Domain "%s" is not valid.',
        'subdomain_invalid': 'Subdomain "%s" is not valid.',
        },)

    def create_subdomain(self, subdomain, domain):
        return self.machine.create_subdomain(subdomain, domain)

    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)
        self.run(*args, **options)

    def get_related_options(self, **options):
        try:
            self.fullurl = options.get('domain', None)
            if self.fullurl is None:
                try:
                    self.fullurl = settings.WEBFACTION_URL
                except:
                    try:
                        domain = settings.WEBFACTION_DOMAIN
                    except:
                        domain = options.get('domain', None)
                    if not domain is None:
                        try:
                            subdomain = settings.WEBFACTION_SUBDOMAIN
                        except:
                            subdomain = options.get('subdomain', None)
                        if subdomain is None:
                            try:
                                subdomain = settings.WEBFACTION_APPNAME
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
            return {'fullurl':fullurl, 'subdomain':subdomain, 'domain':domain}
        except Exception, error:
            self.machine.raise_error(self.messages['command_fail'] % str(error))

    def run(self, *args, **options):
        try:
            conf = self.get_related_options(**options)
            self.create_subdomain(conf['subdomain'], conf['domain'])
        except Exception, error:
            self.machine.raise_error(self.messages['command_fail'] % str(error))
