"""
URL configuration for florilegiofe project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from main_florife import views
from main_florife import views_api_bible

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.dashboard, name="index"),
    path("articulos/", views.article_list, name="article_list"),
    path("ensayos/", views.essay_list, name="essay_list"),
    path("ensayo/<slug:slug>/", views.essay_detail, name="essay_detail"),
    path("buscar/", views.search_view, name="search"),
    path("articulo/<slug:slug>/", views.article_detail, name="article_detail"),
    path("privacidad/", views.privacy, name="privacy"),
    path("terminos/", views.terms, name="terms"),
    path("contacto/", views.contact, name="contact"),
    path("estudios/", views.estudios, name="estudios"),
    path("planes/", views.planes, name="planes"),
    path("mis-estudios/", views.mis_estudios, name="mis_estudios"),
    path("apoyo/", views.apoyo, name="apoyo"),
    path("api/versiculo/", views.api_get_versiculo, name="api_get_versiculo"),
    path("api/estudios/guardar/", views.api_save_study, name="api_save_study"),
    path("api/estudios/<int:study_id>/", views.api_get_study, name="api_get_study"),
    
    # Auth URLs
    path("registro/", views.register_view, name="register"),
    path("verificar-email/", views.verify_email_view, name="verify_email"),
    path("iniciar-sesion/", views.login_view, name="login"),
    path("cerrar-sesion/", views.logout_view, name="logout"),
    path("perfil/", views.profile_view, name="profile"),
    path("api/perfil/avatar/", views.api_update_avatar, name="update_avatar"),

    # Allauth (Google OAuth, etc.)
    path("accounts/", include("allauth.urls")),

    # API Bible Sync Endpoints for the Admin Panel
    path("api/admin/bible-status/", views_api_bible.api_bible_status, name="api_bible_status"),
    path("api/admin/bible-sync/<str:version_key>/setup/", views_api_bible.api_bible_sync_book_setup, name="api_bible_sync_book_setup"),
    path("api/admin/bible-sync/<str:version_key>/sync/<int:libro_num>/<int:capitulo_num>/", views_api_bible.api_bible_sync_chapter, name="api_bible_sync_chapter"),
    path("api/admin/bible-sync/<str:version_key>/finish/", views_api_bible.api_bible_finish_sync, name="api_bible_finish_sync"),
]
