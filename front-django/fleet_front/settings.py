from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent


def env(name, default=None):
    value = os.environ.get(name, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


SECRET_KEY = env("DJANGO_SECRET_KEY", "django-insecure-frota-frigorifica-front")
DEBUG = env("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [host.strip() for host in env("DJANGO_ALLOWED_HOSTS", "*").split(",") if host.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "monitoring.apps.MonitoringConfig",
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

ROOT_URLCONF = "fleet_front.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "monitoring" / "templates"],
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

WSGI_APPLICATION = "fleet_front.wsgi.application"
ASGI_APPLICATION = "fleet_front.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "monitoring" / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MQTT_HOST = env("MQTT_HOST", "broker.hivemq.com")
MQTT_PORT = int(env("MQTT_PORT", "1883"))
MQTT_BROKERS = [
    broker.strip()
    for broker in env("MQTT_BROKERS", f"{MQTT_HOST}:{MQTT_PORT}").split(",")
    if broker.strip()
]
MQTT_USERNAME = env("MQTT_USERNAME", "")
MQTT_PASSWORD = env("MQTT_PASSWORD", "")
MQTT_CLIENT_ID = env("MQTT_CLIENT_ID", "django-fleet-dashboard")
MQTT_TEMPERATURE_TOPIC = env("MQTT_TEMPERATURE_TOPIC", "logistica/frio/temperatura")
MQTT_STATUS_TOPIC = env("MQTT_STATUS_TOPIC", "logistica/frio/status")
MQTT_COMMAND_TOPIC = env("MQTT_COMMAND_TOPIC", "logistica/frio/comando")
MQTT_PING_TOPIC = env("MQTT_PING_TOPIC", "logistica/frio/comando")
MQTT_CLIENT_ENABLED = env("MQTT_CLIENT_ENABLED", "1") == "1"
