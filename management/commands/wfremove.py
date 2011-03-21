# -*- encoding: utf-8 -*-
from optparse import make_option

from webfaction.utils import get_projectname, append_to_option_list
from webfaction.conf import settings
from webfaction.management.base import WFBaseCommand
from webfaction.management.commands.wfdeploy import Command as WFDeploy


class Command(WFBaseCommand):

    option_list = append_to_option_list(WFBaseCommand.option_list, [])
    option_list = append_to_option_list(option_list, WFDeploy.option_list)

    washandle = False
    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)
        self.washandle = True
        self.run(*args, **options)

    def run(self, *args, **options):
        try:
            fake_task = WFDeploy()
            conf = fake_task.run(*args, **options)
            if (options.get('doemail') or options.get('doall')) and conf['email']:
                self.machine.delete_email(conf['email'])
            if (options.get('domailbox') or options.get('doall')) and conf['mailbox']:
                self.machine.delete_mailbox(conf['mailbox'])
            if (options.get('dodjangoapp') or options.get('doall')) and conf['appname']:
                self.machine.delete_app("%s_django" % conf['appname'])
                self.machine.delete_app("%s_django_admin_media" % conf['appname'])
                self.machine.delete_app("%s_django_media" % conf['appname'])
                self.machine.delete_website(conf['appname'])
            if (options.get('dodatabase') or options.get('doall')) and conf['dbname'] and conf['dbengine']:
                self.machine.delete_db(conf['dbname'],conf['dbengine'])
                self.machine.clear_pgpassfile(conf['dbname'])
        except Exception, error:
            self.machine.raise_error(error)
        self.machine.raise_success('Remove Done')
