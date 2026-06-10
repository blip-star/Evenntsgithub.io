import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-dev-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'events.apps.EventsConfig',
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'events_alerts.db',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Events bot specific settings
EVENTS_DEFAULT_COUNTY = os.getenv('EVENTS_COUNTY', 'Nairobi')
EVENTS_DEFAULT_DAYS_AHEAD = int(os.getenv('EVENTS_DAYS_AHEAD', '30'))

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
TELEGRAM_CHAT_IDS = [c.strip() for c in (os.getenv('TELEGRAM_CHAT_IDS') or TELEGRAM_CHAT_ID or "").split(",") if c.strip()]

NTFY_TOPIC = os.getenv('NTFY_TOPIC')
NTFY_SERVER = os.getenv('NTFY_SERVER', 'https://ntfy.sh')

WHATSAPP_ENABLED = os.getenv('WHATSAPP_ENABLED', 'false').lower() == 'true'
WHATSAPP_PROVIDER = os.getenv('WHATSAPP_PROVIDER', 'callmebot').lower()
CALLMEBOT_API_KEY = os.getenv('CALLMEBOT_API_KEY')
WHATSAPP_RECOMMENDED_ONLY = os.getenv('WHATSAPP_RECOMMENDED_ONLY', 'true').lower() == 'true'
WHATSAPP_INCLUDE_POSTER = os.getenv('WHATSAPP_INCLUDE_POSTER', 'true').lower() == 'true'

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
WHATSAPP_TWILIO_FROM = os.getenv('WHATSAPP_TWILIO_FROM')
WHATSAPP_TO_NUMBERS = os.getenv('WHATSAPP_TO_NUMBERS')

OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
OPENWEATHER_CITY = os.getenv('OPENWEATHER_CITY', 'Nairobi,KE')
WEATHER_TIMEZONE = os.getenv('WEATHER_TIMEZONE', 'Africa/Nairobi')
WEATHER_LAT = float(os.getenv('WEATHER_LAT', '-1.2864'))
WEATHER_LON = float(os.getenv('WEATHER_LON', '36.8172'))

LLM_PROVIDER = os.getenv('LLM_PROVIDER', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2')

AUTOSCAN_ENABLED = os.getenv('AUTOSCAN_ENABLED', 'true').lower() == 'true'
AUTOSCAN_INTERVAL_HOURS = int(os.getenv('AUTOSCAN_INTERVAL_HOURS', '6'))
SOCIAL_SCAN_ENABLED = os.getenv('SOCIAL_SCAN_ENABLED', 'true').lower() == 'true'
SOCIAL_PLATFORMS = os.getenv('SOCIAL_PLATFORMS', 'x,facebook,instagram')

ALERT_ON_CHANGES = os.getenv('ALERT_ON_CHANGES', 'true').lower() == 'true'

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {'verbose': {'format': '{asctime} {levelname} {name} {message}', 'style': '{'}},
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose'},
        'file': {'class': 'logging.handlers.RotatingFileHandler', 'filename': BASE_DIR / 'logs/events_bot.log', 'maxBytes': 2*1024*1024, 'backupCount': 3, 'formatter': 'verbose', 'encoding': 'utf-8'},
    },
    'root': {'handlers': ['console', 'file'], 'level': LOG_LEVEL},
    'loggers': {'events': {'level': LOG_LEVEL, 'propagate': True}, 'django.request': {'level': 'WARNING', 'propagate': True}},
}

EVENT_PREFERENCES = os.getenv('EVENT_PREFERENCES', 'live music,comedy,art,festivals,food,tech,networking,outdoor,car events,motorsport,racing,drag racing,sunset corsa,boxing,mma,rugby,kenyan football,football,sports,automotive')
