import os
import json
from io import StringIO
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.management import call_command
from django.conf import settings
from main_florife.models import VersiculoBiblia, TraduccionHebreo, StrongConcord, LouwNidaConcord

VERSION_MAP = {
    'spa_r09': {'file': 'spa_r09.json', 'name': 'Reina Valera 1909'},
    'spa_bes': {'file': 'spa_bes.json', 'name': 'Biblia Española, Traducción Interconfesional (BES)'},
    'spa_blm': {'file': 'spa_blm.json', 'name': 'La Biblia de las Américas (LBLA)'},
    'spa_pdt': {'file': 'spa_pdt.json', 'name': 'Palabra de Dios para Todos (PDT)'},
    'spa_rvg': {'file': 'spa_rvg.json', 'name': 'Reina Valera Gómez (RVG)'},
    'BSB': {'file': 'BSB.json', 'name': 'Berean Standard Bible (BSB)'},
}


@staff_member_required
def admin_bible_import(request):
    data_dir = os.path.join(settings.BASE_DIR, 'data')

    if request.method == 'POST':
        version_id = request.POST.get('version_id')
        if version_id and version_id in VERSION_MAP:
            out = StringIO()
            err = StringIO()
            try:
                call_command('import_ebible_version', version_id=version_id, force=True, stdout=out, stderr=err)
                result = out.getvalue()
                if err.getvalue():
                    result += '\n' + err.getvalue()
                messages.success(request, result)
            except Exception as e:
                messages.error(request, f'Error: {e}')
        else:
            messages.error(request, f'Versión no válida: {version_id}')
        return redirect('admin_bible_import')

    versions = []
    for vid, info in VERSION_MAP.items():
        file_path = os.path.join(data_dir, info['file'])
        exists = os.path.exists(file_path)
        file_size = os.path.getsize(file_path) if exists else 0
        existing_count = VersiculoBiblia.objects.filter(version=vid).count()
        versions.append({
            'id': vid,
            'name': info['name'],
            'file_name': info['file'],
            'file_exists': exists,
            'file_size': file_size,
            'imported_count': existing_count,
        })

    return render(request, 'admin/bible_import.html', {
        'versions': versions,
        'title': 'Importar Versiones Bíblicas',
    })


@staff_member_required
def admin_import_rv1960_strongs(request):
    filepath = os.path.join(settings.BASE_DIR, 'rvs_strongs_ot.json')

    if request.method == 'POST':
        out = StringIO()
        err = StringIO()
        try:
            call_command('populate_espanol_hebreo', force=True, stdout=out, stderr=err)
            result = out.getvalue()
            if err.getvalue():
                result += '\n' + err.getvalue()
            messages.success(request, result)
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect('admin_import_rv1960_strongs')

    file_exists = os.path.exists(filepath)
    file_size = os.path.getsize(filepath) if file_exists else 0
    strongs_count = 0
    if file_exists:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for bk in data.values():
                for ch in bk['chapters'].values():
                    for v in ch:
                        strongs_count += len(v['words'])

    imported_count = TraduccionHebreo.objects.filter(espanol__isnull=False).exclude(espanol='').count()

    return render(request, 'admin/import_rv1960_strongs.html', {
        'file_exists': file_exists,
        'file_size': file_size,
        'strongs_count': strongs_count,
        'imported_count': imported_count,
        'total_count': TraduccionHebreo.objects.count(),
        'title': 'Importar RV1960 con Números Strong (AT)',
    })


@staff_member_required
def admin_import_strong_concord(request):
    hebreo_path = os.path.join(settings.BASE_DIR, 'strong_hebreo.json')
    griego_path = os.path.join(settings.BASE_DIR, 'strong_griego.json')

    if request.method == 'POST':
        out = StringIO()
        err = StringIO()
        try:
            call_command('import_strong_from_json', force=True, stdout=out, stderr=err)
            result = out.getvalue()
            if err.getvalue():
                result += '\n' + err.getvalue()
            messages.success(request, result)
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect('admin_import_strong_concord')

    heb_exists = os.path.exists(hebreo_path)
    gri_exists = os.path.exists(griego_path)
    heb_size = os.path.getsize(hebreo_path) if heb_exists else 0
    gri_size = os.path.getsize(griego_path) if gri_exists else 0

    heb_count = 0
    if heb_exists:
        with open(hebreo_path, encoding='utf-8') as f:
            data = json.load(f)
            heb_count = len(data[list(data.keys())[0]])

    gri_count = 0
    if gri_exists:
        with open(griego_path, encoding='utf-8') as f:
            data = json.load(f)
            gri_count = len(data[list(data.keys())[0]])

    imported_count = StrongConcord.objects.count()
    h_count = StrongConcord.objects.filter(topic__startswith='H').count()
    g_count = StrongConcord.objects.filter(topic__startswith='G').count()

    return render(request, 'admin/import_strong_concord.html', {
        'heb_exists': heb_exists,
        'gri_exists': gri_exists,
        'heb_size': heb_size,
        'gri_size': gri_size,
        'heb_count': heb_count,
        'gri_count': gri_count,
        'imported_count': imported_count,
        'h_count': h_count,
        'g_count': g_count,
        'title': 'Importar Strong Definitions (strong_concord)',
    })


@staff_member_required
def admin_import_louw_nida(request):
    filepath = os.path.join(settings.BASE_DIR, 'louw_nida.json')

    if request.method == 'POST':
        out = StringIO()
        err = StringIO()
        try:
            call_command('import_louw_nida_from_json', force=True, stdout=out, stderr=err)
            result = out.getvalue()
            if err.getvalue():
                result += '\n' + err.getvalue()
            messages.success(request, result)
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect('admin_import_louw_nida')

    file_exists = os.path.exists(filepath)
    file_size = os.path.getsize(filepath) if file_exists else 0

    json_count = 0
    if file_exists:
        with open(filepath, encoding='utf-8') as f:
            data = json.load(f)
        key = list(data.keys())[0]
        json_count = len(data[key])

    imported_count = LouwNidaConcord.objects.count()

    return render(request, 'admin/import_louw_nida.html', {
        'file_exists': file_exists,
        'file_size': file_size,
        'json_count': json_count,
        'imported_count': imported_count,
        'title': 'Importar Louw-Nida (louw_nida_concord)',
    })
