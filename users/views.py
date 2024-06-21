from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework import views 
from .models import User, WebProvider
from .serializers import UserSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework import status
from rest_framework.response import Response
import jwt
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from django.contrib.auth import authenticate
from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly  # 인증된 사용자만 접근 허용
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import AccessToken
from django.db import transaction

# /register/, post(회원가입)
class RegisterAPIView(views.APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # jwt 토큰 접근
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            return Response(
                {
                    "user": serializer.data,
                    "message": "register successs",
                    "token": {
                        "access": access_token,
                        "refresh": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response({'message':'유저 시리얼라이져 밸리디에이션 에러', 'error': serializer.errors},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# /auth/, get(유저정보 확인), post(로그인), patch(유저정보 수정)
class AuthAPIView(views.APIView):
    def get(self, request):
        permission_classes = [IsAuthenticated]
        try:
            # access token을 decode 해서 유저 id 추출 => 유저 식별
            # token = request.headers.get('Authorization', '')[7:]
            # payload = jwt.decode(token, SECRET_KEY,Salgorithms=['HS256'])
            # user_id = payload.get('user_id')
            # user = get_object_or_404(User, pk=user_id, is_activated=True)
            user = request.user
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except(jwt.exceptions.ExpiredSignatureError):
            # 토큰 만료 시 토큰 갱신
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        except(jwt.exceptions.InvalidTokenError):
            # 사용 불가능한 토큰일 때
            return Response({"message": f"사용 불가능한 토큰입니다 {token}"},status=status.HTTP_400_BAD_REQUEST)
    def post(self, request):
    	# 유저 인증
        user = authenticate(
            email=request.data.get("email"), password=request.data.get("password")
        )
        # 이미 회원가입 된 유저일 때
        if user is not None:
            serializer = UserSerializer(user)
            # jwt 토큰 접근
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            response = Response(
                {
                    "user": serializer.data,
                    "message": "login success",
                    "token": {
                        "access": access_token,
                        "refresh": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )
            return response
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    def patch(self, request):
        permission_classes = [IsAuthenticated]
        try:
            user = request.user
            # access token을 decode 해서 유저 id 추출 => 유저 식별
            # token = request.headers.get('Authorization', '').split('Bearer ')[1]
            # payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            # user_id = payload.get('user_id')
            # user = get_object_or_404(User, pk=user_id, is_activated=True)
            new_name = request.data.get('user_name')
            new_image = request.data.get('profile')
            serializer = UserSerializer(user)
            if new_name is None and new_image is None:
                return Response({"message": "수정할 내용이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
            if new_name is not None:
                user.user_name = new_name
            if new_image is not None:
                user.profile = new_image
            
            user.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except(jwt.exceptions.ExpiredSignatureError):
            # 토큰 만료 시 토큰 갱신
            return Response({"message: 만료된 토큰입니다."},status=status.HTTP_401_UNAUTHORIZED)

        except(jwt.exceptions.InvalidTokenError):
            # 사용 불가능한 토큰일 때
            return Response({"message: 유효하지 않은 토큰입니다."},status=status.HTTP_400_BAD_REQUEST)

class SocialAuthAPIView(views.APIView):
    def post(self, request):
        with transaction.atomic:
            provider_id = request.data.get('provider_id')
            if user_id is None or user_id == '':
                return Response({"error": "user_id가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
                
            provider = request.data.get('provider')
            if provider is None or provider == '':
                return Response({"error": "provider가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
            
            email = request.data.get('email')
            nickname = request.data.get('nickname')
            
            web_provider = WebProvider.objects.get(provider_id=provider_id, provider_type=provider)
            
            if web_provider is None:
                user = User.objects.create(email=email, user_name=nickname)
                WebProvider.objects.create(user=user, provider_id=provider_id, provider_type=provider)
            else:
                user = web_provider.user    
            serializer = UserSerializer(user)
            
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            
            return Response(
                {
                    "user": serializer.data,
                    "message": "login success",
                    "token": {
                        "access": access_token,
                        "refresh": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )    

# /auth/delete, delete(유저정보 삭제)        
class UserDeleteView(views.APIView):
    def delete(self, request):
        try:
            user = request.user
            if user.is_active:
                # 사용자 비활성화
                user.is_active = False
                user.save()
                return Response({"message": "회원 탈퇴 처리가 완료되었습니다."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "이미 비활성화된 계정입니다."}, status=status.HTTP_400_BAD_REQUEST)

        except jwt.ExpiredSignatureError:
            return Response({"error": "토큰이 만료되었습니다."}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"error": "유효하지 않은 토큰입니다."}, status=status.HTTP_400_BAD_REQUEST)
       
#/auth/find , post(이메일 찾기)
class FindEmailView(views.APIView):
    def post(self, rquest):
        serializer = EmailFindSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": "이메일이 올바르지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=serializer.data.get('email'), is_active=True).exists():
            return Response({"message": "이메일이 존재합니다."}, status=status.HTTP_200_OK)
        elif User.objects.filter(email=serializer.data.get('email'), is_active=False).exists():
            return Response({"message": "탈퇴 처리된 회원입니다."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message": "이메일이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

