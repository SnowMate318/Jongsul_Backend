
from rest_framework import serializers
from .serializers import SharedWithTagAndUserWithDirectorySerializer
from drf_yasg import openapi
# swagger request

#library
class SharedQuerySerializer(serializers.Serializer):
    user = serializers.CharField(max_length=256, required=False)
    tags = serializers.CharField(max_length=256, required=False)
    
class TagsPatchSerializer(serializers.Serializer):
    tag_title = serializers.CharField(max_length=100, required=False)

class SharedsPatchSerializer(serializers.Serializer):
    shared_title = serializers.CharField(max_length=100, required=False)
    shared_content = serializers.CharField(max_length=8000, required=False)
    shared_tags = serializers.ListField(child=TagsPatchSerializer(), required=False)
    
shared_requests_query_param = SharedQuerySerializer

shared_requests = {
    'get': None
}
shared_responses = {
    'get': {
        200: SharedWithTagAndUserWithDirectorySerializer(many=True)
    },
}

shared_detail_requests = {
    'get': None,
    'patch': SharedsPatchSerializer,
    'delete': None
}
shared_detail_responses = {
    'get': {
        200: SharedWithTagAndUserWithDirectorySerializer    
    },
    'patch': None,
    'delete': None,
}
#shared download



#header
header_param=[openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer %Your Access Token%", type=openapi.TYPE_STRING)]