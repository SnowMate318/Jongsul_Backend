from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework import views 
from rest_framework.filters import OrderingFilter
from .models import SharedTag, Shared
from .serializers import SharedOnlySerializer, SharedTagSerializer, SharedWithTagAndUserWithDirectorySerializer
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from django.db import transaction
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly  # 인증된 사용자만 접근 허용

# /register/, post(회원가입)


# /shared/, get(커뮤니티 조회)    
class SharedAPIView(views.APIView):
      # 기본 정렬 순서    
    def get(self, request):
        tags = request.query_params.get('tags', None)
        user = request.query_params.get('user', None)
        ordering = request.query_params.get('ordering', '-shared_upload_datetime')
        
        
        # 
        if tags:
            tags_list = tags.split(',')  # 쉼표로 구분된 문자열을 리스트로 변환
            # 태그 리스트에 있는 각 태그에 대해 OR 조건 쿼리를 생성
            if user:
                q_objects = Q(sharedtag__name__in=tags_list, is_activated = True, is_deleted = False, user_id = user)
            else:
                q_objects = Q(sharedtag__name__in=tags_list, is_activated = True, is_deleted = False)
            shareds = Shared.objects.filter(q_objects).distinct().order_by(ordering)
        else:
            if user:
                shareds = Shared.objects.filter(is_activated = True, is_deleted = False, user_id = user).order_by(ordering)
            else: 
                shareds = Shared.objects.filter(is_activated = True, is_deleted = False).order_by(ordering)
        
        
        
        serializer = SharedWithTagAndUserWithDirectorySerializer(shareds, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# 내가 올린 커뮤니티 조회, TODO: 삭제   
class SharedUserFilteredAPIView(views.APIView):  
    def get(self, request):
        permission_classes = [IsAuthenticated]
        # request.user를 사용하여 현재 인증된 사용자 객체를 가져옴
        user = request.user
        if not user.is_authenticated:  # 사용자가 인증되지 않았다면 404 에러 처리
            raise Http404
        
        shareds = Shared.objects.filter(user=user, is_activated = True, is_deleted = False)  # 현재 사용자와 연결된 Shared 객체들을 필터링
        serializer = SharedWithTagAndUserSerializer(shareds, many=True)  # 필터링된 객체들을 시리얼라이즈
        
        return Response(serializer.data, status=status.HTTP_200_OK)
                
# /shared/<int:shared_id>/ , get(커뮤니티 상세 조회), put(커뮤니티 자료 다운로드), delete(커뮤니티 자료 삭제)
class SharedDetailAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, shared_id):
        shared = get_object_or_404(Shared, id=shared_id, is_deleted=False)
        
        serializer = SharedWithTagAndUserWithDirectorySerializer(shared) 
        return Response(serializer.data, status=status.HTTP_200_OK)
    def patch(self, request, shared_id):
        with transaction.atomic():
            new_title = request.data.get('shared_title')
            new_content = request.data.get('shared_content')
            new_tags = request.data['shared_tags']
            user = request.user
            shared = get_object_or_404(Shared, id=shared_id, user=user, is_deleted=False)
            shared.shared_title = new_title
            shared.shared_content = new_content
            shared.save()
            shared_tags = SharedTag.objects.filter(shared=shared).delete()
            for new_tag in new_tags:
                new_name = new_tag['name']                
                SharedTag.objects.create(shared=shared, name=new_name) 
        return Response({"message": "성공적으로 수정되었습니다"},status=status.HTTP_200_OK)   
    def delete(self, request, shared_id):
        shared = get_object_or_404(Shared, id=shared_id, is_deleted=False)
        shared.is_deleted = True
        shared.save()
        return Response({"message": "성공적으로 삭제되었습니다."}, status=status.HTTP_200_OK)     

class SharedDownloadAPIView(views.APIView):
    def post(self, request, shared_id):
        try:
            with transaction.atomic():
                user = request.user
                shared = get_object_or_404(Shared, id=shared_id, is_deleted=False)

                # Step 1: 사용자의 Library 확인 또는 생성
                library, created = Library.objects.get_or_create(
                    user=user, title="다운로드한 문제들"
                )

                # Step 2: 다운로드한 Directory 정보를 기반으로 새 Directory 인스턴스 생성
                copy_num=1
                title = shared.shared_title
                directories = Directory.objects.filter(library=library)
                for directory in directories:
                    if title == directory.title:
                        directory.title = title + f"({copy_num})"
                        copy_num+=1
                downloaded_directory = Directory.objects.create(title=title, library=library, user=user)

                # Step 3: Shared의 download_count 증가, 문제 복사
                questions = Question.objects.filter(directory=shared.directory)
                for question in questions:
                    new_question = Question.objects.create(
                        directory=downloaded_directory,
                        question_num=question.question_num,
                        question_title=question.question_title,
                        question_answer=question.question_answer,
                        question_explanation=question.question_explanation,
                        question_type=question.question_type
                    )
                    choices = Choice.objects.filter(question=question)
                    for choice in choices:
                        Choice.objects.create(
                            question=new_question,
                            choice_num=choice.choice_num,
                            choice_content=choice.choice_content
                        )
                shared.download_count += 1
                shared.save()

            return Response({"message": "성공적으로 다운로드 하였습니다", "download_count": shared.download_count}, status=status.HTTP_200_OK)
        except Shared.DoesNotExist:
            return Response({"message": "해당 공유가 존재하지 않습니다"}, status=status.HTTP_404_NOT_FOUND)

