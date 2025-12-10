from django.contrib import admin
from .models import Message, Blog


# Register your models here.

admin.site.register(Message)
admin.site.register(Blog)

# @admin.register(Message)
# class MessageAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'subject', 'is_read', 'created_at')
    
# @admin.register(Blog)
# class BlogAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title', 'author', 'status', 'created_at', 'updated_at')
