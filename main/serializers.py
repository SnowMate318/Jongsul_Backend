from .models import User, SharedTag, Shared, Library, Directory, Question, Choice, Image
from rest_framework import serializers

# Serializers define the API representation.
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        user = User.objects.create_user(
            email = validated_data['email'],
            password = validated_data['password']
        )
        return user
        
    
class SharedTagSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SharedTag
        fields= ('id','shared', 'name')
    
class SharedOnlySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Shared
        fields = ('id','user', 'shared_title', 'shared_content', 'shared_upload_datetime', 'shared_upload_datetime')

class SharedWithTagSerializer(serializers.ModelSerializer):
    
    shared_tag = SharedTagSerializer(many=True)
    class Meta:
        model = Shared
        fields = ('id', 'user', 'shared_title', 'shared_content', 'shared_upload_datetime', 'shared_upload_datetime','shared_tags')

class LibrarySerializer(serializers.ModelSerializer):
    
    user = UserSerializer(read_only=True)
    class Meta:
        model = Library
        fields = ('user', 'title', 'library_last_access')
        
    
    
class DirectorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Directory
        fields = ('library', 'shared', 'last_successed', 'concept', 'title', 'question_type')
    
class QuestionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Question
        fields = ('directory', 'question_title', 'question_content', 'question_answer', 'question_explaination', 'question_type', 'is_scrapped', 'question_num')
    
class ChoiceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Choice
        fidles = ('choice_num','choice_content')
        
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('image',)