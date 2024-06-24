from .models import Library, Directory, Question, Choice
from users.models import User

from rest_framework import serializers

class LibrarySerializer(serializers.ModelSerializer):
    
    #user = UserSerializer(read_only=True)
    class Meta:
        model = Library
        fields = ('id', 'title', 'library_last_access')
    
class SmallDirectorySerializer(serializers.ModelSerializer):
        
        class Meta:
            model = Directory
            fields = ('id','library', 'concept', 'title', 'directory_last_access')

class LibraryWithDirectorySerializer(serializers.ModelSerializer):
    directories = SmallDirectorySerializer(many=True)
    class Meta:
        model = Library
        fields = ('id', 'title', 'library_last_access', 'directories')

class DirectorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Directory
        fields = ('id','library', 'last_successed', 'concept', 'title', 'directory_last_access', 'is_scrap_directory', 'is_deleted')
             
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
        
        

