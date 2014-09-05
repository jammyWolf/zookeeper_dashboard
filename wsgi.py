import os
import sys

reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append(os.path.abspath("__file__"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zookeeper_dashboard.settings")

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
