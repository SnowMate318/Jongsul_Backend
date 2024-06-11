from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework import views 
from rest_framework.filters import OrderingFilter
from .models import User, SharedTag, Shared, Library, Directory, Question, Choice, Image
from .serializers import UserSerializer, SharedOnlySerializer, SharedTagSerializer, SharedWithTagAndUserWithDirectorySerializer, LibraryWithDirectorySerializer, DirectorySerializer, QuestionSerializer
from .serializers import ChoiceSerializer, QuestionAndChoiceSerializer, LibraryWithDirectorySerializer , SmallDirectorySerializer#, LibrarySerializer, 
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

from rest_framework import status
from rest_framework.response import Response
import jwt
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from django.contrib.auth import authenticate
from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly  # 인증된 사용자만 접근 허용
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import AccessToken
from django.db import transaction
from .langchain_gpt import getQuestions
from .image_to_string import imageToString
from .pdf_to_string import pdfToString
# /register/, post(회원가입)
class RegisterAPIView(views.APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # jwt 토큰 접근
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            return Response(
                {
                    "user": serializer.data,
                    "message": "register successs",
                    "token": {
                        "access": access_token,
                        "refresh": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response({'message':'유저 시리얼라이져 밸리디에이션 에러', 'error': serializer.errors},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# /auth/, get(유저정보 확인), post(로그인), patch(유저정보 수정)
class AuthAPIView(views.APIView):
    def get(self, request):
        permission_classes = [IsAuthenticated]
        try:
            # access token을 decode 해서 유저 id 추출 => 유저 식별
            # token = request.headers.get('Authorization', '')[7:]
            # payload = jwt.decode(token, SECRET_KEY,Salgorithms=['HS256'])
            # user_id = payload.get('user_id')
            # user = get_object_or_404(User, pk=user_id, is_activated=True)
            user = request.user
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except(jwt.exceptions.ExpiredSignatureError):
            # 토큰 만료 시 토큰 갱신
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        except(jwt.exceptions.InvalidTokenError):
            # 사용 불가능한 토큰일 때
            return Response({"message": f"사용 불가능한 토큰입니다 {token}"},status=status.HTTP_400_BAD_REQUEST)
    def post(self, request):
    	# 유저 인증
        user = authenticate(
            email=request.data.get("email"), password=request.data.get("password")
        )
        # 이미 회원가입 된 유저일 때
        if user is not None:
            serializer = UserSerializer(user)
            # jwt 토큰 접근
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            response = Response(
                {
                    "user": serializer.data,
                    "message": "login success",
                    "token": {
                        "access": access_token,
                        "refresh": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )
            return response
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    #def delete(self, request):
        
        # #클라이언트에서 해야할 것: 
        # # shared_preference의 access_token, refresh_token 삭제
        # # 로그인페이지로 이동
        # response = Response({
        #     "message": "Logout success"
        #     }, status=status.HTTP_202_ACCEPTED)

        # return response
        # # 유저 정보 수정
    def patch(self, request):
        permission_classes = [IsAuthenticated]
        try:
            user = request.user
            # access token을 decode 해서 유저 id 추출 => 유저 식별
            # token = request.headers.get('Authorization', '').split('Bearer ')[1]
            # payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            # user_id = payload.get('user_id')
            # user = get_object_or_404(User, pk=user_id, is_activated=True)
            new_name = request.data.get('user_name')
            new_image = request.data.get('profile')
            serializer = UserSerializer(user)
            if new_name is None and new_image is None:
                return Response({"message": "수정할 내용이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
            if new_name is not None:
                user.user_name = new_name
            if new_image is not None:
                user.profile = new_image
            
            user.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except(jwt.exceptions.ExpiredSignatureError):
            # 토큰 만료 시 토큰 갱신
            return Response({"message: 만료된 토큰입니다."},status=status.HTTP_401_UNAUTHORIZED)

        except(jwt.exceptions.InvalidTokenError):
            # 사용 불가능한 토큰일 때
            return Response({"message: 유효하지 않은 토큰입니다."},status=status.HTTP_400_BAD_REQUEST)

# /auth/delete, delete(유저정보 삭제)        
class UserDeleteView(views.APIView):
    def delete(self, request):
        try:
            user = request.user
            if user.is_active:
                # 사용자 비활성화
                user.is_active = False
                user.save()
                return Response({"message": "회원 탈퇴 처리가 완료되었습니다."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "이미 비활성화된 계정입니다."}, status=status.HTTP_400_BAD_REQUEST)

        except jwt.ExpiredSignatureError:
            return Response({"error": "토큰이 만료되었습니다."}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"error": "유효하지 않은 토큰입니다."}, status=status.HTTP_400_BAD_REQUEST)
       

#/auth/find , post(이메일 찾기)
class FindEmailView(views.APIView):
    def post(self, rquest):
        serializer = EmailFindSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": "이메일이 올바르지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=serializer.data.get('email'), is_active=True).exists():
            return Response({"message": "이메일이 존재합니다."}, status=status.HTTP_200_OK)
        elif User.objects.filter(email=serializer.data.get('email'), is_active=False).exists():
            return Response({"message": "탈퇴 처리된 회원입니다."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message": "이메일이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)




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

# class LibraryWithDirectoryAPIView(views.APIView):
#     def get(self, request):
#         user = request.user
#         libraries = Library.objects.filter(user=user)    
#         serializer = LibraryWithDirectorySerializer(libraries, many=True)
        
#         return Response(serializer.data, status=status.HTTP_200_OK)

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
                questions = getQuestions(script, difficulty, multiple_choice, short_answer, ox_prob, all_prob)['questions']
                if questions is None:
                    return Response({'message': 'GPT_API 관련 오류'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                library = get_object_or_404(Library, id=library_id)
                directory = Directory.objects.create(library=library, title=title, user=request.user)
                
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

# 문제 스크랩
# /question/<int:question_id>/scrap/
class QuestionScrapAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, question_id):
        
        is_scrapped = request.data.get('is_scrapped')
        question = get_object_or_404(Question, pk=question_id)
        user = request.user
        question.is_scrapped = is_scrapped
        question.save()
        
        return Response({'message': '스크랩 성공했습니다.'},status=status.HTTP_200_OK)          

class FileAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 사용자로부터 이미지 파일을 받습니다.
        image_file = request.FILES.get('image')
        pdf_file = request.FILES.get('file')
        print(test)
        print(request.accepted_media_type)
        if not image_file and not pdf_file:
            return Response({'error': '이미지 또는 PDF 파일이 제공되지 않았습니다.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if image_file:
                extracted_text = imageToString(image_file)
                new_image = Image.objects.create(image=image_file, text=extracted_text)
            elif pdf_file:
                extracted_text = pdfToString(pdf_file)
                new_pdf = Image.objects.create(type_data='PDF', text=extracted_text)

            return Response({'message': '파일 처리 완료', 'extracted_text': extracted_text}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error': '파일 처리 중 오류가 발생했습니다.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
        #return Response({'message': '이미지 처리 완료', 'extracted_text': extracted_text}, status=status.HTTP_200_OK)
