from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from diary.tasks import check_is_complete, create_and_delete_month_folder
from webmessage.task import send_web_push, send_scheduled_notifications
from webmessage.models import Subscription
import pytz
from django.utils import timezone





def startSchedule():
    scheduler = BackgroundScheduler()

    kst = pytz.timezone('Asia/Seoul')

    # 매일 새벽 05시에 실행
    scheduler.add_job(check_is_complete, CronTrigger(hour=5, minute=0, timezone=kst))

    # 매월 1일 새벽05시00분20초에 실행
    scheduler.add_job(create_and_delete_month_folder, CronTrigger(hour=5, minute=0, second=20, day=1, timezone=kst))
    
    # 매 분마다 구독자 알림 확인
    scheduler.add_job(send_scheduled_notifications, CronTrigger(minute="*", timezone=kst))

    scheduler.start()
