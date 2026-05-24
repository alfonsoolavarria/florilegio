from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Article, Essay


class ArticleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Article.objects.filter(status='liberado')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('article_detail', args=[obj.slug])


class EssaySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Essay.objects.filter(status='liberado')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('essay_detail', args=[obj.slug])


class StaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return ['index', 'article_list', 'essay_list', 'estudios', 'planes', 'apoyo', 'contacto', 'privacidad', 'terminos', 'creditos']

    def location(self, item):
        return reverse(item)
