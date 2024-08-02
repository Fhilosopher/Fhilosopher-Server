from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import os
import pymysql
import mimetypes
# mysql connection
pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

AUTH_USER_MODEL = 'accounts.User'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/
load_dotenv()
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# ALLOWED_HOSTS = []
ALLOWED_HOSTS = ['boda-sogang.site','www.boda-sogang.site','localhost']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # django apps
    'accounts',
    'diary',
    'challenge',
    'firstQuestion',
    'webmessage',
    # library
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth.registration',

    'django_apscheduler',
    'corsheaders', 	
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]


CORS_ORIGIN_WHITELIST = [
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "https://boda-sogang.site",
    "http://localhost:3000",
]

CORS_ALLOW_HEADERS = [
    'content-type',
    'authorization',
    'x-csrftoken',
    'access-control-allow-origin',
]

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hackathon',  # 데이터베이스 이름
        'USER': 'hackathon',  # 데이터베이스 사용자
        'PASSWORD': 'hackathon',  # 데이터베이스 비밀번호
        'HOST': 'localhost',  # 데이터베이스 호스트
        'PORT': '3306',  # 데이터베이스 포트
          'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql', # engine: mysql
#         'NAME' : 'fhilosopher', # DB Name
#         'USER' : 'admin', # DB User
#         'PASSWORD' : 'hdh20-72021377', # Password
#         'HOST': 'database-1.c58imuyo4xi3.ap-northeast-2.rds.amazonaws.com', # 생성한 데이터베이스 엔드포인트
#         'PORT': '3306', # 데이터베이스 포트
#         'OPTIONS':{
#             'init_command' : "SET sql_mode='STRICT_TRANS_TABLES'"
#         }
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# media 루트 설정
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

# settings.py

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    BASE_DIR / "webmessage/static", #오류 날수도 있음. 
]

# MIME 타입 설정
mimetypes.add_type("application/javascript", ".js", True)


# static 루트 설정
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_HTTPONLY': False,
    'JWT_AUTH_COOKIE' : 'access',
    'JWT_AUTH_REFRESH_COOKIE' : "refresh_token",
}
SITE_ID = 1
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False #username 필드 사용 x
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_REQUIRED = True # email 필드 사용 o
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'none' # 회원가입 과정에서 이메일 인증 x

AUTHENTICATION_BACKENDS = (
    'allauth.account.auth_backends.AuthenticationBackend',
)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
    'dj_rest_auth.jwt_auth.JWTCookieAuthentication',
    'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    }


TIME_ZONE = 'Asia/Seoul'
USE_TZ = True


APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"  # Default

SCHEDULER_DEFAULT = True
VAPID_PUBLIC_KEY= 'BKd1I8PDrg7zidthfuKgR-0k_-CwlXZk3p1_F1tLWAur3w3lDdSfiAQHFl_cXRi6pguzNe9Akfxrqo25XXXxGZ4'
VAPID_PRIVATE_KEY= 'L5rFgenmml4G_EeQk8mq8iZx3EUrbssCfGLZs27UePo'
VAPID_CLAIMS = {
    "sub": "mailto:jmg0916789@gmail.com"
}
