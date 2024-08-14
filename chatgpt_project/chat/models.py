from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text_input = models.TextField(blank=True, null=True)  
    file_name = models.CharField(max_length=200, blank=True, null=True) 
    url_domain = models.URLField(max_length=200, blank=True, null=True)
    summary_result = models.TextField(blank=True, null=True) 
    translation_result = models.TextField(blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)  # 레코드 생성 시간

    def __str__(self):
        return f"Search by {self.user.username} on {self.created_at}"