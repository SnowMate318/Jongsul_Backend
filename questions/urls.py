from django.urls import path, include
from .views import QuestionAPIView, QuestionDetailAPIView, DirectoryShareAPIView, LibraryChangeAPIView
from .views import QuestionSolveAPIView, QuestionScrapAPIView, QuestionsTestAPIView, LibraryAPIView, LibraryDetailAPIView, DirectoryAPIView, DirectoryDetailAPIView
from rest_framework import routers

router = routers.DefaultRouter()
# 첫 번째 인자는 url의 prefix
# 두 번째 인자는 ViewSet


#router.register('library',LibraryViewSet, basename='library')
#router.register('directory',DirectoryViewSet, basename='directory')


urlpatterns =[
    path('', include(router.urls)),
    path("library/", LibraryAPIView.as_view()),
    path("library/<int:library_id>", LibraryDetailAPIView.as_view()),
    path("library/<int:library_id>/", LibraryDetailAPIView.as_view()),
    path("library/<int:library_id>/directory/",DirectoryAPIView.as_view()),
    path("directory/<int:directory_id>",DirectoryDetailAPIView.as_view()),
    path("directory/<int:directory_id>/",DirectoryDetailAPIView.as_view()),
    path("directory/<int:directory_id>/share/",DirectoryShareAPIView.as_view()),
    path("library/<int:library_id>/directory/<int:directory_id>/change/",LibraryChangeAPIView.as_view()),
    path("library/<int:library_id>/directory/<int:directory_id>/question/", QuestionAPIView.as_view()),
    path("directory/<int:directory_id>/question/test/", QuestionsTestAPIView.as_view()),

    path("question/<int:question_id>", QuestionDetailAPIView.as_view()),
    path("question/<int:question_id>/", QuestionDetailAPIView.as_view()),
    path("question/<int:question_id>/solve/", QuestionSolveAPIView.as_view()),
    path("question/<int:question_id>/scrap/", QuestionScrapAPIView.as_view()),
]
