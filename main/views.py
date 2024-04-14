from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework import views 
from rest_framework.filters import OrderingFilter
from .models import User, SharedTag, Shared, Library, Directory, Question, Choice
from .serializers import UserSerializer, SharedOnlySerializer, SharedTagSerializer, SharedWithTagSerializer, LibrarySerializer, DirectorySerializer, QuestionSerializer
from .serializers import ChoiceSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework import status
from rest_framework.response import Response
import jwt
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from django.contrib.auth import authenticate
from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import IsAuthenticated  # 인증된 사용자만 접근 허용



class RegisterAPIView(views.APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # jwt 토큰 접근
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            response = Response(
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
            
            # jwt 토큰 => 쿠키에 저장
            response.set_cookie("access", access_token, httponly=True)
            response.set_cookie("refresh", refresh_token, httponly=True)
    
class AuthAPIView(views.APIView):
    # 유저 정보 확인
    def get(self, request):
        try:
            # access token을 decode 해서 유저 id 추출 => 유저 식별
            access = request.COOKIES['access'] # 이 부분 다른 방법으로
            payload = jwt.decode(access, SECRET_KEY, algorithms=['HS256'])
            pk = payload.get('user_id')
            user = get_object_or_404(User, pk=pk)
            serializer = UserSerializer(instance=user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except(jwt.exceptions.ExpiredSignatureError):
            # 토큰 만료 시 토큰 갱신
            data = {'refresh': request.COOKIES.get('refresh', None)}
            serializer = TokenRefreshSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                access = serializer.data.get('access', None)
                refresh = serializer.data.get('refresh', None)
                payload = jwt.decode(access, SECRET_KEY, algorithms=['HS256'])
                pk = payload.get('user_id')
                user = get_object_or_404(User, pk=pk)
                serializer = UserSerializer(instance=user)
                response = Response(serializer.data, status=status.HTTP_200_OK)
                response.set_cookie('access', access)
                response.set_cookie('refresh', refresh)
                return response
            raise jwt.exceptions.InvalidTokenError

        except(jwt.exceptions.InvalidTokenError):
            # 사용 불가능한 토큰일 때
            return Response(status=status.HTTP_400_BAD_REQUEST)

    # 로그인
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
            # jwt 토큰 => 쿠키에 저장
            response.set_cookie("access", access_token, httponly=True)
            response.set_cookie("refresh", refresh_token, httponly=True)
            return response
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    # 로그아웃
    def delete(self, request):
        # 쿠키에 저장된 토큰 삭제 => 로그아웃 처리
        response = Response({
            "message": "Logout success"
            }, status=status.HTTP_202_ACCEPTED)
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        return response
    
class SharedAPIView(views.APIView):
    
    def get(self, request):
        
        shareds = Shared.objects.filter(is_activated = True, is_deleted = False)
        serializer = SharedOnlySerializer(shareds, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)    
    

    
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
        
        
        
        serializer = SharedOnlySerializer(shareds, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class SharedUserFilteredAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        
        # request.user를 사용하여 현재 인증된 사용자 객체를 가져옴
        user = request.user
        if not user.is_authenticated:  # 사용자가 인증되지 않았다면 404 에러 처리
            raise Http404
        
        shareds = Shared.objects.filter(user=user, is_activated = True, is_deleted = False)  # 현재 사용자와 연결된 Shared 객체들을 필터링
        serializer = SharedOnlySerializer(shareds, many=True)  # 필터링된 객체들을 시리얼라이즈
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
            
class SharedDetailAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, shared_id):
        shared = get_object_or_404(Shared, id=shared_id)
        
        serializer = SharedWithTagSerializer(shared) 
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # 커뮤니티 다운로드
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
    #삭제    
    def delete(self, request, shared_id):
        shared = get_object_or_404(Shared, id=shared_id)
        shared.is_deleted = True
        shared.save()
        return Response({"message": "Shared successfully marked as deleted."}, status=status.HTTP_200_OK)     
    
class LibraryViewSet(viewsets.ModelViewSet):
    serializer_class = LibrarySerializer    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        #인증된 사용자의 Library 객체 반환
        user = self.request.user
        return Library.objects.filter(user=user, is_deleted=False)
    
    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        library_id = kwargs.get('pk')
        library = get_object_or_404(Library, id=library_id)
        directories = Directory.objects.filter(user=user, library=library)
        for directory in directories:
            directory.is_deleted=True
            directory.save()
            
        library.is_deleted=True
        library.save()
        
        return Response({"message": "라이브러리 삭제가 완료되었습니다", }, status=status.HTTP_204_NO_CONTENT)
        
    
#없는걸 만들어낼 수 있냐? -> put
#있는것만 건들거냐? -> patch

class DirectoryAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, library_id):
        user = request.user
        library = get_object_or_404(Library, user=user, id=library_id)
        directories = Directory.objects.filter(library = library_id, is_deleted=False)
        serializer = DirectorySerializer(directories, many=True)
        return Response({"message": "성공적으로 디렉토리 정보를 가져왔습니다."}, status=status.HTTP_200_OK)
    
    

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
    
class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    
 
    
