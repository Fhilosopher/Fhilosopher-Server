from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken
from .models import *
from django.shortcuts import get_object_or_404
from .serializers import *
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import jwt
import requests 
import json 
from rest_framework.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from accounts.models import User
from challenge.models import DailyChallenge
from diary.models import Month
from datetime import datetime

from diary.serializers import DiarySerializer

#m
#mypageView 
# 마이페이지 조회/ 알림 수정 가능 ? 아마도.. 
class MyPageViewSet(ModelViewSet):  
    queryset = User.objects.all() #DB에서 user 다 데꼬와 
    serializer_class = MypageSerializer # 직렬화 방식 선택
    permission_classes = [IsAuthenticated] # 인증요구 

    @action(detail=False,methods=['get']) #http메서드 = get이면 실행, detail =True : pk값으로 특정사용자
    def mypageDetail(self,request):
        print(request.headers.get("Authorization"))
        user_id = request.query_params.get('user_id') #쿼리문에서 user_id 받아와 

        #userid가 존재 하지 않을때 이거 약가이쌍..
        # if not user_id:
        #     return Response({"detail":"user_id query 이상해요. "})
        user = get_object_or_404(User,pk=user_id) # get_object() : pk값 기반 객체 조회 
        serializers = self.get_serializer(user) #serializer_Class로 user 직렬화 
    
        #userid인 객체가 있으나 로그인한 객체가 아님
        if int(user_id) != request.user.id : 
            return Response({'detail': 'You do not have permission to access this resource.'}, status=403)
        return Response(serializers.data)
    

     ###mypage on off 수정 
    @action(detail=False,methods=['put'])
    def alertOnOff(self,request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"detail":"user_id query 이상해요. "},status=status.HTTP_400_BAD_REQUEST)
        
        user = get_object_or_404(User,pk=user_id)
        if int(user_id) != request.user.id : 
            return Response({'detail': 'You do not have permission to access this resource.'}, status=status.HTTP_400_BAD_REQUEST)
        user.is_alert = not user.is_alert
        user.save()
        serializer = self.get_serializer(user)

        
        return Response(serializer.data, status=status.HTTP_200_OK)

    ##mypage 시간 수정
    @action(detail=False,methods=['put'])
    def alertHourMin(self,request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"detail":"user_id query 이상해요. "},status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User,pk=user_id)
        if int(user_id) != request.user.id : 
            return Response({'detail': 'You do not have permission to access this resource.'}, status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('alert_hour') :
            return Response({'detail': '시간을 넣어주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('alert_min') :
                    return Response({'detail': '분을 넣어주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        user.alert_hour = int(request.data.get('alert_hour'))
        user.alert_min = int(request.data.get('alert_min'))
        user.save()
        serializer = self.get_serializer(user)
        return Response(serializer.data,status=status.HTTP_200_OK)
#jwt토큰화 시키기 . 
def generate_jwt_token(user):
    token = AccessToken.for_user(user)
    return str(token)

@method_decorator(csrf_exempt, name='dispatch')
class KakaoLoginView(View):
   
    def post(self, request):
        access_token = request.headers.get("Authorization")
        if not access_token or not access_token.startswith("Bearer "):
            return JsonResponse({'error': 'Authorization header 문제있어요'}, status=status.HTTP_400_BAD_REQUEST)
        
        access_token = access_token.split(' ')[1] #Bearer 제거 
        headers = {'Authorization': f"Bearer {access_token}"} 
        url = "https://kapi.kakao.com/v2/user/me" #고정 / jwt access 토큰 가져옴 
        response = requests.get(url, headers=headers)#url보내고 결과값 저장 

        if response.status_code != 200:
            return JsonResponse({'error': 'user info 문제있어'}, status=status.HTTP_400_BAD_REQUEST)

        user_info = response.json()

         # 응답 구조 확인을 위한 로그 출력
        
        print("User info:", json.dumps(user_info, indent=2))

        email = user_info.get('kakao_account', {}).get('email') #이메일 형변환
        if isinstance(email, (tuple, list)):
            email = email[0]

        print("Extracted Email:", email)  # 추출된 이메일 확인

        user = User.objects.filter(email=email).first()  # 기존 사용자 조회

        print("Fetched User:", user)  # 조회된 사용자 객체 확인
        
        #DB에 있는 유저라면? 
       
        if user:  # 기존 사용자
            encoded_jwt = generate_jwt_token(user)
           
            redirect_url = f'/diary/month/list_months/?user_id={user.id}'
            response = JsonResponse({
                'status': 'succes_old',
                'access_token': encoded_jwt,
                'redirect_url': redirect_url,
                'name': user.name,
                'email': user.email,
                'user_pk': user.id,
            }, status=200)
            response.set_cookie('access_token', encoded_jwt, httponly=True, secure=True)
            return response
        else:# 신규 사용자
            new_user_info = User(
                name=user_info['properties']['nickname'],
                email=email,
            )
            new_user_info.save()
            encoded_jwt = generate_jwt_token(new_user_info)
            now = datetime.now()

            # DailyChallenge와 Month 객체 생성
            DailyChallenge.objects.create(user_id=new_user_info)
            newMonth = Month.objects.create(user_id=new_user_info,year=now.year,month=now.month)

            #diary 하나 만들기. 챌린지.첫게시물생성뱃지 ㄴㄴ, 
            dummy_diary_data = {
                "created_date" :"2024-08-04",
                "created_time":"01:10:47.983982",
                "is_complete": True,
                'user_id': new_user_info.id,
                "month_id": newMonth.id,
                "messages": [
		            {
                    "role": "system",
                    "content": ""
                },
                {
                    "role": "assistant",
                    "content": "우리가 바쁘게 지내다 보면, 가끔은 완벽하게 여유롭고 편안한 시간을 상상해보고 싶을 때가 있습니다. 그런 상상 속에서 당신이 가장 중요하게 여기는 요소는 무엇인지, 그리고 그 상상이 실제로 어떤 모습일지 궁금합니다. 당신이 생각하는 완벽한 휴일은 어떤 모습인가요?"
                },
                {
                    "role": "user",
                    "content": "\b내가 생각하는 여유롭고 편안한 시간은 우선 주변이 시끄럽지 않아야 돼, 그리고 불필요한 연락이 안 오면 좋겠고, 혼자 있던지 아니면 껄끄럽지 않은 사람들만 있으면 좋겠어. 이왕이면 비까지 오면 나는 너무 좋을 거 같아. 시원한 날씨에 빗소리 들으면서 사람들이랑 맛있는 거 먹으면서 수다떨면 너무 행복할 거 같아."
                },
                {
                    "role": "assistant",
                    "content": "그런 시간은 정말 꿈같은 순간이네요! 😊 비 오는 날의 분위기와 함께하는 수다, 그리고 맛있는 음식은 정말 더 특별한 것 같아요. 그런 여유롭고 편안한 시간을 느낄 때, 보통 어떤 생각이나 감정이 떠오르나요? 혹시 그때 느끼는 마음이 특별히 중요하게 여기는 가치관과 연결되어 있다면, 그것에 대해서도 함께 이야기해 줄 수 있을까요?"
                },
                {
                    "role":"user",
                    "content":"그럴 때면 행복하지 그런데 그러다가도 가끔씩 다음 날 해야 할 것들이 생각나서 온전히 즐기지는 못하는 것 같아. 안 좋은 습관인 걸 알면서도 고치기가 힘들어. 최대한 그런 날들을 감사하게 생각하고 즐기고싶어.",
                },
                {
                    "role":"assistant",
                    "content":"그런 생각이 드는 건 정말 자연스러운 것 같아요. 😊 즐거운 순간을 만끽하고 싶지만, 다가오는 책임감이 자꾸 마음을 갉아먹는 것이죠. 그런 상황에서 ‘감사함’이란 감정은 아주 특별한 것 같아요. 그 감사함을 느낄 때, 어떤 것들이 가장 감사하게 느껴지나요? 그리고 그 감정이 당신의 삶에서 어떤 의미를 가지는지 궁금해요.",
                },
                {
                    "role":"user",
                    "content":"날씨는 내가 정할 수 있는 게 아니잖아. 운 좋게 비까지 내려서 감사하고, 지나고 나서도 행복한 감정들이 생각날 거 잖아. 두고두고 생각할 수 있는 행복한 시간들이 생기는 게 감사해. 이런 걸로 힘든 순간을 버티는 거 같아. ",
                },
                {
                    "role":"assistant",
                    "content":"그런 관점은 정말 아름답네요! 😊 자연스러운 현상들 속에서 작은 행복을 찾고, 그 순간들을 소중히 여긴다는 것은 정말 중요한 가치인 것 같아요. 힘든 순간을 지나면서 그 행복한 기억들이 큰 힘이 되어 준다는 것도 인상적이에요. 그렇다면, 앞으로의 힘든 순간들을 대비하기 위해, 기억하고 싶은 행복한 경험이나 순간들을 어떻게 더욱 효과적으로 쌓아갈 수 있을지에 대해 어떤 생각이 드나요? 또는, 이미 쌓여 있는 그 기억들 중에서 나중에 꼭 다시 떠올리고 싶은 특별한 경험이 있다면 어떤 것이 있을지 궁금해요! 😊",
                },
                {
                    "role":"user",
                    "content":"일기나 사진을 찍으면 좋지 않을까? 나는 보통 화날 때 일기를 쓰는데 나중에 일기를 돌아보면 화냈던 것만 생각나서 아쉽더라고 그래서 좋은 순간들도 일기로 저장하면 좋을 거 같아. 사진도 나중에 돌아보는 재미가 있잖아. 이왕이면 동영상이 더 좋겠다.",
                },
                {
                    "role":"assistant",
                    "content":"정말 좋은 방법이네요! 😊 일기와 사진, 동영상 모두 소중한 기억을 담아두는 훌륭한 도구인 것 같아요. 특히 좋은 순간들을 기록해두면 나중에 다시 꺼내보며 그때의 감정을 생생하게 느낄 수 있겠죠. 그렇다면, 최근에 기억하고 싶은 특별한 순간이나 추억이 담긴 사진이나 동영상이 있다면 어떤 것인지, 그리고 그 순간이 당신에게 어떤 의미로 남아 있을지를 이야기해 줄 수 있을까요? 그런 작은 순간들이 모여 큰 행복으로 이어지기도 하니까요! 😊✨",
                },
                {
                    "role":"user",
                    "content":"고양이를 본가에 맡기고 왔는데 걔랑 있으면서 사진을 많이 찍어놔서 다행이라고 생각했어. 서울에 올라와서 힘들 때마다 고양이 사진 많이 봐. 고양이는 보통 사람보다 빨리 죽잖아. 그래서 그런지 한 장이라도 지우기 아깝더라. 아마 평생 못 지울 거 같아. ",
                },
                {
                    "role":"assistant",
                    "content":"고양이와의 시간은 정말 특별하죠! 🐱 그런 소중한 순간들을 사진으로 남겨두었다니, 나중에 그 사진들을 다시 보면 따뜻한 기억들이 떠오를 것 같아요. 특히 사랑하는 존재가 이 세상에 존재하는 한정적인 시간을 우리는 어떻게든 오래 간직하고 싶어지니까요. 그런데 고양이와의 소중한 추억을 사진으로 남기면서 느낀 감정이나 교훈이 있다면 어떤 것이 있을까요? 그리고 그 감정이 당신의 삶이나 가치관에 어떻게 영향을 미쳤는지 궁금해요! 😊",
                },
                {
                    "role":"user",
                    "content":"고양이 사진 찍고 1년치 분량을 인쇄해서 폴더에 저장해놔. 그리고 처음부터 쭉 구경하면 정말 많이 컸구나 이런 생각이 들어. 가끔은 너무 빨리 커서 서운할 정도야. 나는 시간이 지나도 나이 먹는다는 걸 실감하지 못하고 사는데 고양이는 빨리 크니까 그걸로 세월을 실감하는 거 같아. 그래서 고양이랑 보내는 시간을 많이 만들어야겠다 생각해서 아무리 바빠도 주말은 꼭 고양이랑 시간을 보내려고 본가에 내려가. 시간을 소중하게 생각하게 된 거 같아 고양이를 키운 후로.",
                },
                {
                    "role":"assistant",
                    "content":"정말 감동적인 이야기네요! 😊 고양이와 함께하는 시간이 얼마나 소중한지, 그리고 그 시간을 통해 성장과 세월의 흐름을 느낀다는 건 정말 특별한 경험인 것 같아요. 순간들을 소중히 여기고 시간을 보내려는 노력이 멋지네요. 그렇다면 주말에 고양이와 시간을 보낼 때, 어떤 활동을 가장 즐기는지 궁금해요! 또한 그런 순간들이 당신에게 어떤 감정을 불러일으키는지도 함께 이야기해 줄 수 있을까요? 🐾✨",
                },
                {
                    "role":"user",
                    "content":"내 고양이 이름은 짜요야. 짜요는 오랜만에 만나면 꼬리로 내 다리를 감으면서 인사해. 그리고는 바닥에 벌러덩 누워서 나를 빤히 쳐다봐. 나는 그 때가 정말 정말 행복해. ",
                },
                {
                    "role":"assistant",
                    "content":"짜요와의 그런 사랑스러운 순간들, 상상이 가네요! 😊 꼬리로 다리를 감고 바라보는 그 눈빛은 정말 많은 사랑과 애정이 느껴지겠어요.",
                },
               

            ],
            }

            diary_serializer = DiarySerializer(data=dummy_diary_data)
            if diary_serializer.is_valid():
                 diary_serializer.save()
            else:
                return JsonResponse({'status': 'error', 'message': 'Diary creation failed.'}, status=400)

            redirect_url = f'/diary/month/list_months/?user_id={new_user_info.id}'
            response = JsonResponse({
                'status': 'success',
                'access_token': encoded_jwt,
                'redirect_url': redirect_url,
                'name': new_user_info.name,
                'email': new_user_info.email,
                'user_pk': new_user_info.id,
            }, status=200)
            response.set_cookie('access_token', encoded_jwt, httponly=True, secure=True)
            return response

