# music_diary/settings.py

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'your-default-secret-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Add your new app to INSTALLED_APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'calendar_app',  # Add your new app here
]

# Django needs to know where to find its templates, especially for the admin interface
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
            ],
        },
    },
]

# Middleware in Django acts like a series of processing layers that your requests go through
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # Handles sessions
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Handles authentication
    'django.contrib.messages.middleware.MessageMiddleware',  # Handles messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Django uses SQLite, which is perfect for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # This tells Django to use SQLite
        'NAME': BASE_DIR / 'db.sqlite3',  # This creates the database file in your project directory
    }
}

# Static files configuration
STATIC_URL = 'static/'  # The URL prefix for static files (like CSS and JavaScript)
STATIC_ROOT = BASE_DIR / "staticfiles"  # Where Django will collect all static files for deployment

# User model
AUTH_USER_MODEL = 'calendar_app.User'

# Add these settings for Spotify authentication
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = 'http://localhost:8000/spotify/callback/'

# Authentication settings
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'

# Tells Django where to find the main URL configuration for your project
ROOT_URLCONF = 'music_diary.urls'