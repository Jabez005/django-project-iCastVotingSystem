
from pathlib import Path
import os


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-nvhd*q53*y-e+6^h#3*$9tm2wnrle5zqwm^st%h6dqkcxtxjdi'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    'https://django-project-icastvotingsystem-production.up.railway.app',
    'localhost',
    '127.0.0.1',
]

CSRF_TRUSTED_ORIGIN=['django-project-icastvotingsystem-production.up.railway.app']

CORS_ALLOWED_ORIGINS=[
    'https://django-project-icastvotingsystem-production.up.railway.app',
    "http://localhost:8000/",
    "http://127.0.0.1:8000/",
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_io',

    'votingsystembase',
    'superadmin',
    'VotingAdmin',
    'Voters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'VotingSystem.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        'libraries': {
                'custom_filters': 'VotingAdmin.templatetag.custom_filters',  # Replace with the correct path to your custom filter module.
            },
        },
    },
]

WSGI_APPLICATION = 'VotingSystem.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'railway',
        'USER': 'postgres',
        'PASSWORD': 'A3b5G5dcACeg44CbefFC14GG-ccaCcFd',
        'HOST': 'viaduct.proxy.rlwy.net',
        'PORT': '33284',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Where `collectstatic` will collect static files for deployment.
STATICFILES_DIRS = [
    os.path.join(BASE_DIR,'static'),
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_URL = '/media/'  # URL to use when referring to media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Path where media is stored


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Your SMTP server hostname
EMAIL_PORT = 587  # SMTP server port
EMAIL_USE_TLS = True  # Use TLS for secure connection
EMAIL_HOST_USER = 'icastvotingsystem@gmail.com'  # Your SMTP username
EMAIL_HOST_PASSWORD = 'qmyn uvhn sxvk rbhv'  # Your SMTP password

APPEND_SLASH = False

AUTHENTICATION_BACKENDS = [
    'Voters.backends.VoterAuthenticationBackend',  
    'django.contrib.auth.backends.ModelBackend',  
]

LOGOUT_REDIRECT_URL = 'home'

