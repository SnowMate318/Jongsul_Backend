from django.db import models
import uuid
from django.core.exceptions import ValidationError
from users.models import User

# #문제 라이브러리 테이블
class Library(models.Model):
    user = models.ForeignKey(User, related_name="library", on_delete=models.CASCADE)
    title = models.CharField(max_length=30, null=True)
    library_last_access = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'library'
        constraints = [
            models.UniqueConstraint(
                fields = ["user", "title"],
                name = "unique library title"
            )
        ]
   
class Directory(models.Model):
    library = models.ForeignKey(Library, related_name = 'directories', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name = 'directories', on_delete=models.CASCADE)
    last_successed = models.IntegerField(null=True)
    concept = models.CharField(max_length=8000, null=True)
    title = models.CharField(max_length=30)
    question_type = models.CharField(max_length=100, null=True, blank=True)
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

  
# #문제 테이블        
class Question(models.Model):
    question_num = models.IntegerField()
    directory = models.ForeignKey(Directory, related_name="questions", on_delete=models.CASCADE)
    question_title = models.CharField(max_length=1000)
    question_content = models.CharField(max_length=2000, null=True, blank=True)
    question_answer = models.CharField(max_length=100)
    question_explanation = models.CharField(max_length=2000)
    question_type = models.IntegerField()
    last_solved = models.BooleanField(null=True)
    is_scrapped = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'question'
    
class Choice(models.Model):
    question = models.ForeignKey(Question, related_name="choices", on_delete=models.CASCADE)
    choice_num = models.IntegerField()
    choice_content = models.CharField(max_length=500)
    
    class Meta:
        db_table = 'choice'

        
