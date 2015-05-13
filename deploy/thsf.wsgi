# pinax.wsgi is configured to live in projects/smeuhsocial/deploy.

import os
import sys

from os.path import abspath, dirname, join
from site import addsitedir

addsitedir("/home/thsf/.virtualenvs/smeuhsocial/lib/python2.7/site-packages")
sys.path.insert(0, "/home/thsf/smeuhsocial")
sys.path.insert(1, "/home/thsf/.virtualenvs/smeuhsocial/lib/python2.7/site-packages")

from django.conf import settings
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

sys.path.insert(0, join(settings.PROJECT_ROOT, "apps"))

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
