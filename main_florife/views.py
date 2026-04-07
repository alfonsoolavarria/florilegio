import json
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Article, Category, LibroBiblia

def dashboard(request):
    featured_articles = Article.objects.filter(is_featured=True, status='liberado')[:6]
    latest_articles = Article.objects.filter(is_featured=False, status='liberado').order_by('-created_at')
    categories = Category.objects.all()
    
    return render(request, 'index.html', {
        "featured_articles": featured_articles,
        "latest_articles": latest_articles,
        "categories": categories
    })

def article_list(request):
    category_id = request.GET.get('categoria')
    categories = Category.objects.all()
    articles = Article.objects.filter(status='liberado').order_by('-created_at')
    
    selected_category = None
    if category_id:
        selected_category = get_object_or_404(Category, id=category_id)
        articles = articles.filter(category=selected_category)
    
    paginator = Paginator(articles, 9) # 9 articles per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'article-list.html', {
        "page_obj": page_obj,
        "categories": categories,
        "selected_category": selected_category
    })

def search_view(request):
    query = request.GET.get('q')
    results = Article.objects.filter(status='liberado').order_by('-created_at')
    
    if query:
        results = results.filter(
            Q(title__unaccent__icontains=query) | 
            Q(content__unaccent__icontains=query)
        )
    
    paginator = Paginator(results, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'search-results.html', {
        "page_obj": page_obj,
        "query": query
    })

def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, status='liberado')
    related_articles = Article.objects.filter(
        category=article.category, 
        status='liberado'
    ).exclude(id=article.id)[:3]
    categories = Category.objects.all()
    
    return render(request, 'blog-details.html', {
        "article": article,
        "related_articles": related_articles,
        "categories": categories
    })

def privacy(request):
    return render(request, 'privacy.html')

def terms(request):
    return render(request, 'terms.html')

def contact(request):
    return render(request, 'contact.html')

def estudios(request):
    libros_nt = LibroBiblia.objects.filter(testamento="Nuevo Testamento").order_by('numero')
    
    estructura_datos = {libro.numero: libro.estructura_capitulos for libro in libros_nt}
    
    return render(request, 'estudios.html', {
        'libros': libros_nt,
        'estructura_json': json.dumps(estructura_datos, cls=DjangoJSONEncoder)
    })

def api_get_versiculo(request):
    tipo = request.GET.get('tipo', 'estudio')
    libro = request.GET.get('libro')
    capitulo = request.GET.get('capitulo')
    versiculo = request.GET.get('versiculo') # Opcional en modo biblia, pero se usa para scroll/enfocar
    version = request.GET.get('version', 'rv1960')
    
    if not all([libro, capitulo]):
        return JsonResponse({'status': 'error', 'message': 'Faltan parámetros requeridos (libro, capitulo).'}, status=400)
    
    try:
        from .models import PalabraBiblia, VersiculoBiblia
        
        if tipo == 'biblia':
            # Obtener todos los versículos del capítulo
            versiculos = VersiculoBiblia.objects.filter(
                version=version,
                libro=libro,
                capitulo=capitulo
            ).order_by('versiculo')
            
            data = []
            for v in versiculos:
                data.append({
                    'versiculo': v.versiculo,
                    'texto': v.texto
                })
            return JsonResponse({'status': 'success', 'modo': 'biblia', 'data': data})
            
        else:
            # Modo estudio (interlineal) - Solo el versículo específico
            if not versiculo:
                return JsonResponse({'status': 'error', 'message': 'El modo estudio requiere un versículo específico.'}, status=400)
                
            palabras = PalabraBiblia.objects.filter(
                libro=libro, 
                capitulo=capitulo, 
                versiculo=versiculo
            ).select_related('traduccion', 'morfologia').order_by('ognt_sort')
            
            data = []
            for p in palabras:
                data.append({
                    'ognt_sort': p.ognt_sort,
                    'espanol': p.traduccion.espanol if hasattr(p, 'traduccion') else '',
                    'griego': p.traduccion.griego if hasattr(p, 'traduccion') else '',
                    'raiz_griega': p.traduccion.raiz_griega if hasattr(p, 'traduccion') else '',
                    'rmac': p.morfologia.rmac if hasattr(p, 'morfologia') else '',
                    'descripcion_rmac': p.morfologia.descripcion_rmac if hasattr(p, 'morfologia') else '',
                    'low_nida_number': p.morfologia.low_nida_number if hasattr(p, 'morfologia') else '',
                    'strong': p.morfologia.strong if hasattr(p, 'morfologia') else '',
                })
            # Buscar el texto en la versión RV1960 para mostrar arriba del interlineal
            texto_rv1960 = ""
            try:
                v_obj = VersiculoBiblia.objects.get(version='rv1960', libro=libro, capitulo=capitulo, versiculo=versiculo)
                texto_rv1960 = v_obj.texto
            except VersiculoBiblia.DoesNotExist:
                pass
                
            return JsonResponse({'status': 'success', 'modo': 'estudio', 'texto_rv1960': texto_rv1960, 'data': data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)