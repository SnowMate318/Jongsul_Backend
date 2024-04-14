from django.db import models
import uuid
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, password, **kwargs):
    # 주어진 이메일, 비밀번호 등 개인정보로 User 인스턴스 생성
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=email,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, password=None, **extra_fields):     
    #주어진 이메일, 비밀번호 등 개인정보로 User 인스턴스 생성, 최상위 사용자 권한 부여
        superuser = self.create_user(
            email=email,
            password=password,
        )
        
        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.is_active = True
        
        superuser.save(using=self._db)
        return superuser

# AbstractBaseUser를 상속해서 유저 커스텀
class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=30, unique=True, null=False, blank=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user_name = models.CharField(null = True, max_length=30)
    #이메일과 비밀번호
    profile = models.URLField(max_length=200, null=True)
	# 헬퍼 클래스 사용
    objects = UserManager()

	# 사용자의 username field는 email으로 설정 (이메일로 로그인)
    USERNAME_FIELD = 'email'



# #문제 라이브러리 테이블
class Library(models.Model):
    user = models.ForeignKey(User, related_name="library", on_delete=models.CASCADE)
    title = models.CharField(max_length=30, null=True)
    library_last_access = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    class Meta:
        db_table = 'library'
        constraints = [
            models.UniqueConstraint(
                fields = ["user", "title"],
                name = "unique library title"
            )
        ]
   
# #문제 디렉토리 테이블     


class Directory(models.Model):
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    last_successed = models.IntegerField(null=True)
    concept = models.CharField(max_length=2000, null=True)
    title = models.CharField(max_length=30)
    question_type = models.CharField(max_length=100, null=True)
    directory_last_access = models.DateTimeField(auto_now=True)
    is_scrap_directory = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    # 스크랩 폴더 여부(스크랩 폴더 추가시 해당 항목을 True로 설정하기)
    
    class Meta:
        db_table = 'directory'
        
        constraints = [
            models.UniqueConstraint(
                fields = ["library", "title"],
                name = "unique directory title"
            )
        ]

class Shared(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shared_title = models.CharField(max_length=30)
    shared_content = models.CharField(max_length=500)
    shared_upload_datetime = models.DateTimeField(auto_now_add=True)
    is_activated = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    directory = models.ForeignKey(Directory, on_delete=models.CASCADE, null=True, blank=True)
    download_count = models.IntegerField(default = 0)

    class Meta:
        db_table = 'shared'
        

class SharedTag(models.Model):
    shared = models.ForeignKey(Shared,related_name = 'shared_tag', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    class Meta:
        db_table = "shared_tag"
        constraints = [
            models.UniqueConstraint(
                fields = ["shared", "name"],
                name = "unique shared tag name"
            )
        ]
  
# #문제 테이블        
class Question(models.Model):
    question_num = models.IntegerField()
    directory = models.ForeignKey(Directory, related_name="question", on_delete=models.CASCADE)
    question_title = models.CharField(max_length=1000)
    question_content = models.CharField(max_length=2000, null=True)
    question_answer = models.CharField(max_length=100)
    question_explaination = models.CharField(max_length=2000)
    question_type = models.IntegerField()
    is_scrapped = models.BooleanField(default=False)

    class Meta:
        db_table = 'question'
    
class Choice(models.Model):
    question = models.ForeignKey(Question, related_name="choice", on_delete=models.CASCADE)
    choice_num = models.IntegerField()
    choice_content = models.CharField(max_length=500)
    
class Image(models.Model):
    image_url = models.ImageField(upload_to='images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.pk} uploaded on {self.created_at}" # 관리자페이지, 디버깅에 사용
    
#유저 정보 테이블
# class ServiceUser(models.Model):
#     user_id = models.CharField(max_length=100, primary_key=True)
#     user_name = models.CharField(null=False, max_length=30)
#     #이메일과 비밀번호
#     profile = models.URLField(max_length=200, null=True)
#     #올린 문제? 아니면 라이브러리?
    
#     class Meta: 
#         #app_label = 'ulifeapp'
#         db_table = 'serviceuser'


# #태그 정보 테이블
# class UserTag(models.Model):
#     user = models.ForeignKey(ServiceUser, on_delete=models.CASCADE)
#     #user_tag_id = models.AutoField(primary_key=True)
#     user_tag_name = models.CharField(max_length=30, null=False)
#     #태그정보: 최대 30자
#     class Meta:
#         db_table = 'usertag'

# class Tag(models.Model):
#     tag_name = models.CharField(max_length=30)
#     class Meta:
#         db_table = 'tag'    

# class Search(models.Model):
#     user_id = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE)
#     shared_id = models.ForeignKey(Shared, related_name='search', on_delete=models.CASCADE)
#     shared_name = models.CharField(max_length=50, null=True)
#     shared_content = models.CharField(null=True)
#     shared_user_name = models.CharField(max_length=30, null=True)  
#     search_tag = models.CharField(max_length=30, null=True)

#     class Meta:
#         unique_together = ('user_id', 'shared_id')
#         managed = False
#         db_table = 'search'


        
