from django.contrib import admin
from .models import Book, QueryCache, UserOTP

admin.site.site_header = "Administration Dashboard"
admin.site.site_title = "NSR BOOKS Admin"
admin.site.index_title = "Welcome to the Administration Dashboard"

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'rating', 'purchases_count', 'created_at')
    search_fields = ('title', 'author')

@admin.register(QueryCache)
class QueryCacheAdmin(admin.ModelAdmin):
    list_display = ('query', 'created_at')
    search_fields = ('query', 'response')

@admin.register(UserOTP)
class UserOTPAdmin(admin.ModelAdmin):
    list_display = ('email', 'code', 'is_verified', 'created_at')
    search_fields = ('email',)
