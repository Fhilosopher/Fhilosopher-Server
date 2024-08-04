# apps.py
from django.apps import AppConfig
import os

class DiaryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'diary'

    def ready(self):
        if os.environ.get('RUN_MAIN') != 'true' and os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
            print('RUN_MAIN:', os.environ.get('RUN_MAIN'))
            from . import scheduler  # 같은 디렉토리에 있는 scheduler 모듈을 임포트
            scheduler.startSchedule()
