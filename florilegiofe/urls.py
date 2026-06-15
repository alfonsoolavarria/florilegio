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
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from main_florife import views
from main_florife import views_api_bible
from main_florife import views_youversion
from main_florife import views_authors
from main_florife.admin_views import admin_bible_import, admin_import_rv1960_strongs, admin_import_strong_concord
from main_florife.sitemap import ArticleSitemap, EssaySitemap, StaticSitemap

sitemaps = {
    'articles': ArticleSitemap,
    'essays': EssaySitemap,
    'static': StaticSitemap,
}


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /api/",
        "Disallow: /accounts/",
        "Disallow: /mis-estudios/",
        "Disallow: /perfil/",
        "",
        "Sitemap: https://florilegiodelafe.com/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

urlpatterns = [
    # Importar versiones bíblicas desde JSON (admin) — antes que admin.site.urls
    path("admin/bible-import/", admin_bible_import, name="admin_bible_import"),
    path("admin/import-rv1960-strongs/", admin_import_rv1960_strongs, name="admin_import_rv1960_strongs"),
    path("admin/import-strong-concord/", admin_import_strong_concord, name="admin_import_strong_concord"),


    path('admin/', admin.site.urls),
    path("", views.dashboard, name="index"),
    path("articulos/", views.article_list, name="article_list"),
    path("ensayos/", views.essay_list, name="essay_list"),
    path("ensayo/<slug:slug>/", views.essay_detail, name="essay_detail"),
    path("buscar/", views.search_view, name="search"),
    path("articulo/<slug:slug>/", views.article_detail, name="article_detail"),
    path("privacidad/", views.privacy, name="privacy"),
    path("terminos/", views.terms, name="terms"),
    path("creditos/", views.credits, name="credits"),
    path("contacto/", views.contact, name="contact"),
    path("estudios/", views.estudios, name="estudios"),
    path("planes/", views.planes, name="planes"),
    path("mis-estudios/", views.mis_estudios, name="mis_estudios"),
    path("apoyo/", views.apoyo, name="apoyo"),
    path("madres/", views.madres_maestras, name="madres_maestras"),
    path("madres/<slug:slug>/", views.madre_maestra_detail, name="madre_maestra_detail"),
    path("api/versiculo/", views.api_get_versiculo, name="api_get_versiculo"),
    path("api/estudios/guardar/", views.api_save_study, name="api_save_study"),
    path("api/estudios/<int:study_id>/", views.api_get_study, name="api_get_study"),
    path("api/strong/<int:numero>/", views.api_get_strong, name="api_get_strong"),
    path("api/contexto/<int:libro_numero>/", views.api_get_contexto_libro, name="api_get_contexto_libro"),
    path("palabra/<str:idioma>/<str:pk>/", views.palabra_detalle, name="palabra_detalle"),
    
    # Auth URLs
    path("registro/", views.register_view, name="register"),
    path("verificar-email/", views.verify_email_view, name="verify_email"),
    path("iniciar-sesion/", views.login_view, name="login"),
    path("cerrar-sesion/", views.logout_view, name="logout"),
    path("perfil/", views.profile_view, name="profile"),
    path("api/perfil/avatar/", views.api_update_avatar, name="update_avatar"),
    path("api/paypal/subscription/activate/", views.api_paypal_activate, name="api_paypal_activate"),

    # Portal de Autores
    path("autores/panel/", views_authors.author_dashboard, name="author_dashboard"),
    path("autores/articulo/nuevo/", views_authors.author_article_create, name="author_article_create"),
    path("autores/articulo/<int:article_id>/editar/", views_authors.author_article_edit, name="author_article_edit"),

    # Allauth (Google OAuth, etc.)
    path("accounts/", include("allauth.urls")),

    # API Bible Sync Endpoints for the Admin Panel
    path("api/admin/bible-status/", views_api_bible.api_bible_status, name="api_bible_status"),
    path("api/admin/bible-sync/<str:version_key>/setup/", views_api_bible.api_bible_sync_book_setup, name="api_bible_sync_book_setup"),
    path("api/admin/bible-sync/<str:version_key>/sync/<int:libro_num>/<int:capitulo_num>/", views_api_bible.api_bible_sync_chapter, name="api_bible_sync_chapter"),
    path("api/admin/bible-sync/<str:version_key>/finish/", views_api_bible.api_bible_finish_sync, name="api_bible_finish_sync"),

    # YouVersion Platform API
    path("api/youversion/bibles/", views_youversion.youversion_bibles, name="youversion_bibles"),
    path("api/youversion/chapter/", views_youversion.youversion_chapter, name="youversion_chapter"),

    # SEO
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", robots_txt, name="robots_txt"),
]

handler400 = "main_florife.views.handler400"
handler403 = "main_florife.views.handler403"
handler404 = "main_florife.views.handler404"
handler500 = "main_florife.views.handler500"
