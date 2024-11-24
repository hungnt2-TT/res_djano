"""
Django settings for res project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', '1234567890')

# SECURITY WARNING: don't run with debug turned on in production!
import dotenv
from django.contrib.messages import constants as messages

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False')
# Application definition
ENVIRONMENT = os.getenv('ENVIRONMENT', 'local')

if ENVIRONMENT == 'production':
    ALLOWED_HOSTS = [
            '*'
    ]
    SITE_ID = 4

    # SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # SECURE_SSL_REDIRECT = True

elif ENVIRONMENT == 'staging':
    ALLOWED_HOSTS = [
        '127.0.0.1',
        'localhost',
    ]

    SITE_ID = 3
elif ENVIRONMENT == 'development':
    ALLOWED_HOSTS = [
        '127.0.0.1',
        'localhost',
    ]

    SITE_ID = 2
else:
    ALLOWED_HOSTS = [
        '127.0.0.1',
        'snail-tight-albacore.ngrok-free.app',
        'adequate-zebra-major.ngrok-free.app',
        'localhost',
    ]

    SITE_ID = 1

CSRF_TRUSTED_ORIGINS = ['https://snail-tight-albacore.ngrok-free.app', 'https://adequate-zebra-major.ngrok-free.app']

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_celery_beat",
    "geoposition",
    "employee",
    "restaurant",
    "vendor",
    "wallet",
    "widget_tweaks",
    "menu",
    "customers",
    "marketplace",
    "django_ckeditor_5",
    'django.contrib.gis',

    'paypal.standard.ipn',
    'django_extensions',
    'orders',
    'csp'
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "res.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'res/templates')],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "vendor.views.get_google_api",
                "employee.context_processors.get_vendor",
                "marketplace.context_processors.get_cart_counter",
                "marketplace.context_processors.get_cart_amount",
                "employee.context_processors.get_vendor",
                "employee.context_processors.get_paypal_client_id",
                "employee.context_processors.role",
                "employee.context_processors.request_order",
                "employee.context_processors.request_shipper",
            ],
        },
    },
]

WSGI_APPLICATION = "res.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
if 'RDS_DB_NAME' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': os.getenv('RDS_DB_NAME'),
            'USER': os.getenv('RDS_USERNAME'),
            'PASSWORD': os.getenv('RDS_PASSWORD'),
            'HOST': os.getenv('RDS_HOSTNAME'),
            'PORT': os.getenv('RDS_PORT'),
        }
    }
else:  # Local SQlite not used anymore for local dev
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


AUTH_USER_MODEL = 'employee.Profile'
# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = 'staticfiles/'

STATICFILES_DIRS = [
    BASE_DIR / 'static/'
]
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"
# Add s3 in aws
# AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', default=False)
# if AWS_STORAGE_BUCKET_NAME:
#     AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
#     AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
#     AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
#     AWS_DEFAULT_ACL = 'public-read'
#     AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
#     AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
#
#     # s3 public media settings
#     PUBLIC_MEDIA_LOCATION = 'media'
#     MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
# else:
#     MEDIA_URL = '/media/'
#     MEDIA_ROOT = BASE_DIR / "media"

# Celery base setup
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", 'redis://localhost:6379')
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", 'redis://localhost:6379')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyD-9tSrke72PouQMnMX-a7eZSW0jkFMBWY")
GOOGLE_API_KEY_BY_IP = os.getenv("GOOGLE_API_KEY_BY_IP", "AIzaSyD-9tSrke72PouQMSSX-a7eZSW0jkFMBWY")
# LOGIN redirections
LOGIN_REDIRECT_URL = '/employee/home/'
LOGOUT_REDIRECT_URL = '/employee/home/'

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_PORT = 587
EMAIL_HOST_USER = str(os.getenv('EMAIL_USER'))
EMAIL_HOST_PASSWORD = str(os.getenv('EMAIL_PASSWORD'))

MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin-allow-popups"

TWILIO_ACCOUNT_SID = os.getenv("MY_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("MY_TWILIO_NUMBER")
SECRET_KEY_TWILIO = os.getenv("SECRET_KEY_TWILIO")
SMS_BROADCAST_TO_NUMBERS = [
    "+23XXXXXXXXXXX",
    "+23XXXXXXXXXXX",  # use the format +1XXXXXXXXXX
]
CK_EDITOR_5_UPLOAD_FILE_VIEW_NAME = 'custom_upload_file'

CKEDITOR_5_UPLOADS_ROOT = 'uploads/'
CKEDITOR_5_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
customColorPalette = [
    {
        'color': 'hsl(4, 90%, 58%)',
        'label': 'Red'
    },
    {
        'color': 'hsl(340, 82%, 52%)',
        'label': 'Pink'
    },
    {
        'color': 'hsl(291, 64%, 42%)',
        'label': 'Purple'
    },
    {
        'color': 'hsl(262, 52%, 47%)',
        'label': 'Deep Purple'
    },
    {
        'color': 'hsl(231, 48%, 48%)',
        'label': 'Indigo'
    },
    {
        'color': 'hsl(207, 90%, 54%)',
        'label': 'Blue'
    },
]
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],

    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
                    'code', 'subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing', 'insertImage',
                    'bulletedList', 'numberedList', 'todoList', '|', 'blockQuote', 'imageUpload', '|',
                    'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                    'insertTable', ],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                        'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side', '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]

        },
        'table': {
            'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells',
                               'tableProperties', 'tableCellProperties'],
            'tableProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            },
            'tableCellProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            }
        },
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'}
            ]
        }
    },
    'list': {
        'properties': {
            'styles': 'true',
            'startIndex': 'true',
            'reversed': 'true',
        }
    }
}

# COOKIE SETTINGS
# SESSION_COOKIE_AGE = 60 * 60 * 24 * 7
# SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
# SESSION_CACHE_ALIAS = 'default'
# PASSWORD RESET SETTINGS
PASSWORD_RESET_TIMEOUT_DAYS = 1

GDAL_LIBRARY_PATH = os.getenv('GDAL_LIBRARY_PATH', '/usr/lib/x86_64-linux-gnu/libgdal.so')

# PayPal Standard IPN
PAYPAL_TEST = True
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
PAYPAL_RECEIVER_EMAIL = os.getenv('PAYPAL_RECEIVER_EMAIL')


# VNPAY CONFIG
VNPAY_TMN_CODE = os.getenv('VNPAY_TMN_CODE')
VNPAY_HASH_SECRET_KEY = os.getenv('VNPAY_HASH_SECRET_KEY')
VNPAY_RETURN_URL = '/order_detail/{order_number}/'
VNPAY_PAYMENT_URL = os.getenv('VNPAY_PAYMENT_URL')
VNPAY_API_URL = os.getenv('VNPAY_API_URL')

# CURRENCY
CURRENCYFREAKS_API_KEY = os.getenv('CURRENCYFREAKS_API_KEY')

SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin-allow-popups"
