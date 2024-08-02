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
            Month.objects.create(user_id=new_user_info,year=now.year,month=now.month)

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
