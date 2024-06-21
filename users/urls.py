from django.urls import path, include
from .views import RegisterAPIView, AuthAPIView,UserDeleteView, FindEmailView
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
    path("auth/", AuthAPIView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()), # jwt 토큰 재발급
    path('kakao/login', kakao_login, name='kakao_login'),
    path('kakao/login/callback', kakao_callback, name='kakao_callback'),
    path("auth/delete/", UserDeleteView.as_view()),
    path("auth/find/", FindEmailView.as_view()),
]
