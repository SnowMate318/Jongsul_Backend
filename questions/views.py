from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework import views 
from rest_framework.filters import OrderingFilter
from .models import Library, Directory, Question, Choice
from .serializers import LibraryWithDirectorySerializer, DirectorySerializer, QuestionSerializer
from .serializers import ChoiceSerializer, QuestionAndChoiceSerializer, LibraryWithDirectorySerializer , SmallDirectorySerializer#, LibrarySerializer, 
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly  # 인증된 사용자만 접근 허용
from django.db import transaction
from .langchain_gpt import getQuestions

# /register/, post(회원가입)

# /library/ post(라이브러리 생성), get(전체 라이브러리 조회)
class LibraryAPIView(views.APIView):
    
    permission_classes = [IsAuthenticated]
    def post(self, request):
        title = request.data.get("title")
        user = request.user
        if title == "":
            return Response({'message':'제목을 입력해야합니다'},status=status.HTTP_400_BAD_REQUEST)
        library = Library.objects.create(user=user, title=title)
        return Response({'message': '새로운 라이브러리가 생성되었습니다'},status=status.HTTP_201_CREATED)
    def get(self, request):
        user = request.user
        ordering = request.query_params.get('ordering', '-library_last_access')
        libraries = Library.objects.filter(user=user).order_by(ordering)    
        
        
        serializer = LibraryWithDirectorySerializer(libraries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LibraryDetailAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, library_id):
        user = request.user
        library = get_object_or_404(Library, id=library_id)
        serializer = LibraryWithDirectorySerializer(library)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    def patch(self, request, library_id):
        user = request.user
        title = request.data.get('title')
        library = get_object_or_404(Library, id=library_id)
        library.title = title
        library.save()
        
        return Response({'message':'라이브러리 제목이 수정되었습니다'},status=status.HTTP_200_OK)
    def delete(self, request, library_id):
        user = request.user
        title = request.data.get('title')
        library = get_object_or_404(Library, id=library_id)
        library.delete()
        
        return Response({'message':'라이브러리 삭제가 완료되었습니다'},status=status.HTTP_200_OK)

#없는걸 만들어낼 수 있냐? -> put
#있는것만 건들거냐? -> patch

