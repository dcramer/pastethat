import os, sys, os.path

# Add the project to the python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

# Set our settings module
os.environ['DJANGO_SETTINGS_MODULE']='pastethat.settings'

import django.core.handlers.wsgi

# Run WSGI handler for the application
application = django.core.handlers.wsgi.WSGIHandler()
