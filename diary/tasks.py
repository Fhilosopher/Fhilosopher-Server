from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()
from challenge.models import DailyChallenge, Badge
from diary.models import Month, Diary, QandA
from accounts.models import User
from datetime import datetime, timedelta

#매일 5시, 작성중인 일기 qandas 개수 확인 후 is_complete 변경, 업적 정보 업데이트
def check_is_complete():
    objects = Diary.objects.filter(is_complete=False)

    for diary in objects:
        qandas = QandA.objects.filter(diary_id=diary.id)
        if qandas.exists():
            diary.is_complete = True
            diary.save()

            month_obj = diary.month_id
            if month_obj:
                month_obj.count += 1
                month_obj.save()

            daily_challenge = DailyChallenge.objects.filter(user_id=diary.user_id).first()
            if daily_challenge:
                daily_challenge.today_complete = True
                daily_challenge.current_day += 1
                daily_challenge.save()

                user = User.objects.get(id=diary.user_id.id)
                if not user.is_firstday:
                    user.is_firstday = True
                    user.save()

                    Badge.objects.create(
                        title="1",
                        type="firstday",
                        user_id=user
                    )

                if daily_challenge.current_day == daily_challenge.goal_day:
                    goal_badge_exists = Badge.objects.filter(
                        title=str(daily_challenge.goal_day),
                        user_id=user
                    ).exists()
                    if not goal_badge_exists:
                        Badge.objects.create(
                            title=str(daily_challenge.goal_day),
                            type="goal_day",
                            user_id=user
                        )
                    daily_challenge.current_day = daily_challenge.goal_day
                    daily_challenge.goal_day += 7
                    daily_challenge.save()

    # 모든 유저의 daily_challenge 확인해서 today_complete가 False이면 current_day=0, goal_day=7로 설정, True라면 False로 초기화
    # 일단 하드코딩, 구현방식 이야기해봐야함
    all_daily_challenges = DailyChallenge.objects.all()
    for challenge in all_daily_challenges:
        if challenge.today_complete:
            challenge.today_complete = False
        else:
            challenge.current_day = 0
            challenge.goal_day = 7
        challenge.save()
    print(f'Objects modified at: {datetime.now()}')

#매달 1일 새 폴더 생성, 이전 달 빈폴더 삭제(미완성인 diary객체도 같이 삭제됨)
def create_and_delete_month_folder():
    users = User.objects.all()  # 모든 유저를 조회
    now = datetime.now()  # 현재 날짜와 시간
    current_year = now.year
    current_month = now.month
    first_day_of_current_month = datetime(now.year, now.month, 1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    previous_month_year = last_day_of_previous_month.year
    previous_month = last_day_of_previous_month.month


    for user in users:
        # 이미 해당 월의 Month 객체가 존재하는지 확인
        if not Month.objects.filter(user_id=user, year=current_year, month=current_month).exists():
            # 존재하지 않는 경우 새로 생성
            Month.objects.create(
                date=now,
                year=current_year,
                month=current_month,
                user_id=user
            )
    for user in users:
        # 해당 유저의 전달에 해당하는 Month 객체를 조회
        month_obj = Month.objects.filter(user_id=user, year=previous_month_year, month=previous_month, count=0)
        if month_obj.exists():
            # count가 0인 경우 삭제
            month_obj.delete()
    print(f'Month folder check at: {datetime.now()}')
