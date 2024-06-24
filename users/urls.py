from django.urls import path, include
from .views import RegisterAPIView, UserAPIView, AuthAPIView, UserDeleteVPIView, SocialAuthAPIView
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView
from .kakao_auth import kakao_login, kakao_callback

router = routers.DefaultRouter()
# 첫 번째 인자는 url의 prefix
# 두 번째 인자는 ViewSet


#router.register('library',LibraryViewSet, basename='library')
#router.register('directory',DirectoryViewSet, basename='directory')


urlpatterns =[
    path('', include(router.urls)),
    path("register/", RegisterAPIView.as_view()),
    path("login/", AuthAPIView.as_view()),
    path("user/", UserAPIView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()), # jwt 토큰 재발급
    
    path("social/", SocialAuthAPIView.as_view()),
    path('social/web/kakao', kakao_login, name='kakao_login'),
    path('social/web/kakao/callback', kakao_callback, name='kakao_callback'),
    path("delete/", UserDeleteAPIView.as_view()),
]
