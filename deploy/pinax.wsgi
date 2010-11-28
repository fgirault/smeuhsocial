# pinax.wsgi is configured to live in projects/smeuhsocial/deploy.

import os
import sys

from os.path import abspath, dirname, join
from site import addsitedir

addsitedir("/home/smeuhsocial/env/lib/python2.5/site-packages")
sys.path.insert(0, "/home/smeuhsocial")

from django.conf import settings
os.environ["DJANGO_SETTINGS_MODULE"] = "smeuhsocial.settings"

sys.path.insert(0, join(settings.PROJECT_ROOT, "apps"))

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
