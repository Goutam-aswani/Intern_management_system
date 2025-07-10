# from . import tasks
# accounts/__init__.py
from __future__ import absolute_import, unicode_literals

# This line ensures tasks.py is imported when Django starts
default_app_config = 'accounts.apps.UsersConfig'

