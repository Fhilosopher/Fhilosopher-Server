from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from diary.tasks import check_is_complete, create_and_delete_month_folder  # 적절한 경로로 수정
import pytz

def startSchedule():
    scheduler = BackgroundScheduler()

    kst = pytz.timezone('Asia/Seoul')

    # 매일 새벽 05시에 실행
    scheduler.add_job(check_is_complete, CronTrigger(hour=5, minute=0, timezone=kst))

    # 매월 1일 새벽05시00분20초에 실행
    scheduler.add_job(create_and_delete_month_folder, CronTrigger(hour=5, minute=0, second=20, day=1, timezone=kst))
    
    scheduler.start()
