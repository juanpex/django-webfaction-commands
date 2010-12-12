# -*- coding: utf-8 -*-
import sys
import os
from webfaction.conf import settings

def get_projectname():
    mod = __import__(settings.SETTINGS_MODULE, {}, {}, [''])
    folders = os.path.dirname(os.path.abspath(mod.__file__)).split("/")
    folders.reverse()
    return folders[0]

def get_server_path(username, appname, extraapp=''):
    return '/home/%(username)s/webapps/%(appname)s_django%(extraapp)s/media' % {'username': username, 'appname': appname, 'extraapp': extraapp}

def get_django_admin_media_path(username, appname):
    return get_server_path(username, appname, '/lib/python2.5/django/contrib/admin')

def get_django_media_path(username, appname):
    return get_server_path(username, appname, '/' + appname)

def email_valid(emailkey):
    """Email validation"""
    import re
    emailregex = "^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3\})(\\]?)$"
    if len(emailkey) > 7:
        if re.match(emailregex, emailkey) != None:
            return True
    return False

def append_to_option_list(option_list, newoptions):
    for o in newoptions:
        try:
            append = True
            for x in option_list:
                if x.get_opt_string() == o.get_opt_string():
                   append = False
            if append:
                option_list = option_list + tuple([o,])
        except Exception, e:
            pass
    return option_list

def custom_color_style():
    from django.utils import termcolors
    class dummy: pass
    style = dummy()
    style.ERROR = termcolors.make_style(fg='red', opts=('bold',))
    style.WARNING = termcolors.make_style(fg='yellow')
    style.SUCCESS = termcolors.make_style(fg='green', opts=('bold',))
    return style

def logginginfo(text):
    sys.stderr.write(text)
