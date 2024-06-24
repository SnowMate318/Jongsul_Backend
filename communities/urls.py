from django.urls import path, include
from .views import SharedAPIView, SharedDetailAPIView, SharedUserFilteredAPIView, SharedDownloadAPIView
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

router = routers.DefaultRouter()
# 첫 번째 인자는 url의 prefix
# 두 번째 인자는 ViewSets


#router.register('library',LibraryViewSet, basename='library')
#router.register('directory',DirectoryViewSet, basename='directory')


urlpatterns =[
    path('', include(router.urls)),
    path("user/<str:uuid>/shared", SharedUserFilteredAPIView.as_view()),
    path("shared/", SharedAPIView.as_view()),
    path("shared/<int:shared_id>",SharedDetailAPIView.as_view()),
    path("shared/<int:shared_id>/download/",SharedDownloadAPIView.as_view()),
    
]

