# -*- encoding: utf-8 -*-
from optparse import make_option

from webfaction.conf import settings
from webfaction.utils import email_valid, append_to_option_list
from webfaction.management.base import WFBaseCommand


class Command(WFBaseCommand):
    custom_option_list = (
        make_option('--mailbox', action='store', dest='mailbox',
            help='Mailbox asociated with the email.'),

    )
    option_list = append_to_option_list(WFBaseCommand.option_list, custom_option_list)

    WFBaseCommand.messages.update({
        'mailbox_empty': 'No mailbox was suplied.',
        'mailbox_invalid': 'Mailbox "%s" does not exist.',
        },)

    def create_mailbox(self, mailbox, safe=False):
        aux_machine = self.machine
        aux_machine.safemode = safe
        if not aux_machine.create_mailbox(mailbox) and not safe:
            #aux_machine.raise_error(self.messages['command_fail'] % 'Unknown')
            return False
        return True

    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)
        self.run(*args, **options)

    def get_related_options(self, **options):
        try:
            mailbox = options.get('mailbox', None)
            if mailbox is None or len(mailbox) == 0 or mailbox.startswith("-"):
                try:
                    mailbox = settings.WEBFACTION_MAILBOX
                except:
                    mailbox = None
                if mailbox is None:
                    self.machine.raise_error(self.messages['mailbox_empty'])
                    return
            return {'mailbox':mailbox}
        except Exception, error:
            self.machine.raise_error(self.messages['command_fail'] % str(error))


    def run(self, *args, **options):
        try:
            conf = self.get_related_options(**options)
            self.create_mailbox(conf['mailbox'])
        except Exception, error:
            self.machine.raise_error(self.messages['command_fail'] % str(error))
