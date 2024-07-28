from django.apps import AppConfig
import os

class DiaryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'diary'

    def ready(self):
        if os.environ.get('RUN_MAIN', None) != 'true': # main인 경우에 스케쥴러 실행-두번 실행 방지
            print(' RUN_MAIN :', os.environ.get('RUN_MAIN', None))
            from . import scheduler  # 같은 디렉토리에 있는 scheduler 모듈을 임포트
            scheduler.startSchedule()