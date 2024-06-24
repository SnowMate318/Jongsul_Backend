from rest_framework import serializers
from .serializers import LibraryWithDirectorySerializer, SmallDirectorySerializer, DirectorySerializer, QuestionAndChoiceSerializer
from drf_yasg import openapi
# swagger request

#library
class LibraryInputSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100, required=True)

library_requests = {
    'post': LibraryInputSerializer,
    'get': None
}
library_responses = {
    'get': {
        200: LibraryWithDirectorySerializer(many=True)
    },
    'post': {
        400: '제목을 입력해야합니다.'
    },
}

library_detail_requests = {
    'get': None,
    'patch': LibraryInputSerializer,
    'delete': None
}
library_detail_responses = {
    'get': {
        200: LibraryWithDirectorySerializer    
    },
    'patch': None,
    'delete': None,
}

#directory    
class DirectoryCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100, required=True)
    concept = serializers.CharField(max_length=8000, required=True)
    difficulty = serializers.IntegerField(required=True)
    multiple_choice = serializers.IntegerField(required=True)
    short_answer = serializers.IntegerField(required=True)
    ox_prob = serializers.IntegerField(required=True)

class DirectoryPatchSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100, required=False)
    concept = serializers.CharField(max_length=8000, required=False)
    


directory_requests = {
    'get': None,
    'post': DirectoryCreateSerializer
}

directory_responses = {
    'get': {
        200: DirectorySerializer(many=True)
    },
    'post': {
        400: '제목을 입력해야합니다', 
        500: 'GPT_API 관련 오류'
        }
}

directory_detail_requests = {
    'get': None,
    'patch': DirectoryPatchSerializer,
    'delete': None
}

directory_detail_responses = {
    'get': {
        200: DirectorySerializer
    },
    'patch': {
        200: '성공적으로 디렉토리 내용을 변경했습니다.'
    },
    'delete': {
        200: '디렉토리가 성공적으로 삭제되었습니다.'
    }
}
#directory change
class DirectoryChangeSerializer(serializers.Serializer):
    library_id = serializers.IntegerField(required=True)
    new_library_title = serializers.CharField(max_length=30, required=True)
    
directory_change_request = DirectoryChangeSerializer

directory_change_response = {
    400: '이동할 라이브러리가 없습니다. or 라이브러리 정보가 제공되지 않았습니다.'
}

#directory share
class DirectoryShareSerializer(serializers.Serializer):
    shared_title = serializers.CharField(max_length=100, required=True)
    shared_content = serializers.CharField(max_length=2000, required=True)
    shared_tags = serializers.ListField(child=serializers.CharField(max_length=30), required=False)
    
directory_share_request = DirectoryShareSerializer

directory_share_response = None

#question
class ChoicePatchSerializer(serializers.Serializer):
    choice_num = serializers.IntegerField()
    choice_content = serializers.CharField(max_length=200)

class QuestionPatchSerializer(serializers.Serializer):
    question_title = serializers.CharField(max_length=1000, required=False)
    question_content = serializers.CharField(max_length=2000, required=False)
    question_answer = serializers.CharField(max_length=200, required=False)
    question_explanation = serializers.CharField(max_length=2000, required=False)
    choices = serializers.ListField(child=ChoicePatchSerializer(), required=False)
    
    
question_requests = {
    'get': None,
}
question_responses = {
    'get': {
        200: QuestionAndChoiceSerializer(many=True)    
    },
}
question_detail_requests = {
    'get': None,
    'patch': QuestionPatchSerializer,
    'delete': None
}
question_detail_responses = {
    'get': {
        200: QuestionAndChoiceSerializer
    },
    'patch': None, 
    'delete': {
        404: '문제를 찾을 수 없습니다.'
    }
}

#question solve
class QuestionSolveSerializer(serializers.Serializer):
    last_solved = serializers.BooleanField(required=True)
    
question_solve_request = QuestionSolveSerializer
question_solve_response = {
        400: '정답 여부를 입력해주세요.'
}

#question scrap
class QuestionScrapSerializer(serializers.Serializer):
    is_scrapped = serializers.BooleanField(required=True)
    dir_name = serializers.CharField(max_length=100, required=True)
    
question_scrap_request = QuestionScrapSerializer
question_scrap_response = {
    400: '스크랩 여부를 입력해주세요. or 디렉토리 이름을 입력해주세요.'
}
#header
header_param=[openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer %Your Access Token%", type=openapi.TYPE_STRING)]