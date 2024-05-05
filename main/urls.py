from django.urls import path, include
from .views import RegisterAPIView, AuthAPIView, SharedAPIView, SharedDetailAPIView, SharedUserFilteredAPIView
from .views import UserDeleteView, SharedUserFilteredAPIView, QuestionAPIView, QuestionDetailAPIView
from .views import  DirectoryAPIView, DirectoryDetailAPIView, DirectoryShareAPIView, LibraryChangeAPIView
from .views import QuestionSolveAPIView, QuestionScrapAPIView
from .views import LibraryViewSet
from rest_framework import routers
from .views import CustomTokenRefreshView

router = routers.DefaultRouter()
# 첫 번째 인자는 url의 prefix
# 두 번째 인자는 ViewSet


router.register('library',LibraryViewSet, basename='library')
#router.register('directory',DirectoryViewSet, basename='directory')


urlpatterns =[
    path('', include(router.urls)),
    path("register/", RegisterAPIView.as_view()),
    path("auth/", AuthAPIView.as_view()),
    path("auth/refresh/", CustomTokenRefreshView.as_view()), # jwt 토큰 재발급
    path("auth/delete/", UserDeleteView.as_view()),
    path("user/<str:user_id>/shared", SharedUserFilteredAPIView.as_view()),
    path("shared/", SharedAPIView.as_view()),
    path("shared/<int:shared_id>/",SharedDetailAPIView.as_view()),
    path("shared/<int:shared_id>/directory/",DirectoryAPIView.as_view()),
    path("library/<int:library_id>/directory/<int:directory_id>/",DirectoryAPIView.as_view()),
    path("library/<int:library_id>/directory/<int:directory_id>/share/",DirectoryAPIView.as_view()),
    path("library/<int:library_id>/directory/<int:directory_id>/change/",LibraryChangeAPIView.as_view()),
    path("library/<int:library_id>/directory/<int:directory_id>/question/", QuestionAPIView.as_view()),
    path("library/<int:library_id>/directory/<int:directory_id>/question/<int:question_id>/", QuestionDetailAPIView.as_view()),
    path("library/<int:library_id>/directory/<int:directory_id>/question/<int:question_id>/solve/", QuestionSolveAPIView.as_view()),
    path("library/<int:library_id>/directory/<int:directory_id>/question/<int:question_id>/scrap/", QuestionDetailAPIView.as_view()),
]
