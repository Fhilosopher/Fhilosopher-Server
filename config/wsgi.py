import os
from django.core.wsgi import get_wsgi_application
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

lock_file = '/tmp/scheduler.lock'

def start_scheduler_once():
    if os.path.exists(lock_file):
        print('스케줄러가 이미 실행 중입니다.')
        return
    else:
        open(lock_file, 'w').close()  # 락 파일 생성

    from diary.scheduler import startSchedule
    startSchedule()

if not settings.DEBUG or os.environ.get('RUN_MAIN') == 'true':
    start_scheduler_once()

# 서버 종료 시 락 파일 삭제
def remove_lock_file():
    if os.path.exists(lock_file):
        os.remove(lock_file)

import atexit
atexit.register(remove_lock_file)
