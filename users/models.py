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
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=50, unique=True, null=True)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user_name = models.CharField(blank = True, max_length=30)
    #이메일과 비밀번호
    profile = models.ImageField(upload_to='%Y%m%d/', null=True, blank=True)
	# 헬퍼 클래스 사용
    objects = UserManager()

	# 사용자의 username field는 email으로 설정 (이메일로 로그인)
    USERNAME_FIELD = 'email'

class WebProvider(models.Model):
    user = models.ForeignKey(User, related_name="web_provider", on_delete=models.CASCADE, to_field='uuid')
    provider_type = models.CharField(max_length=30)
    provider_id = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'web_provider'
