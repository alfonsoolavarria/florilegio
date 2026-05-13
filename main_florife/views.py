import json
import re
import random
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
from django.views.decorators.http import require_POST
from .models import Article, Category, LibroBiblia, Essay, UserStudy

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
    paginator = Paginator(articles, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'article-list.html', {
        "page_obj": page_obj,
        "categories": categories,
        "selected_category": selected_category
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
    return render(request, 'essays.html', {
        "page_obj": page_obj,
        "categories": categories,
        "selected_category": selected_category,
        "query": query
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
        "toc_items": toc_items
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
    return render(request, 'contact.html', {'sent': sent, 'error': error})

def apoyo(request):
    return render(request, 'apoyo.html')

def planes(request):
    return render(request, 'planes.html')


def estudios(request):
    libros_nt = LibroBiblia.objects.filter(testamento="Nuevo Testamento").order_by('numero')
    estructura_datos = {libro.numero: libro.estructura_capitulos for libro in libros_nt}
    return render(request, 'estudios.html', {
        'libros': libros_nt,
        'estructura_json': json.dumps(estructura_datos, cls=DjangoJSONEncoder)
    })


@login_required
def mis_estudios(request):
    studies = UserStudy.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'mis_estudios.html', {
        'studies': studies
    })


@login_required
@require_POST
def api_save_study(request):
    data = json.loads(request.body)
    content = data.get('content', '')
    title = data.get('title', '')
    reference = data.get('reference', '')
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
            texto_rv1960 = ""
            try:
                v_obj = VersiculoBiblia.objects.get(version='rv1960', libro=libro, capitulo=capitulo, versiculo=versiculo)
                texto_rv1960 = v_obj.texto
            except VersiculoBiblia.DoesNotExist:
                pass
            return JsonResponse({'status': 'success', 'modo': 'estudio', 'texto_rv1960': texto_rv1960, 'data': data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


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
        if not re.match(r'^[^@]+@[^@]+\.com$', email):
            return render(request, 'registration/register.html', {'error': 'Ingresa un correo válido que termine en .com', 'next': next_url})

        code = str(random.randint(100000, 999999))
        request.session['pending_email'] = email
        request.session['pending_password'] = password1
        request.session['pending_nombre'] = nombre
        request.session['pending_code'] = code
        request.session['pending_next'] = next_url

        sent = _send_brevo_code(email, code)
        if not sent:
            api_key_set = bool(settings.BREVO_API_KEY)
            template_set = bool(settings.BREVO_TEMPLATE_ID)
            return render(request, 'registration/register.html', {
                'error': f'Error al enviar el código. Verifica que BREVO_API_KEY y BREVO_TEMPLATE_ID estén configurados en .env y reinicia el servidor. (API: {"✓" if api_key_set else "✗"}, Template: {"✓" if template_set else "✗"})'
            })

        return redirect('verify_email')
    return render(request, 'registration/register.html', {
        'next': request.GET.get('next', '/')
    })


def verify_email_view(request):
    if request.method == 'POST':
        entered_code = request.POST.get('code', '').strip()
        stored_code = request.session.get('pending_code')
        email = request.session.get('pending_email')
        password = request.session.get('pending_password')
        nombre = request.session.get('pending_nombre', '')

        if not stored_code or not email:
            return redirect('register')

        if entered_code != stored_code:
            return render(request, 'registration/verify_email.html', {
                'email': email,
                'error': 'Código incorrecto. Intenta de nuevo.'
            })

        username = email.split('@')[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=nombre
        )

        next_url = request.session.get('pending_next', '/')
        for key in ['pending_email', 'pending_password', 'pending_nombre', 'pending_code', 'pending_next']:
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
