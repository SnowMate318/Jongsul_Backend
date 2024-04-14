from django.urls import path, include
from .views import RegisterAPIView, AuthAPIView, SharedAPIView, SharedDetailAPIView

from .views import  DirectoryAPIView, DirectoryDetailAPIView, DirectoryShareAPIView, LibraryChangeAPIView
from .views import LibraryViewSet, QuestionViewSet
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

router = routers.DefaultRouter()
# 첫 번째 인자는 url의 prefix
# 두 번째 인자는 ViewSet


router.register('library',LibraryViewSet, basename='library')
#router.register('directory',DirectoryViewSet, basename='directory')
router.register('question',QuestionViewSet)

urlpatterns =[
    path('', include(router.urls)),
    path("register/", RegisterAPIView.as_view()),
    path("auth/", AuthAPIView.as_view()),
    path("auth/refresh/", TokenRefreshView.as_view()), # jwt 토큰 재발급
    path("shared/", SharedAPIView.as_view()),
    path("shared/<int:shared_id>/",SharedDetailAPIView.as_view()),
    path("shared/<int:shared_id>/directory/",DirectoryAPIView.as_view()),
    path("shared/<int:library_id>/directory/<int:directory_id>",DirectoryAPIView.as_view()),
    path("shared/<int:library_id>/directory/<int:directory_id>/share/",DirectoryAPIView.as_view()),
    path("shared/<int:library_id>/directory/<int:directory_id>/change/",LibraryChangeAPIView.as_view()),

]