# /library/<int:library_id>/directory/ post(디렉토리 추가),get(전체 디렉토리 조회)
class DirectoryAPIView(views.APIView):
    permission_classes = [IsAuthenticated] 
    
    #post(문제 생성), get(문제 조회)
    #로직 생성 문제 선택 -> 라이브러리 선택 과정에서 library_id를 클라이언트 측에서 uri에 넣어서 주소를 요청한다. TODO: 클라이언트에서 library_id를 저장하는지 보기   
    def post(self, request, library_id):
        with transaction.atomic():
            title = request.data.get('title')
            script = request.data.get('script')
            difficulty = request.data.get('difficulty')
            multiple_choice = request.data.get('multiple_choice')
            short_answer = request.data.get('short_answer')
            ox_prob = request.data.get('ox_prob')
            all_prob = request.data.get('all_prob')
            
            try:
                questions = getQuestions(script, multiple_choice, short_answer, ox_prob)
                if questions is None:
                    return Response({'message': 'GPT_API 관련 오류'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                library = get_object_or_404(Library, id=library_id)
                directory = Directory.objects.create(library=library, title=title, user=request.user)
                directory.concept = script
                directory.save()
                for ques in questions:
                    question = Question.objects.create(
                        directory=directory, 
                        question_num=ques['question_num'],
                        question_title=ques['question_title'],
                        question_answer=ques['question_answer'],
                        question_explanation=ques['question_explanation'],
                        question_type=ques['question_type']
                    )
                    choices = ques.get('choices')
                    if choices:
                        for cho in choices:
                            Choice.objects.create(
                                question=question,
                                choice_num=cho['choice_num'],
                                choice_content=cho['choice_content']
                            )
                serializer = SmallDirectorySerializer(directory)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def get(self, request, library_id):
        user = request.user
        library = get_object_or_404(Library, user=user, id=library_id)
        ordering = request.query_params.get('ordering', '-directory_last_access')
        directories = Directory.objects.filter(library = library_id, is_deleted=False)
        serializer = DirectorySerializer(directories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# /library/<int:library_id>/directory/<int:directory_id>/ get(디렉토리 상세조회) patch(디렉토리 수정)    *delete 필요할까
class DirectoryDetailAPIView(views.APIView):
    
    permission_classes = [IsAuthenticated]
    def get(self, request, directory_id):
        user = request.user
        directory = get_object_or_404(Directory, user=user, id = directory_id, is_deleted=False)
        
        serializer = DirectorySerializer(directory)
        return Response(serializer.data, status=status.HTTP_200_OK)  
    def patch(self, request, directory_id):
        user = request.user
        directory = get_object_or_404(Directory, id = directory_id, is_deleted=False)
        
        dir_title = request.data.get('title')
        if dir_title:
            directory.title = dir_title
            
        dir_concept = request.data.get('concept')
        if dir_concept:
            directory.concept = dir_concept
            
        dir_type = request.data.get('type')
        if dir_type:
            directory.question_type = dir_type
        
        directory.save()
        return Response({"message": "성공적으로 디렉토리 내용을 변경했습니다."}, status=status.HTTP_200_OK)
    def delete(self, request, directory_id):
        directory = get_object_or_404(Directory, id=directory_id, is_deleted=False)
        directory.is_deleted=True
        directory.save()
        return Response({'message':'디렉토리가 성공적으로 삭제되었습니다.'}, status=status.HTTP_200_OK) # 소프트삭제

#---------

class QuestionsTestAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,directory_id):
        directory = get_object_or_404(Directory, id=directory_id)
        questions = Question.objects.filter(directory = directory)
        serializer = QuestionAndChoiceSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
#---------

# 디렉토리 -> 라이브러리 변경
# /library/<int:library_id>/directory/<int:directory_id>/change/
class LibraryChangeAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, directory_id):
        library = get_object_or_404(Library, user=user, id=library_id)
        new_library_title = request.body.get('new_library_title')
        new_library = get_object_or_404(Library, user=user, title=new_library_title)
        directory = get_object_or_404(Directory, id=directory_id)
        directory.library = new_library
        directory.save()
        return Response({"message": "문제 폴더를 다른 라이브러리로 이동하는데에 성공했습니다"}, status=status.HTTP_200_OK)

# 디렉토리 -> 공유
# /library/<int:library_id>/directory/<int:directory_id>/share/
class DirectoryShareAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, directory_id):
        user = request.user
        shared_title = request.data.get('shared_title')
        shared_content = request.data.get('shared_content')
        shared_tags = request.data['shared_tags']
        
        with transaction.atomic():
            directory = get_object_or_404(Directory, id=directory_id)
            shared = Shared.objects.create(user=user, shared_title = shared_title, shared_content = shared_content, directory=directory)
            
            for shared_tag in shared_tags:
                title = shared_tag['name']
                SharedTag.objects.create(shared=shared, name=title)
    
        return Response({"message": "성공적으로 업로드 되었습니다."}, status=status.HTTP_200_OK)

