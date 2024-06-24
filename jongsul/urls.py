
from django.contrib import admin
from django.urls import path, include, re_path

from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_url_patterns = [
    path('api/auth/', include('users.urls')),
    path('api/', include('communities.urls')),
    path('api/', include('questions.urls')),
]

schema_view_v1 = get_schema_view(
    openapi.Info(
        title="문제톡톡 API",
        default_version='v1',
        description="문제톡톡 API 문서",
    ),
    public=True,
    permission_classes=(AllowAny,),
    patterns=schema_url_patterns,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/',include('users.urls')),
    path('api/',include('communities.urls')),
    path('api/',include('questions.urls')),
    
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view_v1.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view_v1.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view_v1.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]


