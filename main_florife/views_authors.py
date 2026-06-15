import re
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Article, Author, Category


def _get_author(user):
    return getattr(user, 'author_profile', None)


def _author_required(view):
    def wrapper(request, *args, **kwargs):
        author = _get_author(request.user)
        if not author:
            return HttpResponseForbidden("No tienes un perfil de autor asignado.")
        return view(request, author, *args, **kwargs)
    return wrapper


@login_required
@_author_required
def author_dashboard(request, author):
    articles = Article.objects.filter(author=author).order_by('-created_at')
    return render(request, 'autores/panel.html', {
        'author': author,
        'articles': articles,
        'seo_title': 'Panel de Autor - Florilegio de la Fe',
    })


@login_required
@_author_required
def author_article_create(request, author):
    categories = Category.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        category_id = request.POST.get('category')
        image_url = request.POST.get('image_url', '').strip()

        errors = {}
        if not title:
            errors['title'] = 'El título es obligatorio.'
        if not content:
            errors['content'] = 'El contenido es obligatorio.'
        if not category_id:
            errors['category'] = 'Selecciona una categoría.'

        if not errors:
            slug = _generate_slug(title)
            # Ensure unique slug
            base_slug = slug
            counter = 1
            while Article.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            Article.objects.create(
                title=title,
                slug=slug,
                author=author,
                category_id=category_id,
                image_url=image_url or 'https://via.placeholder.com/800x400',
                content=content,
                status='revision',
            )
            return redirect('author_dashboard')

        return render(request, 'autores/articulo_form.html', {
            'author': author,
            'categories': categories,
            'errors': errors,
            'data': request.POST,
            'seo_title': 'Nuevo Artículo - Florilegio de la Fe',
        })

    return render(request, 'autores/articulo_form.html', {
        'author': author,
        'categories': categories,
        'seo_title': 'Nuevo Artículo - Florilegio de la Fe',
    })


@login_required
@_author_required
def author_article_edit(request, author, article_id):
    article = get_object_or_404(Article, id=article_id, author=author)
    categories = Category.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        category_id = request.POST.get('category')
        image_url = request.POST.get('image_url', '').strip()

        errors = {}
        if not title:
            errors['title'] = 'El título es obligatorio.'
        if not content:
            errors['content'] = 'El contenido es obligatorio.'
        if not category_id:
            errors['category'] = 'Selecciona una categoría.'

        if not errors:
            article.title = title
            article.content = content
            article.category_id = category_id
            article.image_url = image_url or 'https://via.placeholder.com/800x400'
            article.save()
            return redirect('author_dashboard')

        return render(request, 'autores/articulo_form.html', {
            'author': author,
            'categories': categories,
            'article': article,
            'errors': errors,
            'data': request.POST,
            'seo_title': f'Editar: {article.title} - Florilegio de la Fe',
        })

    return render(request, 'autores/articulo_form.html', {
        'author': author,
        'categories': categories,
        'article': article,
        'seo_title': f'Editar: {article.title} - Florilegio de la Fe',
    })


def _generate_slug(title):
    slug = title.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    slug = slug.strip('-')
    return slug or 'articulo'
