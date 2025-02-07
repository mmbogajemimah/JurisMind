import uuid

from django.db import models


class LegalDocument(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="legal_documents/")  # Store actual files
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class QueryJob(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    query = models.TextField()
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    result = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.id}: {self.query[:50]}..."