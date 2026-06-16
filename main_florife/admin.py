from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db import models
from allauth.socialaccount.models import SocialAccount
from .models import Category, Article, Author, ApiBibleSyncStatus, Essay, UserProfile, UserStudy, AgeCategory, MadreMaestraResource
from .widgets import CKEditorWidget

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name',)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'user_email', 'social_handle', 'has_photo')
    search_fields = ('name', 'bio', 'user__email')
    raw_id_fields = ('user',)
    fieldsets = (
        (None, {'fields': ('user', 'name', 'bio', 'image_url', 'photo', 'social_handle')}),
    )

    def has_photo(self, obj):
        return bool(obj.photo)
    has_photo.boolean = True
    has_photo.short_description = 'Foto'

    def user_email(self, obj):
        return obj.user.email if obj.user else '—'
    user_email.short_description = 'Usuario'

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},
    }
    list_display = ('title', 'author', 'category', 'status', 'is_featured', 'created_at', 'meta_description_preview')
    list_filter = ('category', 'status', 'is_featured', 'created_at')
    search_fields = ('title', 'content', 'tags', 'meta_description')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('status', 'is_featured')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'author', 'category', 'image_url', 'content', 'tags')}),
        ('SEO', {'fields': ('meta_description',), 'classes': ('collapse',),
                 'description': 'Descripción para motores de búsqueda y redes sociales. Máximo 160 caracteres.'}),
        ('Publicación', {'fields': ('status', 'is_featured')}),
    )

    def meta_description_preview(self, obj):
        if obj.meta_description:
            return obj.meta_description[:80] + ('...' if len(obj.meta_description) > 80 else '')
        return '(auto-generado)'
    meta_description_preview.short_description = 'Meta Desc'

@admin.register(ApiBibleSyncStatus)
class ApiBibleSyncStatusAdmin(admin.ModelAdmin):
    change_list_template = "admin/main_florife/apibiblesyncstatus/change_list.html"

@admin.register(Essay)
class EssayAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},
    }
    list_display = ('title', 'author', 'category', 'status', 'is_featured', 'created_at', 'meta_description_preview')
    list_filter = ('category', 'status', 'is_featured', 'created_at')
    search_fields = ('title', 'content', 'tags', 'meta_description')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('status', 'is_featured')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'author', 'category', 'image_url', 'content', 'tags')}),
        ('SEO', {'fields': ('meta_description',), 'classes': ('collapse',),
                 'description': 'Descripción para motores de búsqueda y redes sociales. Máximo 160 caracteres.'}),
        ('Publicación', {'fields': ('status', 'is_featured')}),
    )

    def meta_description_preview(self, obj):
        if obj.meta_description:
            return obj.meta_description[:80] + ('...' if len(obj.meta_description) > 80 else '')
        return '(auto-generado)'
    meta_description_preview.short_description = 'Meta Desc'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username', 'user__email', 'bio')

@admin.register(UserStudy)
class UserStudyAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'reference', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email', 'title', 'reference', 'content')
    ordering = ('-updated_at',)


@admin.register(AgeCategory)
class AgeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort_order')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(MadreMaestraResource)
class MadreMaestraResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'age_category', 'status', 'time_minutes', 'created_at')
    list_filter = ('age_category', 'status', 'created_at')
    search_fields = ('title', 'content', 'summary', 'bible_passage', 'objective', 'materials')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('status',)
    ordering = ('-created_at',)
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'age_category', 'image_url')}),
        ('Plan de Lección', {'fields': ('bible_passage', 'key_verse', 'objective', 'materials', 'time_minutes')}),
        ('Contenido', {'fields': ('content', 'summary', 'tags')}),
        ('Publicación', {'fields': ('status',)}),
    )


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

