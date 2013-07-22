# Django settings for wotw project.

from os.path import dirname, join
import django

# Calculated paths for Django and the site
# Used as starting points for various other paths
DJANGO_ROOT = dirname(django.__file__) #/django/
SRC_ROOT = dirname(__file__) #ie. wotw/src/wotw_project/
#The wotw/ folder containing everything (eg. wotw/src/wotw_project)
WOTW_FOLDER_ROOT = dirname(dirname(dirname(dirname(SRC_ROOT))))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('qasim', 'email@notrequired.com'),
)

MANAGERS = ADMINS

INTERNAL_IPS = ("127.0.0.1",)

DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.sqlite3',
        
        # Or path to database file if using sqlite3.
        'NAME': join(SRC_ROOT, 'wotw_database'),
        
    'USER': '',                        # Not used with sqlite3.
    'PASSWORD': '',                    # Not used with sqlite3.
    'HOST': '',                        # Set to empty string for localhost. Not used with sqlite3.
    'PORT': '',                        # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = None #'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
STATIC_URL = '/static/'
#STATIC_ROOT = join(WOTW_FOLDER_ROOT, 'wotw_static')

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'gq!+%jh_#h7tr3)g4c3*=o0bkj!v*t41eh-@0f+08uawra-(k#'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.transaction.TransactionMiddleware'
)

ROOT_URLCONF = 'wotw_project.urls'

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/game/"



TEMPLATE_DIRS = (
    join(WOTW_FOLDER_ROOT, 'wotw_public'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    "game.context_processors.wotw_processor"
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.staticfiles',
    'south',
    'wotw_project.main_website',
    'wotw_project.game'
)

GAME_MAP_LOCATION = join(WOTW_FOLDER_ROOT, "wotw_other")
