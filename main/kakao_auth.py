from .models import User, WebProvider
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .serializers import UserSerializer, WebProviderSerializer
from jongsul.my_settings import SOCIALACCOUNT_PROVIDERS
from django.shortcuts import redirect
import requests
from rest_framework.renderers import JSONRenderer

BASE_URL = 'http://127.0.0.1:8000'
KAKAO_CALLBACK_URI = BASE_URL + '/api/kakao/login/callback'

# 인가코드 받기
def kakao_login(request): 
    client_id = SOCIALACCOUNT_PROVIDERS['kakao']['APP']['client_id']
    redirect_uri = KAKAO_CALLBACK_URI
    kakao_oauth_url = f"https://kauth.kakao.com/oauth/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"
    #카카오 로그인창을 띄우고 인증 코드를 받아옴
    return redirect(kakao_oauth_url)

#토큰 받기
def kakao_callback(request):
    client_id = SOCIALACCOUNT_PROVIDERS['kakao']['APP']['client_id']
    code = request.GET.get('code')
    
    token_request = requests.get(f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={KAKAO_CALLBACK_URI}&code={code}")
    # 요청한 토큰을 받음
    token_response_json = token_request.json()
    
    error = token_response_json.get("error",None)
    
    if error is not None:
        return Response(error, status=status.HTTP_400_BAD_REQUEST)
    
    #받은 토큰에서 access_token 추출
    access_token = token_response_json.get('access_token')
    
    # 해당 access_token으로 유저 정보 요청
    profile_request = requests.post(
        'https://kapi.kakao.com/v2/user/me',
        headers = {'Authorization': f'Bearer {access_token}'}
    )
    
    
    kakao_id = profile_request.json().get("id", None)
    

    if kakao_id is None:
        return Response({"message":"카카오 아이디를 받아오지 못했습니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    kakao_profile = profile_request.json().get("profile",None)
    if kakao_profile is not None:
        kakao_nickname = kakao_profile.get("nickname", None)
        kakao_thumbnail_image = kakao_profile.get("thumbnail_image_url", None)    
    
    try:
        provided = WebProvider.objects.get(provider_type='KAKAO', provider_id=kakao_id)   
    except WebProvider.DoesNotExist:
        provided = None
        
    if provided is not None:
        user = provided.user
    else: 
        with transaction.atomic():
            user = User.objects.create()
            if kakao_profile is not None:
                if kakao_nickname is not None:
                    user.user_name = kakao_nickname
                if kakao_thumbnail_image is not None:
                    user.profile_image = kakao_thumbnail_image
                user.save()
            WebProvider.objects.create(user=user, provider_type='KAKAO', provider_id=kakao_id)
    
    
    serializer = UserSerializer(user)
    providers = WebProvider.objects.filter(user=user)
    provider_serializer = WebProviderSerializer(providers, many=True)
        # jwt 토큰 접근
    token = TokenObtainPairSerializer.get_token(user)
    refresh_token = str(token)
    access_token = str(token.access_token)
    response = Response(
        {
            "user": serializer.data,
            "providers": provider_serializer.data,
            "message": "login success",
            "token": {
                "access": access_token,
                "refresh": refresh_token,
            },
        },
        status=status.HTTP_200_OK,
    )
    response.accepted_renderer = JSONRenderer()
    response.accepted_media_type = 'application/json'
    response.renderer_context = {}
    
    return response



    

