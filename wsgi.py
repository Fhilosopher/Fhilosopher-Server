import os
from django.core.wsgi import get_wsgi_application

# DJANGO_SETTINGS_MODULE 환경 변수를 설정합니다.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# WSGI 애플리케이션을 생성합니다.
application = get_wsgi_application()
