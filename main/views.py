from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework import views 
from rest_framework.filters import OrderingFilter
from .models import User, SharedTag, Shared, Library, Directory, Question, Choice
from .serializers import UserSerializer, SharedOnlySerializer, SharedTagSerializer, SharedWithTagSerializer, LibrarySerializer, DirectorySerializer, QuestionSerializer
from .serializers import ChoiceSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import status
from rest_framework.response import Response
import jwt
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from django.contrib.auth import authenticate
from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly  # 인증된 사용자만 접근 허용
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import AccessToken
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
        try:
            # access token을 decode 해서 유저 id 추출 => 유저 식별
            token = request.headers.get('Authorization', '').split('Bearer ')[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            user = get_object_or_404(User, pk=user_id, is_activated=True)
            serializer = UserSerializer(instance=user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except(jwt.exceptions.ExpiredSignatureError):
            # 토큰 만료 시 토큰 갱신
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        except(jwt.exceptions.InvalidTokenError):
            # 사용 불가능한 토큰일 때
            return Response(status=status.HTTP_400_BAD_REQUEST)
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
        try:
            # access token을 decode 해서 유저 id 추출 => 유저 식별
            token = request.headers.get('Authorization', '').split('Bearer ')[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            user = get_object_or_404(User, pk=user_id, is_activated=True)
            
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()  # 업데이트된 데이터 저장
                return Response({"message": "유저 정보가 성공적으로 수정되었습니다."}, status=status.HTTP_200_OK)
            
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
            # 토큰에서 사용자 ID 추출
            token = request.headers.get('Authorization', '').split('Bearer ')[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')

            # 해당 사용자 찾기
            user = get_object_or_404(User, pk=user_id)
            if user.is_activated:
                # 사용자 비활성화
                user.is_activated = False
                user.save()
                return Response({"message": "회원 탈퇴 처리가 완료되었습니다."}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "이미 비활성화된 계정입니다."}, status=status.HTTP_400_BAD_REQUEST)

        except jwt.ExpiredSignatureError:
            return Response({"error": "토큰이 만료되었습니다."}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"error": "유효하지 않은 토큰입니다."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        

# /auth/refresh, post(리프레시토큰 갱신)
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            # 토큰 관련 오류 처리
            raise InvalidToken({"error": str(e.args[0])})

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

# /shared/, get(커뮤니티 조회)    
class SharedAPIView(views.APIView):    
    def get(self, request):
        tags = request.query_params.get('tags', None)
        user = request.query_params.get('user', None)
        # 
        if tags:
            tags_list = tags.split(',')  # 쉼표로 구분된 문자열을 리스트로 변환
            # 태그 리스트에 있는 각 태그에 대해 OR 조건 쿼리를 생성
            if user:
                q_objects = Q(sharedtag__name__in=tags_list, is_activated = True, is_deleted = False, user_id = user)
            else:
                q_objects = Q(sharedtag__name__in=tags_list, is_activated = True, is_deleted = False)
            shareds = Shared.objects.filter(q_objects).distinct()
        else:
            if user:
                shareds = Shared.objects.filter(is_activated = True, is_deleted = False, user_id = user)
            else: 
                shareds = Shared.objects.filter(is_activated = True, is_deleted = False)
        
        
        
        serializer = SharedWithTagSerializer(shareds, many=True)
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
        serializer = SharedWithTagSerializer(shareds, many=True)  # 필터링된 객체들을 시리얼라이즈
        
        return Response(serializer.data, status=status.HTTP_200_OK)
                
# /shared/<int:shared_id>/ , get(커뮤니티 상세 조회), put(커뮤니티 자료 다운로드), delete(커뮤니티 자료 삭제)
class SharedDetailAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, shared_id):
        shared = get_object_or_404(Shared, id=shared_id)
        
        serializer = SharedWithTagSerializer(shared) 
        return Response(serializer.data, status=status.HTTP_200_OK)
    def put(self, request, shared_id):
        user = request.user
        shared = get_object_or_404(Shared, id=shared_id)

        # Step 1: 사용자의 Library 확인 또는 생성
        library, created = Library.objects.get_or_create(
            user=user, defaults={'title': "다운로드한 문제들"}
        )

        # Step 2: 다운로드한 Directory 정보를 기반으로 새 Directory 인스턴스 생성
        original_directory = shared.directory
        if original_directory:
            new_directory = Directory.objects.create(
                library=library,
                concept=original_directory.concept,
                title=original_directory.title + " (복사)",
                question_type=original_directory.question_type
                # 필요한 나머지 필드도 이와 같은 방식으로 복사
            )

        # Step 3: Shared의 download_count 증가
        shared.download_count += 1
        shared.save()

        return Response({"message": "Download successful", "download_count": shared.download_count}, status=status.HTTP_200_OK)
    def delete(self, request, shared_id):
        shared = get_object_or_404(Shared, id=shared_id)
        shared.is_deleted = True
        shared.save()
        return Response({"message": "Shared successfully marked as deleted."}, status=status.HTTP_200_OK)     

# /library/ post(라이브러리 생성), get(전체 라이브러리 조회)
class LibraryAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        title = request.data.get("title")
        user = request.user
        
        library = Library.objects.create(user=user, title=title)
        return Response({'message': '새로운 라이브러리가 생성되었습니다'},status=status.HTTP_201_CREATED)
    def get(self, request):
        user = request.user
        libraries = Library.objects.filter(user=user, is_deleted=False)    
        serializer = LibrarySerializer(many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class LibraryDetailAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, library_id):
        user = request.user
        library = get_object_or_404(Library, id=library_id)
        serializer = LibrarySerializer()
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    def patch(self, request, library_id):
        user = request.user
        title = request.data.get(title)
        library = get_object_or_404(Library, id=library_id)
        library.title = title
        library.save()
        
        return Response({'message':'라이브러리 제목이 수정되었습니다'},status=status.HTTP_200_OK)
    def delete(self, request, library_id):
        user = request.user
        title = request.data.get(title)
        library = get_object_or_404(Library, id=library_id)
        library.is_deleted = true
        library.save()
        
        return Response({'message':'라이브러리 삭제가 수정되었습니다'},status=status.HTTP_200_OK)
# /library/ 뷰셋 활용    
# class LibraryViewSet(viewsets.ModelViewSet):
#     serializer_class = LibrarySerializer    
#     permission_classes = [IsAuthenticatedOrReadOnly]
    
#     def get_queryset(self, request):
#         #인증된 사용자의 Library 객체 반환
#         user = request.user
#         return Library.objects.filter(user=user, is_deleted=False)
    
#     def destroy(self, request, *args, **kwargs):
#         with transaction.atomic():
#             user = request.user
#             library_id = kwargs.get('pk')
#             library = get_object_or_404(Library, id=library_id)
#             directories = Directory.objects.filter(user=user, library=library)
#             for directory in directories:
#                 directory.is_deleted=True
#                 directory.save()
                
#             library.is_deleted=True
#             library.save()
            
#             return Response({"message": "라이브러리 삭제가 완료되었습니다", }, status=status.HTTP_204_NO_CONTENT)
    
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
            all_prob = request.data.get('all_prob')
            
            questions = getQuestions(script, difficulty, multiple_choice, short_answer, all_prob)
            if questions is None:
                return Response({'message': 'GPT_API 관련 오류'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            library = get_object_or_404(Library, id=library_id)
            
            directory = Directory.objects.create(library=library, title=title)
            
            for ques in questions:
                question = Question.objects.create(
                    directory=directory, 
                    defaults={
                        'question_num': ques['question_num'],
                        'question_title': ques['question_title'],
                        'question_answer': ques['question_answer'],
                        'question_explanation': ques['question_explanation'],
                        'question_type': ques['question_type']
                    }
                )
                choices = ques.get('choices')
                if choices is not None:
                    for cho in choices:
                        choice = Choice.objects.create(
                            question=question,
                            defaults={
                                'choice_num': cho['choice_num'],
                                'choice_content': cho['choice_content']
                            }
                        )
            
            return Response({'message': '문제 생성 완료'}, status=status.HTTP_200_OK)
    def get(self, request, library_id):
        user = request.user
        library = get_object_or_404(Library, user=user, id=library_id)
        directories = Directory.objects.filter(library = library_id, is_deleted=False)
        serializer = DirectorySerializer(directories, many=True)
        return Response({"message": "성공적으로 디렉토리 정보를 가져왔습니다."}, status=status.HTTP_200_OK)
    
# /library/<int:library_id>/directory/<int:directory_id>/ get(디렉토리 상세조회) patch(디렉토리 수정)    *delete 필요할까
class DirectoryDetailAPIView(views.APIView):
    
    permission_classes = [IsAuthenticated]
    def get(self, request, directory_id):
        directory = get_object_or_404(Directory, id = directory_id)
        serializer = DirectorySerializer(directory)
        return Response({"message": "성공적으로 디렉토리 정보를 가져왔습니다."}, status=status.HTTP_200_OK)  
    def patch(self, request, directory_id):
        library = get_object_or_404(Library, user=user, id=library_id)
        dir_title = request.body.get('title')
        if dir_title:
            library.title = lib_title
            
        dir_concept = request.body.get('concept')
        if dir_concept:
            library.concept = dir_concept
            
        dir_type = request.body.get('type')
        if dir_type:
            library.question_type = dir_type
        
        library.save()
        return Response({"message": "성공적으로 라이브러리 내용을 변경했습니다."}, status=status.HTTP_200_OK)
    def delete(self, request, directory_id):
        directory = get_object_or_404(Directory)
        directory.is_deleted=True
        directory.save()
        return Response({'message':'메시지가 성공석으로 삭제되었습니다.'}, status=status.HTTP_200_OK) # 소프트삭제

# 디렉토리 -> 라이브러리 변경
# /library/<int:library_id>/directory/<int:directory_id>/change
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
# /library/<int:library_id>/directory/<int:directory_id>/change
class DirectoryShareAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, library_id, directory_id, pk=None):
        user = request.user
        shared_title = request.data.get('shared_title')
        shared_contents = request.data.get('shared_contents')
        
        library = get_object_or_404(Library, user=user, title=lib_title)
        directory = get_object_or_404(Directory, library=library, title=dir_title)
        shared, created = Shared.objects.create(shared_title = shared_title, shared_content = shared_contents, directory=directory)
    
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
# /library/<int:library_id>/directory/<int:directory_id>/question/<int:question_id>/
class QuestionDetailAPIView(views.APIView):
    def patch(self, request, question_id):
        question = get_object_or_404(Questkon, pk = question_id)
        
        question.save()
        return Response({'message': '문제가 성공적으로 수정되었습니다.'}, status=status.HTTP_200_OK)    
    def delete(self, request, question_num):
        try:
            with transaction.atomic():  # 트랜잭션 시작
                question = Question.objects.get(question_num=question_num)
                question.delete()
                
                # 삭제된 question_num보다 큰 모든 Question 객체를 조회합니다. 
                questions_to_update = Question.objects.filter(question_num__gt=question_num)
                for q in questions_to_update:
                    q.question_num -= 1
                    q.save()

            return Response({'message': 'Question deleted and order updated successfully'}, status=status.HTTP_204_NO_CONTENT)

        except Question.DoesNotExist:
            return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)
        
#  patch(문제 풀이(정답여부 수정, 현재 풀고있는 문제정보 업데이트))
# /library/<int:library_id>/directory/<int:directory_id>/question/<int:question_id>/solve/
class QuestionSolveAPIView(views.APIView):
    def patch(self, request, question_id):
        answer = request.body.get['answer']
        last_solved = request.body.get['last_solved'] # 문제를 맞추면 true, 아니면 false        
        question = get_object_or_404(Question, pk=question_id)
        question.last_solved = last_solved
        question.save()
        
        return Response({'message': '문제를 풀었습니다.'},status=status.HTTP_200_OK)        

# 문제 스크랩
# /library/<int:library_id>/directory/<int:directory_id>/question/<int:question_id>/scrap/
class QuestionScrapAPIView(views.APIView):
    def patch(self, request, question_id):
        is_scrapped = request.body.get['is_scrapped']

        question = get_object_or_404(Question, pk=question_id)
        question.is_scrapped = is_scrapped
        question.save()
        
        return Response({'message': '스크랩 성공했습니다.'},status=status.HTTP_200_OK)          

    