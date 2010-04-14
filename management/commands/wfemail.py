# -*- encoding: utf-8 -*-
from optparse import make_option

from webfaction.conf import settings
from webfaction.utils import email_valid
from webfaction.management.base import WFBaseCommand
from webfaction.management.commands.wfmailbox import Command as WFMailBox


class Command(WFBaseCommand):
    custom_option_list = (
        make_option('--email', action='store', dest='email',
            help='Email to create.'),
        make_option('--mailbox', action='store', dest='mailbox',
            help='Mailbox asociated with the email.'),
    )
    option_list = WFBaseCommand.option_list + custom_option_list
    
    WFBaseCommand.messages.update({
        'email_empty': 'No email was suplied.',
        'email_invalid': 'Email "%s" is not valid.',
        'mailbox_empty': 'No mailbox was suplied.',
        'mailbox_invalid': 'Mailbox "%s" does not exist.',
        },)
    
    
    def create_email(self, email, mailbox):
        if not email_valid(email):
            self.machine.raise_error(self.messages['email_invalid'] % email)
            return False
        if not self.machine.create_email(email, mailbox):
            self.machine.raise_error(self.messages['command_fail'] % 'Unknown')
            return False
        return True
        
    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)
        self.run(*args, **options)
    
    def run(self, *args, **options):
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
            
            email = options.get('email', None)
            if email is None or len(email) == 0 or email.startswith("-"):
                try:
                    email = settings.WEBFACTION_EMAIL
                except:
                    email = None
                if email is None:
                    self.machine.raise_error(self.messages['email_empty'])
                    return
            
            mbox = WFMailBox()
            mbox.machine = self.machine
            mbox.create_mailbox(mailbox, True)
            self.create_email(email, mailbox)
        except Exception, error:
            self.machine.raise_error(self.messages['command_fail'] % str(error))

