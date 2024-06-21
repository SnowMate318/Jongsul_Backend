from django.db import models
from users.models import User
from questions.models import Directory

class Shared(models.Model):
    user = models.ForeignKey(User,related_name = 'shareds', on_delete=models.CASCADE)
    shared_title = models.CharField(max_length=30)
    shared_content = models.CharField(max_length=500)
    shared_upload_datetime = models.DateTimeField(auto_now_add=True)
    is_activated = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    directory = models.ForeignKey(Directory, related_name='directory',on_delete=models.CASCADE, null=True, blank=True)
    download_count = models.IntegerField(default = 0)

    class Meta:
        db_table = 'shared'
        

class SharedTag(models.Model):
    shared = models.ForeignKey(Shared,related_name = 'shared_tags', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    class Meta:
        db_table = "shared_tag"
        constraints = [
            models.UniqueConstraint(
                fields = ["shared", "name"],
                name = "unique shared tag name"
            )
        ]
  
        
