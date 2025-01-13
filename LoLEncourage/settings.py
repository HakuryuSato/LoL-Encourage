from pathlib import Path
import environ

from decouple import config
from dj_database_url import parse as dburl

import os
import dj_database_url

logging = True

env = environ.Env()
env.read_env(".env")

SECRET_KEY = env("SECRET_KEY")
RIOT_API_KEY = env("RIOT_API_KEY")
DEBUG = env.bool("DEBUG")
ALLOWED_HOSTS = [str(env("ALLOWED_HOSTS"))]

DATABASE_USER = env("DATABASE_USER")
DATABASE_PASSWORD = env("DATABASE_PASSWORD")

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = Path(__file__).resolve().parent.parent

ROOT_URLCONF = "LoLEncourage.urls"

STATIC_URL = "/static/" # URLからアクセスする場所
STATIC_ROOT = os.path.join(ROOT_DIR, 'static') # staticを収集してまとめて保存する場所

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
# STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_DIRS = []


# ↓ 追加
default_dburl = "sqlite:///" + str(ROOT_DIR / "db.sqlite3")


# Render or Django-hosted
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    DATABASES = {
        "default": dj_database_url.config(
            # Feel free to alter this value to suit your needs.
            default="postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@localhost:5432/LoLEncourage",
            conn_max_age=600,
        )
    }

else:
    ALLOWED_HOSTS = ["*"]
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ROOT_DIR / "db.sqlite3",
        }
    }

INSTALLED_APPS = [
    # 'render.apps.RenderConfig',
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "LoLEncourage",
    # "LoLEncourage.apps.LolencourageConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # 追加
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

]


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "LoLEncourage.wsgi.application"

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

LANGUAGE_CODE = "ja"

TIME_ZONE = "Asia/Tokyo"

USE_I18N = True

USE_TZ = True


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if logging == True:
    LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    # デフォルトのロガーを保持します
    }

    LOGGING["handlers"] = {
    "file": {
        "class": "logging.FileHandler",
        "filename": "general.log",
    },
    }

    LOGGING["loggers"] = {
    "": {
        "level": "DEBUG",
        "handlers": ["file"],
    },
    }