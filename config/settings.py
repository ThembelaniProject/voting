from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "django-insecure-phase-one-demo-key-change-before-deployment"
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# Django's checks expect a default connection. An in-memory SQLite connection
# is used only to satisfy the framework; this project defines no models and
# does not persist or read voting data from any database.
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

INSTALLED_APPS = ["django.contrib.staticfiles"]
MIDDLEWARE = ["django.middleware.security.SecurityMiddleware"]
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": []},
}]
