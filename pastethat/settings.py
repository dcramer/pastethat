import os.path

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('David Cramer', 'dcramer@localhost'),
    ('David Cramer', 'dcramer@gmail.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'
DATABASE_HOST = 'localhost'
DATABASE_PORT = ''
DATABASE_NAME = ''
DATABASE_USER = ''
DATABASE_PASSWORD = ''

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
BASE_DOMAIN = 'pastethat.com'
BASE_URL = 'http://www.pastethat.com'

# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'America/Chicago'

# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True

MEDIA_ROOT = os.path.join(BASE_PATH, 'media')

MEDIA_URL = '%s/media/' % (BASE_URL,)

ADMIN_MEDIA_PREFIX = '%s/admin/media/' % (BASE_URL,)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '-!^qh-_7u)_w3aoem&!10a^5r-0*fb6_ic&$wfrebm74os$)9*'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

AUTHENTICATION_BACKENDS = (
    'pastethat.accounts.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'pastethat.pastes.middleware.GroupProcessorMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'pastethat.context_processors.default',
    'pastethat.pastes.context_processors.default',
)

ROOT_URLCONF = 'pastethat.urls'

TEMPLATE_DIRS = (
    os.path.join(BASE_PATH, 'templates'),
)

JINJA2_EXTENSIONS = (
    # 'jinja2.ext.do',
)
JINJA2_FILTERS = (
    'pastethat.utils.template.defaultfilters.urlencode',
    'pastethat.utils.template.defaultfilters.linebreaks',
    'pastethat.utils.template.defaultfilters.intcomma',
    'pastethat.utils.template.defaultfilters.truncatechars',
    'pastethat.utils.template.defaultfilters.ceil',
    'pastethat.utils.template.defaultfilters.floor',
    'pastethat.utils.template.defaultfilters.timesince',
)
JINJA2_GLOBALS = (
    'pastethat.utils.template.defaultfilters.mediaversion',
    'pastethat.utils.template.defaultfilters.mediaurl',
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'coffin',
    'pastethat.accounts',
    'pastethat.pastes',
    'pastethat.profiles',
    'pastethat.utils.template',
    'pastethat.utils.paginator',
    'pastethat.utils.resolver',
    'pastethat.utils.forms',
)

SESSION_ENGINE = 'django.contrib.sessions.backends.file'

try:
    from local_settings import *
except ImportError:
    pass

LOGIN_URL = BASE_URL + '/account/login'