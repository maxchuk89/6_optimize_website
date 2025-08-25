from django.contrib import admin
from .models import Post, Tag, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'published_at', 'author')
    list_select_related = ('author',)
    raw_id_fields = ('author', 'likes', 'tags')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'published_at', 'author', 'post')
    list_select_related = ('author', 'post')
    raw_id_fields = ('author', 'post')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
