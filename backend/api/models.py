from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rating = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    url = models.URLField(max_length=500, null=True, blank=True)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    purchases_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class QueryCache(models.Model):
    query = models.TextField()
    response = models.TextField()
    sources = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.query[:50]
class UserOTP(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.email} - {self.code}"
