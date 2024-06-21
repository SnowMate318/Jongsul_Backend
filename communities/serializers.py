from .models import SharedTag, Shared
from questions.serializers import DirectorySerializer
from users.serializers import MiniUserSerializer
from rest_framework import serializers

class SharedTagSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SharedTag
        fields= ('id','shared', 'name')
    
class SharedOnlySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Shared
        fields = ('id','user', 'shared_title', 'shared_content', 'shared_upload_datetime', 'shared_upload_datetime')


class SharedWithTagAndUserWithDirectorySerializer(serializers.ModelSerializer):
    user = MiniUserSerializer(read_only=True)
    shared_tags = SharedTagSerializer(many=True)
    directory = DirectorySerializer(read_only=True)
    class Meta:
        model = Shared
        fields = ('id', 'user', 'directory', 'shared_title', 'shared_content', 'shared_upload_datetime', 'shared_tags', 'download_count')

