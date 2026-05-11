from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount
from .models import Category, Article, Author, ApiBibleSyncStatus, Essay, UserProfile

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

@admin.register(ApiBibleSyncStatus)
class ApiBibleSyncStatusAdmin(admin.ModelAdmin):
    change_list_template = "admin/main_florife/apibiblesyncstatus/change_list.html"

@admin.register(Essay)
class EssayAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'is_featured', 'created_at')
    list_filter = ('category', 'status', 'is_featured', 'created_at')
    search_fields = ('title', 'content', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('status', 'is_featured')
    ordering = ('-created_at',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username', 'user__email', 'bio')


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'first_name', 'is_staff', 'social_provider', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'username', 'first_name')
    ordering = ('-date_joined',)

    def social_provider(self, obj):
        accounts = SocialAccount.objects.filter(user=obj)
        if accounts:
            return ', '.join(a.provider for a in accounts)
        return '—'
    social_provider.short_description = 'Proveedor'