# get(디렉토리 내 문제 전체 조회
# /library/<int:library_id>/directory/<int:directory_id>/question/
class QuestionAPIView(views.APIView):
    def get(self, request, directory_id):
        directory = get_object_or_404(Directory, pk = directory_id)
        questions = Question.objects.filter(directory = directory)
        serializer = QuestionSerializer(questions, many=True) 
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
# patch(문제 수정), delete(문제 삭제)
# /question/<int:question_id>/
class QuestionDetailAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, question_id):
        question = get_object_or_404(Question, pk = question_id)
        serializer = QuestionAndChoiceSerializer(question)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def patch(self, request, question_id):
        with transaction.atomic():
            question = get_object_or_404(Question, pk=question_id)
            
            # Question 객체 필드 업데이트
            new_title = request.data.get('question_title')
            if new_title is not None:
                question.question_title=new_title

            new_content = request.data.get('question_content')
            if new_content is not None:
                question.question_content=new_content
            new_answer = request.data.get('question_answer')
            if new_answer is not None:
                question.question_answer = new_answer
            new_explanation = request.data.get('question_explanation')
            if new_explanation is not None:
                question.question_explanation = new_explanation
            question.save()
            
            choices = request.data.get('choices', [])
            if choices is not None:
                for cho in choices:
                    choice_num = cho.get('choice_num')
                    choice_content = cho.get('choice_content')
                    choice = get_object_or_404(Choice, question=question, choice_num=choice_num)
                    if choice_content is not None:
                        choice.choice_content = choice_content
                    choice.save()  # Save each choice inside the loop

        return Response({"message": "문제가 성공적으로 업데이트되었습니다."}, status=status.HTTP_200_OK)   
    def delete(self, request, question_id):
        try:
            with transaction.atomic():  # 트랜잭션 시작
                question = get_object_or_404(Question, id=question_id)
                question_num = question.question_num
                question.delete()
                
                # 삭제된 question_num보다 큰 모든 Question 객체를 조회합니다. 
                questions_to_update = Question.objects.filter(question_num__gt=question_num)
                for q in questions_to_update:
                    q.question_num -= 1
                    q.save()

            return Response({'message': '문제가 성공적으로 삭제되었습니다'}, status=status.HTTP_200_OK)

        except Question.DoesNotExist:
            return Response({'error': '문제를 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)
        
#  patch(문제 풀이(정답여부 수정, 현재 풀고있는 문제정보 업데이트))
# /question/<int:question_id>/solve/
class QuestionSolveAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, question_id):
        #answer = request.body.get('answer')
        last_solved = request.data.get('last_solved') # 문제를 맞추면 true, 아니면 false 
        if last_solved is None:
            return Response({'message': '정답 여부를 입력해주세요'}, status=status.HTTP_400_BAD_REQUEST)       
        question = get_object_or_404(Question, pk=question_id)
        question.last_solved = last_solved
        question.save()
        
        return Response({'message': '문제를 풀었습니다.', "ls":last_solved},status=status.HTTP_200_OK)        

class QuestionAllSolveAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, directory_id):
        last_solved = request.data.get('last_solved')
        directory = get_object_or_404(Directory, pk=directory_id)
        directory.questions.update(last_solved=last_solved)
        
        return Response({'message': '문제 풀이를 완료했습니다'}, status=status.HTTP_200_OK)

# 문제 스크랩
# /question/<int:question_id>/scrap/
class QuestionScrapAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, question_id):
        
        with transaction.atomic():
            is_scrapped = request.data.get('is_scrapped')
            dir_name = request.data.get('dir_name')
            
            question = get_object_or_404(Question, pk=question_id)
            user = request.user
            
            question.is_scrapped = is_scrapped
            question.save()
            
            if is_scrapped:
                library, created = Library.objects.get_or_create(user=user, title="스크랩한 문제들")
                directory, created = Directory.objects.get_or_create(user=user, library=library, title=dir_name)
                scrapped_question  = Question.objects.create(directory=directory, question_num=question.question_num, question_title=question.question_title, question_content=question.question_content, question_answer=question.question_answer, question_explanation=question.question_explanation, question_type=question.question_type, is_scrapped=True)
                scrapped_choices = Choice.objects.filter(question=question)
                for scrapped_choice in scrapped_choices:
                    Choice.objects.create(question=scrapped_question, choice_num=scrapped_choice.choice_num, choice_content=scrapped_choice.choice_content)
            else: # 스크랩 취소
                scrapped_question = Question.objects.get(directory=directory, question_num=question.question_num)
                scrapped_question.delete()
        return Response({'message': '스크랩 성공했습니다.'},status=status.HTTP_200_OK)          


