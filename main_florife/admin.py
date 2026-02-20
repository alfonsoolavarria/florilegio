from django.contrib import admin
from .models import Category, Article, Author

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name',)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'social_handle')
    search_fields = ('name', 'bio')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'is_featured', 'created_at')
    list_filter = ('category', 'status', 'is_featured', 'created_at')
    search_fields = ('title', 'content', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('status', 'is_featured')
    ordering = ('-created_at',)
