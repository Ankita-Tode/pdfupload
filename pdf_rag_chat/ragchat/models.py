from django.db import models
from django.db import models

class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="docs/")
    num_pages = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    # path to FAISS assets
    faiss_index_path = models.CharField(max_length=500, blank=True)
    chunks_jsonl_path = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.id}: {self.title}"

class ChatSession(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="chats")
    created_at = models.DateTimeField(auto_now_add=True)

class ChatMessage(models.Model):
    ROLE_CHOICES = [("user", "user"), ("assistant", "assistant")]
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=16, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


# Create your models here.
