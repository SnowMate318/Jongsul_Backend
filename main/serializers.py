from .models import User, WebProvider, SharedTag, Shared, Library, Directory, Question, Choice, Image
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

class EmailFindSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=64, required=True)
    
class WebProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebProvider
        fields = ('id', 'user', 'provider_type', 'provider_id')

class SharedTagSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SharedTag
        fields= ('id','shared', 'name')
    
class SharedOnlySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Shared
        fields = ('id','user', 'shared_title', 'shared_content', 'shared_upload_datetime', 'shared_upload_datetime')

class MiniUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email','user_name','profile')
 
class DirectorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Directory
        fields = ('id','library', 'last_successed', 'concept', 'title', 'question_type')
    
class SmallDirectorySerializer(serializers.ModelSerializer):
        
        class Meta:
            model = Directory
            fields = ('id','library', 'concept', 'title', 'directory_last_access')

class SharedWithTagAndUserWithDirectorySerializer(serializers.ModelSerializer):
    user = MiniUserSerializer(read_only=True)
    shared_tags = SharedTagSerializer(many=True)
    directory = DirectorySerializer(read_only=True)
    class Meta:
        model = Shared
        fields = ('id', 'user', 'directory', 'shared_title', 'shared_content', 'shared_upload_datetime', 'shared_tags', 'download_count')

class LibrarySerializer(serializers.ModelSerializer):
    
    #user = UserSerializer(read_only=True)
    class Meta:
        model = Library
        fields = ('id', 'title', 'library_last_access')
    

class LibraryWithDirectorySerializer(serializers.ModelSerializer):
    directories = SmallDirectorySerializer(many=True)
    class Meta:
        model = Library
        fields = ('id', 'title', 'library_last_access', 'directories')
        
class QuestionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Question
        fields = ('directory', 'question_title', 'question_content', 'question_answer', 'question_explanation', 'question_type', 'is_scrapped', 'question_num')   

class ChoiceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Choice
        fields = ('choice_num','choice_content',)
        
        
class QuestionAndChoiceSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)
    class Meta:
        model = Question
        fields = ('id','choices','directory', 'question_title', 'question_content', 'question_answer', 'question_explanation', 'question_type', 'is_scrapped', 'question_num')
        
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('image',)