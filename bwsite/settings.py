"""
Django settings for bwsite project.

Generated by 'django-admin startproject' using Django 1.10.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
from django.contrib import messages

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&dw26r488i80f#3g7ncj^x#+zvl(wv0=mh*%dkyd9qx4j56rc0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False or os.sys.platform == 'win32'

ALLOWED_HOSTS = ['pybizwiz-moltob.c9users.io', '127.0.0.1', 'diskstation']

# Application definition

INSTALLED_APPS = [
    'bizwiz.accounts',
    'bizwiz.articles',
    'bizwiz.common',
    'bizwiz.customers',
    'bizwiz.invoices',
    'bizwiz.projects',
    'bizwiz.rebates',
    'crispy_forms',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    #'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'djangoformsetjs',
    'django_tables2',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bwsite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'bizwiz.common.context_processors.projects',
                'bizwiz.common.context_processors.session_filter',
            ],
        },
    },
]

WSGI_APPLICATION = 'bwsite.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DATA_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'de-de'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'bower_components'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'static-root')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

CRISPY_TEMPLATE_PACK = 'bootstrap3'
CRISPY_FAIL_SILENTLY = not DEBUG

# override error tag to directly match alert levels in bootstrap:
MESSAGE_TAGS = {
    messages.DEBUG: 'info',
    messages.ERROR: 'danger',
}

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

BIZWIZ_LOG_LEVEL = os.getenv('BIZWIZ_LOG_LEVEL', 'DEBUG' if DEBUG else 'INFO')
DJANGO_LOG_LEVEL = os.getenv('DJANGO_LOG_LEVEL', 'DEBUG' if DEBUG else 'INFO')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(asctime)s %(levelname)s [%(name)s] %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'INFO',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(DATA_DIR, 'bizwiz.log'),
            'maxBytes': 1000000,
            'backupCount': 3,
            'formatter': 'simple',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        'bwsite': {
            'level': BIZWIZ_LOG_LEVEL,
        },
        'bizwiz': {
            'level': BIZWIZ_LOG_LEVEL,
        },
        'import-bw2': {
            'level': 'DEBUG'
        },
        'django': {
            'level': DJANGO_LOG_LEVEL,
        },
    },
    'root': {
        'handlers': ['console', 'file'],
    },
}
