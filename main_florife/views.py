from django.shortcuts import render, get_object_or_404
from .models import Article, Category

def dashboard(request):
    featured_articles = Article.objects.filter(is_featured=True)[:6]
    latest_articles = Article.objects.filter(is_featured=False).order_by('-created_at')
    categories = Category.objects.all()
    
    # Optional: If you want to keep the counts as they were in the mock
    # categories_with_counts = []
    # for cat in categories:
    #     categories_with_counts.append({
    #         "name": cat.name,
    #         "icon": cat.icon,
    #         "count": cat.articles.count()
    #     })

    return render(request, 'index.html', {
        "featured_articles": featured_articles,
        "latest_articles": latest_articles,
        "categories": categories
    })

def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    return render(request, 'blog-details.html', {"article": article})