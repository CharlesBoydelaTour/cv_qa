from django.db import models

# Create your models here.
from django.db import models


class Message(models.Model):
    content = models.TextField()
    answer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Q: {self.content[:50]} | A: {self.answer[:50] if self.answer else 'No answer'}"

    class Meta:
        ordering = ["-created_at"]
