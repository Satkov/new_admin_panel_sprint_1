DEBUG = os.environ.get('DEBUG', 'FALSE').upper() == 'TRUE'

ALLOWED_HOSTS = ['*']

INTERNAL_IPS = ["127.0.0.1"]

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOCALE_PATH = ['movies/locale']
