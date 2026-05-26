import json
import re
import random
import bleach
import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit
from .models import Article, Category, LibroBiblia, Essay, UserStudy

BLEACH_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'blockquote', 'pre', 'code', 'hr',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'a', 'img', 'figure', 'span', 'div',
]
BLEACH_ATTRS = {
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'width', 'height'],
    'span': ['class', 'style'],
    'td': ['style', 'colspan', 'rowspan'],
    'th': ['style', 'colspan', 'rowspan'],
    'div': ['class', 'style'],
    'table': ['style'],
    '*': ['class', 'id', 'style'],
}

def dashboard(request):
    featured_articles = Article.objects.filter(is_featured=True, status='liberado')[:6]
    latest_articles = Article.objects.filter(is_featured=False, status='liberado').order_by('-created_at')
    categories = Category.objects.all()
    return render(request, 'index.html', {
        "featured_articles": featured_articles,
        "latest_articles": latest_articles,
        "categories": categories,
        "seo_title": "Florilegio de la Fe - Teología, Historia y Biografías Cristianas",
        "seo_description": "Profundiza en la intimidad con Dios a través de artículos de teología, historia de la iglesia, biografías cristianas y estudio bíblico.",
    })

def article_list(request):
    category_id = request.GET.get('categoria')
    categories = Category.objects.all()
    articles = Article.objects.filter(status='liberado').order_by('-created_at')
    selected_category = None
    if category_id:
        selected_category = get_object_or_404(Category, id=category_id)
        articles = articles.filter(category=selected_category)
    paginator = Paginator(articles, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if selected_category:
        seo_title = f"Artículos sobre {selected_category.name} - Florilegio de la Fe"
        seo_description = f"Explora artículos sobre {selected_category.name}. Teología, historia y biografías cristianas."
    else:
        seo_title = "Artículos - Florilegio de la Fe"
        seo_description = "Explora todos los artículos de teología, historia de la iglesia y biografías cristianas."

    return render(request, 'article-list.html', {
        "page_obj": page_obj,
        "categories": categories,
        "selected_category": selected_category,
        "seo_title": seo_title,
        "seo_description": seo_description,
    })

def essay_list(request):
    category_id = request.GET.get('categoria')
    query = request.GET.get('q')
    categories = Category.objects.all()
    essays = Essay.objects.filter(status='liberado').order_by('-created_at')
    selected_category = None
    if category_id:
        selected_category = get_object_or_404(Category, id=category_id)
        essays = essays.filter(category=selected_category)
    if query:
        essays = essays.filter(
            Q(title__unaccent__icontains=query) |
            Q(content__unaccent__icontains=query)
        )
    paginator = Paginator(essays, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if selected_category:
        seo_title = f"Ensayos sobre {selected_category.name} - Florilegio de la Fe"
        seo_description = f"Ensayos teológicos sobre {selected_category.name}. Estudios profundos sobre la fe."
    else:
        seo_title = "Ensayos - Florilegio de la Fe"
        seo_description = "Ensayos teológicos profundos sobre la fe, la Biblia y la historia de la iglesia."

    return render(request, 'essays.html', {
        "page_obj": page_obj,
        "categories": categories,
        "selected_category": selected_category,
        "query": query,
        "seo_title": seo_title,
        "seo_description": seo_description,
    })

def essay_detail(request, slug):
    essay = get_object_or_404(Essay, slug=slug, status='liberado')
    related_essays = Essay.objects.filter(
        category=essay.category,
        status='liberado'
    ).exclude(id=essay.id)[:3]
    
    # Generate TOC from content
    toc_items = []
    counter = {'h2': 0, 'h3': 0}
    content = essay.content
    
    # Find all h2 and h3 tags
    pattern = r'<(h[23])[^>]*>(.*?)</\1>'
    headings = re.findall(pattern, content, re.DOTALL)
    
    for i, (tag, text) in enumerate(headings):
        # Clean text (remove HTML tags)
        clean_text = re.sub(r'<[^>]+>', '', text).strip()
        if tag == 'h2':
            counter['h2'] += 1
            counter['h3'] = 0
            number = str(counter['h2']) + '.'
        else:  # h3
            counter['h3'] += 1
            number = str(counter['h2']) + '.' + str(counter['h3']) + '.'
        heading_id = 'section-' + str(i)
        toc_items.append({
            'id': heading_id,
            'number': number,
            'text': clean_text,
            'tag': tag
        })
        # Add id and number to the heading in content
        old_heading = '<' + tag + '>' + text + '</' + tag + '>'
        new_heading = '<' + tag + ' id="' + heading_id + '">' + number + ' ' + text + '</' + tag + '>'
        content = content.replace(old_heading, new_heading, 1)
    
    # Update essay content with IDs
    essay.content_with_ids = content

    return render(request, 'essay_detail.html', {
        "essay": essay,
        "related_essays": related_essays,
        "toc_items": toc_items,
        "seo_title": f"{essay.title} - Florilegio de la Fe",
        "seo_description": essay.seo_description,
        "seo_image": essay.image_url,
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

    seo_title = f"Búsqueda: {query} - Florilegio de la Fe" if query else "Buscar - Florilegio de la Fe"
    seo_description = "Resultados de búsqueda de artículos teológicos, históricos y biografías cristianas."

    return render(request, 'search-results.html', {
        "page_obj": page_obj,
        "query": query,
        "seo_title": seo_title,
        "seo_description": seo_description,
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
        "categories": categories,
        "seo_title": f"{article.title} - Florilegio de la Fe",
        "seo_description": article.seo_description,
        "seo_image": article.image_url,
    })

def privacy(request):
    return render(request, 'privacy.html', {
        'seo_title': 'Política de Privacidad - Florilegio de la Fe',
        'seo_description': 'Política de privacidad y protección de datos de Florilegio de la Fe.',
    })

def terms(request):
    return render(request, 'terms.html', {
        'seo_title': 'Términos y Condiciones - Florilegio de la Fe',
        'seo_description': 'Términos y condiciones de uso del sitio Florilegio de la Fe.',
    })

def credits(request):
    return render(request, 'credits.html', {
        'seo_title': 'Créditos - Florilegio de la Fe',
        'seo_description': 'Créditos y atribuciones de Florilegio de la Fe.',
    })

@ratelimit(key='ip', rate='3/h', method='POST')
def contact(request):
    sent = False
    error = None
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        correo = request.POST.get('correo', '').strip()
        asunto = request.POST.get('asunto', '').strip()
        mensaje = request.POST.get('mensaje', '').strip()
        if not all([nombre, correo, asunto, mensaje]):
            error = 'Todos los campos son obligatorios.'
        else:
            api_key = settings.BREVO_API_KEY
            if api_key:
                try:
                    resp = requests.post(
                        'https://api.brevo.com/v3/smtp/email',
                        headers={
                            'api-key': api_key,
                            'Content-Type': 'application/json',
                            'Accept': 'application/json',
                        },
                        json={
                            'to': [{'email': 'florilegiodelafe@gmail.com'}],
                            'subject': f'[Contacto] {asunto}',
                            'htmlContent': f'<h3>Nuevo mensaje de contacto</h3>'
                                           f'<p><strong>Nombre:</strong> {nombre}</p>'
                                           f'<p><strong>Correo:</strong> {correo}</p>'
                                           f'<p><strong>Asunto:</strong> {asunto}</p>'
                                           f'<p><strong>Mensaje:</strong></p>'
                                           f'<p>{mensaje}</p>',
                            'replyTo': {'email': correo, 'name': nombre},
                        },
                        timeout=10,
                    )
                    sent = resp.ok
                except requests.RequestException:
                    error = 'Error de conexión. Intenta de nuevo.'
            else:
                sent = True  # sin Brevo configurado, simular éxito
            if not sent:
                error = 'Error al enviar el mensaje. Intenta de nuevo.'
    return render(request, 'contact.html', {
        'sent': sent,
        'error': error,
        'seo_title': 'Contacto - Florilegio de la Fe',
        'seo_description': 'Comunícate con el equipo de Florilegio de la Fe.',
    })

def apoyo(request):
    return render(request, 'apoyo.html', {
        'paypal_client_id': settings.PAYPAL_CLIENT_ID,
        'paypal_plan_donation_monthly': settings.PAYPAL_PLAN_DONATION_MONTHLY,
        'paypal_plan_donation_annual': settings.PAYPAL_PLAN_DONATION_ANNUAL,
        'seo_title': 'Apoya - Florilegio de la Fe',
        'seo_description': 'Apoya el ministerio de Florilegio de la Fe con tu donación.',
    })

def planes(request):
    return render(request, 'planes.html', {
        'paypal_client_id': settings.PAYPAL_CLIENT_ID,
        'paypal_plan_premium': settings.PAYPAL_PLAN_PREMIUM,
        'paypal_plan_pro': settings.PAYPAL_PLAN_PRO,
        'seo_title': 'Planes - Florilegio de la Fe',
        'seo_description': 'Planes premium y pro de Florilegio de la Fe para estudios bíblicos avanzados.',
    })


def estudios(request):
    libros_ot = LibroBiblia.objects.filter(testamento="Antiguo Testamento").order_by('numero')
    libros_nt = LibroBiblia.objects.filter(testamento="Nuevo Testamento").order_by('numero')
    libros_todos = list(libros_ot) + list(libros_nt)
    estructura_datos = {libro.numero: libro.estructura_capitulos for libro in libros_todos}
    return render(request, 'estudios.html', {
        'libros_ot': libros_ot,
        'libros_nt': libros_nt,
        'estructura_json': json.dumps(estructura_datos, cls=DjangoJSONEncoder)
    })


@login_required
def mis_estudios(request):
    studies = UserStudy.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'mis_estudios.html', {
        'studies': studies
    })


@ratelimit(key='user_or_ip', rate='60/h', method='POST')
@login_required
@require_POST
def api_save_study(request):
    data = json.loads(request.body)
    content = bleach.clean(data.get('content', ''), tags=BLEACH_TAGS, attributes=BLEACH_ATTRS)
    title = bleach.clean(data.get('title', ''), tags=[])
    reference = bleach.clean(data.get('reference', ''), tags=[])
    study_id = data.get('study_id')
    
    if study_id:
        study = get_object_or_404(UserStudy, id=study_id, user=request.user)
        study.content = content
        study.title = title
        study.reference = reference
        study.save()
        return JsonResponse({
            'status': 'success',
            'message': 'Estudio actualizado correctamente.',
            'study_id': study.id,
            'updated': True
        })
    
    profile = request.user.profile
    limit = profile.study_limit()
    current_count = UserStudy.objects.filter(user=request.user).count()
    
    if limit is not None and current_count >= limit:
        return JsonResponse({
            'status': 'plan_limit_reached',
            'message': f'Has alcanzado el límite de {limit} estudios de tu plan. Actualiza tu plan para seguir guardando.',
            'limit': limit,
            'plan': profile.plan
        }, status=403)
    
    study = UserStudy.objects.create(
        user=request.user,
        title=title,
        reference=reference,
        content=content
    )
    
    return JsonResponse({
        'status': 'success',
        'message': 'Estudio guardado correctamente.',
        'study_id': study.id
    })


@ratelimit(key='user_or_ip', rate='60/h', method='GET')
@login_required
def api_get_study(request, study_id):
    try:
        study = UserStudy.objects.get(id=study_id, user=request.user)
        return JsonResponse({
            'status': 'success',
            'study': {
                'id': study.id,
                'title': study.title,
                'reference': study.reference,
                'content': study.content,
                'updated_at': study.updated_at.isoformat()
            }
        })
    except UserStudy.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Estudio no encontrado.'}, status=404)


def api_get_strong(request, numero):
    from .models import VineConcord

    try:
        results = VineConcord.objects.filter(strong_numbers__contains=[numero])
        data = [{'topic': r.topic, 'definition': r.definition} for r in results]
        return JsonResponse({'status': 'success', 'data': data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def palabra_detalle(request, idioma, pk):
    from .models import (
        StrongConcord, VineConcord,
        PalabraBiblia, TraduccionLiteral, Morfologia,
        PalabraHebreo, TraduccionHebreo, MorfologiaHebreo,
        LouwNidaConcord
    )

    word_data = {}
    strong_def = None
    vine_defs = []
    louw_nida_def = None
    strong_num = None

    try:
        if idioma == 'griego':
            palabra = PalabraBiblia.objects.select_related(
                'traduccion', 'morfologia'
            ).get(ognt_sort=pk)
            word_data = {
                'original': palabra.traduccion.griego if hasattr(palabra, 'traduccion') else '',
                'translation': palabra.traduccion.espanol if hasattr(palabra, 'traduccion') else '',
                'root': palabra.traduccion.raiz_griega if hasattr(palabra, 'traduccion') else '',
                'morph_code': palabra.morfologia.rmac if hasattr(palabra, 'morfologia') else '',
                'morph_desc': palabra.morfologia.descripcion_rmac if hasattr(palabra, 'morfologia') else '',
                'low_nida': palabra.morfologia.low_nida_number if hasattr(palabra, 'morfologia') else '',
                'ref': f'{palabra.libro}:{palabra.capitulo}:{palabra.versiculo}',
            }
            strong_num = palabra.morfologia.strong if hasattr(palabra, 'morfologia') else None
        elif idioma == 'hebreo':
            palabra = PalabraHebreo.objects.select_related(
                'traduccion_hebreo', 'morfologia_hebreo'
            ).get(oshb_id=pk)
            word_data = {
                'original': palabra.traduccion_hebreo.hebreo if hasattr(palabra, 'traduccion_hebreo') else '',
                'translation': palabra.traduccion_hebreo.espanol if hasattr(palabra, 'traduccion_hebreo') else '',
                'root': palabra.traduccion_hebreo.raiz_hebrea if hasattr(palabra, 'traduccion_hebreo') else '',
                'morph_code': palabra.morfologia_hebreo.morph_code if hasattr(palabra, 'morfologia_hebreo') else '',
                'morph_desc': describir_morfologia_hebrea(palabra.morfologia_hebreo.morph_code) if hasattr(palabra, 'morfologia_hebreo') and palabra.morfologia_hebreo.morph_code else '',
                'low_nida': '',
                'ref': f'{palabra.libro}:{palabra.capitulo}:{palabra.versiculo}',
            }
            strong_num = palabra.morfologia_hebreo.strong if hasattr(palabra, 'morfologia_hebreo') else None

    except (PalabraBiblia.DoesNotExist, PalabraHebreo.DoesNotExist):
        return render(request, 'palabra_detalle.html', {
            'error': 'Palabra no encontrada',
            'idioma': idioma,
        })

    if strong_num:
        strong_prefix = strong_num[0].upper()
        strong_key = strong_num if strong_prefix in ('G', 'H') else f'{idioma[0].upper()}{strong_num}'
        strong_def = StrongConcord.objects.filter(topic=strong_key).first()

        num_part = ''.join(c for c in strong_num if c.isdigit())
        if num_part:
            vine_defs = list(VineConcord.objects.filter(strong_numbers__contains=[int(num_part)]))

    if idioma == 'griego' and word_data.get('low_nida'):
        ln_id = word_data['low_nida'].removeprefix('LN-').strip()
        louw_nida_def = LouwNidaConcord.objects.filter(id=ln_id).first()

    word_data['strong_num'] = strong_num

    return render(request, 'palabra_detalle.html', {
        'idioma': idioma,
        'word': word_data,
        'strong_def': strong_def,
        'vine_defs': vine_defs,
        'louw_nida_def': louw_nida_def,
    })


def _desc_nombre(rest):
    GENERO = {'m': 'masculino', 'f': 'femenino', 'c': 'común', 'b': 'ambos'}
    NUMERO = {'s': 'singular', 'p': 'plural', 'd': 'dual'}
    ESTADO = {'a': 'absoluto', 'c': 'constructo', 'd': 'determinado'}
    features = []
    while rest:
        c = rest[0]
        is_last = len(rest) == 1
        if is_last and c in ESTADO:
            features.append(ESTADO[c])
        elif len(rest) >= 2 and rest[:2] == 'cb':
            features.append('común/ambos')
            rest = rest[1:]
        elif c in GENERO:
            features.append(GENERO[c])
        elif c in NUMERO:
            features.append(NUMERO[c])
        elif c in ESTADO:
            features.append(ESTADO[c])
        else:
            features.append(c)
        rest = rest[1:]
    return ', '.join(features)


def _desc_verbo(rest):
    VERBO_RAIZ = {
        'q': 'Qal', 'n': 'Niphal', 'p': 'Piel', 'h': 'Hiphil',
        't': 'Hithpael', 'o': 'Poel', 'm': 'Polel',
    }
    VERBO_FORMA = {
        'p': 'perfecto', 'i': 'imperfecto', 'j': 'yusivo',
        'h': 'cohortativo', 'q': 'participio', 'w': 'consecutivo',
        'v': 'consecutivo perfecto', 'c': 'infinitivo constructo',
        'a': 'infinitivo absoluto', 'r': 'participio',
    }
    GENERO = {'m': 'masculino', 'f': 'femenino'}
    NUMERO = {'s': 'singular', 'p': 'plural'}
    PERSONA = {'1': '1ª', '2': '2ª', '3': '3ª'}
    ESTADO = {'a': 'absoluto', 'c': 'constructo', 'd': 'determinado'}

    partes = []
    r = rest.lower() if rest else ''

    if r and r[0] in VERBO_RAIZ:
        partes.append(VERBO_RAIZ[r[0]])
        rest = rest[1:]
        r = r[1:]
    if r and r[0] in VERBO_FORMA:
        frm = VERBO_FORMA[r[0]]
        partes.append(frm)
        rest = rest[1:]
        r = r[1:]

        if frm == 'participio':
            if rest and rest[0] in GENERO:
                partes.append(GENERO[rest[0]])
                rest = rest[1:]
            if rest and rest[0] in NUMERO:
                partes.append(NUMERO[rest[0]])
                rest = rest[1:]
            if rest and rest[0] in ESTADO:
                partes.append(ESTADO[rest[0]])
                rest = rest[1:]
        else:
            if rest and rest[0] in PERSONA:
                partes.append(PERSONA[rest[0]])
                rest = rest[1:]
            if rest and rest[0] in GENERO:
                partes.append(GENERO[rest[0]])
                rest = rest[1:]
            if rest and rest[0] in NUMERO:
                partes.append(NUMERO[rest[0]])
                rest = rest[1:]
    return ', '.join(partes)


def _desc_pronombre(rest):
    GENERO = {'m': 'masculino', 'f': 'femenino', 'c': 'común'}
    NUMERO = {'s': 'singular', 'p': 'plural'}
    PERSONA = {'1': '1ª', '2': '2ª', '3': '3ª'}
    parts = []
    if rest.startswith('p'):
        rest = rest[1:]
        if rest and rest[0] in PERSONA:
            parts.append(PERSONA[rest[0]])
            rest = rest[1:]
        if rest and rest[0] in GENERO:
            parts.append(GENERO[rest[0]])
            rest = rest[1:]
        if rest and rest[0] in NUMERO:
            parts.append(NUMERO[rest[0]])
            rest = rest[1:]
    elif rest.startswith('dx'):
        parts.append('demostrativo')
        rest = rest[2:]
        if rest and rest[0] in GENERO:
            parts.append(GENERO[rest[0]])
            rest = rest[1:]
        if rest and rest[0] in NUMERO:
            parts.append(NUMERO[rest[0]])
            rest = rest[1:]
    elif rest.startswith('in'):
        parts.append('interrogativo')
    elif rest.startswith('r'):
        parts.append('relativo')
    return ', '.join(parts)


def _desc_adjetivo(rest):
    GENERO = {'m': 'masculino', 'f': 'femenino', 'c': 'común', 'b': 'ambos'}
    NUMERO = {'s': 'singular', 'p': 'plural', 'd': 'dual'}
    ESTADO = {'a': 'absoluto', 'c': 'constructo', 'd': 'determinado'}
    features = []
    while rest:
        c = rest[0]
        is_last = len(rest) == 1
        if is_last and c in ESTADO:
            features.append(ESTADO[c])
        elif len(rest) >= 2 and rest[:2] == 'ob':
            features.append('ob')
            rest = rest[1:]
        elif c in GENERO:
            features.append(GENERO[c])
        elif c in NUMERO:
            features.append(NUMERO[c])
        elif c in ESTADO:
            features.append(ESTADO[c])
        else:
            features.append(c)
        rest = rest[1:]
    return ', '.join(features)


def describir_morfologia_hebrea(morph):
    if not morph:
        return ''

    code = morph
    if code.startswith('H'):
        code = code[1:]

    PREFIJOS = {
        'C': 'conjunción',
        'R': 'preposición',
        'D': 'artículo definido',
        'T': 'marcador de objeto directo',
        'M': 'interrogativo',
        'B': 'preposición "en"',
        'K': 'preposición "como"',
        'L': 'preposición "a/para"',
        'W': 'conjunción',
    }

    TIPOS_POS = {
        'N': ('sustantivo', _desc_nombre),
        'V': ('verbo', _desc_verbo),
        'A': ('adjetivo', _desc_adjetivo),
        'P': ('pronombre', _desc_pronombre),
    }

    PREFIJO_COMPUESTO = {
        'Td': 'marcador de objeto directo + artículo',
    }

    parts = code.split('/')
    desc_parts = []

    for idx, part in enumerate(parts):
        if part in PREFIJO_COMPUESTO:
            desc_parts.append(PREFIJO_COMPUESTO[part])
            continue

        if part in ('R', 'D', 'C', 'M', 'B', 'K', 'L', 'W') and idx < len(parts) - 1:
            desc_parts.append(PREFIJOS.get(part, part))
            continue

        if part in ('C', 'D', 'M') and idx == len(parts) - 1 and len(parts) == 1:
            desc_parts.append(PREFIJOS.get(part, part))
            continue

        if part in ('R',) and idx == len(parts) - 1:
            desc_parts.append('preposición')
            continue
        if part == 'D' and idx == len(parts) - 1:
            desc_parts.append('artículo definido')
            continue
        if part == 'C':
            desc_parts.append('conjunción')
            continue

        if part.startswith('Sp'):
            rest = part[2:]
            suf = ['pronombre sufijo']
            PERSONA = {'1': '1ª', '2': '2ª', '3': '3ª'}
            GENERO = {'m': 'masculino', 'f': 'femenino'}
            NUMERO = {'s': 'singular', 'p': 'plural'}
            if rest and rest[0] in PERSONA:
                suf.append(PERSONA[rest[0]])
                rest = rest[1:]
            if rest and rest[0] in GENERO:
                suf.append(GENERO[rest[0]])
                rest = rest[1:]
            if rest and rest[0] in NUMERO:
                suf.append(NUMERO[rest[0]])
                rest = rest[1:]
            desc_parts.append(', '.join(suf))
            continue

        if part == 'Sd':
            desc_parts.append('artículo determinado')
            continue
        if part == 'Sh':
            desc_parts.append('interrogativo')
            continue
        if part == 'To':
            desc_parts.append('marcador de objeto directo')
            continue
        if part == 'Tn':
            desc_parts.append('marcador de objeto directo')
            continue
        if part == 'Ti':
            desc_parts.append('marcador de objeto directo')
            continue
        if part == 'Np':
            desc_parts.append('nombre propio')
            continue
        if part in ('Ngmpa', 'Ngmsa', 'Ngfp', 'Ngfs'):
            desc_parts.append('gentilicio')
            continue

        first = part[0] if part else ''
        if first in TIPOS_POS:
            pos_name, parser = TIPOS_POS[first]
            rest = part[1:]
            result = parser(rest)
            if result:
                desc_parts.append(f'{pos_name}: {result}')
            else:
                desc_parts.append(pos_name)
        else:
            if part:
                desc_parts.append(part)

    return ', '.join(desc_parts)


@ratelimit(key='ip', rate='200/m', method='GET')
def api_get_versiculo(request):
    tipo = request.GET.get('tipo', 'estudio')
    libro = request.GET.get('libro')
    capitulo = request.GET.get('capitulo')
    versiculo = request.GET.get('versiculo')
    version = request.GET.get('version', 'rv1960')
    if not all([libro, capitulo]):
        return JsonResponse({'status': 'error', 'message': 'Faltan parametros requeridos (libro, capitulo).'}, status=400)
    try:
        from .models import PalabraBiblia, VersiculoBiblia
        if tipo == 'biblia':
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
            if not versiculo:
                return JsonResponse({'status': 'error', 'message': 'El modo estudio requiere un versiculo especifico.'}, status=400)
            libro_int = int(libro)
            is_ot = libro_int <= 39
            if is_ot:
                from .models import PalabraHebreo
                palabras = PalabraHebreo.objects.filter(
                    libro=libro,
                    capitulo=capitulo,
                    versiculo=versiculo
                ).select_related('traduccion_hebreo', 'morfologia_hebreo').order_by('orden')
                data = []
                for p in palabras:
                    data.append({
                        'idioma': 'hebreo',
                        'oshb_id': p.oshb_id,
                        'espanol': p.traduccion_hebreo.espanol if hasattr(p, 'traduccion_hebreo') else '',
                        'hebreo': p.traduccion_hebreo.hebreo if hasattr(p, 'traduccion_hebreo') else '',
                        'raiz_hebrea': p.traduccion_hebreo.raiz_hebrea if hasattr(p, 'traduccion_hebreo') else '',
                        'morph_code': p.morfologia_hebreo.morph_code if hasattr(p, 'morfologia_hebreo') else '',
                        'descripcion_morfologia': describir_morfologia_hebrea(p.morfologia_hebreo.morph_code) if hasattr(p, 'morfologia_hebreo') and p.morfologia_hebreo.morph_code else '',
                        'strong': p.morfologia_hebreo.strong if hasattr(p, 'morfologia_hebreo') else '',
                        'rmac': '',
                        'descripcion_rmac': '',
                        'low_nida_number': '',
                        'griego': '',
                    })
            else:
                palabras = PalabraBiblia.objects.filter(
                    libro=libro,
                    capitulo=capitulo,
                    versiculo=versiculo
                ).select_related('traduccion', 'morfologia').order_by('ognt_sort')
                data = []
                for p in palabras:
                    data.append({
                        'idioma': 'griego',
                        'ognt_sort': p.ognt_sort,
                        'espanol': p.traduccion.espanol if hasattr(p, 'traduccion') else '',
                        'griego': p.traduccion.griego if hasattr(p, 'traduccion') else '',
                        'raiz_griega': p.traduccion.raiz_griega if hasattr(p, 'traduccion') else '',
                        'rmac': p.morfologia.rmac if hasattr(p, 'morfologia') else '',
                        'descripcion_rmac': p.morfologia.descripcion_rmac if hasattr(p, 'morfologia') else '',
                        'low_nida_number': p.morfologia.low_nida_number if hasattr(p, 'morfologia') else '',
                        'strong': p.morfologia.strong if hasattr(p, 'morfologia') else '',
                        'hebreo': '',
                        'raiz_hebrea': '',
                        'morph_code': '',
                    })
            texto_rv1960 = ""
            try:
                v_obj = VersiculoBiblia.objects.get(version='rv1960', libro=libro, capitulo=capitulo, versiculo=versiculo)
                texto_rv1960 = v_obj.texto
            except VersiculoBiblia.DoesNotExist:
                pass
            return JsonResponse({'status': 'success', 'modo': 'estudio', 'idioma': 'hebreo' if is_ot else 'griego', 'texto_rv1960': texto_rv1960, 'data': data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@ratelimit(key='ip', rate='5/h', method='POST')
def register_view(request):
    next_url = request.GET.get('next') or request.POST.get('next') or '/'
    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        nombre = request.POST.get('nombre', '')

        if not email or not password1 or not password2:
            return render(request, 'registration/register.html', {'error': 'Todos los campos son obligatorios.', 'next': next_url})
        if password1 != password2:
            return render(request, 'registration/register.html', {'error': 'Las contraseñas no coinciden.', 'next': next_url})
        if User.objects.filter(email=email).exists():
            return render(request, 'registration/register.html', {'error': 'Ya existe un usuario con ese correo.', 'next': next_url})

        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'registration/register.html', {'error': 'Ingresa un correo electrónico válido.', 'next': next_url})

        username = email.split('@')[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=nombre
        )
        user.is_active = False
        user.save()

        code = str(random.randint(100000, 999999))
        request.session['pending_email'] = email
        request.session['pending_user_id'] = user.id
        request.session['pending_code'] = code
        request.session['pending_next'] = next_url

        sent = _send_brevo_code(email, code)
        if not sent:
            user.delete()
            api_key_set = bool(settings.BREVO_API_KEY)
            template_set = bool(settings.BREVO_TEMPLATE_ID)
            return render(request, 'registration/register.html', {
                'error': f'Error al enviar el código. Verifica que BREVO_API_KEY y BREVO_TEMPLATE_ID estén configurados en .env y reinicia el servidor. (API: {"✓" if api_key_set else "✗"}, Template: {"✓" if template_set else "✗"})'
            })

        return redirect('verify_email')
    return render(request, 'registration/register.html', {
        'next': request.GET.get('next', '/')
    })


@ratelimit(key='ip', rate='10/15m', method='POST')
def verify_email_view(request):
    if request.method == 'POST':
        entered_code = request.POST.get('code', '').strip()
        stored_code = request.session.get('pending_code')
        email = request.session.get('pending_email')
        user_id = request.session.get('pending_user_id')

        if not stored_code or not email or not user_id:
            return redirect('register')

        if entered_code != stored_code:
            return render(request, 'registration/verify_email.html', {
                'email': email,
                'error': 'Código incorrecto. Intenta de nuevo.'
            })

        try:
            user = User.objects.get(id=user_id, email=email, is_active=False)
            user.is_active = True
            user.save()
        except User.DoesNotExist:
            return redirect('register')

        next_url = request.session.get('pending_next', '/')
        for key in ['pending_email', 'pending_user_id', 'pending_code', 'pending_next']:
            request.session.pop(key, None)

        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        return redirect(next_url)

    email = request.session.get('pending_email')
    if not email:
        return redirect('register')
    return render(request, 'registration/verify_email.html', {'email': email})


def _send_brevo_code(email, code):
    api_key = settings.BREVO_API_KEY
    template_id = settings.BREVO_TEMPLATE_ID
    if not api_key or not template_id:
        return False
    try:
        template_id = int(template_id)
    except (ValueError, TypeError):
        return False
    try:
        resp = requests.post(
            'https://api.brevo.com/v3/smtp/email',
            headers={
                'api-key': api_key,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            json={
                'to': [{'email': email}],
                'templateId': int(template_id),
                'params': {'CODE': code},
            },
            timeout=10,
        )
        return resp.ok
    except requests.RequestException:
        return False


@ratelimit(key='ip', rate='10/15m', method='POST')
def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next') or '/'
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect(next_url)
        return render(request, 'registration/login.html', {'error': 'Correo o contraseña inválidos.'})
    return render(request, 'registration/login.html')


@ratelimit(key='user_or_ip', rate='10/h', method='POST')
@login_required
@require_POST
def api_paypal_activate(request):
    data = json.loads(request.body)
    subscription_id = data.get('subscription_id')
    plan = data.get('plan')

    if not subscription_id or plan not in ('premium', 'pro'):
        return JsonResponse({'status': 'error', 'message': 'Datos inválidos.'}, status=400)

    profile = request.user.profile
    profile.plan = plan
    profile.save()

    return JsonResponse({'status': 'success', 'plan': plan, 'subscription_id': subscription_id})


@ratelimit(key='user_or_ip', rate='10/h', method='POST')
@login_required
@require_POST
def api_update_avatar(request):
    data = json.loads(request.body)
    avatar = data.get('avatar', '')
    profile = request.user.profile
    profile.avatar_url = avatar
    profile.save()
    return JsonResponse({'status': 'success', 'avatar': avatar})


def logout_view(request):
    logout(request)
    return redirect('/')


@login_required
def profile_view(request):
    import os
    avatares_dir = os.path.join(settings.BASE_DIR, 'static', 'avatares')
    avatares = []
    if os.path.isdir(avatares_dir):
        for f in sorted(os.listdir(avatares_dir)):
            if f.lower().endswith(('.webp', '.png', '.jpg', '.jpeg', '.gif')):
                avatares.append(f)
    return render(request, 'profile.html', {
        'profile_user': request.user,
        'avatares': avatares
    })


def handler404(request, exception):
    return render(request, '404.html', status=404)


def handler400(request, exception):
    return render(request, '400.html', status=400)


def handler403(request, exception):
    return render(request, '403.html', status=403)


def handler500(request):
    return render(request, '500.html', status=500)
