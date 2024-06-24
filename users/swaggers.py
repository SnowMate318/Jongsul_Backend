
from rest_framework import serializers
from .serializers import UserSerializer
from drf_yasg import openapi
# swagger request

#library
class EmailPasswordInputSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
class AuthOutputSerializer(serializers.Serializer):
    user = serializers.DictField()
    message = serializers.CharField()
    token = serializers.DictField()
    
register_request = EmailPasswordInputSerializer

register_response = {
    200: AuthOutputSerializer,
    500: '유저 시리얼라이져 밸리디에이션 에러'
}

login_request = EmailPasswordInputSerializer
login_response = {
    200: AuthOutputSerializer,
    400: '요청하신 정보가 존재하지 않습니다.'
}

#user

class UserPatchInputSerializer(serializers.Serializer):
    user_name = serializers.CharField(required=False, max_length=30)
    profile = serializers.ImageField(required=False)

user_detail_requests = {
    'get': None,
    'patch': UserPatchInputSerializer
}

user_detail_responses = {
    'get': {
        200: UserSerializer,
        400: '사용 불가능한 토큰입니다.',
        401: '토큰이 만료되었습니다.'
    },
    'patch': {
        200: UserSerializer,
        400: '수정할 내용이 없습니다.',
    }
}

user_delete_request = None
user_delete_response = {
    400: '유효하지 않은 토큰입니다.',
    401: '토큰이 만료되었습니다.',
    404: '이미 비활성화된 계정이거나, 존재하지 않는 계정입니다.'
}

#social login
class SocialInputSerializer(serializers.Serializer):
    provider_type = serializers.CharField(max_length=30)
    provider_id = serializers.CharField(max_length=100)
    email = serializers.EmailField(required=False)
    user_name = serializers.CharField(required=False)

social_request = SocialInputSerializer
social_response = {
    200: AuthOutputSerializer,
    400: '요청하신 정보가 존재하지 않습니다.'
}

#header
header_param=[openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer %Your Access Token%", type=openapi.TYPE_STRING)]