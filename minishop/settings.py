"""
Django settings for the MiniShop project.
"""
import os
from pathlib import Path

# BASE_DIR is the MiniShop/ folder (the one that contains manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# Load KEY=value lines from MiniShop/.env into the environment (the .env file is not pushed to GitHub)
_env_file = BASE_DIR / '.env'
if _env_file.exists():
    for _line in _env_file.read_text(encoding='utf-8').splitlines():
        _line = _line.strip()
        if _line and not _line.startswith('#') and '=' in _line:
            _key, _value = _line.split('=', 1)
            os.environ.setdefault(_key.strip(), _value.strip())

# SECURITY: on the server (Dokploy) set a long random SECRET_KEY and DEBUG=False.
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-minishop-university-demo-key-change-me')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Domain names that may open the site, comma separated, e.g. "minishop.example.com"
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

# Needed for forms (login, add product...) on https, e.g. "https://minishop.example.com"
CSRF_TRUSTED_ORIGINS = [url for url in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if url]

# Dokploy's proxy (Traefik) handles https and tells Django with this header
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# ------------------------------------------------------------------
# Installed apps
# ------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.auth',          # users, login, passwords
    'django.contrib.contenttypes',
    'django.contrib.sessions',      # used by the shopping cart
    'django.contrib.messages',      # flash messages ("Product saved!")
    'django.contrib.staticfiles',   # CSS, images, Bootstrap

    'products',                     # our MiniShop app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # serves static files on the server
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'minishop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],       # our templates/ folder
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # our own: makes cart count + categories available in every template
                'products.context_processors.shop_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'minishop.wsgi.application'


# ------------------------------------------------------------------
# Database: PostgreSQL (connection details come from the .env file)
# ------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'postgres'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            # Keep MiniShop tables inside their own PostgreSQL schema called "minishop"
            # (like a folder inside the database) so they don't mix with other tables.
            'options': '-c search_path=minishop',
        },
    }
}


# ------------------------------------------------------------------
# Password validation
# ------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ------------------------------------------------------------------
# Language / time
# ------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dhaka'
USE_I18N = True
USE_TZ = True


# ------------------------------------------------------------------
# Static files (CSS, JavaScript, images that are part of the design)
# ------------------------------------------------------------------
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'      # "collectstatic" copies everything here for the server

STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    # WhiteNoise compresses CSS/JS so pages load faster
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'},
}

# Media files (images uploaded by the admin for products)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Where the custom admin panel sends users who are not logged in
LOGIN_URL = 'admin_login'
